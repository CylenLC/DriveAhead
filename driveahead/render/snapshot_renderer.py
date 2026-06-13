from __future__ import annotations

import math

import pygame

from driveahead.content.maps import MapSpec
from driveahead.content.vehicles import vehicle_by_key
from driveahead.core.match import MatchState
from driveahead.net.protocol import GameSnapshotMessage, VehicleSnapshot
from driveahead.render.camera import Camera
from driveahead.render.ui import UI


class SnapshotRenderer:
    def __init__(self, screen: pygame.Surface, camera: Camera) -> None:
        self.screen = screen
        self.camera = camera
        self.ui = UI()

    def draw(self, snapshot: GameSnapshotMessage | None, map_spec: MapSpec, status_text: str = "") -> None:
        self.screen.fill(map_spec.background_color)
        self._draw_terrain(map_spec)
        if snapshot is not None:
            for vehicle in snapshot.vehicles:
                self._draw_vehicle(vehicle)
            match = MatchState()
            match.scores = snapshot.scores
            match.winner_id = snapshot.winner_id
            vehicle_names = {
                vehicle.player_id: vehicle_by_key(vehicle.vehicle_key).name
                for vehicle in snapshot.vehicles
            }
            self.ui.draw_hud(
                self.screen,
                match,
                map_spec.name,
                vehicle_names.get(1, "P1"),
                vehicle_names.get(2, "P2"),
            )
        if status_text:
            text = self.ui.small.render(status_text, True, (235, 235, 235))
            self.screen.blit(text, (20, self.screen.get_height() - 52))
        self.ui.draw_menu_hint(self.screen)

    def _draw_terrain(self, map_spec: MapSpec) -> None:
        for start, end in map_spec.terrain_segments:
            pygame.draw.line(
                self.screen,
                (205, 208, 198),
                self.camera.world_to_screen(start),
                self.camera.world_to_screen(end),
                10,
            )

    def _draw_vehicle(self, vehicle: VehicleSnapshot) -> None:
        spec = vehicle_by_key(vehicle.vehicle_key)
        self._draw_body(vehicle, spec.color, spec.body_size)
        self._draw_wheel((vehicle.front_wheel_x, vehicle.front_wheel_y), spec.wheel_radius)
        self._draw_wheel((vehicle.rear_wheel_x, vehicle.rear_wheel_y), spec.wheel_radius)
        pygame.draw.circle(self.screen, (250, 235, 210), self.camera.world_to_screen((vehicle.head_x, vehicle.head_y)), 13)
        pygame.draw.circle(self.screen, (45, 40, 35), self.camera.world_to_screen((vehicle.head_x, vehicle.head_y)), 13, 2)

    def _draw_body(
        self,
        vehicle: VehicleSnapshot,
        color: tuple[int, int, int],
        body_size: tuple[float, float],
    ) -> None:
        width, height = body_size
        corners = [
            (-width / 2, -height / 2),
            (width / 2, -height / 2),
            (width / 2, height / 2),
            (-width / 2, height / 2),
        ]
        points = []
        cos_angle = math.cos(vehicle.angle)
        sin_angle = math.sin(vehicle.angle)
        for x, y in corners:
            world_x = vehicle.x + x * cos_angle - y * sin_angle
            world_y = vehicle.y + x * sin_angle + y * cos_angle
            points.append(self.camera.world_to_screen((world_x, world_y)))
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, (30, 30, 34), points, 3)

    def _draw_wheel(self, position: tuple[float, float], radius: float) -> None:
        center = self.camera.world_to_screen(position)
        pygame.draw.circle(self.screen, (32, 34, 38), center, int(radius))
        pygame.draw.circle(self.screen, (225, 225, 215), center, max(3, int(radius * 0.38)))
