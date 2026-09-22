"""Render components for WeatherSense.

Every component assumes the payload has already been through
:func:`weather_sense.api.normalize_forecast`, but still defends against missing
values: a weather API can return ``null`` for any field at any time, and one
``None`` must never be allowed to blank the whole screen.
"""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st

from weather_sense.api import (
    aqi_info, build_alerts, code_info, daylight_left, fmt_clock, fmt_day, fmt_int,
    fmt_t, local_now, mosquito, num, num_or, outdoor_score, stargazing,
    sun_progress, to_unit, wind_dir_full, wind_dir_name,
)
from weather_sense.compat import has
from weather_sense.icons import LOGO_SVG, icon, logo_mark, weather_icon

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
RAIL_HOURS = 24
RAIL_COL_W = 64          # must match .rail-col width in styles.py
RAIL_SPARK_H = 64


def _hour_index(times: list[str], current_iso: Any) -> int:
    """Index of the hourly slot matching the current time (hour precision)."""
    if not times:
        return 0
    prefix = str(current_iso or "")[:13]
    if prefix:
        for i, t in enumerate(times):
            if str(t)[:13] == prefix:
                return i
        for i, t in enumerate(times):
            if str(t) >= prefix:
                return i
    return 0


def _hourly_window(data: dict) -> dict:
    """Current-hour values from the hourly block, tolerant of short arrays."""
    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        return {"index": 0, "uv_index": None, "visibility": None,
                "precipitation_probability": None}
    idx = _hour_index(times, (data.get("current") or {}).get("time"))

    def pick(key: str) -> Any:
        arr = hourly.get(key) or []
        return arr[idx] if idx < len(arr) else None

    return {
        "index": idx,
        "uv_index": pick("uv_index"),
        "visibility": pick("visibility"),
        "precipitation_probability": pick("precipitation_probability"),
    }


def _note(text: str) -> None:
    """Quiet placeholder used when a section has no data at all."""
    st.markdown(
        f'<div class="panel"><div class="metric-sub">{text}</div></div>',
        unsafe_allow_html=True,
    )


def sec(title: str, ic: str = "", aside: str = "") -> None:
    left = f"{icon(ic, 13) if ic else ''}{title}"
    right = f'<span class="aside">{aside}</span>' if aside else ""
    st.markdown(
        f'<div class="sec-title">{left}<span class="spacer"></span>{right}</div>',
        unsafe_allow_html=True,
    )


