#!/usr/bin/env python3
# =============================================================================
# main.py — Garage LED Panel — Main render loop
#
# Usage:
#   python3 main.py
#
# Countdown mode:
#   Set COUNTDOWN_MODE = True and COUNTDOWN_TARGET to any future datetime to
#   override the normal display with a full-panel countdown timer.
# =============================================================================

import time
import datetime
import logging
import signal
import sys

from display.panel import create_matrix
from data.weather import WeatherFetcher
from data.sports import SportsFetcher, GameState
from scenes.clock_weather import ClockWeatherScene
from scenes.sports import SportsScene
from scenes.countdown import CountdownScene

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")

# =============================================================================
# COUNTDOWN MODE
# Set COUNTDOWN_MODE = True to display a full-panel countdown instead of the
# normal clock/weather/sports display.
# COUNTDOWN_TARGET is a naive local datetime — adjust to your event.
# =============================================================================
COUNTDOWN_MODE   = False
COUNTDOWN_TARGET = datetime.datetime(2026, 12, 31, 23, 59, 59)  # New Year's Eve

# =============================================================================

TARGET_FPS = 20
FRAME_TIME = 1.0 / TARGET_FPS


def has_active_sports(sports_fetcher: SportsFetcher) -> bool:
    """Return True if any tracked team has a game today (any state)."""
    data = sports_fetcher.get()
    return bool(data.games)


def main():
    logger.info("Starting Garage LED Panel...")

    # --- Hardware ---
    matrix = create_matrix()
    logger.info("Matrix initialized: %dx%d", matrix.width, matrix.height)

    # --- Countdown mode — skip all other setup if enabled ---
    if COUNTDOWN_MODE:
        logger.info("Countdown mode enabled — target: %s", COUNTDOWN_TARGET)
        countdown_scene = CountdownScene(matrix, COUNTDOWN_TARGET)

        running = True

        def _handle_signal(sig, frame):
            nonlocal running
            logger.info("Caught signal %s — shutting down.", sig)
            running = False

        signal.signal(signal.SIGINT,  _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        while running:
            frame_start = time.time()
            countdown_scene.render()
            elapsed    = time.time() - frame_start
            sleep_for  = FRAME_TIME - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

        logger.info("Clearing matrix and exiting.")
        matrix.Clear()
        sys.exit(0)

    # --- Normal mode ---

    # Data fetchers
    weather_fetcher = WeatherFetcher()
    sports_fetcher  = SportsFetcher()

    # Pre-fetch so first frame isn't blank
    weather_fetcher.get()
    sports_fetcher.get()

    # Scenes
    clock_weather_scene = ClockWeatherScene(matrix, weather_fetcher)
    sports_scene        = SportsScene(matrix, sports_fetcher)

    # Graceful shutdown
    running = True

    def _handle_signal(sig, frame):
        nonlocal running
        logger.info("Caught signal %s — shutting down.", sig)
        running = False

    signal.signal(signal.SIGINT,  _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Main render loop
    logger.info("Entering render loop.")

    while running:
        frame_start = time.time()

        sports_active = has_active_sports(sports_fetcher)

        if sports_active:
            # Top strip: compressed clock + weather
            clock_weather_scene.render(compressed=True)
            # Bottom section: live scores / countdowns / finals
            sports_scene.render()
        else:
            # Full panel: clock + weather + forecast
            clock_weather_scene.render(compressed=False)

        elapsed   = time.time() - frame_start
        sleep_for = FRAME_TIME - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)

    # Cleanup
    logger.info("Clearing matrix and exiting.")
    matrix.Clear()
    sys.exit(0)


if __name__ == "__main__":
    main()
