from __future__ import annotations

import math
from dataclasses import dataclass

import pymunk

from driveahead.content.vehicles import VehicleSpec
from driveahead.core.input import PlayerInput
from driveahead.physics.collision import CollisionType

WHEEL_X_FACTOR = 0.68
WHEEL_Y_FACTOR = 1.25
SUSPENSION_TRAVEL = 10
SUSPENSION_REST_LENGTH_FACTOR = 1.08
BODY_CENTER_OF_GRAVITY_Y_FACTOR = 0.46
GROUND_ROTATION_CONTROL = 0.22
AIR_ROTATION_CONTROL = 0.78
GROUNDED_ANGULAR_DAMPING = 0.82
AIR_ANGULAR_DAMPING = 0.985
MAX_ANGULAR_VELOCITY = 4.8
DRIVE_IMPULSE = 42.0
REVERSE_IMPULSE = 26.0
MAX_GROUND_SPEED = 220.0
DRIVE_POINT_Y_FACTOR = 0.05
GROUND_DRIVE_ACCEL = 32.0
GROUND_REVERSE_ACCEL = 24.0
UPRIGHT_TORQUE = 2600000.0
UPRIGHT_DAMPING_TORQUE = 340000.0
AIR_UPRIGHT_TORQUE = 650000.0
AIR_UPRIGHT_DAMPING_TORQUE = 130000.0
ACCELERATION_LEAN_BACK_TORQUE = 950000.0
COAST_GROUND_DAMPING = 0.86
COAST_MAX_SPEED = 90.0
ACCELERATION_LEAN_BACK_ANGLE = 0.18
ACCELERATION_LEAN_BLEND = 0.16


