# =============================================================================
# data/sports.py — Sports data via ESPN's unofficial scoreboard API
# =============================================================================

import time
import logging
import datetime
import requests
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict, Tuple

import config

logger = logging.getLogger(__name__)

ESPN_BASE = "http://site.api.espn.com/apis/site/v2/sports"


class GameState(Enum):
    NO_GAME      = auto()   # No game scheduled today
    PRE_GAME     = auto()   # Scheduled but not started
    IN_PROGRESS  = auto()   # Live
    FINAL        = auto()   # Game over (show rest of day)


@dataclass
class GameInfo:
    state:         GameState = GameState.NO_GAME
    home_abbr:     str = ""
    away_abbr:     str = ""
    home_score:    int = 0
    away_score:    int = 0
    status_detail: str = ""   # "Q3 8:42", "Top 7th", "Final", etc.
    game_time:     Optional[datetime.datetime] = None   # UTC tipoff/kickoff
    sport:         str = ""
    league:        str = ""
    # Which of our tracked team abbreviations triggered this entry
    tracked_abbr:  str = ""


@dataclass
class SportsData:
    games: List[GameInfo] = field(default_factory=list)
    fetched_at: float = 0.0
    error: Optional[str] = None


class SportsFetcher:
    """
    Polls ESPN scoreboard endpoints for each unique league in TRACKED_TEAMS.
    Filters results to only games involving a tracked team.
    """

    def __init__(self):
        self._data = SportsData()
        self._last_fetch: Dict[str, float] = {}

    def get(self) -> SportsData:
        """Return up-to-date game data, refreshing stale leagues."""
        now = time.time()
        leagues: Dict[Tuple[str, str], dict] = {}
        for team in config.TRACKED_TEAMS:
            key = (team["sport"], team["league"])
            if key not in leagues:
                leagues[key] = {"sport": team["sport"], "league": team["league"]}

        refresh_interval = config.SPORTS_REFRESH_SECS
        # Use longer interval if no games are currently live
        if not any(g.state == GameState.IN_PROGRESS for g in self._data.games):
            refresh_interval = config.SCHEDULE_REFRESH_SECS

        all_games: List[GameInfo] = []
        for key, info in leagues.items():
            if now - self._last_fetch.get(key, 0) > refresh_interval:
                games = self._fetch_league(info["sport"], info["league"])
                self._last_fetch[key] = now
                all_games.extend(games)
            else:
                # Keep existing data for this league
                all_games.extend(
                    g for g in self._data.games
                    if g.league == info["league"]
                )

        self._data.games = all_games
        return self._data

    # ------------------------------------------------------------------
    def _fetch_league(self, sport: str, league: str) -> List[GameInfo]:
        url = f"{ESPN_BASE}/{sport}/{league}/scoreboard"
        tracked_abbrs = {
            t["abbr"].upper()
            for t in config.TRACKED_TEAMS
            if t["league"] == league
        }

        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            events = r.json().get("events", [])
        except Exception as e:
            logger.error("ESPN fetch failed (%s/%s): %s", sport, league, e)
            self._data.error = str(e)
            return []

        results: List[GameInfo] = []
        today = datetime.date.today()

        for event in events:
            competition = event.get("competitions", [{}])[0]
            competitors  = competition.get("competitors", [])
            if len(competitors) < 2:
                continue

            home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

            home_abbr = home.get("team", {}).get("abbreviation", "").upper()
            away_abbr = away.get("team", {}).get("abbreviation", "").upper()

            # Only include if one of our tracked teams is playing
            matched = tracked_abbrs & {home_abbr, away_abbr}
            if not matched:
                continue

            # Parse game time
            date_str = event.get("date", "")
            game_time: Optional[datetime.datetime] = None
            try:
                game_time = datetime.datetime.fromisoformat(
                    date_str.replace("Z", "+00:00")
                )
            except Exception:
                pass

            # Skip games not on today's date (local time)
            if game_time:
                local_dt = game_time.astimezone(tz=None)
                if local_dt.date() != today:
                    continue

            # Determine state
            status = competition.get("status", {})
            type_state = status.get("type", {}).get("state", "").lower()
            completed   = status.get("type", {}).get("completed", False)

            if completed or type_state == "post":
                state = GameState.FINAL
            elif type_state == "in":
                state = GameState.IN_PROGRESS
            elif type_state == "pre":
                state = GameState.PRE_GAME
            else:
                state = GameState.PRE_GAME

            # Build status detail string
            detail = status.get("type", {}).get("shortDetail", "")
            if state == GameState.FINAL:
                detail = "Final"

            for tracked_abbr in matched:
                results.append(GameInfo(
                    state=state,
                    home_abbr=home_abbr,
                    away_abbr=away_abbr,
                    home_score=int(home.get("score", 0) or 0),
                    away_score=int(away.get("score", 0) or 0),
                    status_detail=detail,
                    game_time=game_time,
                    sport=sport,
                    league=league,
                    tracked_abbr=tracked_abbr,
                ))

        return results
