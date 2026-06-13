from __future__ import annotations

import pygame

from driveahead.config import FIXED_DT, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, SNAPSHOT_HZ
from driveahead.content.maps import MAPS, map_by_key
from driveahead.content.vehicles import VEHICLES, vehicle_by_key
from driveahead.core.events import MatchWon, RoundScored
from driveahead.core.game import Game
from driveahead.modes.local_match import read_local_player_input
from driveahead.net.client import LanClient
from driveahead.net.host import DEFAULT_PORT, LanHost
from driveahead.render.camera import Camera
from driveahead.render.pygame_renderer import PygameRenderer
from driveahead.render.snapshot_renderer import SnapshotRenderer


def run_lan_host(port: int = DEFAULT_PORT) -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("DriveAhead LAN Host")
    clock = pygame.time.Clock()

    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])
    host = LanHost(game, port=port)
    renderer = PygameRenderer(screen, Camera(game.map_spec.camera_bounds, (SCREEN_WIDTH, SCREEN_HEIGHT)))
    snapshot_interval = 1.0 / SNAPSHOT_HZ
    snapshot_timer = 0.0
    round_reset_timer = 0.0

    try:
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RETURN:
                        game.reset_match()

            host.poll()
            if round_reset_timer > 0:
                round_reset_timer -= dt
                if round_reset_timer <= 0 and game.match.winner_id is None:
                    game.reset_round()
            else:
                events = game.step(host.inputs(read_local_player_input()), FIXED_DT)
                if any(isinstance(event, RoundScored) for event in events):
                    round_reset_timer = 1.0
                if any(isinstance(event, MatchWon) for event in events):
                    round_reset_timer = 0.0

            snapshot_timer += dt
            if snapshot_timer >= snapshot_interval:
                snapshot_timer = 0.0
                host.broadcast_snapshot()

            renderer.draw(game)
            _draw_lan_status(screen, f"HOST {host.status.bind_address[0]}:{host.status.bind_address[1]}  client: {host.status.client_address or 'waiting'}")
            pygame.display.flip()
    finally:
        host.close()
        pygame.quit()


def run_lan_client(host_ip: str, port: int = DEFAULT_PORT) -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("DriveAhead LAN Client")
    clock = pygame.time.Clock()
    client = LanClient(host_ip, port=port)
    fallback_map = MAPS[0]
    renderer = SnapshotRenderer(screen, Camera(fallback_map.camera_bounds, (SCREEN_WIDTH, SCREEN_HEIGHT)))

    try:
        running = True
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            client.poll()
            client.send_input(read_local_player_input())

            map_spec = _client_map(client) or fallback_map
            renderer.camera = Camera(map_spec.camera_bounds, (SCREEN_WIDTH, SCREEN_HEIGHT))
            renderer.draw(client.latest_snapshot, map_spec, _client_status_text(client))
            pygame.display.flip()
    finally:
        client.close()
        pygame.quit()


def _client_map(client: LanClient):
    if client.latest_snapshot is not None:
        return map_by_key(client.latest_snapshot.map_key)
    if client.welcome is not None:
        return map_by_key(client.welcome.map_key)
    return None


def _client_status_text(client: LanClient) -> str:
    if client.welcome is None:
        return f"Connecting to {client.server_address[0]}:{client.server_address[1]}..."
    return (
        f"Connected as P{client.welcome.assigned_player_id}  "
        f"P1 {vehicle_by_key(client.welcome.player_1_vehicle_key).name}  "
        f"P2 {vehicle_by_key(client.welcome.player_2_vehicle_key).name}"
    )


def _draw_lan_status(screen: pygame.Surface, text: str) -> None:
    font = pygame.font.SysFont("arial", 18)
    surface = font.render(text, True, (235, 235, 235))
    screen.blit(surface, (20, SCREEN_HEIGHT - 52))
