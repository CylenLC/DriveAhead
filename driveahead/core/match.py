from __future__ import annotations

from dataclasses import dataclass, field

from driveahead.config import SCORE_TO_WIN
from driveahead.core.events import MatchWon, RoundScored


@dataclass
class MatchState:
    score_to_win: int = SCORE_TO_WIN
    scores: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0})
    winner_id: int | None = None
    round_index: int = 1

    def score_head_hit(self, victim_id: int, reason: str = "head_hit") -> list[object]:
        if self.winner_id is not None:
            return []

        scorer_id = 2 if victim_id == 1 else 1
        self.scores[scorer_id] += 1
        events: list[object] = [RoundScored(scorer_id, victim_id, reason)]
        if self.scores[scorer_id] >= self.score_to_win:
            self.winner_id = scorer_id
            events.append(MatchWon(scorer_id))
        else:
            self.round_index += 1
        return events

    def reset(self) -> None:
        self.scores = {1: 0, 2: 0}
        self.winner_id = None
        self.round_index = 1