def gap(sm: bool = False, lg: bool = False) -> None:
    cls = "ws-gap-sm" if sm else ("ws-gap-lg" if lg else "ws-gap")
    st.markdown(f'<div class="{cls}"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# opening splash — minimalist logo + micro loader
# ---------------------------------------------------------------------------
def loader_svg(size: int = 20) -> str:
    """Two counter-rotating arcs — the app's in-page spinner."""
    return (
        f'<svg class="ws-ring" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" aria-hidden="true">'
        f'<circle class="ws-ring-track" cx="12" cy="12" r="9.4" stroke-width="1.7"/>'
        f'<circle class="ws-ring-a" cx="12" cy="12" r="9.4" stroke-width="1.7" '
        f'stroke-linecap="round" pathLength="100" stroke-dasharray="28 72"/>'
        f'<circle class="ws-ring-b" cx="12" cy="12" r="5.2" stroke-width="1.5" '
        f'stroke-linecap="round" pathLength="100" stroke-dasharray="16 84"/>'
        f"</svg>"
    )


def splash_html(status: str = "Reading the sky", ready: bool = False,
                fade: bool = False) -> str:
    """The intro card: brand mark drawing itself, loader, wordmark.

    Rendered into a placeholder *before* any network work so the first paint is
    instant, then re-rendered with ``ready=True`` and ``fade=True`` on the way
    out. Pure HTML/CSS — no JS, no extra dependencies.
    """
    classes = "ws-splash" + (" ws-ready" if ready else "") + (" ws-out" if fade else "")
    dots = "" if ready else '<span class="ws-dots"><i>.</i><i>.</i><i>.</i></span>'
    logo = logo_mark(78, uid="splash", stroke=1.45, animated=True)
    return (
        f'<div class="{classes}">'
        f'<div class="ws-splash-badge">{logo}</div>'
        f'<div class="ws-word">WeatherSense</div>'
        f'<div class="ws-loader">{loader_svg(20)}'
        f'<span class="ws-status">{status}{dots}</span></div>'
        f'<div class="ws-bar"><i></i></div>'
        f'<div class="ws-tag">live weather · distilled</div>'
        f"</div>"
    )


def fatal(title: str, detail: str, hint: str = "") -> None:
    """Friendly error card — shown instead of a raw traceback or blank screen."""
    st.markdown(
        f"""
        <div class="ws-fatal">
          <div class="ttl">{icon('alert', 16)}{title}</div>
          <div class="body">{detail}</div>
          {f'<code>{hint}</code>' if hint else ''}
        </div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# header
# ---------------------------------------------------------------------------
def header(local_time: str = "", tz_label: str = "", offline: bool = False) -> None:
    live = '<span class="live-dot"></span>' if not offline else ""
    meta = ""
    if local_time:
        meta = f'{live}{local_time} <span style="opacity:.6">{tz_label}</span>'
    st.markdown(
        f"""
        <div class="ws-header">
          <div class="brand">{LOGO_SVG}<span class="name">WeatherSense</span></div>
          <div class="meta">{meta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def unit_toggle() -> None:
    """Celsius / Fahrenheit switch, with a fallback for older Streamlit."""
    unit = st.session_state.get("unit", "C")
    st.markdown(
        """
        <style>
        div[data-testid="stSegmentedControl"] { align-self: flex-end; }
        div[data-testid="stSegmentedControl"] button {
          height: 34px !important; min-height: 34px !important;
          font-size: .76rem !important; font-weight: 600 !important;
          padding: 0 14px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _, right = st.columns([5.2, 1])
    options = ["°C", "°F"]
    choice: Any = None
    with right:
        if has("segmented_control"):
            choice = st.segmented_control(
                "Unit", options=options, default=f"°{unit}",
                selection_mode="single", label_visibility="collapsed", key="unit_seg",
            )
        else:  # Streamlit < 1.40
            choice = st.radio(
                "Unit", options=options, index=options.index(f"°{unit}"),
                label_visibility="collapsed", key="unit_seg", horizontal=True,
            )
    # `segmented_control` returns the option itself, `radio` the same — but be
    # defensive: accept "°C", "C" or ["°C"].
    picked = choice[0] if isinstance(choice, (list, tuple)) and choice else choice
    if isinstance(picked, str) and picked:
        new_unit = picked[-1].upper()
        if new_unit in ("C", "F") and new_unit != unit:
            st.session_state.unit = new_unit
            st.rerun()


# ---------------------------------------------------------------------------
# hero
# ---------------------------------------------------------------------------
def hero(data: dict, place: dict, unit: str) -> tuple[str, str]:
    cur = data.get("current") or {}
    label, key, _ = code_info(cur.get("weather_code"), bool(cur.get("is_day", 1)))
    daily = data.get("daily") or {}
    hi = (daily.get("temperature_2m_max") or [None])[0]
    lo = (daily.get("temperature_2m_min") or [None])[0]

    loc = str(place.get("name") or "Unknown location")
    admin = str(place.get("admin") or "")
    if admin and admin.lower() != loc.lower():
        loc += f" · {admin}"
    country = str(place.get("country") or "")
    loc_full = f"{loc}, {country}" if country else loc

    temp_val = to_unit(cur.get("temperature_2m"), unit)
    temp_num = f"{temp_val:.0f}" if temp_val is not None else "--"
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-row">
            <div>
              <div class="hero-temp">{temp_num}<span class="deg">°</span></div>
              <div class="hero-cond">{label}</div>
              <div class="hero-loc">{icon('pin', 14)}{loc_full}</div>
              <div class="hero-sub">
                <span>H <b>{fmt_t(hi, unit)}</b></span>
                <span>L <b>{fmt_t(lo, unit)}</b></span>
                <span>Feels <b>{fmt_t(cur.get('apparent_temperature'), unit)}</b></span>
              </div>
            </div>
            <div class="hero-icon">{weather_icon(key, 92, stroke=1.25)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return label, key


# ---------------------------------------------------------------------------
# alerts
# ---------------------------------------------------------------------------
_FAMILY_BY_CODE_GROUP = {
    "clear": "clear", "clear-day": "clear", "clear-night": "clear",
    "mostly": "clear", "mostly-day": "clear", "mostly-night": "clear",
    "partly": "partly", "partly-day": "partly", "partly-night": "partly",
    "overcast": "overcast", "fog": "fog", "drizzle": "drizzle",
    "rain": "rain", "heavy-rain": "rain", "sleet": "sleet",
    "snow": "snow", "thunder": "thunder", "hail": "thunder", "cloud": "overcast",
}


def _family_of(code: Any) -> str:
    _, key, _ = code_info(code, True)
    return _FAMILY_BY_CODE_GROUP.get(key, "partly")


def alerts_block(label: str, data: dict, aqi: Optional[float]) -> None:
    cur = data.get("current") or {}
    family = _family_of(cur.get("weather_code"))
    items = build_alerts(
        label,
        cur.get("temperature_2m"),
        cur.get("wind_speed_10m"),
        aqi,
        cur.get("wind_gusts_10m"),
        family,
    )
    if not items:
        return
    sec("Alerts", "alert")
    for title, body, color in items:
        st.markdown(
            f"""
            <div class="alert" style="border-left-color:{color}">
              <div style="color:{color};margin-top:1px">{icon('alert', 15)}</div>
              <div><div class="ttl">{title}</div><div class="body">{body}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# metric grid
# ---------------------------------------------------------------------------
def _uv_note(uv: float) -> str:
    if uv < 3:
        return "Low — no protection needed"
    if uv < 6:
        return "Moderate — seek shade midday"
    if uv < 8:
        return "High — use SPF 30+"
    if uv < 11:
        return "Very high — protection essential"
    return "Extreme — avoid midday sun"


def metrics_grid(data: dict, aqi: Optional[float], unit: str) -> None:
    cur = data.get("current") or {}
    hw = _hourly_window(data)

    uv = num(hw.get("uv_index"))
    vis_m = num(hw.get("visibility"))
    vis_km = round(vis_m / 1000, 1) if vis_m is not None else None
    pop = num(hw.get("precipitation_probability"))
    hum = num(cur.get("relative_humidity_2m"))
    wind = num_or(cur.get("wind_speed_10m"), 0)
    gusts = num_or(cur.get("wind_gusts_10m"), 0)
    press = num(cur.get("pressure_msl"))
    bearing = num(cur.get("wind_direction_10m"))
    precip = num(cur.get("precipitation"))

    if hum is None:
        hum_sub = "Humidity unavailable right now"
    elif hum >= 80:
        hum_sub = "Dew point feels muggy"
    elif hum <= 45:
        hum_sub = "Dew point feels dry"
    else:
        hum_sub = "Dew point feels comfortable"

    cells = [
        ("droplet", "Humidity", fmt_int(hum, "%"), hum_sub),
        ("thermometer", "Feels like", fmt_t(cur.get("apparent_temperature"), unit),
         "Wind chill applied"),
        ("umbrella", "Precipitation", fmt_int(pop, "%"),
         f"{precip:.1f} mm in the last hour" if precip is not None else "No rainfall reported"),
        ("uv", "UV index", fmt_int(uv), _uv_note(uv if uv is not None else 0)),
        ("eye", "Visibility",
         f"{vis_km}<small>km</small>" if vis_km is not None else "--",
         "Crystal clear" if (vis_km or 0) >= 15 else "Moderate" if (vis_km or 0) >= 5 else "Poor"
         if vis_km is not None else "Visibility unavailable"),
        ("gauge", "Pressure", f"{press:.0f}<small>hPa</small>" if press is not None else "--",
         "Sea level, mean reduced"),
    ]

    grid = "".join(
        f'''<div class="metric">
              <div class="metric-head">{icon(ic, 13)}{lbl}</div>
              <div class="metric-val">{val}</div>
              <div class="metric-sub">{sub}</div>
            </div>'''
        for ic, lbl, val, sub in cells
    )
    st.markdown(f'<div class="metrics">{grid}</div>', unsafe_allow_html=True)

    gap(sm=True)
    st.markdown(
        f"""
        <div class="panel compass">
          <div class="ring" style="--deg:{bearing if bearing is not None else 0}deg">
            <span class="n">N</span><span class="e">E</span><span class="s">S</span><span class="w">W</span>
            <div class="needle"></div><div class="hub"></div>
          </div>
          <div class="info">
            <div class="metric-head">{icon('wind', 13)}Wind</div>
            <div class="deg">{wind:.0f} km/h <span style="font-size:.7em;color:var(--text-2)">{wind_dir_name(bearing)}</span></div>
            <div class="sub">Blowing from the {wind_dir_full(bearing)}<br>Gusts up to {gusts:.0f} km/h</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# hourly rail
# ---------------------------------------------------------------------------
def _sparkline(vals: list[Optional[float]], unit: str) -> tuple[str, int]:
    """Return (svg, width). Missing samples are interpolated, never dropped."""
    w = RAIL_COL_W * len(vals)
    h = RAIL_SPARK_H
    if not vals:
        return "", 0

    known = [v for v in vals if v is not None]
    if not known:
        return "", w
    fallback = sum(known) / len(known)
    series = [v if v is not None else fallback for v in vals]

    vmin, vmax = min(series), max(series)
    span = (vmax - vmin) or 1.0
    pts = []
    for i, v in enumerate(series):
        x = RAIL_COL_W * i + RAIL_COL_W / 2
        y = h - 14 - (v - vmin) / span * (h - 30)
        pts.append((x, y))
    path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = path + f" L{pts[-1][0]:.1f} {h} L{pts[0][0]:.1f} {h} Z"
    svg = f'''
    <svg class="spark" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">
      <defs>
        <linearGradient id="ws-spark" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="var(--accent)" stop-opacity=".22"/>
          <stop offset="1" stop-color="var(--accent)" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path d="{area}" fill="url(#ws-spark)"/>
      <path d="{path}" stroke="var(--accent)" stroke-width="1.75"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>'''
    return svg, w


def hourly_rail(data: dict, unit: str) -> None:
    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        _note("Hourly forecast unavailable.")
        return

    start = _hour_index(times, (data.get("current") or {}).get("time"))
    start = max(0, min(start, len(times) - 1))
    count = min(RAIL_HOURS, len(times) - start)

    def col(key: str) -> list:
        arr = hourly.get(key) or []
        return arr[start:start + count]

    temps, codes = col("temperature_2m"), col("weather_code")
    pops, is_days = col("precipitation_probability"), col("is_day")

    vals = [to_unit(t, unit) for t in temps]
    spark_svg, w = _sparkline(vals, unit)
    w = w or RAIL_COL_W * count

    cells = ""
    for i in range(count):
        t = times[start + i]
        _, key, _ = code_info(codes[i] if i < len(codes) else None,
                              bool(is_days[i]) if i < len(is_days) else True)
        hr = "Now" if i == 0 else fmt_clock(t)
        pop = num(pops[i]) if i < len(pops) else None
        pop_s = f"{pop:.0f}%" if pop else ""
        cells += f'''
          <div class="rail-col">
            <div class="rail-t">{fmt_t(temps[i] if i < len(temps) else None, unit)}</div>
            {weather_icon(key, 21, stroke=1.45)}
            <div class="rail-hr" {'style="color:var(--accent);font-weight:650"' if i == 0 else ''}>{hr}</div>
            <div class="rail-p">{pop_s}</div>
          </div>'''

    st.markdown(
        f'''
        <div class="rail-wrap">
          <div class="rail-scroll">
            <div style="min-width:{w}px">{spark_svg}</div>
            <div class="rail-inner">{cells}</div>
          </div>
        </div>''',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 7-day forecast
# ---------------------------------------------------------------------------
def daily_rows(data: dict, unit: str) -> None:
    daily = data.get("daily") or {}
    times = daily.get("time") or []
    n = len(times)
    if not n:
        _note("7-day forecast unavailable.")
        return

    his = [to_unit(v, unit) for v in (daily.get("temperature_2m_max") or [None] * n)]
    los = [to_unit(v, unit) for v in (daily.get("temperature_2m_min") or [None] * n)]
    known = [v for v in his + los if v is not None]
    if not known:
        _note("Temperature data unavailable for this period.")
        return
    gmin, gmax = min(known), max(known)
    span = (gmax - gmin) or 1.0

    codes = daily.get("weather_code") or []
    pops = daily.get("precipitation_probability_max") or []

    rows = ""
    for i in range(n):
        hi = his[i] if i < len(his) else None
        lo = los[i] if i < len(los) else None
        label, key, _ = code_info(codes[i] if i < len(codes) else None, True)
        pop = num(pops[i]) if i < len(pops) else None
        pop_s = f"{pop:.0f}" if pop else ""

        # range bar — fall back to a full-width bar when a bound is missing
        lo_v = lo if lo is not None else gmin
        hi_v = hi if hi is not None else gmax
        left = max(0.0, min(100.0, (lo_v - gmin) / span * 100))
        width = max(4.0, min(100.0 - left, (hi_v - lo_v) / span * 100))
        dot = min(97.0, max(3.0, (hi_v - gmin) / span * 100))
        rows += f'''
          <div class="day" title="{label}">
            <div class="day-name">{("Today" if i == 0 else fmt_day(times[i], "%a"))}
              <span class="sub">{fmt_day(times[i], "%b %d")}</span></div>
            <div style="color:var(--text-2)">{weather_icon(key, 20, stroke=1.45)}</div>
            <div class="day-pop">{pop_s}</div>
            <div style="display:flex;align-items:center;gap:.55rem">
              <span class="day-lo">{fmt_t(lo, unit)}</span>
              <div class="range" style="flex:1">
                <span class="fill" style="left:{left:.1f}%;width:{width:.1f}%"></span>
                <span class="dot" style="left:{dot:.1f}%"></span>
              </div>
            </div>
            <div class="day-hi">{fmt_t(hi, unit)}</div>
          </div>'''
    st.markdown(f'<div class="days">{rows}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# AQI
# ---------------------------------------------------------------------------
def aqi_panel(aqi_data: dict) -> None:
    cur = (aqi_data or {}).get("current") or {}
    val = num(cur.get("us_aqi"))
    pm25 = num(cur.get("pm2_5"))
    pm10 = num(cur.get("pm10"))
    label, color, pct, advice = aqi_info(val)
    st.markdown(
        f"""
        <div class="panel">
          <div class="aqi-top">
            <div>
              <div class="metric-head">{icon('layers', 13)}Air quality · US AQI</div>
              <div class="aqi-val" style="color:{color};margin-top:.35rem">
                {f'{val:.0f}' if val is not None else '--'}
                <span class="aqi-label" style="font-size:.5em;color:var(--text-2);font-family:var(--font)">{label}</span>
              </div>
            </div>
          </div>
          <div class="aqi-bar"><span class="aqi-knob" style="left:{min(max(pct, 2), 97)}%"></span></div>
          <div class="aqi-ticks"><span>Good</span><span>Moderate</span><span>Unhealthy</span><span>Hazardous</span></div>
          <div class="aqi-advice">{advice}</div>
          <div class="pm-row">
            <div class="it">Fine particles (PM2.5)<b>{f'{pm25:.1f} µg/m³' if pm25 is not None else '--'}</b></div>
            <div class="it">Coarse particles (PM10)<b>{f'{pm10:.1f} µg/m³' if pm10 is not None else '--'}</b></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# sun arc
# ---------------------------------------------------------------------------
def sun_panel(data: dict) -> None:
    daily = data.get("daily") or {}
    tz = data.get("timezone") or "UTC"
    now = local_now(tz)
    sunrise = (daily.get("sunrise") or [""])[0]
    sunset = (daily.get("sunset") or [""])[0]
    sr, ss_ = fmt_clock(sunrise), fmt_clock(sunset)
    prog = sun_progress(sunrise, sunset, now)

    if not sunrise and not sunset:
        note = "Sun times unavailable for this location"
    elif prog is not None:
        note = daylight_left(sunset, now) or "Daylight in progress"
    else:
        note = "Sun is below the horizon"

    # arc geometry: semicircle from (24, 76) to (296, 76) inside a 320x92 box
    import math as _m
    W, H = 320, 92
    x0, x1, base = 24, 296, 76
    cx, cy, rx, ry = (x0 + x1) / 2, base, (x1 - x0) / 2, 58
    if prog is None:
        below = True
        t = 0.85 if now.hour >= 6 else 0.15
    else:
        below = False
        t = prog
    ang = _m.pi * (1 - t)
    dx, dy = cx + rx * _m.cos(ang), cy - ry * _m.sin(ang)
    knob = "var(--text-3)" if below else "var(--accent)"
    ring = "transparent" if below else "var(--accent)"

    st.markdown(
        f"""
        <div class="panel sun-wrap">
          <div class="metric-head" style="margin-bottom:.4rem">{icon('sunrise', 13)}Sun path</div>
          <svg width="100%" viewBox="0 0 {W} {H}" fill="none" style="display:block" aria-hidden="true">
            <line x1="8" y1="{base}" x2="{W-8}" y2="{base}"
                  stroke="var(--line)" stroke-width="1" stroke-dasharray="3 5"/>
            <path d="M{x0} {base} A{rx} {ry} 0 0 1 {x1} {base}"
                  stroke="var(--line-strong)" stroke-width="1.5" stroke-dasharray="4 6"/>
            <path d="M{x0} {base} A{rx} {ry} 0 0 1 {x1} {base}"
                  stroke="var(--accent)" stroke-width="1.75" stroke-linecap="round"
                  pathLength="100" stroke-dasharray="{t*100:.1f} 100"
                  opacity="{0.25 if below else 1}"/>
            <circle cx="{dx:.1f}" cy="{dy:.1f}" r="6.5" fill="{knob}"/>
            <circle cx="{dx:.1f}" cy="{dy:.1f}" r="11" fill="none" stroke="{ring}"
                    stroke-opacity=".35" stroke-width="1.5"/>
            <circle cx="{x0}" cy="{base}" r="3" fill="var(--text-3)"/>
            <circle cx="{x1}" cy="{base}" r="3" fill="var(--text-3)"/>
          </svg>
          <div class="sun-times">
            <div class="lbl"><span>Sunrise</span><b style="font-size:1.05rem;color:var(--text);font-weight:650">{sr}</b></div>
            <div class="lbl right"><span>Sunset</span><b style="font-size:1.05rem;color:var(--text);font-weight:650">{ss_}</b></div>
          </div>
          <div class="sun-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# insights
# ---------------------------------------------------------------------------
def insights_row(data: dict, aqi: Optional[float]) -> None:
    cur = data.get("current") or {}
    cloud = num_or(cur.get("cloud_cover"), 50)
    hum = num_or(cur.get("relative_humidity_2m"), 50)
    temp = num(cur.get("temperature_2m"))
    family = _family_of(cur.get("weather_code"))

    sg_score, sg_val, sg_col, sg_tip = stargazing(cloud, aqi, family)
    mo_val, mo_col, mo_tip = mosquito(temp, hum)
    sp_score, sp_val, sp_col, sp_tip = outdoor_score(
        temp, cur.get("wind_speed_10m"), aqi, family
    )

    cards = [
        ("star", "Stargazing", sg_val, sg_col, sg_score, sg_tip),
        ("bug", "Mosquito risk", mo_val, mo_col,
         85 if mo_val == "High" else 50 if mo_val == "Moderate" else 15, mo_tip),
        ("bike", "Outdoors", sp_val, sp_col, sp_score, sp_tip),
    ]
    html = ""
    for ic, lbl, val, col, score, tip in cards:
        html += f'''
          <div class="insight">
            <div class="lbl">{icon(ic, 12)}{lbl}</div>
            <div class="val" style="color:{col}">{val}</div>
            <div class="bar"><i style="width:{max(3, min(100, score))}%;background:{col}"></i></div>
            <div class="tip">{tip}</div>
          </div>'''
    st.markdown(f'<div class="insights">{html}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# empty state
# ---------------------------------------------------------------------------
def empty_state() -> None:
    st.markdown(
        f"""
        <div class="empty">
          <span class="mark">{logo_mark(52, uid="empty", stroke=1.4)}</span>
          <h1>Weather, distilled.</h1>
          <p>Live conditions, hourly and 7-day forecasts, air quality<br>
          and safety insights — for any city on Earth.</p>
        </div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# footer
# ---------------------------------------------------------------------------
def footer(now_label: str, offline: bool) -> None:
    src = (
        "Sample data (offline mode)"
        if offline
        else 'Weather data by <a href="https://open-meteo.com" target="_blank" rel="noopener">Open-Meteo</a>'
    )
    st.markdown(
        f'<div class="ws-foot"><span>{src}</span>'
        f'<span>Local time {now_label} · refreshes automatically</span></div>',
        unsafe_allow_html=True,
    )
