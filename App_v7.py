import streamlit as st
import requests
from datetime import datetime
import math

st.set_page_config(page_title="WeatherSense", page_icon="🌤️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #0a0f1e !important;
    color: #e8eaf0 !important;
}
[data-testid="stAppViewContainer"] {
    background: #0a0f1e !important;
    min-height: 100vh;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
section[data-testid="stMain"] > div {
    background: transparent !important;
}
[data-testid="stMainBlockContainer"] {
    max-width: 480px !important;
    margin: 0 auto !important;
    padding: 1.5rem 1rem 4rem !important;
}

/* ── GLASS CARDS ── */
.card {
    background: linear-gradient(135deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.03) 100%);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 28px;
    padding: 1.6rem 1.4rem;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08);
    animation: fadeUp .5s cubic-bezier(.22,.68,0,1.15) both;
    margin-bottom: 0.9rem;
}
.card-sm {
    background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 1rem 0.75rem;
    text-align: center;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    animation: fadeUp .55s cubic-bezier(.22,.68,0,1.15) both;
}
.card-mini {
    background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1rem 1rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    animation: fadeUp .5s cubic-bezier(.22,.68,0,1.15) both;
}

/* ── HERO ── */
.hero-wrap { text-align: center; padding: 0.5rem 0 1rem; }
.hero-emoji {
    font-size: 88px; line-height: 1;
    filter: drop-shadow(0 0 32px rgba(255,200,50,.35));
    animation: floatEmoji 4s ease-in-out infinite;
    display: inline-block;
}
.hero-temp {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(72px, 18vw, 96px);
    font-weight: 700;
    line-height: .9;
    letter-spacing: -4px;
    background: linear-gradient(180deg, #ffffff 30%, rgba(255,255,255,.5) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: .4rem 0 .2rem;
}
.hero-place {
    font-size: .95rem;
    font-weight: 500;
    color: rgba(255,255,255,.55);
    letter-spacing: .02em;
    margin-bottom: .3rem;
}
.hero-cond {
    font-size: 1.05rem;
    font-weight: 600;
    color: rgba(255,255,255,.85);
}
.outfit-badge {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 999px;
    padding: .5rem 1.1rem;
    font-size: .88rem;
    font-weight: 600;
    color: #e8eaf0;
    margin-top: .8rem;
    backdrop-filter: blur(12px);
}

/* ── STAT PILLS ── */
.stat-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: .5rem;
    margin-top: 1rem;
}
.stat-pill {
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 999px;
    padding: .3rem .8rem;
    font-size: .78rem;
    font-weight: 600;
    color: rgba(255,255,255,.75);
    white-space: nowrap;
}

/* ── SECTION LABEL ── */
.sec-label {
    font-size: .68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .12em;
    color: rgba(255,255,255,.35);
    margin: 1.4rem 0 .6rem .2rem;
}