@dataclass
class Vehicle:
    player_id: int
    spec: VehicleSpec
    facing_direction: int
    body: pymunk.Body
    body_shape: pymunk.Poly
    front_wheel: pymunk.Body
    rear_wheel: pymunk.Body
    front_wheel_shape: pymunk.Circle
    rear_wheel_shape: pymunk.Circle
    head_shape: pymunk.Circle
    head_offset: tuple[float, float]
    constraints: list[pymunk.Constraint]
    has_rotation_input: bool = False
    drive_direction: int = 0
    is_accelerating: bool = False

    @property
    def position(self) -> tuple[float, float]:
        return float(self.body.position.x), float(self.body.position.y)

    @property
    def angle(self) -> float:
        return float(self.body.angle)

    def apply_input(self, player_input: PlayerInput) -> None:
        forward = pymunk.Vec2d(self.facing_direction, 0).rotated(self.body.angle)
        grounded = self._is_grounded()
        drive_point = self.body.local_to_world((0, self.spec.body_size[1] * DRIVE_POINT_Y_FACTOR))
        self.drive_direction = 0
        self.is_accelerating = False

        if player_input.accelerate:
            self.drive_direction = self.facing_direction
            self.is_accelerating = True
            self._cap_ground_speed(forward)
            if grounded:
                self._apply_arcade_drive(self.facing_direction, GROUND_DRIVE_ACCEL)
            else:
                self.body.apply_force_at_world_point(forward * self.spec.engine_force, drive_point)
                self.body.apply_impulse_at_world_point(
                    forward * self.spec.body_mass * DRIVE_IMPULSE,
                    drive_point,
                )
            self.front_wheel.angular_velocity -= 9 * self.facing_direction
            self.rear_wheel.angular_velocity -= 9 * self.facing_direction

        if player_input.brake:
            self.drive_direction = -self.facing_direction
            self.body.velocity *= self.spec.brake_force
            if grounded:
                self._cap_ground_speed(-forward)
                self._apply_arcade_drive(-self.facing_direction, GROUND_REVERSE_ACCEL)
                self.front_wheel.angular_velocity += 6 * self.facing_direction
                self.rear_wheel.angular_velocity += 6 * self.facing_direction
            else:
                self.body.apply_force_at_world_point(-forward * self.spec.engine_force * 0.6, drive_point)
                self.body.apply_impulse_at_world_point(
                    -forward * self.spec.body_mass * REVERSE_IMPULSE,
                    drive_point,
                )
                self.front_wheel.angular_velocity *= self.spec.brake_force
                self.rear_wheel.angular_velocity *= self.spec.brake_force

        torque = 0.0
        if player_input.rotate_left:
            torque -= self.spec.air_rotation_torque
        if player_input.rotate_right:
            torque += self.spec.air_rotation_torque
        self.has_rotation_input = bool(torque)
        if torque:
            modifier = GROUND_ROTATION_CONTROL if grounded else AIR_ROTATION_CONTROL
            self.body.torque += torque * modifier
        elif self.is_accelerating and grounded:
            self.body.torque += self.facing_direction * ACCELERATION_LEAN_BACK_TORQUE
        self._stabilize_rotation(grounded, self.has_rotation_input or self.is_accelerating)

    def _is_grounded(self) -> bool:
        return (
            abs(self.front_wheel.velocity.y) < 420
            or abs(self.rear_wheel.velocity.y) < 420
        )

    def _stabilize_rotation(self, grounded: bool, has_rotation_input: bool) -> None:
        if not has_rotation_input:
            angle = math.atan2(math.sin(self.body.angle), math.cos(self.body.angle))
            upright_torque = UPRIGHT_TORQUE if grounded else AIR_UPRIGHT_TORQUE
            damping_torque = UPRIGHT_DAMPING_TORQUE if grounded else AIR_UPRIGHT_DAMPING_TORQUE
            self.body.torque += -angle * upright_torque
            self.body.torque += -self.body.angular_velocity * damping_torque
        damping = GROUNDED_ANGULAR_DAMPING if grounded else AIR_ANGULAR_DAMPING
        self.body.angular_velocity *= damping
        self.body.angular_velocity = max(
            -MAX_ANGULAR_VELOCITY,
            min(MAX_ANGULAR_VELOCITY, self.body.angular_velocity),
        )

    def _cap_ground_speed(self, direction: pymunk.Vec2d) -> None:
        directional_speed = self.body.velocity.dot(direction.normalized())
        if directional_speed <= MAX_GROUND_SPEED:
            return
        excess = directional_speed - MAX_GROUND_SPEED
        correction = direction.normalized() * excess
        for body in self._rig_bodies():
            body.velocity -= correction

    def _apply_arcade_drive(self, direction: int, acceleration: float) -> None:
        next_x = self.body.velocity.x + direction * acceleration
        next_x = max(-MAX_GROUND_SPEED, min(MAX_GROUND_SPEED, next_x))
        self._set_rig_x_velocity(next_x)

    def post_step_stabilize(self) -> None:
        if self.has_rotation_input:
            return
        if self._is_grounded():
            if not self.drive_direction:
                self._apply_ground_coast_friction()
            self.body.angle *= 0.94
            self.body.angular_velocity *= 0.64
            if self.is_accelerating:
                target_angle = -self.facing_direction * ACCELERATION_LEAN_BACK_ANGLE
                self.body.angle = (
                    self.body.angle * (1 - ACCELERATION_LEAN_BLEND)
                    + target_angle * ACCELERATION_LEAN_BLEND
                )
                self.body.angular_velocity *= 0.72
        else:
            self.body.angle *= 0.985
            self.body.angular_velocity *= 0.9
        if self.drive_direction:
            minimum_speed = 80.0
            if self.body.velocity.x * self.drive_direction < minimum_speed:
                self._set_rig_x_velocity(self.drive_direction * minimum_speed)

    def _apply_ground_coast_friction(self) -> None:
        next_x = self.body.velocity.x * COAST_GROUND_DAMPING
        next_x = max(-COAST_MAX_SPEED, min(COAST_MAX_SPEED, next_x))
        if abs(next_x) < 2:
            next_x = 0
        self._set_rig_x_velocity(next_x)

    def _set_rig_x_velocity(self, x_velocity: float) -> None:
        for body in self._rig_bodies():
            body.velocity = (x_velocity, body.velocity.y)

    def _rig_bodies(self) -> tuple[pymunk.Body, pymunk.Body, pymunk.Body]:
        return self.body, self.front_wheel, self.rear_wheel

    def reset(self, position: tuple[float, float], angle_degrees: float) -> None:
        self.body.position = position
        self.body.angle = math.radians(angle_degrees)
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0

        local_front, local_rear = wheel_local_positions(self.spec)
        self.front_wheel.position = self.body.local_to_world(local_front)
        self.rear_wheel.position = self.body.local_to_world(local_rear)
        for wheel in (self.front_wheel, self.rear_wheel):
            wheel.velocity = (0, 0)
            wheel.angular_velocity = 0


