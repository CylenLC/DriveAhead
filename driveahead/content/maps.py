from __future__ import annotations

from dataclasses import dataclass, field


Point = tuple[float, float]
Segment = tuple[Point, Point]
Color = tuple[int, int, int]


@dataclass(frozen=True)
class SpawnPoint:
    position: Point
    angle_degrees: float
    facing_direction: int = 1


@dataclass(frozen=True)
class MapSpec:
    key: str
    name: str
    spawn_points: dict[int, SpawnPoint]
    terrain_segments: tuple[Segment, ...]
    camera_bounds: tuple[float, float, float, float]
    background_color: Color
    hazards: tuple[object, ...] = field(default_factory=tuple)
    entities: tuple[object, ...] = field(default_factory=tuple)


MAPS: tuple[MapSpec, ...] = (
    MapSpec(
        key="arena",
        name="Arena",
        spawn_points={
            1: SpawnPoint((310, 480), 0),
            2: SpawnPoint((970, 480), 0, -1),
        },
        terrain_segments=(
            ((80, 590), (260, 535)),
            ((260, 535), (430, 505)),
            ((430, 505), (640, 530)),
            ((640, 530), (850, 505)),
            ((850, 505), (1020, 535)),
            ((1020, 535), (1200, 590)),
            ((80, 590), (80, 690)),
            ((1200, 590), (1200, 690)),
            ((80, 690), (1200, 690)),
        ),
        camera_bounds=(0, 0, 1280, 720),
        background_color=(30, 34, 42),
    ),
    MapSpec(
        key="bridge",
        name="Bridge",
        spawn_points={
            1: SpawnPoint((230, 430), 0),
            2: SpawnPoint((1050, 430), 0, -1),
        },
        terrain_segments=(
            ((60, 560), (340, 500)),
            ((340, 500), (520, 500)),
            ((760, 500), (940, 500)),
            ((940, 500), (1220, 560)),
            ((520, 500), (590, 565)),
            ((690, 565), (760, 500)),
            ((590, 565), (690, 565)),
            ((60, 680), (1220, 680)),
            ((60, 560), (60, 680)),
            ((1220, 560), (1220, 680)),
        ),
        camera_bounds=(0, 0, 1280, 720),
        background_color=(27, 39, 47),
    ),
    MapSpec(
        key="hills",
        name="Hills",
        spawn_points={
            1: SpawnPoint((260, 410), 0),
            2: SpawnPoint((1010, 410), 0, -1),
        },
        terrain_segments=(
            ((50, 620), (180, 560)),
            ((180, 560), (330, 470)),
            ((330, 470), (510, 585)),
            ((510, 585), (650, 500)),
            ((650, 500), (805, 585)),
            ((805, 585), (960, 470)),
            ((960, 470), (1110, 560)),
            ((1110, 560), (1230, 620)),
            ((50, 690), (1230, 690)),
            ((50, 620), (50, 690)),
            ((1230, 620), (1230, 690)),
        ),
        camera_bounds=(0, 0, 1280, 720),
        background_color=(35, 37, 32),
    ),
)


def map_by_key(key: str) -> MapSpec:
    for map_spec in MAPS:
        if map_spec.key == key:
            return map_spec
    raise KeyError(f"Unknown map: {key}")
