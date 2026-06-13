from driveahead.core.input import PlayerInput
from driveahead.content.maps import MAPS
from driveahead.content.vehicles import VEHICLES
from driveahead.core.game import Game
from driveahead.net.host import snapshot_from_game
from driveahead.net.protocol import (
    GameSnapshotMessage,
    InputMessage,
    WelcomeMessage,
    VehicleSnapshot,
    decode_message,
    encode_message,
)


def test_input_message_round_trips_player_input_bits():
    original_input = PlayerInput(
        accelerate=True,
        brake=False,
        rotate_left=True,
        rotate_right=False,
        boost=True,
    )
    message = InputMessage.from_input(player_id=2, tick=42, player_input=original_input)

    decoded = decode_message(encode_message(message))

    assert isinstance(decoded, InputMessage)
    assert decoded.player_id == 2
    assert decoded.tick == 42
    assert decoded.to_input() == original_input


def test_snapshot_message_round_trips_int_score_keys():
    message = GameSnapshotMessage(
        type="snapshot",
        tick=10,
        map_key="arena",
        scores={1: 2, 2: 3},
        vehicles=(
            VehicleSnapshot(1, "buggy", 100.0, 200.0, 0.2, 5.0, 6.0, 0.1, 90, 220, 110, 221, 100, 170),
            VehicleSnapshot(2, "truck", 300.0, 220.0, -0.1, -3.0, 2.0, -0.2, 280, 245, 320, 246, 300, 180),
        ),
        winner_id=None,
    )

    decoded = decode_message(encode_message(message))

    assert isinstance(decoded, GameSnapshotMessage)
    assert decoded.scores == {1: 2, 2: 3}
    assert decoded.vehicles[0].player_id == 1
    assert decoded.vehicles[1].x == 300.0
    assert decoded.vehicles[1].vehicle_key == "truck"


def test_welcome_message_round_trips():
    message = WelcomeMessage(
        type="welcome",
        assigned_player_id=2,
        map_key="arena",
        player_1_vehicle_key="buggy",
        player_2_vehicle_key="truck",
    )

    decoded = decode_message(encode_message(message))

    assert decoded == message


def test_snapshot_from_game_includes_renderable_vehicle_state():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])

    snapshot = snapshot_from_game(game, tick=7)

    assert snapshot.tick == 7
    assert snapshot.map_key == MAPS[0].key
    assert len(snapshot.vehicles) == 2
    assert {vehicle.vehicle_key for vehicle in snapshot.vehicles} == {"buggy", "truck"}
    for vehicle in snapshot.vehicles:
        assert vehicle.front_wheel_x != vehicle.rear_wheel_x
        assert vehicle.head_y < vehicle.y
