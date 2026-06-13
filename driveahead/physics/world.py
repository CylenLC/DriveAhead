from __future__ import annotations

import pymunk
from typing import TYPE_CHECKING

from driveahead.config import PHYSICS_GRAVITY
from driveahead.content.maps import MapSpec
from driveahead.core.input import EMPTY_INPUT, PlayerInput
from driveahead.physics.collision import CollisionType, owner_id
from driveahead.physics.vehicle import Vehicle, create_vehicle

SPAWN_GROUND_CLEARANCE = 8.0

if TYPE_CHECKING:
    from driveahead.core.game import PlayerLoadout


class PhysicsWorld:
    def __init__(
        self,
        map_spec: MapSpec,
        loadouts: dict[int, PlayerLoadout],
        on_head_hit,
    ):
        self.map_spec = map_spec
        self.loadouts = loadouts
        self.on_head_hit = on_head_hit
        self.space = pymunk.Space()
        self.space.gravity = PHYSICS_GRAVITY
        self.space.iterations = 18
        self.vehicles: dict[int, Vehicle] = {}
        self.events: list[object] = []
        self._round_locked = False

        self._build_terrain()
        self._build_vehicles()
        self._install_collision_handlers()

    def apply_inputs(self, inputs: dict[int, PlayerInput]) -> None:
        if self._round_locked:
            return
        for player_id, vehicle in self.vehicles.items():
            vehicle.apply_input(inputs.get(player_id, EMPTY_INPUT))

    def step(self, dt: float) -> None:
        self.space.step(dt)
        for vehicle in self.vehicles.values():
            vehicle.post_step_stabilize()

    def reset_round(self) -> None:
        self._round_locked = False
        for player_id, vehicle in self.vehicles.items():
            spawn = self.map_spec.spawn_points[player_id]
            vehicle.reset(
                adjusted_spawn_position(self.map_spec, vehicle.spec, spawn.position),
                spawn.angle_degrees,
            )

    def queue_events(self, events: list[object]) -> None:
        self.events.extend(events)

    def drain_events(self) -> list[object]:
        events = self.events
        self.events = []
        return events

    def _build_terrain(self) -> None:
        for start, end in self.map_spec.terrain_segments:
            segment = pymunk.Segment(self.space.static_body, start, end, 7)
            segment.friction = 1.0
            segment.elasticity = 0.15
            segment.collision_type = CollisionType.TERRAIN
            self.space.add(segment)

    def _build_vehicles(self) -> None:
        for player_id, loadout in self.loadouts.items():
            spawn = self.map_spec.spawn_points[player_id]
            self.vehicles[player_id] = create_vehicle(
                self.space,
                player_id,
                loadout.vehicle,
                adjusted_spawn_position(self.map_spec, loadout.vehicle, spawn.position),
                spawn.angle_degrees,
                spawn.facing_direction,
            )

    def _install_collision_handlers(self) -> None:
        targets = (
            CollisionType.TERRAIN,
            CollisionType.VEHICLE_BODY,
            CollisionType.WHEEL,
        )
        for target in targets:
            if hasattr(self.space, "add_collision_handler"):
                handler = self.space.add_collision_handler(CollisionType.HEAD, target)
                handler.begin = self._on_head_collision
            else:
                self.space.on_collision(
                    CollisionType.HEAD,
                    target,
                    begin=self._on_head_collision,
                )

    def _on_head_collision(self, arbiter, _space, _data) -> bool:
        if self._round_locked:
            return True

        shape_a, shape_b = arbiter.shapes
        head = shape_a if shape_a.collision_type == CollisionType.HEAD else shape_b
        other = shape_b if head is shape_a else shape_a
        victim_id = owner_id(head)
        other_id = owner_id(other)
        if victim_id is None or other_id == victim_id:
            return True

        self._round_locked = True
        self.on_head_hit(victim_id, "head_hit")
        return True


def adjusted_spawn_position(
    map_spec: MapSpec,
    vehicle_spec,
    requested_position: tuple[float, float],
) -> tuple[float, float]:
    ground_y = terrain_y_at_x(map_spec, requested_position[0])
    if ground_y is None:
        return requested_position

    body_height = vehicle_spec.body_size[1]
    wheel_bottom_from_body = body_height / 2 + vehicle_spec.wheel_radius * 2.25
    safe_body_y = ground_y - wheel_bottom_from_body - SPAWN_GROUND_CLEARANCE
    return requested_position[0], min(requested_position[1], safe_body_y)


def terrain_y_at_x(map_spec: MapSpec, x: float) -> float | None:
    hits: list[float] = []
    for start, end in map_spec.terrain_segments:
        x1, y1 = start
        x2, y2 = end
        if x1 == x2:
            continue
        min_x, max_x = sorted((x1, x2))
        if not (min_x <= x <= max_x):
            continue
        t = (x - x1) / (x2 - x1)
        if 0 <= t <= 1:
            hits.append(y1 + (y2 - y1) * t)
    if not hits:
        return None
    return min(hits)