/* ── COMPASS ── */
.compass-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: .5rem;
}
.compass-ring {
    width: 120px; height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,.05) 0%, rgba(255,255,255,.02) 100%);
    border: 1.5px solid rgba(255,255,255,.12);
    position: relative;
    box-shadow: 0 0 30px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.08);
}
.compass-label {
    position: absolute;
    font-size: .6rem;
    font-weight: 700;
    color: rgba(255,255,255,.45);
}
.compass-n { top: 6px; left: 50%; transform: translateX(-50%); color: #f87171 !important; }
.compass-s { bottom: 6px; left: 50%; transform: translateX(-50%); }
.compass-e { right: 7px; top: 50%; transform: translateY(-50%); }
.compass-w { left: 7px; top: 50%; transform: translateY(-50%); }
.compass-needle-wrap {
    position: absolute;
    top: 50%; left: 50%;
    width: 4px; height: 90px;
    transform-origin: 50% 50%;
    transform: translate(-50%, -50%) rotate(VAR_DEG);
    margin-top: 0;
}
.compass-north {
    position: absolute;
    bottom: 50%;
    left: 50%;
    transform: translateX(-50%);
    width: 0; height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 42px solid #f87171;
    filter: drop-shadow(0 0 8px #f87171);
}
.compass-south {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translateX(-50%);
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 38px solid rgba(255,255,255,.25);
}
.compass-dot {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 8px; height: 8px;
    border-radius: 50%;
    background: white;
    box-shadow: 0 0 8px rgba(255,255,255,.6);
    z-index: 10;
}
.compass-dir-label {
    font-size: 1rem;
    font-weight: 700;
    color: #f87171;
    letter-spacing: .05em;
}
.compass-speed {
    font-size: .78rem;
    color: rgba(255,255,255,.45);
}

/* ── AQI BAR ── */
.aqi-bar-bg {
    width: 100%; height: 8px; border-radius: 99px;
    background: linear-gradient(90deg,#22c55e,#84cc16,#eab308,#f97316,#ef4444,#7c3aed);
    position: relative; margin: .6rem 0 .25rem; overflow: visible;
}
.aqi-dot {
    width: 14px; height: 14px; border-radius: 50%;
    background: white; border: 2px solid #1a1a2e;
    position: absolute; top: -3px;
    transform: translateX(-50%);
    box-shadow: 0 0 8px rgba(255,255,255,.5);
}

/* ── SCORE BAR ── */
.score-bar-bg {
    width: 100%; height: 5px; border-radius: 99px;
    background: rgba(255,255,255,.1); margin: .45rem 0 .25rem; overflow: hidden;
}
.score-bar-fill { height: 100%; border-radius: 99px; }

/* ── ALERT CARD ── */
.alert-card {
    border-radius: 16px;
    padding: .85rem 1rem;
    margin-bottom: .55rem;
    border-left: 3px solid;
    background: rgba(255,255,255,.04);
    backdrop-filter: blur(12px);
    animation: fadeUp .4s cubic-bezier(.22,.68,0,1.15) both;
}
.alert-title { font-weight: 700; font-size: .88rem; margin-bottom: .15rem; }
.alert-body  { font-size: .78rem; opacity: .65; line-height: 1.45; }

/* ── SUN ROW ── */
.sun-row { display: flex; gap: 1rem; align-items: center; }
.sun-item { flex: 1; text-align: center; }
.sun-divider { width: 1px; height: 40px; background: rgba(255,255,255,.1); }
.sun-icon { font-size: 1.5rem; }
.sun-lbl { font-size: .65rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; opacity: .4; margin: .2rem 0; }
.sun-time { font-size: 1rem; font-weight: 700; }

/* ── FORECAST ── */
.fc-day  { font-size: .65rem; font-weight: 700; opacity: .45; text-transform: uppercase; letter-spacing: .06em; }
.fc-emoji{ font-size: 1.6rem; margin: .35rem 0 .25rem; }
.fc-hi   { font-size: .82rem; font-weight: 700; }
.fc-lo   { font-size: .72rem; opacity: .4; font-weight: 500; }

/* ── INSIGHT GRID ── */
.insight-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .7rem; }
.insight-lbl { font-size: .65rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; opacity: .4; margin-bottom: .35rem; }
.insight-val { font-size: 1.1rem; font-weight: 700; margin-bottom: .15rem; }
.insight-sub { font-size: .72rem; opacity: .5; line-height: 1.4; }

/* ── INPUT & BUTTONS ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,.07) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    border-radius: 14px !important;
    color: #e8eaf0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .95rem !important;
    padding: .65rem 1rem !important;
    transition: border .2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(255,255,255,.28) !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,.06) !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,.25) !important; }
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    background: rgba(255,255,255,.08) !important;
    color: #e8eaf0 !important;
    transition: all .2s !important;
    padding: .5rem .75rem !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,.14) !important;
    transform: translateY(-1px) !important;
}

/* ── APP TITLE ── */
.app-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: rgba(255,255,255,.9);
    letter-spacing: -.02em;
    text-align: center;
    margin-bottom: .15rem;
}
.app-sub {
    font-size: .75rem;
    color: rgba(255,255,255,.3);
    text-align: center;
    margin-bottom: 1.2rem;
    letter-spacing: .02em;
}

/* ── FAV BAR ── */
.fav-bar {
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 16px;
    padding: .7rem .9rem;
    margin-bottom: .8rem;
}
.fav-lbl { font-size: .62rem; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; opacity: .35; margin-bottom: .4rem; }

/* ── ANIMATIONS ── */
@keyframes fadeUp {
    from { opacity:0; transform:translateY(18px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes floatEmoji {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-10px); }
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
    r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                     params={"name": city_name, "count": 1})
    data = r.json()
    if "results" in data:
        res = data["results"][0]
        return res["latitude"], res["longitude"], res["name"], res.get("country", "")
    return None, None, None, None

def get_weather(lat, lon):
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon,
        "current_weather": True,
        "daily": "temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset",
        "hourly": "relativehumidity_2m,apparent_temperature,surface_pressure,visibility,cloudcover",
        "timezone": "auto",
    })
    return r.json()

