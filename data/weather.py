# =============================================================================
# data/weather.py — Weather fetching via Open-Meteo (no API key required)
# =============================================================================

import time
import logging
import requests
from dataclasses import dataclass, field
from typing import List, Optional

import config

logger = logging.getLogger(__name__)

# WMO Weather Interpretation Codes → human label + color key
WMO_CODES = {
    0:  ("Clear",       "sunny"),
    1:  ("Mostly Clear","sunny"),
    2:  ("Partly Cloudy","cloudy"),
    3:  ("Overcast",    "cloudy"),
    45: ("Foggy",       "fog"),
    48: ("Icy Fog",     "fog"),
    51: ("Light Drizzle","rain"),
    53: ("Drizzle",     "rain"),
    55: ("Heavy Drizzle","rain"),
    61: ("Light Rain",  "rain"),
    63: ("Rain",        "rain"),
    65: ("Heavy Rain",  "rain"),
    71: ("Light Snow",  "snow"),
    73: ("Snow",        "snow"),
    75: ("Heavy Snow",  "snow"),
    77: ("Sleet",       "snow"),
    80: ("Showers",     "rain"),
    81: ("Showers",     "rain"),
    82: ("Heavy Showers","rain"),
    85: ("Snow Showers","snow"),
    86: ("Heavy Snow Showers","snow"),
    95: ("Thunderstorm","storm"),
    96: ("Thunderstorm","storm"),
    99: ("Severe Storm","storm"),
}


@dataclass
class CurrentWeather:
    temp: float = 0.0
    feels_like: float = 0.0
    condition: str = "Unknown"
    condition_key: str = "default"
    humidity: int = 0
    wind_speed: float = 0.0


@dataclass
class ForecastDay:
    label: str = ""          # "Mon", "Tue", etc.
    high: float = 0.0
    low: float = 0.0
    condition_key: str = "default"


@dataclass
class WeatherData:
    current: CurrentWeather = field(default_factory=CurrentWeather)
    forecast: List[ForecastDay] = field(default_factory=list)
    fetched_at: float = 0.0
    error: Optional[str] = None


class WeatherFetcher:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self._data = WeatherData()
        self._last_current_fetch = 0.0
        self._last_forecast_fetch = 0.0

    def get(self) -> WeatherData:
        """Return cached data, refreshing stale fields as needed."""
        now = time.time()
        if now - self._last_current_fetch > config.WEATHER_REFRESH_SECS:
            self._fetch_current()
            self._last_current_fetch = now
        if now - self._last_forecast_fetch > config.FORECAST_REFRESH_SECS:
            self._fetch_forecast()
            self._last_forecast_fetch = now
        return self._data

    def _is_imperial(self) -> bool:
        return config.UNIT_SYSTEM == "imperial"

    def _fetch_current(self):
        params = {
            "latitude":            config.LATITUDE,
            "longitude":           config.LONGITUDE,
            "current":             "temperature_2m,apparent_temperature,weather_code,relative_humidity_2m,wind_speed_10m",
            "temperature_unit":    "fahrenheit" if self._is_imperial() else "celsius",
            "wind_speed_unit":     "mph" if self._is_imperial() else "kmh",
            "timezone":            config.TIMEZONE,
        }
        try:
            r = requests.get(self.BASE_URL, params=params, timeout=10)
            r.raise_for_status()
            j = r.json()
            c = j["current"]
            code = c.get("weather_code", 0)
            label, key = WMO_CODES.get(code, ("Unknown", "default"))
            self._data.current = CurrentWeather(
                temp=round(c["temperature_2m"]),
                feels_like=round(c["apparent_temperature"]),
                condition=label,
                condition_key=key,
                humidity=c.get("relative_humidity_2m", 0),
                wind_speed=round(c.get("wind_speed_10m", 0)),
            )
            self._data.error = None
        except Exception as e:
            logger.error("Weather current fetch failed: %s", e)
            self._data.error = str(e)

    def _fetch_forecast(self):
        import datetime
        params = {
            "latitude":         config.LATITUDE,
            "longitude":        config.LONGITUDE,
            "daily":            "temperature_2m_max,temperature_2m_min,weather_code",
            "temperature_unit": "fahrenheit" if self._is_imperial() else "celsius",
            "timezone":         config.TIMEZONE,
            "forecast_days":    5,
        }
        try:
            r = requests.get(self.BASE_URL, params=params, timeout=10)
            r.raise_for_status()
            j = r.json()
            daily = j["daily"]
            forecast = []
            for i, date_str in enumerate(daily["time"]):
                if i == 0:
                    label = "Today"
                else:
                    dt = datetime.date.fromisoformat(date_str)
                    label = dt.strftime("%a")
                code = daily["weather_code"][i]
                _, key = WMO_CODES.get(code, ("", "default"))
                forecast.append(ForecastDay(
                    label=label,
                    high=round(daily["temperature_2m_max"][i]),
                    low=round(daily["temperature_2m_min"][i]),
                    condition_key=key,
                ))
            self._data.forecast = forecast
            self._data.fetched_at = time.time()
        except Exception as e:
            logger.error("Weather forecast fetch failed: %s", e)
            self._data.error = str(e)
