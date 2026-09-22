"""Open-Meteo clients: geocoding, forecast, air quality, IP location.

Robustness rules applied throughout this module:

* **Never cache a failure.** Cached helpers raise :class:`WeatherError` when a
  service is unreachable — Streamlit does not cache exceptions — and the public
  wrappers translate that into the offline sample fallback. Without this, one
  bad request would pin the app to stale/empty data for the whole TTL.
* **Never hang the first paint.** Every request uses an explicit
  ``(connect, read)`` timeout and a cached connectivity probe short-circuits
  the whole network path when the sandbox has no egress.
* **Never trust the payload shape.** :func:`normalize_forecast` rebuilds the
  forecast dict so every key the UI reads exists, numbers are numbers (or
  ``None``), and list lengths always match ``time``.
"""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Optional

import requests
import streamlit as st

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
IP_URL = "https://ipwho.is/"

# (connect, read) — a dead network must fail in ~4 s, not 12+.
CONNECT_TIMEOUT = 4.0
READ_TIMEOUT = 10.0
TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)
PROBE_TIMEOUT = (3.0, 5.0)

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

# Condition family -> (label, accent). These stay *real hex*: the accent is the
# one colour the palette re-tunes at paint time (styles.accent_for walks it down
# in lightness until it reads on cream), and severity colours elsewhere in this
# module are CSS var() references so alerts, AQI and insights follow the theme.
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


def code_info(code: Any, is_day: bool = True) -> tuple[str, str, str]:
    """Return (condition label, icon key, accent hex) for a WMO weather code."""
    try:
        code_i = int(code)
    except (TypeError, ValueError):
        code_i = -1
    label, family = _CODES.get(code_i, ("Unknown", "partly"))
    style_label, accent = FAMILY_STYLE.get(family, ("Partly cloudy", "#9FB4CC"))
    if family in ("clear", "mostly", "partly"):
        label = style_label
        key = family + ("-day" if is_day else "-night")
    else:
        key = family
    return label, key, accent


def wind_dir_name(deg: Any) -> str:
    """Compass point for a bearing; tolerant of ``None``/garbage input."""
    d = num(deg)
    if d is None:
        return "--"
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[int(round(d / 45.0)) % 8]


def wind_dir_full(deg: Any) -> str:
    full = {
        "N": "north", "NE": "north-east", "E": "east", "SE": "south-east",
        "S": "south", "SW": "south-west", "W": "west", "NW": "north-west",
    }
    return full.get(wind_dir_name(deg), "unknown direction")


# ---------------------------------------------------------------------------
# Numeric coercion helpers
# ---------------------------------------------------------------------------
def num(value: Any) -> Optional[float]:
    """Best-effort float, or ``None`` when the value is unusable."""
    if value is None or isinstance(value, bool):
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if f != f or f in (float("inf"), float("-inf")):  # NaN / inf
        return None
    return f


def num_or(value: Any, default: float = 0.0) -> float:
    v = num(value)
    return default if v is None else v


def valid_place(place: Any) -> bool:
    """A place is usable only if it carries numeric coordinates."""
    if not isinstance(place, dict):
        return False
    lat, lon = num(place.get("lat")), num(place.get("lon"))
    if lat is None or lon is None:
        return False
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def _get(url: str, params: dict, timeout: Any = TIMEOUT) -> dict:
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except (requests.exceptions.RequestException, ValueError) as exc:
        raise WeatherError(str(exc)) from exc


@st.cache_data(ttl=120, show_spinner=False)
def network_ok() -> bool:
    """Cheap egress probe so an offline sandbox never waits on three timeouts.

    Any HTTP response (even 4xx) proves egress works; only transport errors
    mean "offline". Cached for 2 minutes, so recovery is picked up quickly.
    """
    for method, args in (
        ("head", (FORECAST_URL,)),
        ("get", (GEO_URL,)),
    ):
        try:
            if method == "head":
                requests.head(args[0], timeout=PROBE_TIMEOUT, allow_redirects=True)
            else:
                requests.get(args[0], params={"name": "London", "count": 1},
                             timeout=PROBE_TIMEOUT)
            return True
        except Exception:
            continue
    return False


def _submit_ctx(pool: ThreadPoolExecutor, fn, *args, **kwargs):
    """Submit `fn` to `pool`, carrying the Streamlit script-run context over.

    Without this, cached calls made from worker threads log
    "missing ScriptRunContext" noise. Purely cosmetic — degrades silently.
    """
    ctx = None
    try:
        from streamlit.runtime.scriptrunner import (  # type: ignore
            add_script_run_ctx, get_script_run_ctx,
        )
        ctx = get_script_run_ctx()
    except Exception:
        add_script_run_ctx = None  # type: ignore

    def runner():
        if ctx is not None and add_script_run_ctx is not None:
            try:
                add_script_run_ctx(threading.current_thread(), ctx)
            except Exception:
                pass
        return fn(*args, **kwargs)

    return pool.submit(runner)


