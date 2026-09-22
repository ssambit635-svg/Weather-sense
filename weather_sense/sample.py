"""Procedural sample data — used ONLY when the live APIs are unreachable.

Keeps the UI demonstrable in offline/sandboxed environments. Every screen
labels this state explicitly so nothing is ever passed off as live data.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone


def _rng(lat: float, lon: float, salt: int = 0) -> random.Random:
    seed = int(abs(lat) * 1000 + abs(lon) * 1000) + salt * 7919
    return random.Random(seed)


def _base_temp(lat: float, lon: float, hour: int) -> float:
    # Rough climate model: colder toward the poles, daily sinusoid.
    seasonal = 30 - abs(lat) * 0.55
    diurnal = 6 * math.sin((hour - 9) / 24 * 2 * math.pi)
    return round(seasonal + diurnal + random.uniform(-1.5, 1.5), 1)


def forecast(lat: float, lon: float) -> dict:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    r = _rng(lat, lon)

    family_pool = ["clear", "partly", "cloud", "rain", "drizzle", "snow", "thunder", "fog"]
    daily_codes = {
        "clear": 0, "partly": 2, "cloud": 3, "rain": 61,
        "drizzle": 51, "snow": 71, "thunder": 95, "fog": 45,
    }

    # ---- hourly (48h starting at current hour) ----
    h_times, h_temp, h_code, h_precip, h_uv, h_vis, h_day = [], [], [], [], [], [], []
    for i in range(-6, 42):
        t = now + timedelta(hours=i)
        hr = t.hour
        temp = _base_temp(lat, lon, hr)
        fam = family_pool[(int(abs(lat + lon)) + hr // 6) % len(family_pool)]
        code = daily_codes[fam]
        if fam == "clear":
            uv = max(0, round(8 * math.sin(max(0, (hr - 6) / 12) * math.pi), 1))
            vis = 24000
            precip = 0
        elif fam in ("rain", "drizzle", "thunder"):
            uv = 0.0
            vis = 9000 if fam != "drizzle" else 14000
            precip = r.choice([45, 60, 75, 85])
        elif fam == "snow":
            uv, vis, precip = 1.0, 7000, 65
        elif fam == "fog":
            uv, vis, precip = 0.5, 900, 5
        else:
            uv = max(0, round(5 * math.sin(max(0, (hr - 6) / 12) * math.pi), 1))
            vis = 18000
            precip = 5
        h_times.append(t.isoformat())
        h_temp.append(temp)
        h_code.append(code)
        h_precip.append(precip)
        h_uv.append(uv)
        h_vis.append(vis)
        h_day.append(1 if 6 <= hr < 20 else 0)

    # ---- daily (7 days) ----
    d_times, d_max, d_min, d_code, d_rise, d_set, d_uvmax, d_pprob, d_psum, d_wind = (
        [], [], [], [], [], [], [], [], [], []
    )
    today0 = now.replace(hour=0)
    for d in range(7):
        day = today0 + timedelta(days=d)
        hr_noon = 12
        base = _base_temp(lat, lon, hr_noon) + random.uniform(-2, 2)  # noqa: F841
        fam = family_pool[r.randrange(len(family_pool))]
        d_times.append(day.date().isoformat())
        d_max.append(round(base + 3, 1))
        d_min.append(round(base - 7, 1))
        d_code.append(daily_codes[fam])
        d_rise.append((day + timedelta(hours=6, minutes=12)).isoformat())
        d_set.append((day + timedelta(hours=19, minutes=48)).isoformat())
        d_uvmax.append(round(random.uniform(2, 9), 1))
        d_pprob.append(r.choice([0, 10, 25, 45, 60]))
        d_psum.append(round(random.uniform(0, 12), 1))
        d_wind.append(round(random.uniform(4, 38), 1))

    # current = first future hour slot (index where hour matches)
    idx = 6  # -6 offset brings us to current hour
    return {
        "latitude": lat,
        "longitude": lon,
        "timezone": "UTC",
        "current_units": {"temperature_2m": "°C"},
        "current": {
            "time": h_times[idx],
            "temperature_2m": h_temp[idx],
            "relative_humidity_2m": r.randint(38, 88),
            "apparent_temperature": round(h_temp[idx] + random.uniform(-3, 3), 1),
            "is_day": h_day[idx],
            "precipitation": 0 if h_precip[idx] < 40 else round(r.uniform(0.2, 3.0), 1),
            "weather_code": h_code[idx],
            "cloud_cover": r.randint(0, 100),
            "pressure_msl": r.randint(1002, 1024),
            "wind_speed_10m": round(random.uniform(3, 34), 1),
            "wind_direction_10m": r.randrange(0, 360, 15),
            "wind_gusts_10m": round(random.uniform(6, 55), 1),
        },
        "hourly": {
            "time": h_times,
            "temperature_2m": h_temp,
            "weather_code": h_code,
            "precipitation_probability": h_precip,
            "uv_index": h_uv,
            "visibility": h_vis,
            "is_day": h_day,
        },
        "daily": {
            "time": d_times,
            "weather_code": d_code,
            "temperature_2m_max": d_max,
            "temperature_2m_min": d_min,
            "sunrise": d_rise,
            "sunset": d_set,
            "uv_index_max": d_uvmax,
            "precipitation_probability_max": d_pprob,
            "precipitation_sum": d_psum,
            "wind_speed_10m_max": d_wind,
        },
    }


# Small offline gazetteer — only consulted when the geocoding API is unreachable.
_CITIES = [
    ("London", "England", "United Kingdom", "GB", 51.5074, -0.1278),
    ("New York", "New York", "United States", "US", 40.7128, -74.0060),
    ("Tokyo", "Tokyo", "Japan", "JP", 35.6762, 139.6503),
    ("Paris", "Île-de-France", "France", "FR", 48.8566, 2.3522),
    ("Berlin", "Berlin", "Germany", "DE", 52.5200, 13.4050),
    ("Sydney", "New South Wales", "Australia", "AU", -33.8688, 151.2093),
    ("Mumbai", "Maharashtra", "India", "IN", 19.0760, 72.8777),
    ("Delhi", "Delhi", "India", "IN", 28.6139, 77.2090),
    ("Singapore", "", "Singapore", "SG", 1.3521, 103.8198),
    ("Dubai", "Dubai", "United Arab Emirates", "AE", 25.2048, 55.2708),
    ("Cairo", "Cairo Governorate", "Egypt", "EG", 30.0444, 31.2357),
    ("Lima", "Lima", "Peru", "PE", -12.0464, -77.0428),
    ("São Paulo", "São Paulo", "Brazil", "BR", -23.5505, -46.6333),
    ("Toronto", "Ontario", "Canada", "CA", 43.6532, -79.3832),
    ("Moscow", "Moscow", "Russia", "RU", 55.7558, 37.6173),
    ("Beijing", "Beijing", "China", "CN", 39.9042, 116.4074),
    ("Seoul", "Seoul", "South Korea", "KR", 37.5665, 126.9780),
    ("Istanbul", "Istanbul", "Türkiye", "TR", 41.0082, 28.9784),
    ("Rome", "Lazio", "Italy", "IT", 41.9028, 12.4964),
    ("Madrid", "Madrid", "Spain", "ES", 40.4168, -3.7038),
    ("Cape Town", "Western Cape", "South Africa", "ZA", -33.9249, 18.4241),
    ("Nairobi", "Nairobi", "Kenya", "KE", -1.2921, 36.8219),
    ("Los Angeles", "California", "United States", "US", 34.0522, -118.2437),
    ("San Francisco", "California", "United States", "US", 37.7749, -122.4194),
    ("Reykjavík", "Capital Region", "Iceland", "IS", 64.1466, -21.9426),
]


def gazetteer(query: str, count: int = 6) -> list[dict]:
    """Prefix/fuzzy match against the offline city list."""
    q = query.strip().lower()
    if not q:
        return []
    starts, contains = [], []
    for name, admin, country, cc, lat, lon in _CITIES:
        item = {"name": name, "admin": admin, "country": country,
                "country_code": cc, "lat": lat, "lon": lon}
        if name.lower().startswith(q):
            starts.append(item)
        elif q in name.lower() or q in country.lower():
            contains.append(item)
    return (starts + contains)[:count]


def air_quality(lat: float, lon: float) -> dict:
    r = _rng(lat, lon, salt=3)
    aqi = r.randint(18, 165)
    return {
        "current": {
            "us_aqi": aqi,
            "pm2_5": round(aqi * 0.22 + r.uniform(0, 4), 1),
            "pm10": round(aqi * 0.38 + r.uniform(0, 7), 1),
        },
    }