def create_vehicle(
    space: pymunk.Space,
    player_id: int,
    spec: VehicleSpec,
    position: tuple[float, float],
    angle_degrees: float,
    facing_direction: int,
) -> Vehicle:
    width, height = spec.body_size
    moment = pymunk.moment_for_box(spec.body_mass, (width, height))
    body = pymunk.Body(spec.body_mass, moment)
    body.center_of_gravity = (0, height * BODY_CENTER_OF_GRAVITY_Y_FACTOR)
    body.position = position
    body.angle = math.radians(angle_degrees)

    body_shape = pymunk.Poly.create_box(body, (width, height))
    body_shape.friction = 0.85
    body_shape.elasticity = 0.2
    body_shape.collision_type = CollisionType.VEHICLE_BODY
    body_shape.player_id = player_id

    wheel_moment = pymunk.moment_for_circle(spec.wheel_mass, 0, spec.wheel_radius)
    local_front, local_rear = wheel_local_positions(spec)
    front_wheel = pymunk.Body(spec.wheel_mass, wheel_moment)
    rear_wheel = pymunk.Body(spec.wheel_mass, wheel_moment)
    front_wheel.position = body.local_to_world(local_front)
    rear_wheel.position = body.local_to_world(local_rear)

    front_shape = pymunk.Circle(front_wheel, spec.wheel_radius)
    rear_shape = pymunk.Circle(rear_wheel, spec.wheel_radius)
    for shape in (front_shape, rear_shape):
        shape.friction = 1.5
        shape.elasticity = 0.25
        shape.collision_type = CollisionType.WHEEL
        shape.player_id = player_id

    head_offset = (spec.head_offset[0] * facing_direction, spec.head_offset[1])
    head_shape = pymunk.Circle(body, 13, head_offset)
    head_shape.sensor = True
    head_shape.collision_type = CollisionType.HEAD
    head_shape.player_id = player_id

    constraints: list[pymunk.Constraint] = []
    for wheel, anchor in (
        (front_wheel, local_front),
        (rear_wheel, local_rear),
    ):
        groove = pymunk.GrooveJoint(
            body,
            wheel,
            (anchor.x, anchor.y - SUSPENSION_TRAVEL),
            (anchor.x, anchor.y + SUSPENSION_TRAVEL),
            (0, 0),
        )
        groove.error_bias = 0.22
        spring = pymunk.DampedSpring(
            body,
            wheel,
            anchor,
            (0, 0),
            spec.wheel_radius * SUSPENSION_REST_LENGTH_FACTOR,
            spec.suspension_stiffness * 1.6,
            spec.suspension_damping * 1.8,
        )
        constraints.extend([groove, spring])

    space.add(
        body,
        body_shape,
        front_wheel,
        front_shape,
        rear_wheel,
        rear_shape,
        head_shape,
        *constraints,
    )
    vehicle = Vehicle(
        player_id=player_id,
        spec=spec,
        facing_direction=facing_direction,
        body=body,
        body_shape=body_shape,
        front_wheel=front_wheel,
        rear_wheel=rear_wheel,
        front_wheel_shape=front_shape,
        rear_wheel_shape=rear_shape,
        head_shape=head_shape,
        head_offset=head_offset,
        constraints=constraints,
        has_rotation_input=False,
        drive_direction=0,
        is_accelerating=False,
    )
    vehicle.reset(position, angle_degrees)
    return vehicle


def wheel_local_positions(spec: VehicleSpec) -> tuple[pymunk.Vec2d, pymunk.Vec2d]:
    width, height = spec.body_size
    wheel_y = height / 2 + spec.wheel_radius * WHEEL_Y_FACTOR
    wheel_x = width / 2 * WHEEL_X_FACTOR
    return pymunk.Vec2d(wheel_x, wheel_y), pymunk.Vec2d(-wheel_x, wheel_y)
