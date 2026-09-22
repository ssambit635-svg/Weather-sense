"""WeatherSense — minimalist live weather app.

Structure of a run:

1. paint the palette (``?theme=`` -> session -> dark) and the intro card — the
   first paint is instant because it happens before any network call;
2. bootstrap the active city (``?city=`` param -> IP geolocation -> default);
3. render the shell (header clock, unit + theme pills, offline notice) and
   search;
4. fade the intro card out and render the live dashboard fragment.

Everything is wrapped in an error boundary at the bottom of this file, so a
failure shows an actionable card instead of a blank screen or a raw traceback.
"""

from __future__ import annotations

import time
from datetime import timedelta
from typing import Optional

import streamlit as st

from weather_sense import components as ui
from weather_sense.api import (
    city_temps, code_info, fetch_bundle, fmt_t, geocode, local_now, locate_by_ip,
    network_ok, num, valid_place,
)
from weather_sense.compat import (
    MIN_STREAMLIT, STREAMLIT_VERSION, control_flow_exceptions, fragment, stretch,
    version_ok,
)
from weather_sense.icons import LOGO_DATA_URI, icon
from weather_sense.styles import DEFAULT_THEME, THEMES, apply_theme, inject, set_accent

# The intro card holds long enough for the logo to finish drawing itself.
MIN_SPLASH_SECONDS = 1.15
SPLASH_FADE_SECONDS = 0.42

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

# palette: ?theme= wins (shareable), then the session choice, then dark
_q_theme = str(st.query_params.get("theme") or "").lower()
if _q_theme in THEMES:
    ss["theme"] = _q_theme
ss.setdefault("theme", DEFAULT_THEME)


def persist_city(place: dict) -> None:
    ss["place"] = place
    # flag only — the text_input widget is already instantiated this run,
    # so the value itself is synced at the top of the next run.
    ss["_sync_input"] = True
    try:
        st.query_params["city"] = place.get("name") or ""
        if place.get("country_code"):
            st.query_params["cc"] = place["country_code"]
        elif "cc" in st.query_params:
            del st.query_params["cc"]
    except Exception:
        pass


def resolve_query_city() -> Optional[dict]:
    """Geocode the ?city= URL parameter once per session."""
    q = st.query_params.get("city")
    if not q or ss.get("_q_resolved"):
        return ss.get("place")
    ss["_q_resolved"] = True
    hits = geocode(q, count=5)
    if not hits:
        return ss.get("place")
    cc = st.query_params.get("cc")
    if cc:
        for h in hits:
            if h.get("country_code") == cc:
                ss["place"] = h
                return h
    ss["place"] = hits[0]
    return hits[0]


def bootstrap_place() -> Optional[dict]:
    """URL param -> IP geolocation -> a guaranteed-usable default city."""
    place = resolve_query_city()
    if valid_place(place):
        return place
    here = locate_by_ip()                     # best effort (needs network)
    if valid_place(here):
        return here
    hits = geocode("London", count=1)         # gazetteer fallback always answers
    return hits[0] if hits else None


def render_shell(place: Optional[dict], bundle: Optional[dict]) -> None:
    """Header (live clock), unit toggle and the offline notice.

    `bundle` is passed in rather than fetched here so the intro splash covers
    the one network round-trip instead of the user watching it happen.
    """
    offline = bool(bundle.get("offline")) if bundle else False

    @fragment(run_every=timedelta(seconds=45))
    def topbar() -> None:
        """Live local clock + brand mark (re-renders without touching the page).

        Failures are swallowed on purpose: a broken clock must never take the
        header (or the page) down with it.
        """
        lt = tl = ""
        is_offline = False
        try:
            p = ss.get("place")
            if valid_place(p):
                b = fetch_bundle(p["lat"], p["lon"])
                is_offline = bool(b.get("offline"))
                tzn = (b.get("weather") or {}).get("timezone") or "UTC"
                lt = local_now(tzn).strftime("%H:%M")
                tl = (tzn.split("/")[-1] if tzn else "").replace("_", " ")
        except Exception:
            lt, tl, is_offline = "", "", False
        ui.header(lt, tl, is_offline)

    topbar()
    ui.controls_row()

    if offline:
        st.markdown(
            """
            <div class="notice info">
              <span style="color:var(--accent);margin-top:1px">%s</span>
              <div><b>Offline preview.</b> Live weather services are unreachable from this
              environment, so a generated sample dataset is shown. Anywhere with network
              access fetches real conditions from Open-Meteo.</div>
            </div>""" % icon("wifi-off", 15),
            unsafe_allow_html=True,
        )