# ---------------------------------------------------------------------------
# Cached remote calls (raise on failure so failures are never cached)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def _remote_geocode(query: str, count: int = 6) -> list[dict]:
    data = _get(GEO_URL, {"name": query, "count": count,
                          "language": "en", "format": "json"})
    out: list[dict] = []
    for r in data.get("results") or []:
        if not isinstance(r, dict):
            continue
        place = {
            "name": r.get("name") or query,
            "admin": r.get("admin1") or "",
            "country": r.get("country") or "",
            "country_code": r.get("country_code") or "",
            "lat": num(r.get("latitude")),
            "lon": num(r.get("longitude")),
        }
        # drop malformed hits instead of crashing the UI later
        if valid_place(place):
            out.append(place)
    return out


def geocode(query: str, count: int = 6) -> list[dict]:
    """City search via Open-Meteo geocoding (offline gazetteer fallback)."""
    q = (query or "").strip()
    if not q:
        return []
    hits: Optional[list[dict]] = None
    if network_ok():
        try:
            hits = _remote_geocode(q, count)
        except WeatherError:
            hits = None
    if hits is None:
        from weather_sense.sample import gazetteer
        return gazetteer(q, count)
    return hits


@st.cache_data(ttl=300, show_spinner=False)
def _remote_forecast(lat: float, lon: float) -> dict:
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
def _remote_aqi(lat: float, lon: float) -> dict:
    return _get(AQI_URL, {
        "latitude": lat, "longitude": lon,
        "current": "us_aqi,pm2_5,pm10",
        "timezone": "auto",
    })


