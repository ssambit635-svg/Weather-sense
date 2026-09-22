"""Render components for WeatherSense."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import streamlit as st

from weather_sense.api import (
    aqi_info, build_alerts, code_info, daylight_left, fmt_clock, fmt_t,
    local_now, mosquito, outdoor_score, stargazing, sun_progress,
    wind_dir_full, wind_dir_name, to_unit,
)
from weather_sense.icons import LOGO_SVG, icon, weather_icon

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _hour_index(times: list[str], current_iso: str) -> int:
    """Index of the hourly slot matching the current time (hour precision)."""
    prefix = current_iso[:13]
    for i, t in enumerate(times):
        if t[:13] == prefix:
            return i
    # fall back: first slot >= current time, else 0
    for i, t in enumerate(times):
        if t >= current_iso:
            return i
    return 0


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
    """Native segmented Celsius / Fahrenheit switch."""
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
        [data-testid="stWidgetLabel"]:has(+ div[data-testid="stSegmentedControl"]) { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _, right = st.columns([5.2, 1])
    with right:
        choice = st.segmented_control(
            "Unit",
            options=["°C", "°F"],
            default=f"°{unit}",
            selection_mode="single",
            label_visibility="collapsed",
            key="unit_seg",
        )
    if choice and choice != f"°{unit}":
        st.session_state.unit = choice[1]
        st.rerun()


# ---------------------------------------------------------------------------
# hero
# ---------------------------------------------------------------------------
def hero(data: dict, place: dict, unit: str) -> tuple[str, str]:
    cur = data["current"]
    label, key, accent = code_info(cur["weather_code"], bool(cur.get("is_day", 1)))
    daily = data["daily"]
    hi, lo = daily["temperature_2m_max"][0], daily["temperature_2m_min"][0]

    loc = place.get("name", "")
    if place.get("admin") and place["admin"].lower() != loc.lower():
        loc += f" · {place['admin']}"
    country = place.get("country", "")
    loc_full = f"{loc}, {country}" if country else loc

    temp_num = f"{to_unit(cur['temperature_2m'], unit):.0f}"
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
                <span>Feels <b>{fmt_t(cur['apparent_temperature'], unit)}</b></span>
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
def alerts_block(label: str, data: dict, aqi: Optional[float]) -> None:
    cur = data["current"]
    family = _family_of(cur["weather_code"])
    items = build_alerts(
        label,
        cur["temperature_2m"],
        cur.get("wind_speed_10m") or 0,
        aqi,
        cur.get("wind_gusts_10m") or 0,
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


_FAMILY_BY_CODE_GROUP = {
    "clear": "clear", "mostly": "clear", "partly": "partly",
    "overcast": "overcast", "fog": "fog", "drizzle": "drizzle",
    "rain": "rain", "heavy-rain": "rain", "sleet": "sleet",
    "snow": "snow", "thunder": "thunder", "hail": "thunder",
}


def _family_of(code: int) -> str:
    _, key, _ = code_info(code, True)
    return _FAMILY_BY_CODE_GROUP.get(key, "partly")


# ---------------------------------------------------------------------------
# metric grid
# ---------------------------------------------------------------------------
def metrics_grid(data: dict, aqi: Optional[float], unit: str) -> None:
    cur = data["current"]
    hourly = data["hourly"]
    idx = _hour_index(hourly["time"], cur["time"])
    uv = hourly.get("uv_index", [0] * len(hourly["time"]))[idx]
    vis_m = hourly.get("visibility", [20000] * len(hourly["time"]))[idx]
    vis_km = round((vis_m or 0) / 1000, 1)
    pop = hourly.get("precipitation_probability", [0] * len(hourly["time"]))[idx] or 0
    hum = cur.get("relative_humidity_2m")
    wind = cur.get("wind_speed_10m") or 0
    gusts = cur.get("wind_gusts_10m") or 0
    press = cur.get("pressure_msl")

    cells = [
        ("droplet", "Humidity", f"{hum}<small>%</small>",
         "Dew point feels " + ("muggy" if (hum or 0) >= 80 else "dry" if (hum or 0) <= 45 else "comfortable")),
        ("thermometer", "Feels like", fmt_t(cur["apparent_temperature"], unit),
         "Wind chill applied"),
        ("umbrella", "Precipitation", f"{pop}<small>%</small>",
         f"{cur.get('precipitation') or 0} mm in the last hour"),
        ("uv", "UV index", f"{uv:.0f}" if uv is not None else "--",
         _uv_note(uv or 0)),
        ("eye", "Visibility", f"{vis_km}<small>km</small>",
         "Crystal clear" if vis_km >= 15 else "Moderate" if vis_km >= 5 else "Poor"),
        ("gauge", "Pressure", f"{press:.0f}<small>hPa</small>" if press else "--",
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
    # wind metric replaces one cell to keep 2x3? We include wind via compass row below.
    st.markdown(f'<div class="metrics">{grid}</div>', unsafe_allow_html=True)

    gap(sm=True)
    st.markdown(
        f"""
        <div class="panel compass">
          <div class="ring" style="--deg:{cur.get('wind_direction_10m', 0)}deg">
            <span class="n">N</span><span class="e">E</span><span class="s">S</span><span class="w">W</span>
            <div class="needle"></div><div class="hub"></div>
          </div>
          <div class="info">
            <div class="metric-head">{icon('wind', 13)}Wind</div>
            <div class="deg">{wind:.0f} km/h <span style="font-size:.7em;color:var(--text-2)">{wind_dir_name(cur.get('wind_direction_10m', 0))}</span></div>
            <div class="sub">Blowing from the {wind_dir_full(cur.get('wind_direction_10m', 0))}<br>Gusts up to {gusts:.0f} km/h</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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


