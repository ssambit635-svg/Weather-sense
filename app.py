"""WeatherSense — minimalist live weather app."""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

import streamlit as st

from weather_sense import components as ui
from weather_sense.api import (
    city_temps, code_info, fetch_bundle, fmt_t, geocode, local_now, locate_by_ip,
)
from weather_sense.icons import LOGO_DATA_URI, LOGO_ONLY_SVG, icon
from weather_sense.styles import inject, set_accent

st.set_page_config(
    page_title="WeatherSense",
    page_icon=LOGO_DATA_URI,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# session state
# ---------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("unit", "C")
ss.setdefault("favorites", [])       # list[place dicts]
ss.setdefault("place", None)         # active place
ss.setdefault("pending_hits", None)  # alternate geocode results


def persist_city(place: dict) -> None:
    ss["place"] = place
    # flag only — the text_input widget is already instantiated this run,
    # so the value itself is synced at the top of the next run.
    ss["_sync_input"] = True
    try:
        st.query_params["city"] = place["name"]
        if place.get("country_code"):
            st.query_params["cc"] = place["country_code"]
    except Exception:
        pass


def resolve_query_city() -> Optional[dict]:
    """Geocode the ?city= URL parameter once per session."""
    q = st.query_params.get("city")
    if not q or ss.get("_q_resolved"):
        return ss.get("place")
    ss["_q_resolved"] = True
    hits = geocode(q, count=1)
    if hits:
        cc = st.query_params.get("cc")
        if cc:
            for h in hits:
                if h.get("country_code") == cc:
                    ss["place"] = h
                    return h
        ss["place"] = hits[0]
    return ss.get("place")


# ---------------------------------------------------------------------------
# styles + bootstrap
# ---------------------------------------------------------------------------
inject()

if not ss.get("booted"):
    ss["booted"] = True
    place0 = resolve_query_city()
    if place0 is None:
        place0 = locate_by_ip()                 # best effort (needs network)
    if place0 is None:
        hits = geocode("London", count=1)       # always succeeds (gazetteer fallback)
        place0 = hits[0] if hits else None
    if place0:
        ss["place"] = place0

place: Optional[dict] = ss.get("place")

# ---------------------------------------------------------------------------
# header + unit toggle (header lives in a fragment so its clock stays fresh)
# ---------------------------------------------------------------------------
bundle = None
offline = False
local_t, tz_label = "", ""
if place:
    bundle = fetch_bundle(place["lat"], place["lon"])
    offline = bundle.get("offline", False)
    tz_name = bundle["weather"].get("timezone", "UTC")
    local_t = local_now(tz_name).strftime("%H:%M")
    tz_label = (tz_name.split("/")[-1] if tz_name else "").replace("_", " ")
else:
    local_t, tz_label = "", ""


@st.fragment(run_every=timedelta(seconds=45))
def topbar() -> None:
    """Live local clock + brand mark."""
    lt, tl = "", ""
    p = ss.get("place")
    if p:
        b = fetch_bundle(p["lat"], p["lon"])
        tzn = b["weather"].get("timezone", "UTC")
        lt = local_now(tzn).strftime("%H:%M")
        tl = (tzn.split("/")[-1] if tzn else "").replace("_", " ")
    ui.header(lt, tl, b.get("offline", False) if p else False)


topbar()
ui.unit_toggle()

if offline:
    st.markdown(
        """
        <div class="notice">
          <span style="color:var(--warn);margin-top:1px">%s</span>
          <div><b>Offline preview.</b> Live weather services are unreachable from this
          environment, so a generated sample dataset is shown. Anywhere with network
          access fetches real conditions from Open-Meteo.</div>
        </div>""" % icon("alert", 15),
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------
st.markdown(
    "<style>div.stTextInput { margin-bottom: 0 !important; }</style>",
    unsafe_allow_html=True,
)

# keep the search box in sync with the active city
if ss.get("_sync_input"):
    ss["city_input"] = ss["place"]["name"] if ss.get("place") else ""
    ss["_sync_input"] = False
elif "city_input" not in ss:
    ss["city_input"] = place["name"] if place else ""

with st.form("search_form", clear_on_submit=False):
    q1, q2 = st.columns([4.6, 1.35])
    with q1:
        query = st.text_input(
            "Search for a city",
            key="city_input",
            placeholder="Search a city — e.g. Tokyo, Oslo, Lima",
            label_visibility="collapsed",
            autocomplete="off",
        )
    with q2:
        submitted = st.form_submit_button("Search", use_container_width=True)

if submitted:
    q = (query or "").strip()
    if not q:
        st.info("Type a city name to search.")
    else:
        hits = geocode(q)
        if not hits:
            st.error(f'No places found for "{q}". Try a different spelling.')
        else:
            persist_city(hits[0])
            ss["pending_hits"] = hits[1:4] or None
            st.rerun()

# alternate matches
if ss.get("pending_hits"):
    alts = ss["pending_hits"]
    ss["pending_hits"] = None
    cols = st.columns([1.35] + [1] * len(alts))
    with cols[0]:
        st.caption("Did you mean")
    for i, alt in enumerate(alts, start=1):
        with cols[i]:
            full = f'{alt["name"]}, {alt.get("country") or alt.get("admin") or ""}'.strip(", ")
            if st.button(full, key=f"alt_{i}", use_container_width=True):
                persist_city(alt)
                st.rerun()

# ---------------------------------------------------------------------------
# quick actions
# ---------------------------------------------------------------------------
ui.gap(sm=True)
la, lb, lr = st.columns([1.6, 1.6, 2.8])
with la:
    if st.button("My location", use_container_width=True):
        with st.spinner("Locating..."):
            here = locate_by_ip()
        if here:
            persist_city(here)
            st.rerun()
        else:
            st.error("Could not determine your location. Search for a city instead.")
with lb:
    if place:
        already = any(f.get("name") == place["name"] for f in ss["favorites"])
        if st.button(
            "Save city" if not already else "Saved",
            use_container_width=True,
            disabled=already,
        ):
            ss["favorites"] = [*ss["favorites"], place]
            st.toast(f"{place['name']} saved.")
            st.rerun()

# ---------------------------------------------------------------------------
# favorites rail (capped so the row never wraps on phones)
# ---------------------------------------------------------------------------
if ss["favorites"]:
    ui.gap(sm=True)
    shown = ss["favorites"][:6]
    temps = city_temps(shown)
    cols = st.columns(len(shown) + 1)
    for i, fav in enumerate(shown):
        with cols[i]:
            t = temps.get(fav["name"])
            label_txt = f"{fav['name']}  {fmt_t(t, ss['unit']) if t is not None else '--'}"
            if st.button(label_txt, key=f"fav_{i}_{fav['name']}", use_container_width=True):
                persist_city(fav)
                st.rerun()
    with cols[-1]:
        if st.button("Clear", key="clear_favs", use_container_width=True):
            ss["favorites"] = []
            st.rerun()

# ---------------------------------------------------------------------------
# empty state (rare — bootstrap normally lands on a city)
# ---------------------------------------------------------------------------
if not place or bundle is None:
    st.markdown(
        """
        <div class="empty">
          <span class="mark">%s</span>
          <h1>Weather, distilled.</h1>
          <p>Live conditions, hourly and 7-day forecasts, air quality<br>
          and safety insights — for any city on Earth.</p>
        </div>""" % LOGO_ONLY_SVG.replace('width="20" height="20"', 'width="52" height="52"'),
        unsafe_allow_html=True,
    )
    st.stop()


# ---------------------------------------------------------------------------
# dashboard fragment — re-renders every 45 s, refetches when cache expires
# ---------------------------------------------------------------------------
cur0 = bundle["weather"]["current"]
_, _, accent = code_info(cur0["weather_code"], bool(cur0.get("is_day", 1)))
set_accent(accent)


@st.fragment(run_every=timedelta(seconds=45))
def dashboard() -> None:
    unit = ss["unit"]
    b = fetch_bundle(place["lat"], place["lon"])
    data = b["weather"]
    aqi_data = b.get("aqi") or {}
    is_offline = b.get("offline", False)
    aqi_val = (aqi_data.get("current") or {}).get("us_aqi")

    c = data["current"]
    lab, key, acc = code_info(c["weather_code"], bool(c.get("is_day", 1)))
    set_accent(acc)

    ui.gap(lg=True)
    ui.hero(data, place, unit)
    ui.alerts_block(lab, data, aqi_val)

    ui.sec("Next 24 hours", "clock", aside="local time")
    ui.hourly_rail(data, unit)

    ui.sec("Forecast", "layers", aside="7 days")
    ui.daily_rows(data, unit)

    ui.sec("Conditions", "thermometer")
    ui.metrics_grid(data, aqi_val, unit)

    ui.sec("Air quality", "spark", aside="US AQI")
    ui.aqi_panel(aqi_data)

    ui.sec("Sun path", "sunrise")
    ui.sun_panel(data)

    ui.sec("Lifestyle insights", "star")
    ui.insights_row(data, aqi_val)

    now_label = local_now(data.get("timezone", "UTC")).strftime("%H:%M")
    ui.footer(now_label, is_offline)


dashboard()
