import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="What Should I Wear?", page_icon="🌤️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp {
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e0f2fe 0%, #fef9c3 60%, #fce7f3 100%) !important;
    min-height: 100vh;
}
[data-testid="stHeader"],
section[data-testid="stMain"] > div {
    background: transparent !important;
}

/* glass cards */
.glass {
    background: rgba(255,255,255,0.28);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.5);
    border-radius: 24px;
    padding: 2rem 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.10);
    animation: slideUp 0.45s cubic-bezier(.22,.68,0,1.2) both;
}
.glass-sm {
    background: rgba(255,255,255,0.25);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.45);
    border-radius: 16px;
    padding: 0.8rem 0.5rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.07);
    animation: slideUp 0.5s cubic-bezier(.22,.68,0,1.2) both;
}
.glass-row {
    background: rgba(255,255,255,0.25);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.45);
    border-radius: 18px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    animation: slideUp 0.55s cubic-bezier(.22,.68,0,1.2) both;
}
.fav-bar {
    background: rgba(255,255,255,0.28);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.45);
    border-radius: 16px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 1rem;
}

/* animations */
@keyframes slideUp {
    from { opacity:0; transform:translateY(22px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes pulse {
    0%,100% { transform:scale(1); }
    50%      { transform:scale(1.10); }
}
.pulse { animation:pulse 2.6s ease-in-out infinite; display:inline-block; }

/* typography */
.app-title {
    font-size: clamp(1.8rem,5vw,2.6rem);
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg,#0ea5e9,#a855f7,#f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: .2rem;
}
.app-sub { text-align:center; opacity:.6; font-size:.95rem; margin-bottom:1.5rem; }
.temp-num { font-size:clamp(3rem,10vw,4.5rem); font-weight:800; margin:0; line-height:1; }
.place-label { font-size:1rem; opacity:.65; margin:.4rem 0 1rem; }
.outfit-pill {
    display:inline-block;
    background:rgba(255,255,255,0.55);
    border-radius:50px;
    padding:.55rem 1.2rem;
    font-size:.95rem;
    font-weight:600;
    margin-top:.5rem;
    border:1px solid rgba(255,255,255,0.7);
}
.stat-row { display:flex; justify-content:center; gap:1rem; margin-top:1rem; flex-wrap:wrap; }
.stat-chip {
    background:rgba(255,255,255,0.4);
    border-radius:50px;
    padding:.3rem .9rem;
    font-size:.82rem;
    font-weight:600;
    border:1px solid rgba(255,255,255,0.55);
}
.section-label {
    font-size:.78rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.08em; opacity:.5; margin:1.3rem 0 .5rem;
}
.fc-day  { font-size:.72rem; font-weight:700; opacity:.55; text-transform:uppercase; letter-spacing:.05em; }
.fc-emoji{ font-size:1.7rem; margin:5px 0 3px; }
.fc-temp { font-size:.78rem; font-weight:700; }

/* aqi bar */
.aqi-bar-bg {
    width:100%; height:10px; border-radius:99px;
    background: linear-gradient(90deg,#22c55e,#84cc16,#eab308,#f97316,#ef4444,#7c3aed);
    position:relative; margin:.6rem 0 .3rem;
}
.aqi-dot {
    width:16px; height:16px; border-radius:50%;
    background:white; border:2px solid #333;
    position:absolute; top:-3px;
    transform:translateX(-50%);
    box-shadow:0 2px 6px rgba(0,0,0,0.25);
}

/* sun row */
.sun-item { text-align:center; flex:1; }
.sun-icon { font-size:1.6rem; }
.sun-label{ font-size:.72rem; font-weight:700; opacity:.5; text-transform:uppercase; letter-spacing:.05em; }
.sun-time { font-size:1.05rem; font-weight:700; margin-top:.15rem; }

/* score bar */
.score-bar-bg {
    width: 100%; height: 8px; border-radius: 99px;
    background: rgba(0,0,0,0.1); margin: 0.5rem 0 0.3rem;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%; border-radius: 99px;
    transition: width 0.6s ease;
}
/* info grid */
.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.7rem;
    margin-top: 0rem;
}
.info-tile {
    background: rgba(255,255,255,0.28);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.45);
    border-radius: 16px;
    padding: 0.85rem 1rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.07);
    animation: slideUp 0.45s cubic-bezier(.22,.68,0,1.2) both;
}
.info-tile-label {
    font-size: 0.72rem; font-weight: 700; opacity: 0.5;
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: 0.25rem;
}
.info-tile-val {
    font-size: 1.4rem; font-weight: 800; line-height: 1.1;
}
.info-tile-sub {
    font-size: 0.78rem; opacity: 0.6; margin-top: 0.2rem;
}

/* alert cards */
.alert-card {
    border-radius: 14px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-left: 4px solid;
    animation: slideUp 0.4s cubic-bezier(.22,.68,0,1.2) both;
}
.alert-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.15rem; }
.alert-body  { font-size: 0.83rem; opacity: 0.8; line-height: 1.4; }

