import time

from driveahead.content.maps import MAPS
from driveahead.content.vehicles import VEHICLES
from driveahead.core.game import Game
from driveahead.core.input import PlayerInput
from driveahead.net.client import LanClient
from driveahead.net.host import LanHost


def test_lan_host_client_handshake_and_input_round_trip():
    host = LanHost(Game(MAPS[0], VEHICLES[0], VEHICLES[1]), bind_ip="127.0.0.1", port=0)
    port = host.status.bind_address[1]
    client = LanClient("127.0.0.1", port=port)

    try:
        for _ in range(20):
            client.poll()
            host.poll()
            client.poll()
            if client.status.connected and host.status.client_address is not None:
                break
            time.sleep(0.01)

        assert client.status.assigned_player_id == 2
        assert host.status.client_address is not None

        client.send_input(PlayerInput(accelerate=True, rotate_right=True))
        for _ in range(10):
            host.poll()
            if host.remote_input.accelerate:
                break
            time.sleep(0.01)

        assert host.remote_input.accelerate is True
        assert host.remote_input.rotate_right is True
    finally:
        client.close()
        host.close()


def test_lan_client_receives_snapshot():
    game = Game(MAPS[0], VEHICLES[0], VEHICLES[1])
    host = LanHost(game, bind_ip="127.0.0.1", port=0)
    port = host.status.bind_address[1]
    client = LanClient("127.0.0.1", port=port)

    try:
        for _ in range(20):
            client.poll()
            host.poll()
            client.poll()
            if client.status.connected:
                break
            time.sleep(0.01)

        host.broadcast_snapshot()
        for _ in range(10):
            client.poll()
            if client.latest_snapshot is not None:
                break
            time.sleep(0.01)

        assert client.latest_snapshot is not None
        assert client.latest_snapshot.map_key == MAPS[0].key
        assert len(client.latest_snapshot.vehicles) == 2
    finally:
        client.close()
        host.close()
