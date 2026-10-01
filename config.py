# =============================================================================
# config.py — Central configuration for the Garage LED Panel
# =============================================================================

# --- Panel Hardware -----------------------------------------------------------
PANEL_ROWS = 64          # Height in pixels (32 or 64)
PANEL_COLS = 64          # Width in pixels (64 or 128)
PANEL_CHAIN = 1          # Number of panels daisy-chained
PANEL_PARALLEL = 1       # Parallel chains (advanced setups)
GPIO_MAPPING = "adafruit-hat"   # "adafruit-hat" or "adafruit-hat-pwm"
GPIO_SLOWDOWN = 2        # Increase if flickering (Pi 4: 2, Pi 5: 4)
PWM_BITS = 11            # Color depth (lower = faster refresh)
BRIGHTNESS = 80          # 0–100

# --- Location (for weather) --------------------------------------------------
LATITUDE = 39.7294       # Your latitude
LONGITUDE = -104.8319    # Your longitude
TIMEZONE = "America/Denver"
LOCATION_NAME = "Denver, CO"
UNIT_SYSTEM = "imperial" # "imperial" (°F) or "metric" (°C)

# --- Sports: Teams to track --------------------------------------------------
# sport options:  "football", "basketball", "baseball", "hockey"
# league options: "nfl", "nba", "mlb", "nhl"
TRACKED_TEAMS = [
    {"name": "Broncos",   "abbr": "DEN", "sport": "football",   "league": "nfl"},
    {"name": "Nuggets",   "abbr": "DEN", "sport": "basketball", "league": "nba"},
    {"name": "Rockies",   "abbr": "COL", "sport": "baseball",   "league": "mlb"},
    {"name": "Avalanche", "abbr": "COL", "sport": "hockey",     "league": "nhl"},
]

# --- Display Timing ----------------------------------------------------------
SPORTS_CYCLE_INTERVAL   = 10   # Seconds between cycling multiple live games
WEATHER_REFRESH_SECS    = 600  # 10 minutes
FORECAST_REFRESH_SECS   = 3600 # 1 hour
SPORTS_REFRESH_SECS     = 30   # 30 seconds during live games
SCHEDULE_REFRESH_SECS   = 3600 # 1 hour for game schedules

# --- Layout ------------------------------------------------------------------
# When sports are active, the clock/weather bar is compressed to the top N rows
CLOCK_WEATHER_FULL_ROWS       = PANEL_ROWS        # when no sports
CLOCK_WEATHER_COMPRESSED_ROWS = 16                # top strip when sports active
SPORTS_SECTION_TOP_ROW        = 16                # where sports section starts

# --- Fonts (relative to project root) ----------------------------------------
FONT_LARGE  = "assets/fonts/9x18.bdf"   # Clock, scores
FONT_MEDIUM = "assets/fonts/6x13.bdf"   # Labels, team names
FONT_SMALL  = "assets/fonts/5x8.bdf"    # Forecast, small text
