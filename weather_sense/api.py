"""Open-Meteo clients: geocoding, forecast, air quality, IP location."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Optional

import requests
import streamlit as st

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
IP_URL = "https://ipwho.is/"
TIMEOUT = 12

CURRENT_FIELDS = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,"
    "precipitation,weather_code,cloud_cover,pressure_msl,"
    "wind_speed_10m,wind_direction_10m,wind_gusts_10m"
)
HOURLY_FIELDS = (
    "temperature_2m,weather_code,precipitation_probability,uv_index,visibility,is_day"
)
DAILY_FIELDS = (
    "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,"
    "uv_index_max,precipitation_probability_max,precipitation_sum,wind_speed_10m_max"
)


class WeatherError(Exception):
    """Raised when an upstream service cannot be reached."""


# ---------------------------------------------------------------------------
# Weather codes
# ---------------------------------------------------------------------------
_CODES: dict[int, tuple[str, str]] = {
    0: ("Clear sky", "clear"),
    1: ("Mainly clear", "mostly"),
    2: ("Partly cloudy", "partly"),
    3: ("Overcast", "overcast"),
    45: ("Fog", "fog"),
    48: ("Depositing rime fog", "fog"),
    51: ("Light drizzle", "drizzle"),
    53: ("Drizzle", "drizzle"),
    55: ("Dense drizzle", "drizzle"),
    56: ("Freezing drizzle", "sleet"),
    57: ("Dense freezing drizzle", "sleet"),
    61: ("Slight rain", "rain"),
    63: ("Rain", "rain"),
    65: ("Heavy rain", "heavy-rain"),
    66: ("Freezing rain", "sleet"),
    67: ("Heavy freezing rain", "sleet"),
    71: ("Slight snow", "snow"),
    73: ("Snow", "snow"),
    75: ("Heavy snow", "snow"),
    77: ("Snow grains", "snow"),
    80: ("Rain showers", "rain"),
    81: ("Heavy rain showers", "heavy-rain"),
    82: ("Violent rain showers", "heavy-rain"),
    85: ("Snow showers", "snow"),
    86: ("Heavy snow showers", "snow"),
    95: ("Thunderstorm", "thunder"),
    96: ("Thunderstorm with hail", "hail"),
    99: ("Thunderstorm with heavy hail", "hail"),
}

# Condition family -> (label family key, accent color)
FAMILY_STYLE: dict[str, tuple[str, str]] = {
    "clear": ("Clear sky", "#F5B94C"),
    "mostly": ("Mainly clear", "#E8C56B"),
    "partly": ("Partly cloudy", "#9FB4CC"),
    "overcast": ("Overcast", "#8B97A8"),
    "fog": ("Fog", "#9AA3B2"),
    "drizzle": ("Drizzle", "#6EA8FE"),
    "rain": ("Rain", "#5B8DEF"),
    "heavy-rain": ("Heavy rain", "#4F8CF7"),
    "sleet": ("Wintry mix", "#7DD3FC"),
    "snow": ("Snow", "#A8D8FF"),
    "thunder": ("Thunderstorm", "#8B7CF6"),
    "hail": ("Thunderstorm", "#8B7CF6"),
}


def code_info(code: int, is_day: bool = True) -> tuple[str, str, str]:
    """Return (condition label, icon key, accent hex) for a WMO weather code."""
    label, family = _CODES.get(code, ("Unknown", "partly"))
    style_label, accent = FAMILY_STYLE.get(family, ("Partly cloudy", "#9FB4CC"))
    if family in ("clear", "mostly", "partly"):
        suffix = "" if family == "clear" else ""
        label = style_label + suffix
        key = family + ("-day" if is_day else "-night")
    else:
        key = family
    return label, key, accent


def wind_dir_name(deg: float) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[round(deg / 45) % 8]


def wind_dir_full(deg: float) -> str:
    full = {
        "N": "north", "NE": "north-east", "E": "east", "SE": "south-east",
        "S": "south", "SW": "south-west", "W": "west", "NW": "north-west",
    }
    return full[wind_dir_name(deg)]


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def _get(url: str, params: dict) -> dict:
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except (requests.exceptions.RequestException, ValueError) as exc:
        raise WeatherError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Cached API calls
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def geocode(query: str, count: int = 6) -> list[dict]:
    """City search via Open-Meteo geocoding (offline gazetteer fallback)."""
    q = query.strip()
    if not q:
        return []
    try:
        data = _get(GEO_URL, {"name": q, "count": count, "language": "en", "format": "json"})
    except WeatherError:
        from weather_sense.sample import gazetteer
        return gazetteer(q, count)
    out = []
    for r in data.get("results", []):
        out.append({
            "name": r.get("name", q),
            "admin": r.get("admin1", ""),
            "country": r.get("country", ""),
            "country_code": r.get("country_code", ""),
            "lat": r["latitude"],
            "lon": r["longitude"],
        })
    return out


@st.cache_data(ttl=300, show_spinner=False)
def fetch_forecast(lat: float, lon: float) -> dict:
    return _get(FORECAST_URL, {
        "latitude": lat, "longitude": lon,
        "current": CURRENT_FIELDS,
        "hourly": HOURLY_FIELDS,
        "daily": DAILY_FIELDS,
        "timezone": "auto",
        "forecast_days": 7,
        "wind_speed_unit": "kmh",
    })


@st.cache_data(ttl=300, show_spinner=False)
def fetch_aqi(lat: float, lon: float) -> dict:
    return _get(AQI_URL, {
        "latitude": lat, "longitude": lon,
        "current": "us_aqi,pm2_5,pm10",
        "timezone": "auto",
    })


@st.cache_data(ttl=60 * 60, show_spinner=False)
def locate_by_ip() -> Optional[dict]:
    """Best-effort city-level location from the public IP (ipwho.is, no key)."""
    try:
        data = _get(IP_URL, {})
    except WeatherError:
        return None
    if not data.get("success", True):
        return None
    if data.get("latitude") is None or data.get("longitude") is None:
        return None
    return {
        "name": data.get("city") or "Current location",
        "admin": data.get("region", ""),
        "country": data.get("country", ""),
        "country_code": data.get("country_code", ""),
        "lat": data["latitude"],
        "lon": data["longitude"],
    }


# ---------------------------------------------------------------------------
# Bundle: weather + AQI fetched in parallel, offline fallback if needed
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def fetch_bundle(lat: float, lon: float) -> dict:
    """Fetch forecast + AQI in parallel. Falls back to sample data offline."""
    weather: Optional[dict] = None
    aqi: Optional[dict] = None
    offline = False
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_weather = pool.submit(fetch_forecast, lat, lon)
        f_aqi = pool.submit(fetch_aqi, lat, lon)
        try:
            weather = f_weather.result()
        except WeatherError:
            weather = None
        try:
            aqi = f_aqi.result()
        except WeatherError:
            aqi = None
    if weather is None:
        offline = True
        from weather_sense import sample
        weather = sample.forecast(lat, lon)
        aqi = aqi or sample.air_quality(lat, lon)
    return {"weather": weather, "aqi": aqi or {}, "offline": offline}


@st.cache_data(ttl=600, show_spinner=False)
def city_temp(place: dict) -> Optional[float]:
    """Current temperature for a saved city chip (sample fallback offline)."""
    try:
        b = fetch_bundle(place["lat"], place["lon"])
        return b["weather"]["current"]["temperature_2m"]
    except WeatherError:
        return None


def city_temps(places: list[dict]) -> dict[str, Optional[float]]:
    """Parallel current temps keyed by place name."""
    out: dict[str, Optional[float]] = {}
    if not places:
        return out
    with ThreadPoolExecutor(max_workers=min(6, len(places))) as pool:
        futs = {pool.submit(city_temp, p): p for p in places}
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                out[p["name"]] = fut.result()
            except Exception:
                out[p["name"]] = None
    return out


# ---------------------------------------------------------------------------
# Derived insights (no extra API calls)
# ---------------------------------------------------------------------------
def aqi_info(aqi: Optional[float]) -> tuple[str, str, float, str]:
    """Return (label, color, bar percent, advice)."""
    if not aqi:
        return "Unavailable", "#8B97A8", 0, "Air quality data unavailable right now."
    if aqi <= 50:
        return "Good", "#34C759", 8, "Air is clean — enjoy outdoor activities."
    if aqi <= 100:
        return "Moderate", "#E5B83E", 24, "Acceptable; unusually sensitive people should take it easy."
    if aqi <= 150:
        return "Unhealthy for sensitive groups", "#F08C2E", 41, "Sensitive groups should reduce intense outdoor activity."
    if aqi <= 200:
        return "Unhealthy", "#EF5B5B", 58, "Everyone may begin to feel effects — limit time outdoors."
    if aqi <= 300:
        return "Very unhealthy", "#A45BF0", 76, "Health alert — avoid outdoor activity if you can."
    return "Hazardous", "#8B4BF0", 94, "Emergency conditions — stay indoors."


def stargazing(cloud: int, aqi: Optional[float], family_key: str) -> tuple[int, str, str, str]:
    if family_key in ("rain", "heavy-rain", "snow", "thunder", "hail", "sleet", "fog", "drizzle"):
        return 0, "Not tonight", "#EF5B5B", "Cloud cover and precipitation block the sky."
    score = max(0, min(100, 100 - cloud - (min(aqi // 5, 30) if aqi else 0)))
    if score >= 75:
        return score, "Excellent", "#34C759", "Clear and dark — ideal for stargazing."
    if score >= 50:
        return score, "Good", "#7BC96F", "Most stars will be visible between clouds."
    if score >= 25:
        return score, "Fair", "#E5B83E", "Broken clouds — bright objects only."
    return score, "Poor", "#EF5B5B", "Too cloudy to see much tonight."


def mosquito(temp: float, humidity: float) -> tuple[str, str, str]:
    if temp >= 25 and humidity >= 70:
        return "High", "#EF5B5B", "Warm and humid — peak activity. Use repellent after sunset."
    if temp >= 20 and humidity >= 55:
        return "Moderate", "#F08C2E", "Some activity in the evening. Take standard precautions."
    return "Low", "#34C759", "Conditions are unfavourable for mosquitoes."


def outdoor_score(temp: float, wind: float, aqi: Optional[float], family: str) -> tuple[int, str, str, str]:
    if family in ("thunder", "hail"):
        return 0, "Dangerous", "#EF5B5B", "Severe weather — stay indoors."
    score = 100
    if temp > 38 or temp < 0:
        score -= 50
    elif temp > 33 or temp < 5:
        score -= 25
    elif 18 <= temp <= 28:
        score += 10
    if wind > 60:
        score -= 40
    elif wind > 40:
        score -= 20
    elif wind > 25:
        score -= 10
    if aqi:
        if aqi > 150:
            score -= 40
        elif aqi > 100:
            score -= 20
        elif aqi > 50:
            score -= 10
    if family in ("rain", "heavy-rain", "snow", "drizzle", "sleet"):
        score -= 30
    if family == "fog":
        score -= 15
    score = max(0, min(100, score))
    if score >= 75:
        return score, "Great", "#34C759", "Excellent conditions — go for it."
    if score >= 55:
        return score, "Good", "#7BC96F", "Solid window for training. Stay hydrated."
    if score >= 35:
        return score, "Moderate", "#E5B83E", "Workable — keep sessions short."
    if score >= 15:
        return score, "Poor", "#F08C2E", "Tough conditions — consider rescheduling."
    return score, "Avoid", "#EF5B5B", "Not recommended right now."


def build_alerts(label: str, temp: float, wind: float, aqi: Optional[float],
                 gusts: float, family: str) -> list[tuple[str, str, str]]:
    alerts: list[tuple[str, str, str]] = []
    if temp >= 40:
        alerts.append(("Extreme heat warning",
                       f"{temp:.0f}\u00b0C is dangerous. Stay hydrated, avoid direct sun.",
                       "#EF5B5B"))
    elif temp >= 35:
        alerts.append(("Heat advisory",
                       f"{temp:.0f}\u00b0C — limit prolonged outdoor exposure.", "#F08C2E"))
    if temp <= 0:
        alerts.append(("Freezing conditions",
                       f"{temp:.0f}\u00b0C — frostbite risk on exposed skin.", "#6EA8FE"))
    if family == "thunder":
        alerts.append(("Thunderstorm",
                       "Avoid open ground, water and metal objects.", "#8B7CF6"))
    if family == "snow" and (gusts or wind) > 40:
        alerts.append(("Blizzard conditions",
                       f"Snow with {max(wind, gusts or 0):.0f} km/h gusts — travel not advised.",
                       "#5B8DEF"))
    if gusts and gusts > 70:
        alerts.append(("High wind gusts",
                        f"Gusts to {gusts:.0f} km/h — secure loose objects.", "#EF5B5B"))
    elif wind > 50:
        alerts.append(("Strong wind",
                       f"{wind:.0f} km/h sustained. Take care outdoors.", "#F08C2E"))
    if aqi and aqi > 200:
        alerts.append(("Unhealthy air quality",
                       f"US AQI {aqi:.0f} — wear a mask outdoors, keep windows shut.", "#A45BF0"))
    elif aqi and aqi > 150:
        alerts.append(("Poor air quality",
                       f"US AQI {aqi:.0f} — sensitive groups should stay indoors.", "#F08C2E"))
    if family == "fog":
        alerts.append(("Dense fog",
                       "Greatly reduced visibility — drive slowly with low beams.", "#9AA3B2"))
    return alerts


# ---------------------------------------------------------------------------
# Units & formatting
# ---------------------------------------------------------------------------
def to_unit(celsius: float, unit: str) -> float:
    if unit == "F":
        return celsius * 9 / 5 + 32
    return celsius


def fmt_t(celsius: Optional[float], unit: str, decimals: int = 0) -> str:
    if celsius is None:
        return "--"
    v = to_unit(celsius, unit)
    return f"{v:.{decimals}f}\u00b0"


def fmt_clock(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%H:%M")
    except ValueError:
        return iso_str or "--"


def local_now(tz_name: str) -> datetime:
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now(timezone.utc)


def _align(now: datetime, *parsed: datetime) -> datetime:
    """Make `now` comparable with parsed timestamps (tz-aware or naive)."""
    if not parsed:
        return now
    target = parsed[0]
    if target.tzinfo is None and now.tzinfo is not None:
        return now.replace(tzinfo=None)
    if target.tzinfo is not None and now.tzinfo is None:
        return now.replace(tzinfo=target.tzinfo)
    return now


def sun_progress(sunrise_iso: str, sunset_iso: str, now: datetime) -> Optional[float]:
    """0..1 progress of daylight, or None if outside daylight."""
    try:
        rise = datetime.fromisoformat(sunrise_iso)
        set_ = datetime.fromisoformat(sunset_iso)
        now = _align(now, rise, set_)
        if now < rise or now > set_:
            return None
        total = (set_ - rise).total_seconds()
        if total <= 0:
            return None
        return max(0.0, min(1.0, (now - rise).total_seconds() / total))
    except ValueError:
        return None


def daylight_left(sunset_iso: str, now: datetime) -> str:
    try:
        set_ = datetime.fromisoformat(sunset_iso)
        now = _align(now, set_)
        delta = set_ - now
        if delta.total_seconds() <= 0:
            return "Daylight has ended"
        mins = int(delta.total_seconds() // 60)
        h, m = divmod(mins, 60)
        return f"{h}h {m}m of daylight left"
    except ValueError:
        return ""
