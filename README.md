# WeatherSense

A minimalist, real-time weather app built with Python and Streamlit.

![preview](https://img.shields.io/badge/UI-minimal-0A0C10)

## What it does

WeatherSense is a genuine weather application, not a static page:

- **Live data** — current conditions, 24-hour timeline and 7-day forecast from the
  [Open-Meteo](https://open-meteo.com) API (no API key required)
- **City search** — geocoding with alternate-match suggestions, shareable
  `?city=` URLs
- **Location** — one-tap "My location" via IP geolocation
- **Saved cities** — favourites rail with live temperatures, fetched in parallel
- **Air quality** — US AQI, PM2.5 and PM10 with health guidance
- **Safety alerts** — heat, freezing, storms, wind, fog and air-quality warnings
  derived from live conditions
- **Lifestyle insights** — stargazing score, mosquito risk, outdoor-sport
  suitability
- **Sun path** — sunrise/sunset arc with daylight remaining
- **Units** — Celsius / Fahrenheit toggle
- **Auto refresh** — the dashboard re-validates every 45 seconds inside a
  Streamlit fragment, with server-side caching every 5 minutes

## Design

- Zero emoji — every glyph is a purpose-drawn SVG icon (brand mark, weather
  states, UI icons)
- Hairline metric grid, quiet surfaces, one condition-driven accent colour
- Tabular numerals, condensed spacing, mobile-first single column

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure

```
app.py                     entry point & app shell
weather_sense/
  api.py                   Open-Meteo clients, insights, alerts, units
  components.py            render components (hero, rail, forecast, ...)
  icons.py                 SVG icon library (no emoji)
  styles.py                design tokens & CSS
  sample.py                offline fallback (sample data + gazetteer)
```

## Offline behaviour

If the network blocks the weather APIs (locked-down sandboxes, for example),
WeatherSense labels itself **Offline preview** and renders a generated sample
dataset so the UI stays demonstrable. With network access, all data is live.

## Data & attribution

Weather and air-quality data by [Open-Meteo](https://open-meteo.com).
Geocoding by Open-Meteo Geocoding. IP geolocation by [ipwho.is](https://ipwho.is).

## Author

Developed by **Sambit Sway**
[linkedin.com/in/sambit-swain-7032a8378](https://www.linkedin.com/in/sambit-swain-7032a8378)
Aspiring Cloud & DevOps Engineer | Python Enthusiast | Continuous Learner
