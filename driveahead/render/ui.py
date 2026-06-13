from __future__ import annotations

import pygame

from driveahead.core.match import MatchState


class UI:
    def __init__(self) -> None:
        self.large = pygame.font.SysFont("arial", 34, bold=True)
        self.medium = pygame.font.SysFont("arial", 24, bold=True)
        self.small = pygame.font.SysFont("arial", 18)

    def draw_hud(
        self,
        surface: pygame.Surface,
        match: MatchState,
        map_name: str,
        p1_vehicle: str,
        p2_vehicle: str,
    ) -> None:
        score = f"P1 {match.scores[1]}  -  {match.scores[2]} P2"
        score_surface = self.large.render(score, True, (245, 245, 245))
        surface.blit(score_surface, score_surface.get_rect(center=(surface.get_width() // 2, 34)))

        info = f"{map_name}    P1: {p1_vehicle}    P2: {p2_vehicle}"
        info_surface = self.small.render(info, True, (210, 215, 220))
        surface.blit(info_surface, (20, 18))

        if match.winner_id:
            winner = self.large.render(f"Player {match.winner_id} wins - press Enter", True, (255, 236, 125))
            surface.blit(winner, winner.get_rect(center=(surface.get_width() // 2, 96)))

    def draw_menu_hint(self, surface: pygame.Surface) -> None:
        hint = "Enter start/restart   A/D or arrows move   W/S or up/down shift weight   M map   1/2 cars"
        hint_surface = self.small.render(hint, True, (220, 220, 220))
        surface.blit(hint_surface, hint_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() - 24)))