def get_aqi(lat, lon):
    r = requests.get("https://air-quality-api.open-meteo.com/v1/air-quality", params={
        "latitude": lat, "longitude": lon,
        "hourly": "us_aqi,pm2_5", "timezone": "auto",
    })
    data = r.json()
    return data["hourly"]["us_aqi"][0], data["hourly"]["pm2_5"][0]

def wind_direction(deg):
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    return dirs[round(deg / 45) % 8]

def code_to_info(code):
    table = {
        0:("Clear sky","☀️","#F59E0B"), 1:("Mostly clear","🌤️","#FBBF24"),
        2:("Partly cloudy","⛅","#94A3B8"), 3:("Overcast","☁️","#64748B"),
        45:("Foggy","🌫️","#94A3B8"), 48:("Icy fog","🌫️","#94A3B8"),
        51:("Light drizzle","🌦️","#60A5FA"), 53:("Drizzle","🌦️","#3B82F6"),
        55:("Heavy drizzle","🌧️","#2563EB"), 61:("Light rain","🌧️","#60A5FA"),
        63:("Rain","🌧️","#3B82F6"), 65:("Heavy rain","🌧️","#1D4ED8"),
        71:("Light snow","🌨️","#BAE6FD"), 73:("Snow","❄️","#7DD3FC"),
        75:("Heavy snow","❄️","#38BDF8"), 95:("Thunderstorm","⛈️","#A78BFA"),
        96:("Thunderstorm","⛈️","#8B5CF6"), 99:("Violent storm","🌪️","#7C3AED"),
    }
    return table.get(code, ("Unknown","🌡️","#94A3B8"))

def get_outfit(condition, temp):
    c = condition.lower()
    if "rain" in c or "drizzle" in c: return "☂️ Umbrella + waterproof shoes"
    if "storm" in c:                  return "⚡ Stay indoors if possible"
    if "snow" in c:                   return "🧤 Heavy jacket, gloves & boots"
    if "fog" in c:                    return "👁️ Layers + careful driving"
    if temp >= 35:                    return "🥵 Ultra light breathable clothing"
    if temp >= 28:                    return "😎 Light clothes + sunglasses"
    if temp >= 18:                    return "🙂 Light layer is enough"
    if temp >= 10:                    return "🧥 Jacket before heading out"
    return                                   "🥶 Bundle up — it's freezing"

def get_alerts(condition, temp, wind, aqi):
    alerts = []
    c = condition.lower()
    if temp >= 40:
        alerts.append(("🔴 Extreme Heat Warning", f"Temp {temp}°C — dangerous. Stay indoors, drink water.", "#ef4444"))
    elif temp >= 35:
        alerts.append(("🟠 Heatwave Alert", f"Temp {temp}°C — limit outdoor exposure.", "#f97316"))
    if temp <= 0:
        alerts.append(("🥶 Extreme Cold", f"Temp {temp}°C — frostbite risk. Cover all skin.", "#60a5fa"))
    if "violent" in c:
        alerts.append(("🌪️ Violent Storm", "Stay indoors, avoid windows, don't drive.", "#7c3aed"))
    elif "thunderstorm" in c:
        alerts.append(("⛈️ Thunderstorm", "Avoid open spaces and metal objects.", "#a855f7"))
    if "heavy snow" in c and wind > 40:
        alerts.append(("❄️ Blizzard Warning", f"Heavy snow + {wind}km/h winds. Do not travel.", "#3b82f6"))
    if wind > 70:
        alerts.append(("💨 Extreme Wind", f"{wind} km/h gusts — dangerous outside.", "#f43f5e"))
    elif wind > 50:
        alerts.append(("💨 High Wind", f"{wind} km/h winds. Be cautious outdoors.", "#fb923c"))
    if aqi and aqi > 200:
        alerts.append(("😷 Very Unhealthy Air", f"AQI {aqi} — wear N95, keep windows shut.", "#dc2626"))
    elif aqi and aqi > 150:
        alerts.append(("😷 Unhealthy Air", f"AQI {aqi} — sensitive groups stay indoors.", "#f97316"))
    if "fog" in c:
        alerts.append(("🌫️ Dense Fog", "Reduced visibility. Slow down, use fog lights.", "#94a3b8"))
    return alerts