def render_search(place: Optional[dict]) -> None:
    """Search box, alternate matches and quick actions."""
    # keep the search field in sync with the active city
    if ss.get("_sync_input"):
        ss["city_input"] = (ss.get("place") or {}).get("name", "") or ""
        ss["_sync_input"] = False
    elif "city_input" not in ss:
        ss["city_input"] = (place or {}).get("name", "") or ""

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
            submitted = st.form_submit_button("Search", **stretch())

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

    if ss.get("pending_hits"):
        alts = ss["pending_hits"]
        ss["pending_hits"] = None
        cols = st.columns([1.35] + [1] * len(alts))
        with cols[0]:
            st.caption("Did you mean")
        for i, alt in enumerate(alts, start=1):
            with cols[i]:
                full = f'{alt["name"]}, {alt.get("country") or alt.get("admin") or ""}'.strip(", ")
                if st.button(full, key=f"alt_{i}", **stretch()):
                    persist_city(alt)
                    st.rerun()

    ui.gap(sm=True)
    la, lb, _ = st.columns([1.6, 1.6, 2.8])
    with la:
        if st.button("My location", **stretch()):
            with st.spinner("Locating..."):
                here = locate_by_ip()
            if valid_place(here):
                persist_city(here)
                st.rerun()
            elif not network_ok():
                st.info("IP location needs internet access and this session is "
                        "offline — search for a city instead.")
            else:
                st.error("Could not determine your location. Search for a city instead.")
    with lb:
        if valid_place(place):
            already = any(f.get("name") == place.get("name") for f in ss["favorites"])
            if st.button(
                "Saved" if already else "Save city",
                disabled=already,
                **stretch(),
            ):
                ss["favorites"] = [*ss["favorites"], place]
                st.toast(f"{place['name']} saved.")
                st.rerun()

    if ss["favorites"]:
        ui.gap(sm=True)
        shown = [f for f in ss["favorites"] if valid_place(f)][:6]
        temps = city_temps(shown)
        cols = st.columns(len(shown) + 1)
        for i, fav in enumerate(shown):
            with cols[i]:
                t = temps.get(fav["name"])
                label_txt = f"{fav['name']}  {fmt_t(t, ss['unit']) if t is not None else '--'}"
                if st.button(label_txt, key=f"fav_{i}_{fav['name']}", **stretch()):
                    persist_city(fav)
                    st.rerun()
        with cols[-1]:
            if st.button("Clear", key="clear_favs", **stretch()):
                ss["favorites"] = []
                st.rerun()


def _rerun_app() -> None:
    """Full-app rerun that also works from inside a fragment."""
    try:
        st.rerun(scope="app")
    except TypeError:            # pre-fragment Streamlit
        st.rerun()


def _fragment_error(exc: BaseException, what: str) -> None:
    """In-fragment error card.

    Exceptions raised inside an ``st.fragment`` are turned into Streamlit's own
    red traceback box *before* any outer ``try`` can see them, so each fragment
    handles its own failures and offers a one-click recovery.
    """
    import traceback

    try:
        st.cache_data.clear()
    except Exception:
        pass
    ui.fatal(
        what,
        "Caches were cleared. Retry now, or reload the page — the rest of the "
        "app keeps working either way.",
        f"{type(exc).__name__}: {exc}",
    )
    if st.button("Retry", key="ws_retry_fragment", **stretch()):
        _rerun_app()
    with st.expander("Traceback"):
        st.code(traceback.format_exc(), language="text")


@fragment(run_every=timedelta(seconds=45))
def dashboard(place: dict, unit: str) -> None:
    """Re-renders every 45 s; refetches only when the server cache expires."""
    try:
        _dashboard(place, unit)
    except Exception as exc:     # pragma: no cover - safety net
        _fragment_error(exc, "The live dashboard could not be rendered")


