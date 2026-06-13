from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerInput:
    accelerate: bool = False
    brake: bool = False
    rotate_left: bool = False
    rotate_right: bool = False
    boost: bool = False

    def as_bits(self) -> int:
        bits = 0
        bits |= int(self.accelerate) << 0
        bits |= int(self.brake) << 1
        bits |= int(self.rotate_left) << 2
        bits |= int(self.rotate_right) << 3
        bits |= int(self.boost) << 4
        return bits

    @classmethod
    def from_bits(cls, bits: int) -> "PlayerInput":
        return cls(
            accelerate=bool(bits & 1),
            brake=bool(bits & 2),
            rotate_left=bool(bits & 4),
            rotate_right=bool(bits & 8),
            boost=bool(bits & 16),
        )


EMPTY_INPUT = PlayerInput()
