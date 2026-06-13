from __future__ import annotations

import socket
from dataclasses import dataclass

from driveahead.core.game import Game
from driveahead.core.input import EMPTY_INPUT, PlayerInput
from driveahead.net.protocol import (
    GameSnapshotMessage,
    HelloMessage,
    InputMessage,
    VehicleSnapshot,
    WelcomeMessage,
    decode_message,
    encode_message,
)

DEFAULT_PORT = 38271
MAX_PACKET_SIZE = 8192


@dataclass
class HostStatus:
    bind_address: tuple[str, int]
    client_address: tuple[str, int] | None = None


class LanHost:
    def __init__(self, game: Game, bind_ip: str = "0.0.0.0", port: int = DEFAULT_PORT):
        self.game = game
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((bind_ip, port))
        self.socket.setblocking(False)
        self.client_address: tuple[str, int] | None = None
        self.remote_input = EMPTY_INPUT
        self.tick = 0

    @property
    def status(self) -> HostStatus:
        return HostStatus(self.socket.getsockname(), self.client_address)

    def close(self) -> None:
        self.socket.close()

    def poll(self) -> None:
        while True:
            try:
                data, address = self.socket.recvfrom(MAX_PACKET_SIZE)
            except BlockingIOError:
                return
            try:
                message = decode_message(data)
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(message, HelloMessage):
                self.client_address = address
                self._send_welcome(address)
            elif isinstance(message, InputMessage) and address == self.client_address:
                if message.player_id == 2:
                    self.remote_input = message.to_input()

    def inputs(self, local_input: PlayerInput) -> dict[int, PlayerInput]:
        return {1: local_input, 2: self.remote_input}

    def broadcast_snapshot(self) -> None:
        if self.client_address is None:
            return
        self.tick += 1
        self.socket.sendto(encode_message(snapshot_from_game(self.game, self.tick)), self.client_address)

    def _send_welcome(self, address: tuple[str, int]) -> None:
        welcome = WelcomeMessage(
            type="welcome",
            assigned_player_id=2,
            map_key=self.game.map_spec.key,
            player_1_vehicle_key=self.game.loadouts[1].vehicle.key,
            player_2_vehicle_key=self.game.loadouts[2].vehicle.key,
        )
        self.socket.sendto(encode_message(welcome), address)


def snapshot_from_game(game: Game, tick: int) -> GameSnapshotMessage:
    vehicles = []
    for player_id, vehicle in game.physics.vehicles.items():
        head = vehicle.body.local_to_world(vehicle.head_offset)
        vehicles.append(
            VehicleSnapshot(
                player_id=player_id,
                vehicle_key=vehicle.spec.key,
                x=float(vehicle.body.position.x),
                y=float(vehicle.body.position.y),
                angle=float(vehicle.body.angle),
                vx=float(vehicle.body.velocity.x),
                vy=float(vehicle.body.velocity.y),
                angular_velocity=float(vehicle.body.angular_velocity),
                front_wheel_x=float(vehicle.front_wheel.position.x),
                front_wheel_y=float(vehicle.front_wheel.position.y),
                rear_wheel_x=float(vehicle.rear_wheel.position.x),
                rear_wheel_y=float(vehicle.rear_wheel.position.y),
                head_x=float(head.x),
                head_y=float(head.y),
            )
        )
    return GameSnapshotMessage(
        type="snapshot",
        tick=tick,
        map_key=game.map_spec.key,
        scores=dict(game.match.scores),
        vehicles=tuple(vehicles),
        winner_id=game.match.winner_id,
    )
