from driveahead.content.maps import MAPS
from driveahead.content.vehicles import VEHICLES
from driveahead.core.game import Game
from driveahead.core.input import PlayerInput
from driveahead.config import FIXED_DT
from driveahead.physics.vehicle import SUSPENSION_TRAVEL, wheel_local_positions
from driveahead.physics.world import SPAWN_GROUND_CLEARANCE, terrain_y_at_x


def test_player_two_spawns_upright_but_faces_left():
    for map_spec in MAPS:
        assert map_spec.spawn_points[2].angle_degrees == 0
        assert map_spec.spawn_points[2].facing_direction == -1


def test_player_two_vehicle_uses_left_facing_direction_without_flipping_body():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])
    player_two = game.physics.vehicles[2]

    assert player_two.facing_direction == -1
    assert player_two.body.angle == 0
    assert player_two.head_offset[0] == -VEHICLES[1].head_offset[0]


def test_spawned_wheels_start_above_terrain():
    for map_spec in MAPS:
        game = Game(map_spec, VEHICLES[0], VEHICLES[1])
        for vehicle in game.physics.vehicles.values():
            ground_y = terrain_y_at_x(map_spec, vehicle.body.position.x)
            assert ground_y is not None
            for wheel in (vehicle.front_wheel, vehicle.rear_wheel):
                wheel_bottom = wheel.position.y + vehicle.spec.wheel_radius
                assert wheel_bottom <= ground_y - SPAWN_GROUND_CLEARANCE + 0.01


def test_player_one_forward_input_moves_right_from_spawn():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])

    for _ in range(30):
        game.step({1: PlayerInput(accelerate=True), 2: PlayerInput()}, FIXED_DT)

    assert game.physics.vehicles[1].body.velocity.x > 0


def test_player_two_forward_input_moves_left_from_spawn():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])

    for _ in range(30):
        game.step({1: PlayerInput(), 2: PlayerInput(accelerate=True)}, FIXED_DT)

    assert game.physics.vehicles[2].body.velocity.x < 0


def test_forward_acceleration_leans_player_one_weight_backward():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])

    for _ in range(30):
        game.step({1: PlayerInput(accelerate=True), 2: PlayerInput()}, FIXED_DT)

    assert game.physics.vehicles[1].body.angle < 0


def test_forward_acceleration_leans_player_two_weight_backward():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])

    for _ in range(30):
        game.step({1: PlayerInput(), 2: PlayerInput(accelerate=True)}, FIXED_DT)

    assert game.physics.vehicles[2].body.angle > 0


def test_coasting_down_slope_has_rolling_resistance():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])

    for _ in range(120):
        game.step({1: PlayerInput(), 2: PlayerInput()}, FIXED_DT)

    assert abs(game.physics.vehicles[1].body.velocity.x) <= 95
    assert abs(game.physics.vehicles[2].body.velocity.x) <= 95


def test_body_and_wheels_stay_attached_after_drive_and_release():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])

    for _ in range(45):
        game.step({1: PlayerInput(accelerate=True), 2: PlayerInput()}, FIXED_DT)
    for _ in range(45):
        game.step({1: PlayerInput(), 2: PlayerInput()}, FIXED_DT)

    vehicle = game.physics.vehicles[1]
    expected_front, expected_rear = wheel_local_positions(vehicle.spec)
    actual_front = vehicle.body.world_to_local(vehicle.front_wheel.position)
    actual_rear = vehicle.body.world_to_local(vehicle.rear_wheel.position)

    assert abs(actual_front.x - expected_front.x) <= 12
    assert abs(actual_rear.x - expected_rear.x) <= 12
    assert abs(actual_front.y - expected_front.y) <= SUSPENSION_TRAVEL + 14
    assert abs(actual_rear.y - expected_rear.y) <= SUSPENSION_TRAVEL + 14
