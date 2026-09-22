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

## Opening experience

The app opens on a short, deliberate intro instead of a blank frame:

- the **brand mark draws itself** — the cloud stroke is traced with a
  normalised dash animation (`pathLength="1"`), then the sun pops in with a
  spring curve and its rays trace in;
- a **micro loader** runs underneath: two counter-rotating arcs and a shimmer
  bar that completes when the first dataset lands;
- the wordmark and tagline rise in, then the whole card fades out and the
  dashboard is revealed as one clean screen.

The intro is pure CSS (no JavaScript), is skipped on every run after the first
one in a session, and collapses to a static logo for users whose OS asks for
reduced motion.

## Brand mark

"Sky loop" — one continuous cloud stroke with a small sun breaking out above
it. Two strokes, no fill, drawn on a 24×24 grid so the same drawing serves the
16px favicon, the 26px header lock-up and the 78px splash. The geometry is
validated numerically (sampled path bounds, optical centring and minimum
clearance between sun and cloud), so nothing ever touches at any size.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

`.streamlit/config.toml` ships with the repo and makes the app open correctly
in any proxied or embedded environment (Codespaces, GitHub Codespaces preview,
Arena preview, ngrok, tunnels, iframes) without extra flags.

### If the app ever "doesn't open"

Symptom: the browser shows a blank page / infinite *Please wait…* spinner and
the server log says
`Rejecting WebSocket connection with disallowed Origin or Host header`.
That is Streamlit refusing the WebSocket handshake because the page is served
through a proxy host. The shipped config sets:

```toml
[server]
enableCORS = false
enableXsrfProtection = false
```

which is exactly what the devcontainer flags used to pass on the command line.
If you start Streamlit with a custom config, keep those two flags (or the
devcontainer command `streamlit run app.py --server.enableCORS false
--server.enableXsrfProtection false`).

## Robustness

The UI must never blank out, so every layer defends itself:

- **Payload normalisation** (`weather_sense/api.normalize_forecast`) rebuilds
  every API response so all keys exist, numbers are numbers (or `None`), and
  hourly/daily arrays always line up with `time` — a `null` from Open-Meteo can
  never crash a formatter or print a literal `None`.
- **Failures are never cached.** Cached helpers raise `WeatherError` (Streamlit
  does not cache exceptions) and the public wrappers fall back to the offline
  sample dataset, so the app recovers by itself when the network returns.
- **No hangs.** All requests use `(connect, read)` timeouts plus a cached
  connectivity probe, so an offline sandbox paints instantly instead of waiting
  on three timeouts.
- **Error boundary.** Anything that still fails — inside or outside a fragment —
  renders a calm error card with a one-click *Retry* and a collapsible
  traceback, instead of a blank screen or Streamlit's raw red box.
- **Version shims** (`weather_sense/compat.py`) detect widget capabilities at
  import time (`width="stretch"` vs `use_container_width`, `st.segmented_control`,
  `st.fragment`), so an older Streamlit degrades instead of dying.

## Tests

```bash
python -m unittest discover -s tests -v      # or: pytest tests/
```

25 tests cover payload normalisation (including the array-truncation
regression), `None`/`NaN`/string coercion, the brand mark's SVG validity,
splash states, compat shims, and full end-to-end runs of `app.py` through
Streamlit's own harness — search, favourites, unit toggle, `?city=` bootstrap
and the fragment error boundary.

## Design

- Zero emoji — every glyph is a purpose-drawn SVG icon (brand mark, weather
  states, UI icons)
- Hairline metric grid, quiet surfaces, one condition-driven accent colour
- Tabular numerals, condensed spacing, mobile-first single column

## Offline behaviour

If the network blocks the weather APIs (locked-down sandboxes, for example),
WeatherSense labels itself **Offline preview** and renders a generated sample
dataset so the UI stays demonstrable. With network access, all data is live.

## Data & attribution

Weather and air-quality data by [Open-Meteo](https://open-meteo.com).
Geocoding by Open-Meteo Geocoding. IP geolocation by [ipwho.is](https://ipwho.is).

## Structure

```
app.py                     entry point, splash orchestration & error boundary
.streamlit/config.toml     server config (proxy-safe CORS/XSRF, dark theme)
tests/                     regression suite (unittest / pytest)
weather_sense/
  api.py                   Open-Meteo clients, normalisation, insights, alerts
  components.py            render components (splash, hero, rail, forecast, …)
  compat.py                Streamlit version shims
  icons.py                 SVG icon library + brand mark (no emoji)
  styles.py                design tokens, splash animation & CSS
  sample.py                offline fallback (sample data + gazetteer)
```

## Author

Developed by **Sambit Sway**
[linkedin.com/in/sambit-swain-7032a8378](https://www.linkedin.com/in/sambit-swain-7032a8378)
Aspiring Cloud & DevOps Engineer | Python Enthusiast | Continuous Learner
