from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Camera:
    bounds: tuple[float, float, float, float]
    screen_size: tuple[int, int]

    def world_to_screen(self, point: tuple[float, float]) -> tuple[int, int]:
        min_x, min_y, _max_x, _max_y = self.bounds
        return int(point[0] - min_x), int(point[1] - min_y)
