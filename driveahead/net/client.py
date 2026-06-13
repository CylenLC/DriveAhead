from __future__ import annotations

import socket
import time
from dataclasses import dataclass

from driveahead.core.input import PlayerInput
from driveahead.net.host import DEFAULT_PORT, MAX_PACKET_SIZE
from driveahead.net.protocol import (
    GameSnapshotMessage,
    HelloMessage,
    InputMessage,
    WelcomeMessage,
    decode_message,
    encode_message,
)

HELLO_INTERVAL_SECONDS = 0.5


@dataclass
class ClientStatus:
    server_address: tuple[str, int]
    assigned_player_id: int | None = None
    connected: bool = False


class LanClient:
    def __init__(self, host_ip: str, port: int = DEFAULT_PORT, player_name: str = "Player"):
        self.server_address = (host_ip, port)
        self.player_name = player_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", 0))
        self.socket.setblocking(False)
        self.assigned_player_id: int | None = None
        self.welcome: WelcomeMessage | None = None
        self.latest_snapshot: GameSnapshotMessage | None = None
        self.tick = 0
        self._last_hello_at = 0.0

    @property
    def status(self) -> ClientStatus:
        return ClientStatus(
            server_address=self.server_address,
            assigned_player_id=self.assigned_player_id,
            connected=self.assigned_player_id is not None,
        )

    def close(self) -> None:
        self.socket.close()

    def poll(self) -> None:
        self._maybe_send_hello()
        while True:
            try:
                data, _address = self.socket.recvfrom(MAX_PACKET_SIZE)
            except BlockingIOError:
                return
            try:
                message = decode_message(data)
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(message, WelcomeMessage):
                self.welcome = message
                self.assigned_player_id = message.assigned_player_id
            elif isinstance(message, GameSnapshotMessage):
                self.latest_snapshot = message

    def send_input(self, player_input: PlayerInput) -> None:
        if self.assigned_player_id is None:
            return
        self.tick += 1
        message = InputMessage.from_input(self.assigned_player_id, self.tick, player_input)
        self.socket.sendto(encode_message(message), self.server_address)

    def _maybe_send_hello(self) -> None:
        if self.assigned_player_id is not None:
            return
        now = time.monotonic()
        if now - self._last_hello_at < HELLO_INTERVAL_SECONDS:
            return
        self._last_hello_at = now
        hello = HelloMessage(type="hello", player_name=self.player_name)
        self.socket.sendto(encode_message(hello), self.server_address)
