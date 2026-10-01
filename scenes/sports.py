# =============================================================================
# scenes/sports.py — Sports scores, countdowns, and final scores
# =============================================================================

import datetime
import time
from typing import List
from rgbmatrix import RGBMatrix

import config
from scenes.base_scene import BaseScene
from data.sports import GameInfo, GameState, SportsFetcher
from utils.colors import (
    WHITE, DIM_WHITE, YELLOW, GREEN, RED, CYAN, GRAY, DARK_GRAY, ORANGE,
    get_team_colors, dim
)
from utils.fonts import load_font


# How many rows the sports section occupies
SPORTS_TOP    = config.SPORTS_SECTION_TOP_ROW
SPORTS_BOTTOM = None   # set at runtime from matrix.height
ROWS_PER_GAME = 12     # pixels allocated per game row


class SportsScene(BaseScene):
    """
    Renders the sports section below the compressed clock/weather strip.

    Layout per game row (12px tall):
      AWAY_ABBR  AWAY_SCORE  :  HOME_SCORE  HOME_ABBR  STATUS
      Countdown / "FINAL" badge

    Cycles through active game pages when there are more games than fit.
    """

    def __init__(self, matrix: RGBMatrix, sports_fetcher: SportsFetcher):
        super().__init__(matrix)
        self._sports = sports_fetcher
        self._font_large  = load_font(config.FONT_LARGE)
        self._font_medium = load_font(config.FONT_MEDIUM)
        self._font_small  = load_font(config.FONT_SMALL)
        self._cycle_index  = 0
        self._last_cycle   = time.time()

    # ------------------------------------------------------------------
    def render(self) -> None:
        data   = self._sports.get()
        games  = data.games

        # Deduplicate: same game may appear twice if two tracked teams play each other
        seen = set()
        unique_games: List[GameInfo] = []
        for g in games:
            key = (g.home_abbr, g.away_abbr, g.league)
            if key not in seen:
                seen.add(key)
                unique_games.append(g)

        # Sort: IN_PROGRESS first, then PRE_GAME (by time), then FINAL
        def sort_key(g: GameInfo):
            order = {GameState.IN_PROGRESS: 0, GameState.PRE_GAME: 1, GameState.FINAL: 2}
            t = g.game_time.timestamp() if g.game_time else 0
            return (order.get(g.state, 9), t)
        unique_games.sort(key=sort_key)

        sports_height = self.matrix.height - SPORTS_TOP
        games_per_page = max(1, sports_height // ROWS_PER_GAME)

        # Advance cycle page
        if unique_games:
            now = time.time()
            total_pages = max(1, -(-len(unique_games) // games_per_page))  # ceil div
            if now - self._last_cycle >= config.SPORTS_CYCLE_INTERVAL:
                self._cycle_index = (self._cycle_index + 1) % total_pages
                self._last_cycle   = now
            # Clamp
            self._cycle_index = min(self._cycle_index, total_pages - 1)

        # Clear sports region
        self._clear_region(SPORTS_TOP, self.matrix.height)

        if not unique_games:
            self._draw_text(
                self._font_small,
                4, SPORTS_TOP + 10,
                DARK_GRAY, "No games today"
            )
            return

        start = self._cycle_index * games_per_page
        page_games = unique_games[start: start + games_per_page]

        for i, game in enumerate(page_games):
            row_top = SPORTS_TOP + i * ROWS_PER_GAME
            self._render_game_row(game, row_top)

        # Page indicator dots if multiple pages
        total_pages = max(1, -(-len(unique_games) // games_per_page))
        if total_pages > 1:
            self._draw_page_dots(total_pages, self._cycle_index)

    # ------------------------------------------------------------------
    def _render_game_row(self, game: GameInfo, y_top: int):
        w = self.matrix.width
        mid_y  = y_top + 7    # baseline for score line
        sub_y  = y_top + 12   # baseline for sub-detail (status / countdown)

        away_primary, _  = get_team_colors(game.away_abbr)
        home_primary, _  = get_team_colors(game.home_abbr)

        if game.state == GameState.IN_PROGRESS:
            self._render_live(game, y_top, mid_y, sub_y, away_primary, home_primary)
        elif game.state == GameState.PRE_GAME:
            self._render_pregame(game, y_top, mid_y, sub_y, away_primary, home_primary)
        elif game.state == GameState.FINAL:
            self._render_final(game, y_top, mid_y, sub_y, away_primary, home_primary)

        # Separator between game rows
        if y_top + ROWS_PER_GAME < self.matrix.height:
            self._draw_line(0, y_top + ROWS_PER_GAME - 1,
                            w - 1, y_top + ROWS_PER_GAME - 1, DARK_GRAY)

    # ------------------------------------------------------------------
    def _render_live(self, game, y_top, mid_y, sub_y, away_col, home_col):
        """AWAY 14 : 7 HOME  Q3"""
        away_str  = game.away_abbr[:3]
        home_str  = game.home_abbr[:3]
        score_str = f"{game.away_score}-{game.home_score}"

        x = 1
        x += self._draw_text(self._font_small, x, mid_y, away_col,  away_str)
        x += 1
        x += self._draw_text(self._font_small, x, mid_y, WHITE,     score_str)
        x += 1
        self._draw_text(self._font_small, x, mid_y, home_col, home_str)

        # Status on sub-line (period/quarter/inning) — green pulsing feel via color
        pulse = GREEN if (int(time.time()) % 2 == 0) else (0, 160, 0)
        self._draw_text(self._font_small, 1, sub_y, pulse,
                        game.status_detail[:14])

    # ------------------------------------------------------------------
    def _render_pregame(self, game, y_top, mid_y, sub_y, away_col, home_col):
        """AWAY vs HOME  7:10PM / T-2h25m"""
        away_str = game.away_abbr[:3]
        home_str = game.home_abbr[:3]

        x = 1
        x += self._draw_text(self._font_small, x, mid_y, away_col, away_str)
        x += self._draw_text(self._font_small, x, mid_y, GRAY,     " vs ")
        self._draw_text(self._font_small, x, mid_y, home_col, home_str)

        # Gametime + countdown
        if game.game_time:
            local_dt = game.game_time.astimezone(tz=None)
            time_str = local_dt.strftime("%-I:%M%p")

            delta = game.game_time - datetime.datetime.now(datetime.timezone.utc)
            total_secs = int(delta.total_seconds())
            if total_secs > 0:
                hours, rem = divmod(total_secs, 3600)
                mins = rem // 60
                if hours > 0:
                    countdown = f"T-{hours}h{mins:02d}m"
                else:
                    countdown = f"T-{mins}m"
            else:
                countdown = "Soon"

            self._draw_text(self._font_small, 1, sub_y, CYAN,
                            f"{time_str} {countdown}"[:14])

    # ------------------------------------------------------------------
    def _render_final(self, game, y_top, mid_y, sub_y, away_col, home_col):
        """AWAY 3 FINAL 5 HOME"""
        away_str = game.away_abbr[:3]
        home_str = game.home_abbr[:3]

        # Highlight winner in brighter color
        away_won = game.away_score > game.home_score
        home_won = game.home_score > game.away_score

        away_color = away_col if away_won else dim(away_col, 0.55)
        home_color = home_col if home_won else dim(home_col, 0.55)

        x = 1
        x += self._draw_text(self._font_small, x, mid_y, away_color, away_str)
        x += 1
        x += self._draw_text(self._font_small, x, mid_y, WHITE,
                              f"{game.away_score}-{game.home_score}")
        x += 1
        self._draw_text(self._font_small, x, mid_y, home_color, home_str)

        self._draw_text(self._font_small, 1, sub_y, DIM_WHITE, "Final")

    # ------------------------------------------------------------------
    def _draw_page_dots(self, total: int, current: int):
        """Small dots at the very bottom of the panel indicating page."""
        y = self.matrix.height - 1
        dot_spacing = 3
        total_width = total * dot_spacing - 1
        start_x = (self.matrix.width - total_width) // 2

        for i in range(total):
            color = WHITE if i == current else DARK_GRAY
            self._set_pixel(start_x + i * dot_spacing, y, color)