def aqi_label(aqi):
    if not aqi: return "N/A", "#94a3b8", 0
    if aqi <= 50:   return "Good", "#22c55e", (aqi/50)*16
    if aqi <= 100:  return "Moderate", "#eab308", 16+((aqi-50)/50)*17
    if aqi <= 150:  return "Unhealthy (sensitive)", "#f97316", 33+((aqi-100)/50)*17
    if aqi <= 200:  return "Unhealthy", "#ef4444", 50+((aqi-150)/50)*17
    if aqi <= 300:  return "Very Unhealthy", "#a855f7", 67+((aqi-200)/100)*16
    return "Hazardous", "#7c3aed", 83+((aqi-300)/200)*17

def mosquito_alert(temp, humidity):
    if temp >= 25 and humidity >= 70:
        return "🦟 High", "#ef4444", "Warm + humid — peak activity. Use repellent after sunset."
    if temp >= 20 and humidity >= 55:
        return "🦟 Moderate", "#f97316", "Some mosquito activity. Take evening precautions."
    return "🦟 Low", "#22c55e", "Unfavorable conditions for mosquitoes."

def stargazing_score(cloud_cover, aqi, condition):
    c = condition.lower()
    if any(x in c for x in ["rain","storm","snow","fog","drizzle"]):
        return 0, "❌ Not tonight", "#64748b", "Sky is blocked by weather."
    score = max(0, 100 - cloud_cover - (min(aqi//5, 30) if aqi else 0))
    if score >= 75: return score, "⭐ Excellent", "#a855f7", "Perfect clear skies — get your telescope out!"
    if score >= 50: return score, "🌟 Good", "#8b5cf6", "Good visibility, catch most stars tonight."
    if score >= 25: return score, "🌤️ Fair", "#6366f1", "Partly cloudy — bright stars visible."
    return score, "☁️ Poor", "#64748b", "Too much cloud cover tonight."

def outdoor_sports_score(temp, wind, aqi, condition):
    c = condition.lower()
    if any(x in c for x in ["storm","violent","blizzard"]):
        return 0, "🚫 Dangerous", "#ef4444", "Severe weather — stay inside."
    score = 100
    if temp > 38 or temp < 0: score -= 50
    elif temp > 33 or temp < 5: score -= 25
    elif 18 <= temp <= 28: score += 10
    if wind > 60: score -= 40
    elif wind > 40: score -= 20
    elif wind > 25: score -= 10
    if aqi:
        if aqi > 150: score -= 40
        elif aqi > 100: score -= 20
        elif aqi > 50: score -= 10
    if any(x in c for x in ["rain","snow","drizzle"]): score -= 30
    if "fog" in c: score -= 15
    score = max(0, min(score, 100))
    if score >= 75: return score, "🏃 Great", "#22c55e", "Go for it — excellent conditions!"
    if score >= 55: return score, "👍 Good", "#84cc16", "Good to go. Stay hydrated."
    if score >= 35: return score, "😐 Moderate", "#eab308", "Manageable. Keep sessions short."
    if score >= 15: return score, "⚠️ Poor", "#f97316", "Tough conditions — consider indoors."
    return score, "🚫 Avoid", "#ef4444", "Not recommended today."

def fmt_time(iso_str):
    try:
        return datetime.fromisoformat(iso_str).strftime("%I:%M %p")
    except Exception:
        return iso_str

# ── UI ──
st.markdown("<div class='app-title'>WeatherSense 🌤️</div>", unsafe_allow_html=True)
st.markdown("<div class='app-sub'>your personal weather intelligence</div>", unsafe_allow_html=True)

if st.session_state.favorites:
    st.markdown("<div class='fav-bar'>", unsafe_allow_html=True)
    st.markdown("<div class='fav-lbl'>⭐ Saved Cities</div>", unsafe_allow_html=True)
    fcols = st.columns(min(len(st.session_state.favorites), 4))
    for i, fav in enumerate(st.session_state.favorites[:4]):
        with fcols[i]:
            if st.button(fav, key=f"fav_{i}", use_container_width=True):
                st.session_state.selected_city = fav
    st.markdown("</div>", unsafe_allow_html=True)

city = st.text_input("City", value=st.session_state.selected_city,
                     placeholder="Search city...", label_visibility="collapsed")

c1, c2, c3 = st.columns([4, 1.1, 1.1])
with c1:
    search = st.button("🔍  Search", use_container_width=True)
with c2:
    save = st.button("⭐ Save", use_container_width=True)
with c3:
    if st.button("🗑️", use_container_width=True):
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
        st.warning("Enter a city first.")

if search:
    if not city.strip():
        st.warning("Enter a city name.")
    else:
        try:
            lat, lon, place, country = get_coordinates(city)
            if lat is None:
                st.error("City not found — check spelling.")
            else:
                with st.spinner(""):
                    data = get_weather(lat, lon)
                    aqi_val, pm25 = get_aqi(lat, lon)

                cw         = data["current_weather"]
                cond, emoji, color = code_to_info(cw["weathercode"])
                outfit     = get_outfit(cond, cw["temperature"])
                humidity   = data["hourly"]["relativehumidity_2m"][0]
                feels_like = data["hourly"]["apparent_temperature"][0]
                pressure   = round(data["hourly"]["surface_pressure"][0])
                visibility = round(data["hourly"]["visibility"][0] / 1000, 1)
                cloud_cover= data["hourly"]["cloudcover"][0]
                wind       = cw["windspeed"]
                wind_deg   = cw.get("winddirection", 0)
                wind_dir   = wind_direction(wind_deg)

                # ── HERO CARD ──
                st.markdown(f"""
                <div class="card" style="border-top: 2px solid {color}40; text-align:center;">
                    <div class="hero-wrap">
                        <div class="hero-emoji">{emoji}</div>
                        <div class="hero-temp">{cw['temperature']}°</div>
                        <div class="hero-cond">{cond}</div>
                        <div class="hero-place">{place}, {country}</div>
                        <div class="outfit-badge">{outfit}</div>
                    </div>
                    <div class="stat-row">
                        <span class="stat-pill">🌡️ Feels {feels_like}°C</span>
                        <span class="stat-pill">💧 {humidity}%</span>
                        <span class="stat-pill">💨 {wind} km/h</span>
                        <span class="stat-pill">🔵 {pressure} hPa</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── ALERTS ──
                alerts = get_alerts(cond, cw["temperature"], wind, aqi_val)
                if alerts:
                    st.markdown("<div class='sec-label'>⚠️ Active Alerts</div>", unsafe_allow_html=True)
                    for title, body, col in alerts:
                        st.markdown(f"""
                        <div class="alert-card" style="border-left-color:{col};">
                            <div class="alert-title" style="color:{col};">{title}</div>
                            <div class="alert-body">{body}</div>
                        </div>""", unsafe_allow_html=True)

                # ── COMPASS + SUN in 2 cols ──
                st.markdown("<div class='sec-label'>Wind & Sun</div>", unsafe_allow_html=True)
                left, right = st.columns(2)

                with left:
                    needle_rotate = wind_deg
                    st.markdown(f"""
                    <div class="card-mini">
                        <div class="insight-lbl">🧭 Compass</div>
                        <div class="compass-wrap">
                            <div class="compass-ring">
                                <span class="compass-label compass-n">N</span>
                                <span class="compass-label compass-s">S</span>
                                <span class="compass-label compass-e">E</span>
                                <span class="compass-label compass-w">W</span>
                                <div class="compass-needle-wrap" style="transform:translate(-50%,-50%) rotate({needle_rotate}deg);">
                                    <div class="compass-north"></div>
                                    <div class="compass-south"></div>
                                </div>
                                <div class="compass-dot"></div>
                            </div>
                            <div class="compass-dir-label">{wind_dir}</div>
                            <div class="compass-speed">{wind} km/h</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with right:
                    sunrise_fmt = fmt_time(data["daily"]["sunrise"][0])
                    sunset_fmt  = fmt_time(data["daily"]["sunset"][0])
                    st.markdown(f"""
                    <div class="card-mini" style="height:100%;">
                        <div class="insight-lbl">🌅 Sun Times</div>
                        <div class="sun-row" style="margin-top:.8rem;">
                            <div class="sun-item">
                                <div class="sun-icon">🌄</div>
                                <div class="sun-lbl">Sunrise</div>
                                <div class="sun-time">{sunrise_fmt}</div>
                            </div>
                            <div class="sun-divider"></div>
                            <div class="sun-item">
                                <div class="sun-icon">🌇</div>
                                <div class="sun-lbl">Sunset</div>
                                <div class="sun-time">{sunset_fmt}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── AQI ──
                aqi_text, aqi_color, dot_pct = aqi_label(aqi_val)
                st.markdown("<div class='sec-label'>🌬️ Air Quality</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:.3rem;">
                        <div>
                            <div style="font-size:2rem;font-weight:800;color:{aqi_color};line-height:1;">{aqi_val if aqi_val else 'N/A'}</div>
                            <div style="font-size:.82rem;color:{aqi_color};font-weight:600;margin-top:.15rem;">{aqi_text}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:.7rem;opacity:.4;text-transform:uppercase;letter-spacing:.06em;">PM2.5</div>
                            <div style="font-size:1.1rem;font-weight:700;">{round(pm25,1) if pm25 else 'N/A'} <span style="font-size:.7rem;opacity:.5;">µg/m³</span></div>
                        </div>
                    </div>
                    <div class="aqi-bar-bg">
                        <div class="aqi-dot" style="left:{min(dot_pct,96)}%;"></div>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:.6rem;opacity:.3;margin-top:.3rem;">
                        <span>Good</span><span>Moderate</span><span>Unhealthy</span><span>Hazardous</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── INSIGHTS GRID ──
                m_label, m_color, m_tip = mosquito_alert(cw["temperature"], humidity)
                sg_score, sg_label, sg_color, sg_tip = stargazing_score(cloud_cover, aqi_val, cond)
                sp_score, sp_label, sp_color, sp_tip = outdoor_sports_score(cw["temperature"], wind, aqi_val, cond)

                st.markdown("<div class='sec-label'>📊 Insights</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="insight-grid">
                    <div class="card-mini">
                        <div class="insight-lbl">👁️ Visibility</div>
                        <div class="insight-val">{visibility} km</div>
                        <div class="insight-sub">{"Crystal clear" if visibility >= 10 else "Reduced" if visibility >= 4 else "Very poor"}</div>
                    </div>
                    <div class="card-mini">
                        <div class="insight-lbl">🦟 Mosquito Risk</div>
                        <div class="insight-val" style="color:{m_color};">{m_label}</div>
                        <div class="insight-sub">{m_tip}</div>
                    </div>
                    <div class="card-mini">
                        <div class="insight-lbl">🔭 Stargazing</div>
                        <div class="insight-val" style="color:{sg_color};font-size:.95rem;">{sg_label}</div>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:{sg_score}%;background:{sg_color};"></div>
                        </div>
                        <div class="insight-sub">{sg_tip}</div>
                    </div>
                    <div class="card-mini">
                        <div class="insight-lbl">⚽ Outdoor Sports</div>
                        <div class="insight-val" style="color:{sp_color};font-size:.95rem;">{sp_label}</div>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:{sp_score}%;background:{sp_color};"></div>
                        </div>
                        <div class="insight-sub">{sp_tip}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── 5-DAY FORECAST ──
                st.markdown("<div class='sec-label'>📅 5-Day Forecast</div>", unsafe_allow_html=True)
                daily  = data["daily"]
                fc2    = st.columns(5)
                for i in range(1, 6):
                    d_name = datetime.strptime(daily["time"][i], "%Y-%m-%d").strftime("%a")
                    hi     = daily["temperature_2m_max"][i]
                    lo     = daily["temperature_2m_min"][i]
                    _, d_emoji, d_color = code_to_info(daily["weathercode"][i])
                    with fc2[i - 1]:
                        st.markdown(
                            f"<div class='card-sm' style='border-top:2px solid {d_color}50;'>"
                            f"<div class='fc-day'>{d_name}</div>"
                            f"<div class='fc-emoji'>{d_emoji}</div>"
                            f"<div class='fc-hi' style='color:{d_color};'>{hi}°</div>"
                            f"<div class='fc-lo'>{lo}°</div>"
                            f"</div>", unsafe_allow_html=True)

        except requests.exceptions.RequestException:
            st.error("Network error — check your connection.")
