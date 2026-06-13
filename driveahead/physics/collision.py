from __future__ import annotations

from enum import IntEnum


class CollisionType(IntEnum):
    TERRAIN = 1
    VEHICLE_BODY = 2
    WHEEL = 3
    HEAD = 4


def owner_id(shape: object) -> int | None:
    return getattr(shape, "player_id", None)