# ---------------------------------------------------------------------------
# hourly rail
# ---------------------------------------------------------------------------
def hourly_rail(data: dict, unit: str) -> None:
    hourly = data["hourly"]
    cur_t = data["current"]["time"]
    start = _hour_index(hourly["time"], cur_t)
    n = 24
    times = hourly["time"][start:start + n]
    temps = hourly["temperature_2m"][start:start + n]
    codes = hourly["weather_code"][start:start + n]
    pops = hourly.get("precipitation_probability", [0] * len(hourly["time"]))[start:start + n]
    is_days = hourly.get("is_day", [1] * len(hourly["time"]))[start:start + n]

    # sparkline geometry — x centers must match .rail-col layout exactly
    col_w, pad = 64, 0
    w = col_w * len(temps)
    h = 64
    vals = [to_unit(t, unit) for t in temps]
    vmin, vmax = min(vals), max(vals)
    span = (vmax - vmin) or 1
    pts = []
    for i, v in enumerate(vals):
        x = pad + col_w * i + col_w / 2
        y = h - 14 - (v - vmin) / span * (h - 30)
        pts.append((x, y))
    path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = path + f" L{pts[-1][0]:.1f} {h} L{pts[0][0]:.1f} {h} Z"

    spark_svg = f'''
    <svg class="spark" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">
      <defs>
        <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="var(--accent)" stop-opacity=".22"/>
          <stop offset="1" stop-color="var(--accent)" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path d="{area}" fill="url(#sg)"/>
      <path d="{path}" stroke="var(--accent)" stroke-width="1.75"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>'''

    cols = ""
    for i, t in enumerate(times):
        label, key, _ = code_info(codes[i], bool(is_days[i]) if i < len(is_days) else True)
        hr = "Now" if i == 0 else datetime.fromisoformat(t).strftime("%H:%M")
        pop = pops[i] if i < len(pops) else None
        pop_s = f"{pop}%" if pop else ""
        cols += f'''
          <div class="rail-col">
            <div class="rail-t">{fmt_t(temps[i], unit)}</div>
            {weather_icon(key, 21, stroke=1.45)}
            <div class="rail-hr" {'style="color:var(--accent);font-weight:650"' if i == 0 else ''}>{hr}</div>
            <div class="rail-p">{pop_s}</div>
          </div>'''

    st.markdown(
        f'''
        <div class="rail-wrap">
          <div class="rail-scroll">
            <div style="min-width:{w}px">{spark_svg}</div>
            <div class="rail-inner">{cols}</div>
          </div>
        </div>''',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 7-day forecast
# ---------------------------------------------------------------------------
def daily_rows(data: dict, unit: str) -> None:
    daily = data["daily"]
    n = len(daily["time"])
    his = [to_unit(v, unit) for v in daily["temperature_2m_max"]]
    los = [to_unit(v, unit) for v in daily["temperature_2m_min"]]
    gmin, gmax = min(los), max(his)
    span = (gmax - gmin) or 1

    rows = ""
    for i in range(n):
        d = datetime.strptime(daily["time"][i], "%Y-%m-%d")
        name = "Today" if i == 0 else d.strftime("%a")
        sub = d.strftime("%b %d")
        label, key, _ = code_info(daily["weather_code"][i], True)
        pop = daily.get("precipitation_probability_max", [0] * n)[i] or 0
        left = (los[i] - gmin) / span * 100
        width = max(4, (his[i] - los[i]) / span * 100)
        dot = min(97, max(3, (his[i] - gmin) / span * 100))
        rows += f'''
          <div class="day" title="{label}">
            <div class="day-name">{name}<span class="sub">{sub}</span></div>
            <div style="color:var(--text-2)">{weather_icon(key, 20, stroke=1.45)}</div>
            <div class="day-pop">{pop if pop else ""}</div>
            <div style="display:flex;align-items:center;gap:.55rem">
              <span class="day-lo">{fmt_t(daily['temperature_2m_min'][i], unit)}</span>
              <div class="range" style="flex:1">
                <span class="fill" style="left:{left:.1f}%;width:{width:.1f}%"></span>
                <span class="dot" style="left:{dot:.1f}%"></span>
              </div>
            </div>
            <div class="day-hi">{fmt_t(daily['temperature_2m_max'][i], unit)}</div>
          </div>'''
    # reorder: lo should sit left of bar — handled above; hi column right.
    st.markdown(f'<div class="days">{rows}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# AQI
# ---------------------------------------------------------------------------
def aqi_panel(aqi_data: dict) -> None:
    cur = (aqi_data or {}).get("current") or {}
    val = cur.get("us_aqi")
    pm25 = cur.get("pm2_5")
    pm10 = cur.get("pm10")
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
    daily = data["daily"]
    tz = data.get("timezone", "UTC")
    now = local_now(tz)
    sunrise, sunset = daily["sunrise"][0], daily["sunset"][0]
    sr, ss = fmt_clock(sunrise), fmt_clock(sunset)
    prog = sun_progress(sunrise, sunset, now)
    note = daylight_left(sunset, now) if prog is not None else "Sun is below the horizon"

    # arc geometry: semicircle from (20, 70) to (300, 70)
    W, H = 320, 92
    x0, x1, base = 24, 296, 76
    cx, cy, rx, ry = (x0 + x1) / 2, base, (x1 - x0) / 2, 58
    import math as _m
    if prog is None:
        daytime = now.hour >= 6
        t = 0.85 if daytime else 0.15
        below = True
    else:
        t = prog
        below = False
    # param angle: left (pi) -> right (0)
    ang = _m.pi * (1 - t)
    dx, dy = cx + rx * _m.cos(ang), cy - ry * _m.sin(ang)

    def half_path(direction: float) -> str:
        # direction 1 = full arc left->right
        return f"M{x0} {base} A{rx} {ry} 0 0 1 {x1} {base}"

    st.markdown(
        f"""
        <div class="panel sun-wrap">
          <div class="metric-head" style="margin-bottom:.4rem">{icon('sunrise', 13)}Sun path</div>
          <svg width="100%" viewBox="0 0 {W} {H}" fill="none" style="display:block">
            <line x1="8" y1="{base}" x2="{W-8}" y2="{base}"
                  stroke="var(--line)" stroke-width="1" stroke-dasharray="3 5"/>
            <path d="M{x0} {base} A{rx} {ry} 0 0 1 {x1} {base}"
                  stroke="var(--line-strong)" stroke-width="1.5" stroke-dasharray="4 6"/>
            <path d="M{x0} {base} A{rx} {ry} 0 0 1 {x1} {base}"
                  stroke="var(--accent)" stroke-width="1.75" stroke-linecap="round"
                  pathLength="100" stroke-dasharray="{t*100:.1f} 100"
                  opacity="{0.25 if below else 1}"/>
            <circle cx="{dx:.1f}" cy="{dy:.1f}" r="6.5"
                    fill="{'var(--text-3)' if below else 'var(--accent)'}"/>
            <circle cx="{dx:.1f}" cy="{dy:.1f}" r="11"
                    fill="none" stroke="{'transparent' if below else 'var(--accent)'}"
                    stroke-opacity=".35" stroke-width="1.5"/>
            <circle cx="{x0}" cy="{base}" r="3" fill="var(--text-3)"/>
            <circle cx="{x1}" cy="{base}" r="3" fill="var(--text-3)"/>
          </svg>
          <div class="sun-times">
            <div class="lbl"><span>Sunrise</span><b style="font-size:1.05rem;color:var(--text);font-weight:650">{sr}</b></div>
            <div class="lbl right"><span>Sunset</span><b style="font-size:1.05rem;color:var(--text);font-weight:650">{ss}</b></div>
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
    cur = data["current"]
    cloud = cur.get("cloud_cover", 0)
    hum = cur.get("relative_humidity_2m", 50) or 50
    family = _family_of(cur["weather_code"])

    sg_score, sg_val, sg_col, sg_tip = stargazing(cloud, aqi, family)
    mo_val, mo_col, mo_tip = mosquito(cur["temperature_2m"], hum)
    sp_score, sp_val, sp_col, sp_tip = outdoor_score(
        cur["temperature_2m"], cur.get("wind_speed_10m") or 0, aqi, family
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
            <div class="bar"><i style="width:{max(3, score)}%;background:{col}"></i></div>
            <div class="tip">{tip}</div>
          </div>'''
    st.markdown(f'<div class="insights">{html}</div>', unsafe_allow_html=True)


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