def _dashboard(place: dict, unit: str) -> None:
    b = fetch_bundle(place["lat"], place["lon"])
    data = b.get("weather") or {}
    aqi_data = b.get("aqi") or {}
    is_offline = bool(b.get("offline"))
    aqi_val = num((aqi_data.get("current") or {}).get("us_aqi"))

    c = data.get("current") or {}
    lab, _key, acc = code_info(c.get("weather_code"), bool(c.get("is_day", 1)))
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

    now_label = local_now(data.get("timezone") or "UTC").strftime("%H:%M")
    ui.footer(now_label, is_offline)


def main() -> None:
    inject()
    apply_theme()            # palette + condition accent, before anything paints

    # -- unsupported Streamlit: say so instead of dying on an AttributeError --
    if not version_ok():
        need = ".".join(str(p) for p in MIN_STREAMLIT[:2])
        have = ".".join(str(p) for p in STREAMLIT_VERSION)
        ui.fatal(
            "Streamlit is too old",
            f"WeatherSense needs Streamlit {need}+ (running {have}). "
            "Upgrade and reload — everything else is fine.",
            f"pip install --upgrade 'streamlit>={need}'",
        )
        return

    # -- 1. intro card: the very first thing painted, before any network work.
    #    st.empty() (not st.container()) gives one slot we can re-render and
    #    then clear, so exactly one splash exists at any moment.
    splash_slot = None
    splash_started = 0.0
    if not ss.get("_splash_done"):
        ss["_splash_done"] = True
        splash_started = time.monotonic()
        splash_slot = st.empty()
        splash_slot.markdown(ui.splash_html("Reading the sky"), unsafe_allow_html=True)

    # -- 2. bootstrap + first fetch (the loader covers this round-trip) --
    if not ss.get("booted"):
        ss["booted"] = True
        found = bootstrap_place()
        if found:
            ss["place"] = found
            ss["_sync_input"] = True

    place = ss.get("place")
    place = place if valid_place(place) else None
    ss["place"] = place

    bundle = fetch_bundle(place["lat"], place["lon"]) if place else None

    # -- 3. fade the intro out, then reveal the app as one clean screen --
    _finish_splash(splash_slot, splash_started)

    render_shell(place, bundle)
    render_search(place)

    if place is None or bundle is None:
        ui.gap(lg=True)
        ui.empty_state()
        return

    cur0 = (bundle.get("weather") or {}).get("current") or {}
    _, _, accent = code_info(cur0.get("weather_code"), bool(cur0.get("is_day", 1)))
    set_accent(accent)

    dashboard(place, ss["unit"])


def _finish_splash(slot, started: float) -> None:
    """Let the logo finish drawing, then fade the intro card away."""
    if slot is None:
        return
    rest = MIN_SPLASH_SECONDS - (time.monotonic() - started)
    if rest > 0:
        time.sleep(rest)
    slot.markdown(
        ui.splash_html("Ready", ready=True, fade=True), unsafe_allow_html=True
    )
    time.sleep(SPLASH_FADE_SECONDS)
    slot.empty()


# ---------------------------------------------------------------------------
# entry point with an error boundary — the app never ends as a blank screen
# ---------------------------------------------------------------------------
try:
    main()
except control_flow_exceptions:      # st.rerun() / st.stop() are control flow
    raise
except Exception as exc:             # pragma: no cover - safety net
    import traceback

    try:
        st.cache_data.clear()
    except Exception:
        pass
    if "booted" in ss:
        del ss["booted"]
    inject()
    apply_theme()
    ui.fatal(
        "WeatherSense hit an unexpected error",
        "This run could not be completed. Caches were cleared — retry now, or "
        "reload the page for a clean state. The exact failure is shown below so "
        "it can be reported.",
        f"{type(exc).__name__}: {exc}",
    )
    if st.button("Retry", key="ws_retry_app", **stretch()):
        _rerun_app()
    with st.expander("Traceback"):
        st.code(traceback.format_exc(), language="text")
