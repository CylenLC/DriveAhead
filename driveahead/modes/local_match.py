from __future__ import annotations

import pygame

from driveahead.config import FIXED_DT, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from driveahead.content.maps import MAPS
from driveahead.content.vehicles import VEHICLES
from driveahead.core.events import MatchWon, RoundScored
from driveahead.core.game import Game
from driveahead.core.input import PlayerInput
from driveahead.render.camera import Camera
from driveahead.render.pygame_renderer import PygameRenderer


def run_local_match() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("DriveAhead MVP")
    clock = pygame.time.Clock()

    map_index = 0
    p1_vehicle_index = 0
    p2_vehicle_index = 1
    game = _make_game(map_index, p1_vehicle_index, p2_vehicle_index)
    renderer = PygameRenderer(
        screen,
        Camera(game.map_spec.camera_bounds, (SCREEN_WIDTH, SCREEN_HEIGHT)),
    )

    running = True
    round_reset_timer = 0.0
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    map_index = (map_index + 1) % len(MAPS)
                    game = _make_game(map_index, p1_vehicle_index, p2_vehicle_index)
                    renderer.camera = Camera(game.map_spec.camera_bounds, (SCREEN_WIDTH, SCREEN_HEIGHT))
                elif event.key == pygame.K_1:
                    p1_vehicle_index = (p1_vehicle_index + 1) % len(VEHICLES)
                    game = _make_game(map_index, p1_vehicle_index, p2_vehicle_index)
                elif event.key == pygame.K_2:
                    p2_vehicle_index = (p2_vehicle_index + 1) % len(VEHICLES)
                    game = _make_game(map_index, p1_vehicle_index, p2_vehicle_index)
                elif event.key == pygame.K_RETURN:
                    game.reset_match()

        if round_reset_timer > 0:
            round_reset_timer -= dt
            if round_reset_timer <= 0 and game.match.winner_id is None:
                game.reset_round()
        else:
            events = game.step(_read_keyboard(), FIXED_DT)
            if any(isinstance(event, RoundScored) for event in events):
                round_reset_timer = 1.0
            if any(isinstance(event, MatchWon) for event in events):
                round_reset_timer = 0.0

        renderer.draw(game)
        pygame.display.flip()

    pygame.quit()


def _make_game(map_index: int, p1_vehicle_index: int, p2_vehicle_index: int) -> Game:
    return Game(MAPS[map_index], VEHICLES[p1_vehicle_index], VEHICLES[p2_vehicle_index])


def _read_keyboard() -> dict[int, PlayerInput]:
    keys = pygame.key.get_pressed()
    return {
        1: PlayerInput(
            accelerate=keys[pygame.K_d],
            brake=keys[pygame.K_a],
            rotate_left=keys[pygame.K_w],
            rotate_right=keys[pygame.K_s],
            boost=keys[pygame.K_LSHIFT],
        ),
        2: PlayerInput(
            accelerate=keys[pygame.K_LEFT],
            brake=keys[pygame.K_RIGHT],
            rotate_left=keys[pygame.K_UP],
            rotate_right=keys[pygame.K_DOWN],
            boost=keys[pygame.K_RSHIFT],
        ),
    }
