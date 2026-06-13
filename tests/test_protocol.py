from driveahead.core.input import PlayerInput
from driveahead.net.protocol import (
    GameSnapshotMessage,
    InputMessage,
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
        scores={1: 2, 2: 3},
        vehicles=(
            VehicleSnapshot(1, 100.0, 200.0, 0.2, 5.0, 6.0, 0.1),
            VehicleSnapshot(2, 300.0, 220.0, -0.1, -3.0, 2.0, -0.2),
        ),
        winner_id=None,
    )

    decoded = decode_message(encode_message(message))

    assert isinstance(decoded, GameSnapshotMessage)
    assert decoded.scores == {1: 2, 2: 3}
    assert decoded.vehicles[0].player_id == 1
    assert decoded.vehicles[1].x == 300.0
