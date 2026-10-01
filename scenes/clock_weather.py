# =============================================================================
# scenes/clock_weather.py — Clock, current conditions, and 5-day forecast
# =============================================================================

import datetime
from rgbmatrix import RGBMatrix

import config
from scenes.base_scene import BaseScene
from data.weather import WeatherData, WeatherFetcher
from utils.colors import WHITE, DIM_WHITE, YELLOW, CYAN, DARK_GRAY, WEATHER_COLORS
from utils.fonts import load_font


# Weather condition → simple icon drawn in pixels
# Each icon is a list of (x_offset, y_offset, color_key) tuples
# relative to an origin point, 5×5 max
def _sun_pixels(cx, cy, color):
    """Draw a simple sun icon centered at cx, cy."""
    pixels = []
    # Center dot
    pixels.append((cx, cy, color))
    # Cardinal rays
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        pixels.append((cx+dx, cy+dy, color))
    # Diagonal rays (dimmer)
    dim_color = tuple(c//2 for c in color)
    for dx, dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
        pixels.append((cx+dx, cy+dy, dim_color))
    return pixels


def _cloud_pixels(cx, cy, color):
    """Draw a simple cloud blob."""
    pixels = []
    for dx, dy in [(-1,0),(0,0),(1,0),(0,-1),(1,-1)]:
        pixels.append((cx+dx, cy+dy, color))
    return pixels


def _rain_pixels(cx, cy, color):
    pixels = _cloud_pixels(cx, cy-1, (140, 140, 160))
    rain_color = (60, 120, 200)
    for dx in [-1, 0, 1]:
        pixels.append((cx+dx, cy+2, rain_color))
    return pixels


def _snow_pixels(cx, cy, color):
    pixels = _cloud_pixels(cx, cy-1, (140, 140, 160))
    for dx in [-1, 0, 1]:
        pixels.append((cx+dx, cy+2, (200, 220, 255)))
    return pixels


ICON_RENDERERS = {
    "sunny":  _sun_pixels,
    "clear":  _sun_pixels,
    "cloudy": _cloud_pixels,
    "rain":   _rain_pixels,
    "snow":   _snow_pixels,
    "fog":    _cloud_pixels,
    "storm":  _rain_pixels,
    "default":_cloud_pixels,
}


class ClockWeatherScene(BaseScene):
    """
    Full-panel mode: large clock top, current conditions middle, forecast bottom.
    Compressed mode: single-line clock + temp + condition across the top strip.
    """

    def __init__(self, matrix: RGBMatrix, weather_fetcher: WeatherFetcher):
        super().__init__(matrix)
        self._weather = weather_fetcher
        self._font_large  = load_font(config.FONT_LARGE)
        self._font_medium = load_font(config.FONT_MEDIUM)
        self._font_small  = load_font(config.FONT_SMALL)

    # ------------------------------------------------------------------
    def render(self, compressed: bool = False) -> None:
        """
        compressed=False → use full panel height
        compressed=True  → draw only into the top CLOCK_WEATHER_COMPRESSED_ROWS rows
        """
        weather = self._weather.get()
        now = datetime.datetime.now()

        if compressed:
            self._render_compressed(now, weather)
        else:
            self._render_full(now, weather)

    # ------------------------------------------------------------------
    def _render_full(self, now: datetime.datetime, weather: WeatherData):
        rows = self.matrix.height

        # --- Row 0-13: Clock ---
        time_str  = now.strftime("%-I:%M")
        ampm_str  = now.strftime("%p")
        date_str  = now.strftime("%a %b %-d")

        self._draw_text(self._font_large,  2, 13, WHITE, time_str)
        self._draw_text(self._font_small, 38,  8, DIM_WHITE, ampm_str)
        self._draw_text(self._font_small,  2, 22, DIM_WHITE, date_str)

        # Separator line
        self._draw_line(0, 24, self.matrix.width - 1, 24, DARK_GRAY)

        # --- Row 25-36: Current conditions ---
        cur = weather.current
        unit = "°F" if config.UNIT_SYSTEM == "imperial" else "°C"
        temp_str  = f"{int(cur.temp)}{unit}"
        feel_str  = f"Feels {int(cur.feels_like)}{unit}"

        self._draw_text(self._font_medium,  2, 34, YELLOW, temp_str)
        self._draw_text(self._font_small,  32, 30, DIM_WHITE, cur.condition[:12])
        self._draw_text(self._font_small,  32, 37, DIM_WHITE, feel_str)

        # Condition icon at top-right
        icon_color = WEATHER_COLORS.get(cur.condition_key, (180,180,180))
        renderer   = ICON_RENDERERS.get(cur.condition_key, _cloud_pixels)
        for px, py, col in renderer(self.matrix.width - 7, 30, icon_color):
            self._set_pixel(px, py, col)

        # Separator line
        self._draw_line(0, 39, self.matrix.width - 1, 39, DARK_GRAY)

        # --- Row 40-63: 5-day forecast ---
        forecast = weather.forecast[:5]
        if forecast:
            col_w = self.matrix.width // len(forecast)
            for i, day in enumerate(forecast):
                x = i * col_w + 1
                # Day label
                self._draw_text(self._font_small, x, 47, CYAN, day.label[:3])
                # High
                self._draw_text(self._font_small, x, 55, (220, 100, 60),
                                f"{int(day.high)}°")
                # Low
                self._draw_text(self._font_small, x, 63, (80, 140, 220),
                                f"{int(day.low)}°")

    # ------------------------------------------------------------------
    def _render_compressed(self, now: datetime.datetime, weather: WeatherData):
        """Single strip: TIME  TEMP  CONDITION — fits in top 16 rows."""
        h = config.CLOCK_WEATHER_COMPRESSED_ROWS

        time_str = now.strftime("%-I:%M%p")
        cur = weather.current
        unit = "°" if config.UNIT_SYSTEM == "imperial" else "°C"
        temp_str = f"{int(cur.temp)}{unit}"
        cond_str = cur.condition[:8]

        self._draw_text(self._font_small, 1,  8, WHITE,    time_str)
        self._draw_text(self._font_small, 1, 15, YELLOW,   temp_str)
        self._draw_text(self._font_small, 28, 15, DIM_WHITE, cond_str)

        # Tiny condition icon (top right)
        icon_color = WEATHER_COLORS.get(cur.condition_key, (180,180,180))
        renderer   = ICON_RENDERERS.get(cur.condition_key, _cloud_pixels)
        for px, py, col in renderer(self.matrix.width - 5, 8, icon_color):
            self._set_pixel(px, py, col)

        # Bottom separator
        self._draw_line(0, h - 1, self.matrix.width - 1, h - 1, DARK_GRAY)
