from __future__ import annotations

from dataclasses import dataclass

from driveahead.content.maps import MapSpec
from driveahead.content.vehicles import VehicleSpec
from driveahead.core.input import PlayerInput
from driveahead.core.match import MatchState
from driveahead.physics.world import PhysicsWorld


@dataclass
class PlayerLoadout:
    player_id: int
    vehicle: VehicleSpec


class Game:
    def __init__(self, map_spec: MapSpec, player_1: VehicleSpec, player_2: VehicleSpec):
        self.map_spec = map_spec
        self.loadouts = {
            1: PlayerLoadout(1, player_1),
            2: PlayerLoadout(2, player_2),
        }
        self.match = MatchState()
        self.physics = PhysicsWorld(map_spec, self.loadouts, self._on_head_hit)

    def step(self, inputs: dict[int, PlayerInput], dt: float) -> list[object]:
        self.physics.apply_inputs(inputs)
        self.physics.step(dt)
        return self.physics.drain_events()

    def reset_round(self) -> None:
        self.physics.reset_round()

    def reset_match(self) -> None:
        self.match.reset()
        self.physics.reset_round()

    def _on_head_hit(self, victim_id: int, reason: str) -> None:
        events = self.match.score_head_hit(victim_id, reason)
        self.physics.queue_events(events)
