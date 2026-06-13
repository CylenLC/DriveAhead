from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoundScored:
    scorer_id: int
    victim_id: int
    reason: str


@dataclass(frozen=True)
class MatchWon:
    winner_id: int
