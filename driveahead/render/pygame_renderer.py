from __future__ import annotations

import math

import pygame

from driveahead.core.game import Game
from driveahead.physics.vehicle import Vehicle
from driveahead.render.camera import Camera
from driveahead.render.ui import UI


class PygameRenderer:
    def __init__(self, screen: pygame.Surface, camera: Camera) -> None:
        self.screen = screen
        self.camera = camera
        self.ui = UI()

    def draw(self, game: Game) -> None:
        self.screen.fill(game.map_spec.background_color)
        self._draw_terrain(game)
        for vehicle in game.physics.vehicles.values():
            self._draw_vehicle(vehicle)
        self.ui.draw_hud(
            self.screen,
            game.match,
            game.map_spec.name,
            game.loadouts[1].vehicle.name,
            game.loadouts[2].vehicle.name,
        )
        self.ui.draw_menu_hint(self.screen)

    def _draw_terrain(self, game: Game) -> None:
        for start, end in game.map_spec.terrain_segments:
            pygame.draw.line(
                self.screen,
                (205, 208, 198),
                self.camera.world_to_screen(start),
                self.camera.world_to_screen(end),
                10,
            )

    def _draw_vehicle(self, vehicle: Vehicle) -> None:
        self._draw_body(vehicle)
        self._draw_wheel(vehicle.front_wheel.position, vehicle.spec.wheel_radius)
        self._draw_wheel(vehicle.rear_wheel.position, vehicle.spec.wheel_radius)
        head_world = vehicle.body.local_to_world(vehicle.head_offset)
        pygame.draw.circle(self.screen, (250, 235, 210), self.camera.world_to_screen(head_world), 13)
        pygame.draw.circle(self.screen, (45, 40, 35), self.camera.world_to_screen(head_world), 13, 2)

    def _draw_body(self, vehicle: Vehicle) -> None:
        width, height = vehicle.spec.body_size
        corners = [
            (-width / 2, -height / 2),
            (width / 2, -height / 2),
            (width / 2, height / 2),
            (-width / 2, height / 2),
        ]
        world = [vehicle.body.local_to_world(corner) for corner in corners]
        points = [self.camera.world_to_screen((point.x, point.y)) for point in world]
        pygame.draw.polygon(self.screen, vehicle.spec.color, points)
        pygame.draw.polygon(self.screen, (30, 30, 34), points, 3)

    def _draw_wheel(self, position, radius: float) -> None:
        center = self.camera.world_to_screen((position.x, position.y))
        pygame.draw.circle(self.screen, (32, 34, 38), center, int(radius))
        pygame.draw.circle(self.screen, (225, 225, 215), center, max(3, int(radius * 0.38)))
        spoke = (
            int(center[0] + math.cos(pygame.time.get_ticks() / 90) * radius * 0.75),
            int(center[1] + math.sin(pygame.time.get_ticks() / 90) * radius * 0.75),
        )
        pygame.draw.line(self.screen, (245, 245, 235), center, spoke, 2)