@st.cache_data(ttl=60 * 60, show_spinner=False)
def _remote_ip_location() -> dict:
    data = _get(IP_URL, {}, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
    if not data.get("success", True):
        raise WeatherError("ipwho.is reported failure")
    place = {
        "name": data.get("city") or "Current location",
        "admin": data.get("region") or "",
        "country": data.get("country") or "",
        "country_code": data.get("country_code") or "",
        "lat": num(data.get("latitude")),
        "lon": num(data.get("longitude")),
    }
    if not valid_place(place):
        raise WeatherError("ipwho.is returned no usable coordinates")
    return place


def locate_by_ip() -> Optional[dict]:
    """Best-effort city-level location from the public IP (ipwho.is, no key)."""
    if not network_ok():
        return None
    try:
        return _remote_ip_location()
    except WeatherError:
        return None


# ---------------------------------------------------------------------------
# Payload normalisation — the UI can then read keys unconditionally
# ---------------------------------------------------------------------------
_CURRENT_NUMERIC = (
    "temperature_2m", "apparent_temperature", "relative_humidity_2m",
    "precipitation", "cloud_cover", "pressure_msl",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
)
_HOURLY_NUMERIC = (
    "temperature_2m", "precipitation_probability", "uv_index", "visibility",
)
_HOURLY_INT = ("weather_code", "is_day")
_DAILY_NUMERIC = (
    "temperature_2m_max", "temperature_2m_min", "uv_index_max",
    "precipitation_probability_max", "precipitation_sum", "wind_speed_10m_max",
)
_DAILY_INT = ("weather_code",)
_DAILY_STR = ("sunrise", "sunset")


def _list(values: Any) -> list:
    """Any sequence -> list; anything else -> empty list (never None)."""
    return list(values) if isinstance(values, (list, tuple)) else []


def _pad(values: Any, n: int, default: Any = None) -> list:
    """Coerce to a list of exactly `n` entries, so index lookups are safe."""
    out = _list(values)
    if len(out) < n:
        out = out + [default] * (n - len(out))
    return out[:n]


def normalize_forecast(raw: Any) -> dict:
    """Rebuild a forecast payload so the UI never hits KeyError/IndexError."""
    raw = raw if isinstance(raw, dict) else {}
    cur_raw = raw.get("current") if isinstance(raw.get("current"), dict) else {}

    now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    current: dict[str, Any] = {
        "time": str(cur_raw.get("time") or now_iso),
        "weather_code": int(num_or(cur_raw.get("weather_code"), 2)),
        "is_day": 0 if cur_raw.get("is_day") in (0, False, "0") else 1,
    }
    for key in _CURRENT_NUMERIC:
        current[key] = num(cur_raw.get(key))

    hourly_raw = raw.get("hourly") if isinstance(raw.get("hourly"), dict) else {}
    times = [str(t) for t in _list(hourly_raw.get("time"))]
    n_h = len(times)
    hourly: dict[str, Any] = {"time": times}
    for key in _HOURLY_NUMERIC:
        hourly[key] = [num(v) for v in _pad(hourly_raw.get(key), n_h, None)]
    for key in _HOURLY_INT:
        default = 1 if key == "is_day" else 2
        hourly[key] = [int(num_or(v, default)) for v in _pad(hourly_raw.get(key), n_h, default)]

    daily_raw = raw.get("daily") if isinstance(raw.get("daily"), dict) else {}
    d_times = [str(t) for t in _list(daily_raw.get("time"))]
    n_d = len(d_times)
    daily: dict[str, Any] = {"time": d_times}
    for key in _DAILY_NUMERIC:
        daily[key] = [num(v) for v in _pad(daily_raw.get(key), n_d, None)]
    for key in _DAILY_INT:
        daily[key] = [int(num_or(v, 2)) for v in _pad(daily_raw.get(key), n_d, 2)]
    for key in _DAILY_STR:
        daily[key] = [(str(v) if v else "") for v in _pad(daily_raw.get(key), n_d, "")]

    return {
        "latitude": num(raw.get("latitude")),
        "longitude": num(raw.get("longitude")),
        "timezone": str(raw.get("timezone") or "UTC"),
        "utc_offset_seconds": int(num_or(raw.get("utc_offset_seconds"), 0)),
        "current_units": raw.get("current_units") or {},
        "current": current,
        "hourly": hourly,
        "daily": daily,
    }


def normalize_aqi(raw: Any) -> dict:
    """Same idea for the air-quality payload."""
    raw = raw if isinstance(raw, dict) else {}
    cur = raw.get("current") if isinstance(raw.get("current"), dict) else {}
    return {
        "timezone": str(raw.get("timezone") or "UTC"),
        "current": {
            "time": str(cur.get("time") or ""),
            "us_aqi": num(cur.get("us_aqi")),
            "pm2_5": num(cur.get("pm2_5")),
            "pm10": num(cur.get("pm10")),
        },
    }


# ---------------------------------------------------------------------------
# Bundle: weather + AQI in parallel, offline fallback when unreachable
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def _offline_bundle(lat: float, lon: float) -> dict:
    """Cached sample dataset — stable across reruns, expires like live data."""
    from weather_sense import sample
    return {
        "weather": normalize_forecast(sample.forecast(lat, lon)),
        "aqi": normalize_aqi(sample.air_quality(lat, lon)),
        "offline": True,
    }


def fetch_bundle(lat: Any, lon: Any) -> dict:
    """Fetch forecast + AQI in parallel; fall back to sample data offline.

    Deliberately *not* cached itself: the cached layer underneath holds live
    results for 5 minutes, while a cached failure would keep the app offline
    long after the network came back.
    """
    lat_f, lon_f = num(lat), num(lon)
    if lat_f is None or lon_f is None:
        return {"weather": normalize_forecast({}), "aqi": {}, "offline": True}

    if not network_ok():
        return _offline_bundle(lat_f, lon_f)

    weather: Optional[dict] = None
    aqi: Optional[dict] = None
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_weather = _submit_ctx(pool, _remote_forecast, lat_f, lon_f)
        f_aqi = _submit_ctx(pool, _remote_aqi, lat_f, lon_f)
        try:
            weather = f_weather.result()
        except Exception:
            weather = None
        try:
            aqi = f_aqi.result()
        except Exception:
            aqi = None

    if weather is None:
        return _offline_bundle(lat_f, lon_f)
    return {
        "weather": normalize_forecast(weather),
        "aqi": normalize_aqi(aqi) if aqi else {},
        "offline": False,
    }


@st.cache_data(ttl=600, show_spinner=False)
def city_temp(lat: float, lon: float) -> Optional[float]:
    """Current temperature for a saved-city chip (sample fallback offline)."""
    try:
        b = fetch_bundle(lat, lon)
        return num(b["weather"]["current"].get("temperature_2m"))
    except Exception:
        return None


def city_temps(places: list[dict]) -> dict[str, Optional[float]]:
    """Parallel current temps keyed by place name."""
    out: dict[str, Optional[float]] = {}
    usable = [p for p in (places or []) if valid_place(p)]
    if not usable:
        return out
    with ThreadPoolExecutor(max_workers=min(6, len(usable))) as pool:
        futs = {_submit_ctx(pool, city_temp, num(p["lat"]), num(p["lon"])): p
                for p in usable}
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
    a = num(aqi)
    if a is None:
        return "Unavailable", "var(--neutral)", 0, "Air quality data unavailable right now."
    if a <= 50:
        return "Good", "var(--good)", 8, "Air is clean — enjoy outdoor activities."
    if a <= 100:
        return "Moderate", "var(--warn)", 24, "Acceptable; unusually sensitive people should take it easy."
    if a <= 150:
        return "Unhealthy for sensitive groups", "var(--warn-soft)", 41, "Sensitive groups should reduce intense outdoor activity."
    if a <= 200:
        return "Unhealthy", "var(--bad)", 58, "Everyone may begin to feel effects — limit time outdoors."
    if a <= 300:
        return "Very unhealthy", "var(--purple)", 76, "Health alert — avoid outdoor activity if you can."
    return "Hazardous", "var(--purple-deep)", 94, "Emergency conditions — stay indoors."


def stargazing(cloud: Any, aqi: Optional[float], family_key: str) -> tuple[int, str, str, str]:
    if family_key in ("rain", "heavy-rain", "snow", "thunder", "hail", "sleet", "fog", "drizzle"):
        return 0, "Not tonight", "var(--bad)", "Cloud cover and precipitation block the sky."
    c = num_or(cloud, 50)
    a = num(aqi)
    score = max(0, min(100, int(100 - c - (min(a / 5.0, 30) if a is not None else 0))))
    if score >= 75:
        return score, "Excellent", "var(--good)", "Clear and dark — ideal for stargazing."
    if score >= 50:
        return score, "Good", "var(--good-soft)", "Most stars will be visible between clouds."
    if score >= 25:
        return score, "Fair", "var(--warn)", "Broken clouds — bright objects only."
    return score, "Poor", "var(--bad)", "Too cloudy to see much tonight."


def mosquito(temp: Any, humidity: Any) -> tuple[str, str, str]:
    t, h = num_or(temp, 15), num_or(humidity, 50)
    if t >= 25 and h >= 70:
        return "High", "var(--bad)", "Warm and humid — peak activity. Use repellent after sunset."
    if t >= 20 and h >= 55:
        return "Moderate", "var(--warn-soft)", "Some activity in the evening. Take standard precautions."
    return "Low", "var(--good)", "Conditions are unfavourable for mosquitoes."


def outdoor_score(temp: Any, wind: Any, aqi: Optional[float], family: str) -> tuple[int, str, str, str]:
    if family in ("thunder", "hail"):
        return 0, "Dangerous", "var(--bad)", "Severe weather — stay indoors."
    t = num(temp)
    if t is None:
        return 50, "Unknown", "var(--neutral)", "Not enough live data to score the outdoors."
    w = num_or(wind, 0)
    a = num(aqi)
    score = 100
    if t > 38 or t < 0:
        score -= 50
    elif t > 33 or t < 5:
        score -= 25
    elif 18 <= t <= 28:
        score += 10
    if w > 60:
        score -= 40
    elif w > 40:
        score -= 20
    elif w > 25:
        score -= 10
    if a is not None:
        if a > 150:
            score -= 40
        elif a > 100:
            score -= 20
        elif a > 50:
            score -= 10
    if family in ("rain", "heavy-rain", "snow", "drizzle", "sleet"):
        score -= 30
    if family == "fog":
        score -= 15
    score = max(0, min(100, score))
    if score >= 75:
        return score, "Great", "var(--good)", "Excellent conditions — go for it."
    if score >= 55:
        return score, "Good", "var(--good-soft)", "Solid window for training. Stay hydrated."
    if score >= 35:
        return score, "Moderate", "var(--warn)", "Workable — keep sessions short."
    if score >= 15:
        return score, "Poor", "var(--warn-soft)", "Tough conditions — consider rescheduling."
    return score, "Avoid", "var(--bad)", "Not recommended right now."


def build_alerts(label: str, temp: Any, wind: Any, aqi: Optional[float],
                 gusts: Any, family: str) -> list[tuple[str, str, str]]:
    t = num(temp)
    w = num_or(wind, 0)
    g = num_or(gusts, 0)
    a = num(aqi)
    alerts: list[tuple[str, str, str]] = []
    if t is not None:
        if t >= 40:
            alerts.append(("Extreme heat warning",
                           f"{t:.0f}\u00b0C is dangerous. Stay hydrated, avoid direct sun.",
                           "var(--bad)"))
        elif t >= 35:
            alerts.append(("Heat advisory",
                           f"{t:.0f}\u00b0C — limit prolonged outdoor exposure.", "var(--warn-soft)"))
        if t <= 0:
            alerts.append(("Freezing conditions",
                           f"{t:.0f}\u00b0C — frostbite risk on exposed skin.", "var(--precip)"))
    if family == "thunder":
        alerts.append(("Thunderstorm",
                       "Avoid open ground, water and metal objects.", "var(--violet)"))
    if family == "snow" and max(w, g) > 40:
        alerts.append(("Blizzard conditions",
                       f"Snow with {max(w, g):.0f} km/h gusts — travel not advised.",
                       "var(--accent)"))
    if g > 70:
        alerts.append(("High wind gusts",
                       f"Gusts to {g:.0f} km/h — secure loose objects.", "var(--bad)"))
    elif w > 50:
        alerts.append(("Strong wind",
                       f"{w:.0f} km/h sustained. Take care outdoors.", "var(--warn-soft)"))
    if a is not None:
        if a > 200:
            alerts.append(("Unhealthy air quality",
                           f"US AQI {a:.0f} — wear a mask outdoors, keep windows shut.", "var(--purple)"))
        elif a > 150:
            alerts.append(("Poor air quality",
                           f"US AQI {a:.0f} — sensitive groups should stay indoors.", "var(--warn-soft)"))
    if family == "fog":
        alerts.append(("Dense fog",
                       "Greatly reduced visibility — drive slowly with low beams.",
                       "var(--neutral)"))
    return alerts


# ---------------------------------------------------------------------------
# Units & formatting
# ---------------------------------------------------------------------------
def to_unit(celsius: Any, unit: str) -> Optional[float]:
    """Convert °C to the display unit; ``None`` in, ``None`` out."""
    c = num(celsius)
    if c is None:
        return None
    return c * 9 / 5 + 32 if unit == "F" else c


def fmt_t(celsius: Optional[float], unit: str, decimals: int = 0) -> str:
    v = to_unit(celsius, unit)
    if v is None:
        return "--"
    return f"{v:.{decimals}f}\u00b0"


def fmt_int(value: Any, suffix: str = "", placeholder: str = "--") -> str:
    """Integer-ish formatting that never prints ``None``."""
    v = num(value)
    return placeholder if v is None else f"{v:.0f}{suffix}"


def _parse_dt(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def fmt_clock(iso_str: Any) -> str:
    dt = _parse_dt(iso_str)
    return dt.strftime("%H:%M") if dt else "--"


def fmt_day(value: Any, fmt: str = "%a") -> str:
    """Parse an Open-Meteo daily date (``YYYY-MM-DD``) defensively."""
    s = str(value or "")
    for parser in (lambda: datetime.strptime(s[:10], "%Y-%m-%d"),
                   lambda: _parse_dt(s)):
        try:
            dt = parser()
        except (TypeError, ValueError):
            dt = None
        if dt:
            return dt.strftime(fmt)
    return s[:10] or "--"


def local_now(tz_name: str) -> datetime:
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now(timezone.utc)


def _align(now: datetime, *parsed: Optional[datetime]) -> datetime:
    """Make `now` comparable with parsed timestamps (tz-aware or naive)."""
    target = next((p for p in parsed if p is not None), None)
    if target is None:
        return now
    if target.tzinfo is None and now.tzinfo is not None:
        return now.replace(tzinfo=None)
    if target.tzinfo is not None and now.tzinfo is None:
        return now.replace(tzinfo=target.tzinfo)
    return now


def sun_progress(sunrise_iso: Any, sunset_iso: Any, now: datetime) -> Optional[float]:
    """0..1 progress of daylight, or None if outside daylight / unknown."""
    rise, set_ = _parse_dt(sunrise_iso), _parse_dt(sunset_iso)
    if rise is None or set_ is None:
        return None
    now = _align(now, rise, set_)
    if now < rise or now > set_:
        return None
    total = (set_ - rise).total_seconds()
    if total <= 0:
        return None
    return max(0.0, min(1.0, (now - rise).total_seconds() / total))


def daylight_left(sunset_iso: Any, now: datetime) -> str:
    set_ = _parse_dt(sunset_iso)
    if set_ is None:
        return ""
    now = _align(now, set_)
    delta = set_ - now
    if delta.total_seconds() <= 0:
        return "Daylight has ended"
    mins = int(delta.total_seconds() // 60)
    h, m = divmod(mins, 60)
    return f"{h}h {m}m of daylight left"