/* inputs */
.stTextInput > div > div > input {
    background:rgba(255,255,255,0.55) !important;
    border:1px solid rgba(255,255,255,0.7) !important;
    border-radius:12px !important;
    font-family:'Outfit',sans-serif !important;
    font-size:1rem !important;
    padding:.6rem 1rem !important;
    color:#111 !important;
}
.stButton > button {
    font-family:'Outfit',sans-serif !important;
    font-weight:700 !important;
    border-radius:12px !important;
    border:none !important;
    transition:transform .15s, box-shadow .15s !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(0,0,0,0.13) !important;
}
</style>
""", unsafe_allow_html=True)

# ── session state ──
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "selected_city" not in st.session_state:
    st.session_state.selected_city = ""


# ── helpers ──
def get_coordinates(city_name):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city_name, "count": 1},
    )
    data = r.json()
    if "results" in data:
        res = data["results"][0]
        return res["latitude"], res["longitude"], res["name"], res.get("country", "")
    return None, None, None, None


def get_weather(lat, lon):
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat, "longitude": lon,
            "current_weather": True,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset",
            "hourly": "relativehumidity_2m,apparent_temperature,surface_pressure,visibility,cloudcover",
            "timezone": "auto",
        },
    )
    return r.json()


def get_aqi(lat, lon):
    r = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={
            "latitude": lat, "longitude": lon,
            "hourly": "us_aqi,pm2_5",
            "timezone": "auto",
        },
    )
    data = r.json()
    aqi   = data["hourly"]["us_aqi"][0]
    pm25  = data["hourly"]["pm2_5"][0]
    return aqi, pm25


def aqi_label(aqi):
    if aqi is None:
        return "N/A", "#6B7280", 0
    if aqi <= 50:
        return "Good 🟢", "#22c55e", (aqi / 50) * 16
    if aqi <= 100:
        return "Moderate 🟡", "#eab308", 16 + ((aqi - 50) / 50) * 17
    if aqi <= 150:
        return "Unhealthy for sensitive groups 🟠", "#f97316", 33 + ((aqi - 100) / 50) * 17
    if aqi <= 200:
        return "Unhealthy 🔴", "#ef4444", 50 + ((aqi - 150) / 50) * 17
    if aqi <= 300:
        return "Very Unhealthy 🟣", "#a855f7", 67 + ((aqi - 200) / 100) * 16
    return "Hazardous ⚫", "#7c3aed", 83 + ((aqi - 300) / 200) * 17


def code_to_info(code):
    table = {
        0:  ("Clear sky",     "☀️",  "#F59E0B"),
        1:  ("Mostly clear",  "🌤️", "#FBBF24"),
        2:  ("Partly cloudy", "⛅",  "#6B7280"),
        3:  ("Overcast",      "☁️",  "#9CA3AF"),
        45: ("Foggy",         "🌫️", "#9CA3A8"),
        48: ("Icy fog",       "🌫️", "#9CA3A8"),
        51: ("Light drizzle", "🌦️", "#3B82F6"),
        53: ("Drizzle",       "🌦️", "#3B82F6"),
        55: ("Heavy drizzle", "🌧️", "#2563EB"),
        61: ("Light rain",    "🌧️", "#3A7CA5"),
        63: ("Rain",          "🌧️", "#2563EB"),
        65: ("Heavy rain",    "🌧️", "#1D4ED8"),
        71: ("Light snow",    "🌨️", "#93C5FD"),
        73: ("Snow",          "❄️",  "#60A5FA"),
        75: ("Heavy snow",    "❄️",  "#3B82F6"),
        95: ("Thunderstorm",  "⛈️",  "#7C3AED"),
        96: ("Thunderstorm",  "⛈️",  "#7C3AED"),
        99: ("Violent storm", "🌪️", "#6D28D9"),
    }
    return table.get(code, ("Unknown", "🌡️", "#6B7280"))


def get_outfit(condition, temp):
    c = condition.lower()
    if "rain" in c or "drizzle" in c: return "☂️ Umbrella + waterproof shoes"
    if "storm" in c:                  return "⚡ Stay indoors if you can"
    if "snow" in c:                   return "🧤 Heavy jacket, gloves & boots"
    if "fog" in c:                    return "👁️ Drive carefully, wear layers"
    if temp >= 35:                    return "🥵 Very hot — light breathable clothing"
    if temp >= 28:                    return "😎 Light clothes and sunglasses"
    if temp >= 18:                    return "🙂 Comfortable — a light layer works"
    if temp >= 10:                    return "🧥 Grab a jacket before heading out"
    return                                   "🥶 Bundle up — it's cold out there"


def get_alerts(condition, temp, wind, aqi):
    alerts = []
    c = condition.lower()

    if temp >= 40:
        alerts.append(("🔴 Extreme Heat Warning",
                        f"Temperature is {temp}°C — dangerous heat. Stay indoors, drink water constantly, avoid all outdoor activity.",
                        "#ef4444"))
    elif temp >= 35:
        alerts.append(("🟠 Heatwave Alert",
                        f"Temperature is {temp}°C — heatwave conditions. Limit outdoor exposure, stay hydrated.",
                        "#f97316"))

    if temp <= 0:
        alerts.append(("🥶 Extreme Cold Warning",
                        f"Temperature is {temp}°C — risk of frostbite. Cover all exposed skin, limit time outside.",
                        "#60a5fa"))

    if "violent storm" in c:
        alerts.append(("🌪️ Violent Storm Warning",
                        "Violent storm detected. Stay indoors, avoid windows, do not drive.",
                        "#7c3aed"))
    elif "thunderstorm" in c:
        alerts.append(("⛈️ Thunderstorm Alert",
                        "Thunderstorms in the area. Avoid open spaces, trees, and metal objects.",
                        "#a855f7"))

    if "heavy snow" in c and wind > 40:
        alerts.append(("❄️ Blizzard Warning",
                        f"Heavy snow + {wind} km/h winds — blizzard conditions. Do not travel.",
                        "#3b82f6"))
    elif "heavy snow" in c:
        alerts.append(("🌨️ Heavy Snow Alert",
                        "Heavy snowfall expected. Roads may be slippery — drive with caution.",
                        "#60a5fa"))

    if wind > 70:
        alerts.append(("💨 Extreme Wind Warning",
                        f"Wind speed is {wind} km/h — dangerous gusts. Secure loose objects, avoid driving.",
                        "#f43f5e"))
    elif wind > 50:
        alerts.append(("💨 High Wind Advisory",
                        f"Wind speed is {wind} km/h. Be cautious outdoors, especially on bridges or open roads.",
                        "#fb923c"))

    if aqi is not None and aqi > 200:
        alerts.append(("😷 Very Unhealthy Air",
                        f"AQI is {aqi} — very unhealthy. Wear an N95 mask outdoors, keep windows closed.",
                        "#dc2626"))
    elif aqi is not None and aqi > 150:
        alerts.append(("😷 Unhealthy Air Quality",
                        f"AQI is {aqi} — unhealthy for everyone. Sensitive groups should stay indoors.",
                        "#f97316"))

    if "fog" in c:
        alerts.append(("🌫️ Dense Fog Advisory",
                        "Visibility is reduced due to fog. Slow down while driving, use fog lights.",
                        "#9ca3af"))

    return alerts


def fmt_time(iso_str):
    try:
        return datetime.fromisoformat(iso_str).strftime("%I:%M %p")
    except Exception:
        return iso_str


def mosquito_alert(temp, humidity):
    if temp >= 25 and humidity >= 70:
        return "🦟 High", "#ef4444", "Warm and humid — peak mosquito activity. Use repellent and wear long sleeves after sunset."
    if temp >= 20 and humidity >= 55:
        return "🦟 Moderate", "#f97316", "Conditions are somewhat favorable for mosquitoes. Take precautions in the evening."
    return "🦟 Low", "#22c55e", "Conditions are unfavorable for mosquitoes right now."


def stargazing_score(cloud_cover, aqi, condition):
    c = condition.lower()
    if any(x in c for x in ["rain", "storm", "snow", "fog", "drizzle"]):
        return 0, "❌ Not possible", "#6b7280", "Sky is obscured by weather — no stargazing tonight."
    score = 100 - cloud_cover
    if aqi is not None:
        score -= min(aqi // 5, 30)
    score = max(0, score)
    if score >= 75:
        return score, "⭐ Excellent", "#a855f7", "Clear skies and clean air — ideal night for stargazing. Get your telescope out!"
    if score >= 50:
        return score, "🌟 Good", "#8b5cf6", "Decent visibility tonight. You'll catch most stars and maybe the Milky Way."
    if score >= 25:
        return score, "🌤️ Fair", "#6366f1", "Partly cloudy — you'll see bright stars and planets but the view is limited."
    return score, "☁️ Poor", "#6b7280", "Too much cloud cover for a good view tonight."


def outdoor_sports_score(temp, wind, aqi, condition):
    c = condition.lower()
    if any(x in c for x in ["storm", "violent", "blizzard"]):
        return 0, "🚫 Dangerous", "#ef4444", "Severe weather — do not go outside for sports."
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
    if aqi is not None:
        if aqi > 150:
            score -= 40
        elif aqi > 100:
            score -= 20
        elif aqi > 50:
            score -= 10
    if any(x in c for x in ["rain", "snow", "drizzle"]):
        score -= 30
    if "fog" in c:
        score -= 15
    score = max(0, min(score, 100))
    if score >= 75:
        return score, "🏃 Great", "#22c55e", "Excellent conditions for outdoor sports — get out there!"
    if score >= 55:
        return score, "👍 Good", "#84cc16", "Good conditions overall. Stay hydrated and wear sunscreen."
    if score >= 35:
        return score, "😐 Moderate", "#eab308", "Manageable but not ideal. Short sessions are fine."
    if score >= 15:
        return score, "⚠️ Poor", "#f97316", "Conditions are tough — consider indoor alternatives."
    return score, "🚫 Avoid", "#ef4444", "Not recommended for outdoor sports today."



    try:
        return datetime.fromisoformat(iso_str).strftime("%I:%M %p")
    except Exception:
        return iso_str


# ── UI ──
st.markdown("<div class='app-title'>What Should I Wear?</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='app-sub'>Real-time weather · outfit advice · air quality · 5-day outlook</div>",
    unsafe_allow_html=True,
)

# favorites bar
if st.session_state.favorites:
    st.markdown("<div class='fav-bar'>", unsafe_allow_html=True)
    st.markdown(
        "<span style='font-size:.78rem;font-weight:700;opacity:.5;text-transform:uppercase;letter-spacing:.06em;'>⭐ Saved</span>",
        unsafe_allow_html=True,
    )
    fcols = st.columns(min(len(st.session_state.favorites), 5))
    for i, fav in enumerate(st.session_state.favorites[:5]):
        with fcols[i]:
            if st.button(fav, key=f"fav_{i}", use_container_width=True):
                st.session_state.selected_city = fav
    st.markdown("</div>", unsafe_allow_html=True)

city = st.text_input(
    "City", value=st.session_state.selected_city,
    placeholder="Enter a city — e.g. Mumbai, Tokyo, London…",
    label_visibility="collapsed",
)

c1, c2, c3 = st.columns([4, 1.2, 1.2])
with c1:
    search = st.button("🔍  Check weather", use_container_width=True)
with c2:
    save = st.button("⭐ Save", use_container_width=True)
with c3:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.favorites = []
        st.rerun()

if save:
    name = city.strip().title()
    if name and name not in st.session_state.favorites:
        st.session_state.favorites.append(name)
        st.success(f"'{name}' saved!")
    elif name in st.session_state.favorites:
        st.info("Already saved.")
    else:
        st.warning("Type a city name first.")

# ── results ──
if search:
    if not city.strip():
        st.warning("Type a city name first.")
    else:
        try:
            lat, lon, place, country = get_coordinates(city)
            if lat is None:
                st.error("City not found — check the spelling and try again.")
            else:
                with st.spinner("Fetching weather data…"):
                    data = get_weather(lat, lon)
                    aqi_val, pm25 = get_aqi(lat, lon)

                cw       = data["current_weather"]
                cond, emoji, color = code_to_info(cw["weathercode"])
                outfit   = get_outfit(cond, cw["temperature"])
                humidity    = data["hourly"]["relativehumidity_2m"][0]
                feels_like  = data["hourly"]["apparent_temperature"][0]
                pressure    = round(data["hourly"]["surface_pressure"][0])
                visibility  = round(data["hourly"]["visibility"][0] / 1000, 1)
                cloud_cover = data["hourly"]["cloudcover"][0]
                wind     = cw["windspeed"]

                # ── main weather card ──
                st.markdown(
                    f"""
                    <div class="glass" style="text-align:center; border-top:4px solid {color};">
                        <div class="pulse" style="font-size:72px;line-height:1;">{emoji}</div>
                        <p class="temp-num" style="color:{color};">{cw['temperature']}°C</p>
                        <p class="place-label">{place}, {country} &nbsp;·&nbsp; {cond}</p>
                        <div class="outfit-pill">{outfit}</div>
                        <div class="stat-row">
                            <span class="stat-chip">💧 {humidity}% humidity</span>
                            <span class="stat-chip">💨 {wind} km/h wind</span>
                            <span class="stat-chip">🌡️ Feels {feels_like}°C</span>
                            <span class="stat-chip">🔵 {pressure} hPa</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ── alerts ──
                alerts = get_alerts(cond, cw["temperature"], wind, aqi_val)
                if alerts:
                    st.markdown("<div class='section-label'>⚠️ Active Alerts</div>", unsafe_allow_html=True)
                    for title, body, col in alerts:
                        st.markdown(
                            f"""<div class="alert-card" style="
                                background:rgba(255,255,255,0.35);
                                border-left-color:{col};">
                                <div>
                                    <div class="alert-title" style="color:{col};">{title}</div>
                                    <div class="alert-body">{body}</div>
                                </div>
                            </div>""",
                            unsafe_allow_html=True,
                        )

                # ── sunrise / sunset + AQI row ──
                sunrise_raw = data["daily"]["sunrise"][0]
                sunset_raw  = data["daily"]["sunset"][0]
                sunrise_fmt = fmt_time(sunrise_raw)
                sunset_fmt  = fmt_time(sunset_raw)
                aqi_text, aqi_color, dot_pct = aqi_label(aqi_val)

                st.markdown("<div class='section-label'>Air & Sun</div>", unsafe_allow_html=True)

                left, right = st.columns(2)

                with left:
                    st.markdown(
                        f"""
                        <div class="glass-row">
                            <div style="font-size:.78rem;font-weight:700;opacity:.5;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.5rem;">🌬️ Air Quality</div>
                            <div style="font-size:1.5rem;font-weight:800;color:{aqi_color};">{aqi_val if aqi_val else 'N/A'}</div>
                            <div style="font-size:.85rem;font-weight:600;color:{aqi_color};margin-bottom:.4rem;">{aqi_text}</div>
                            <div class="aqi-bar-bg">
                                <div class="aqi-dot" style="left:{min(dot_pct, 97)}%;"></div>
                            </div>
                            <div style="font-size:.75rem;opacity:.5;margin-top:.3rem;">PM2.5 — {round(pm25,1) if pm25 else 'N/A'} µg/m³</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with right:
                    st.markdown(
                        f"""
                        <div class="glass-row" style="height:100%;">
                            <div style="font-size:.78rem;font-weight:700;opacity:.5;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.7rem;">🌅 Sun Times</div>
                            <div style="display:flex;gap:1rem;">
                                <div class="sun-item">
                                    <div class="sun-icon">🌄</div>
                                    <div class="sun-label">Sunrise</div>
                                    <div class="sun-time">{sunrise_fmt}</div>
                                </div>
                                <div style="width:1px;background:rgba(0,0,0,0.1);"></div>
                                <div class="sun-item">
                                    <div class="sun-icon">🌇</div>
                                    <div class="sun-label">Sunset</div>
                                    <div class="sun-time">{sunset_fmt}</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # ── extra insights grid ──
                st.markdown("<div class='section-label'>📊 Insights</div>", unsafe_allow_html=True)

                m_label, m_color, m_tip   = mosquito_alert(cw["temperature"], humidity)
                sg_score, sg_label, sg_color, sg_tip = stargazing_score(cloud_cover, aqi_val, cond)
                sp_score, sp_label, sp_color, sp_tip = outdoor_sports_score(cw["temperature"], wind, aqi_val, cond)

                st.markdown(f"""
                <div class="info-grid">
                    <div class="info-tile">
                        <div class="info-tile-label">👁️ Visibility</div>
                        <div class="info-tile-val">{visibility} km</div>
                        <div class="info-tile-sub">{"Crystal clear" if visibility >= 10 else "Reduced visibility" if visibility >= 4 else "Very poor — drive carefully"}</div>
                    </div>
                    <div class="info-tile">
                        <div class="info-tile-label">🦟 Mosquito Risk</div>
                        <div class="info-tile-val" style="color:{m_color};">{m_label}</div>
                        <div class="info-tile-sub">{m_tip}</div>
                    </div>
                    <div class="info-tile">
                        <div class="info-tile-label">🔭 Stargazing</div>
                        <div class="info-tile-val" style="color:{sg_color};">{sg_label}</div>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:{sg_score}%;background:{sg_color};"></div>
                        </div>
                        <div class="info-tile-sub">{sg_tip}</div>
                    </div>
                    <div class="info-tile">
                        <div class="info-tile-label">⚽ Outdoor Sports</div>
                        <div class="info-tile-val" style="color:{sp_color};">{sp_label}</div>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:{sp_score}%;background:{sp_color};"></div>
                        </div>
                        <div class="info-tile-sub">{sp_tip}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── 5-day forecast ──
                st.markdown("<div class='section-label'>5-day forecast</div>", unsafe_allow_html=True)
                daily   = data["daily"]
                fcols2  = st.columns(5)
                for i in range(1, 6):
                    d_name = datetime.strptime(daily["time"][i], "%Y-%m-%d").strftime("%a")
                    hi     = daily["temperature_2m_max"][i]
                    lo     = daily["temperature_2m_min"][i]
                    _, d_emoji, d_color = code_to_info(daily["weathercode"][i])
                    with fcols2[i - 1]:
                        st.markdown(
                            f"<div class='glass-sm' style='border-top:3px solid {d_color};'>"
                            f"<div class='fc-day'>{d_name}</div>"
                            f"<div class='fc-emoji'>{d_emoji}</div>"
                            f"<div class='fc-temp' style='color:{d_color};'>{hi}°"
                            f"<span style='opacity:.45;font-weight:400;'> / {lo}°</span></div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

        except requests.exceptions.RequestException:
            st.error("Network error — check your connection and try again.")