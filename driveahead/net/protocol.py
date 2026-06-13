from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Literal

from driveahead.core.input import PlayerInput

MessageType = Literal["hello", "input", "snapshot"]


@dataclass(frozen=True)
class HelloMessage:
    type: Literal["hello"]
    player_name: str
    protocol_version: int = 1


@dataclass(frozen=True)
class InputMessage:
    type: Literal["input"]
    player_id: int
    tick: int
    input_bits: int

    @classmethod
    def from_input(cls, player_id: int, tick: int, player_input: PlayerInput) -> "InputMessage":
        return cls("input", player_id, tick, player_input.as_bits())

    def to_input(self) -> PlayerInput:
        return PlayerInput.from_bits(self.input_bits)


@dataclass(frozen=True)
class VehicleSnapshot:
    player_id: int
    x: float
    y: float
    angle: float
    vx: float
    vy: float
    angular_velocity: float


@dataclass(frozen=True)
class GameSnapshotMessage:
    type: Literal["snapshot"]
    tick: int
    scores: dict[int, int]
    vehicles: tuple[VehicleSnapshot, ...]
    winner_id: int | None = None


ProtocolMessage = HelloMessage | InputMessage | GameSnapshotMessage


def encode_message(message: ProtocolMessage) -> bytes:
    payload = asdict(message)
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def decode_message(data: bytes) -> ProtocolMessage:
    payload: dict[str, Any] = json.loads(data.decode("utf-8"))
    message_type = payload.get("type")
    if message_type == "hello":
        return HelloMessage(**payload)
    if message_type == "input":
        return InputMessage(**payload)
    if message_type == "snapshot":
        vehicles = tuple(VehicleSnapshot(**vehicle) for vehicle in payload["vehicles"])
        scores = {int(key): value for key, value in payload["scores"].items()}
        return GameSnapshotMessage(
            type="snapshot",
            tick=payload["tick"],
            scores=scores,
            vehicles=vehicles,
            winner_id=payload.get("winner_id"),
        )
    raise ValueError(f"Unknown protocol message type: {message_type}")
