"""WeatherSense design system — hairlines, quiet surfaces, one accent."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ── tokens ── */
:root {
  --bg: #0A0C10;
  --bg-elev: #10131A;
  --card: #12151C;
  --card-hi: #171B24;
  --line: rgba(255,255,255,.075);
  --line-strong: rgba(255,255,255,.13);
  --text: #EDEFF4;
  --text-2: rgba(237,239,244,.62);
  --text-3: rgba(237,239,244,.38);
  --accent: #5B8DEF;
  --accent-soft: rgba(91,141,239,.16);
  --good: #34C759;
  --warn: #E5B83E;
  --bad: #EF5B5B;
  --radius: 16px;
  --radius-sm: 11px;
  --font: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --font-display: 'Space Grotesk', 'Inter', system-ui, sans-serif;
}

/* ── app chrome ── */
html, body { background: var(--bg) !important; }
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp {
  background:
    radial-gradient(1100px 500px at 50% -160px, color-mix(in srgb, var(--accent) 9%, transparent), transparent 70%),
    var(--bg) !important;
  font-family: var(--font) !important;
  color: var(--text) !important;
}
[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
#MainMenu, footer { visibility: hidden !important; }
[data-testid="stStatusWidget"] { display: none !important; }
section[data-testid="stMain"] { background: transparent !important; }
[data-testid="stMainBlockContainer"] {
  max-width: 640px !important;
  padding: 1.4rem 1.2rem 5rem !important;
}

/* streamlit element spacing tuned tight */
.block-container { padding-top: 1.2rem !important; }
.block-container > div { margin-bottom: 0 !important; }
div[data-testid="stVerticalBlock"] > div:has(> .ws-gap) { margin: 0 !important; }

/* ── typography helpers ── */
.ws-gap-sm { height: .55rem; }
.ws-gap { height: .9rem; }
.ws-gap-lg { height: 1.4rem; }
.sec-title {
  display: flex; align-items: center; gap: .5rem;
  font-size: .68rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: .14em; color: var(--text-3);
  margin: 1.7rem 0 .7rem .1rem;
}
.sec-title .ic { opacity: .7; }
.sec-title .spacer { flex: 1; }
.sec-title .aside {
  font-size: .65rem; letter-spacing: .06em; color: var(--text-3);
  text-transform: none; font-weight: 500;
}
.ic, .wic { display: inline-block; vertical-align: -3px; flex-shrink: 0; }

/* ── header ── */
.ws-header {
  display: flex; align-items: center; gap: .6rem;
  padding: .1rem 0 .2rem;
}
.ws-header .brand { display: flex; align-items: center; gap: .55rem; }
.ws-header .name {
  font-family: var(--font-display);
  font-size: 1.02rem; font-weight: 600; letter-spacing: -.01em;
}
.ws-header .meta {
  margin-left: auto; display: flex; align-items: center; gap: .55rem;
  font-size: .72rem; color: var(--text-3); font-variant-numeric: tabular-nums;
}
.live-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--good); display: inline-block; margin-right: .3rem;
  animation: pulse 2.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

/* ── controls ── */
[data-testid="stTextInput"] input {
  background: var(--card) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: .92rem !important;
  height: 44px !important;
  padding: 0 14px !important;
  transition: border-color .15s !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: color-mix(in srgb, var(--accent) 55%, transparent) !important;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 14%, transparent) !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--text-3) !important; }

.stButton > button,
[data-testid="stFormSubmitButton"] > button,
button[data-testid^="baseButton"] {
  font-family: var(--font) !important;
  font-weight: 550 !important;
  font-size: .84rem !important;
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--line) !important;
  background: var(--card) !important;
  color: var(--text-2) !important;
  height: 42px !important;
  transition: all .15s !important;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
button[data-testid^="baseButton"]:hover {
  border-color: var(--line-strong) !important;
  color: var(--text) !important;
  background: var(--card-hi) !important;
}
.stButton > button:disabled,
[data-testid="stFormSubmitButton"] > button:disabled {
  opacity: .45 !important;
  cursor: default !important;
}
/* primary = light pill on dark canvas */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-primary"],
button[data-testid="baseButton-primary"] {
  background: var(--text) !important;
  color: #0B0D12 !important;
  border-color: transparent !important;
}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
  background: #FFFFFF !important;
  color: #000000 !important;
  border-color: transparent !important;
}

/* chips
.chip { display: inline-flex; } */

/* ── hero ── */
.hero { padding: .4rem 0 .2rem; }
.hero-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.hero-icon {
  color: var(--accent);
  filter: drop-shadow(0 6px 24px color-mix(in srgb, var(--accent) 35%, transparent));
  animation: drift 6s ease-in-out infinite;
}
@keyframes drift { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
.hero-temp {
  font-family: var(--font-display);
  font-size: clamp(64px, 16vw, 88px);
  font-weight: 600; line-height: .92; letter-spacing: -.045em;
  color: var(--text);
  font-variant-numeric: tabular-nums;
}
.hero-temp .deg { font-size: .45em; font-weight: 500; vertical-align: .65em; color: var(--text-2); }
.hero-cond {
  font-size: 1.02rem; font-weight: 600; color: var(--text);
  margin-top: .55rem; display: flex; align-items: center; gap: .5rem;
}
.hero-loc {
  display: flex; align-items: center; gap: .35rem;
  font-size: .84rem; color: var(--text-2); margin-top: .3rem;
}
.hero-sub {
  display: flex; gap: .9rem; margin-top: .55rem;
  font-size: .8rem; color: var(--text-3); font-variant-numeric: tabular-nums;
}
.hero-sub b { color: var(--text-2); font-weight: 600; }
.hero-unit { margin-left: auto; }

/* ── generic surface ── */
.panel {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.05rem 1.1rem;
}

/* ── metric grid (hairline) ── */
.metrics {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 1px; background: var(--line);
  border: 1px solid var(--line); border-radius: var(--radius);
  overflow: hidden;
}
.metric { background: var(--card); padding: .95rem 1rem; min-height: 86px; }
.metric-head {
  display: flex; align-items: center; gap: .4rem;
  font-size: .66rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: .1em; color: var(--text-3);
}
.metric-val {
  font-family: var(--font-display);
  font-size: 1.28rem; font-weight: 600; margin-top: .45rem;
  font-variant-numeric: tabular-nums; letter-spacing: -.01em;
}
.metric-val small { font-size: .68em; font-weight: 500; color: var(--text-2); margin-left: .1rem; }
.metric-sub { font-size: .7rem; color: var(--text-3); margin-top: .18rem; }

/* ── alerts ── */
.alert {
  display: flex; gap: .7rem; align-items: flex-start;
  background: var(--card); border: 1px solid var(--line);
  border-left: 2px solid var(--warn);
  border-radius: var(--radius-sm);
  padding: .75rem .85rem; margin-bottom: .5rem;
}
.alert .ttl { font-size: .8rem; font-weight: 650; }
.alert .body { font-size: .74rem; color: var(--text-2); line-height: 1.45; margin-top: .12rem; }

/* ── hourly rail ── */
.rail-wrap {
  border: 1px solid var(--line); border-radius: var(--radius);
  background: var(--card); overflow: hidden;
}
.rail-scroll { overflow-x: auto; scrollbar-width: none; -ms-overflow-style: none; }
.rail-scroll::-webkit-scrollbar { display: none; }
.rail-inner { display: flex; min-width: min-content; padding: .9rem 0 .8rem; }
.rail-col {
  width: 64px; flex: 0 0 64px;
  display: flex; flex-direction: column; align-items: center; gap: .45rem;
  position: relative;
}
.rail-col + .rail-col::before {
  content: ''; position: absolute; left: 0; top: 12%; bottom: 12%;
  width: 1px; background: var(--line);
}
.rail-hr { font-size: .64rem; color: var(--text-3); font-variant-numeric: tabular-nums; letter-spacing: .03em; }
.rail-t { font-size: .82rem; font-weight: 650; font-variant-numeric: tabular-nums; }
.rail-p { font-size: .6rem; color: #6EA8FE; font-variant-numeric: tabular-nums; min-height: .8em; }
.rail-now {
  position: absolute; top: 0; bottom: 0; left: 50%; width: 1px;
  background: color-mix(in srgb, var(--accent) 45%, transparent);
  z-index: 0;
}

/* ── daily rows ── */
.days { border: 1px solid var(--line); border-radius: var(--radius); background: var(--card); overflow: hidden; }
.day {
  display: grid;
  grid-template-columns: 52px 26px 40px 1fr 44px;
  align-items: center; gap: .7rem;
  padding: .72rem 1rem;
}
.day + .day { border-top: 1px solid var(--line); }
.day-name { font-size: .8rem; font-weight: 600; }
.day-name .sub { display: block; font-size: .62rem; color: var(--text-3); font-weight: 500; }
.day-pop { font-size: .66rem; color: #6EA8FE; text-align: right; font-variant-numeric: tabular-nums; }
.day-lo, .day-hi {
  font-size: .84rem; font-weight: 600; font-variant-numeric: tabular-nums;
  text-align: center;
}
.day-lo { color: var(--text-3); }
.day-hi { color: var(--text); }
.range {
  position: relative; height: 4px; border-radius: 99px;
  background: rgba(255,255,255,.07);
}
.range .fill {
  position: absolute; top: 0; bottom: 0; border-radius: 99px;
  background: linear-gradient(90deg, #6EA8FE, var(--accent));
}
.range .dot {
  position: absolute; top: 50%; width: 7px; height: 7px;
  border-radius: 50%; background: var(--text);
  transform: translate(-50%, -50%);
  box-shadow: 0 0 0 2px var(--card);
}

/* ── AQI ── */
.aqi-top { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; }
.aqi-val {
  font-family: var(--font-display); font-size: 1.7rem; font-weight: 650;
  font-variant-numeric: tabular-nums;
}
.aqi-label { font-size: .8rem; font-weight: 600; }
.aqi-advice { font-size: .74rem; color: var(--text-2); line-height: 1.5; margin-top: .5rem; }
.aqi-bar {
  position: relative; height: 5px; border-radius: 99px; margin-top: .85rem;
  background: linear-gradient(90deg, #34C759, #E5B83E, #F08C2E, #EF5B5B, #A45BF0, #8B4BF0);
}
.aqi-knob {
  position: absolute; top: 50%; width: 13px; height: 13px; border-radius: 50%;
  background: #fff; border: 3px solid var(--bg-elev);
  transform: translate(-50%, -50%);
  box-shadow: 0 1px 6px rgba(0,0,0,.5);
}
.aqi-ticks {
  display: flex; justify-content: space-between;
  font-size: .58rem; color: var(--text-3); margin-top: .4rem;
  text-transform: uppercase; letter-spacing: .06em;
}
.pm-row { display: flex; gap: 1.4rem; margin-top: .8rem; padding-top: .8rem; border-top: 1px solid var(--line); }
.pm-row .it { font-size: .7rem; color: var(--text-3); }
.pm-row .it b { display: block; font-size: .95rem; color: var(--text); font-weight: 650; margin-top: .15rem; font-variant-numeric: tabular-nums; }

/* ── sun arc ── */
.sun-wrap { position: relative; padding-top: .4rem; }
.sun-times {
  display: flex; justify-content: space-between; margin-top: .2rem;
  font-size: .74rem; color: var(--text-2); font-variant-numeric: tabular-nums;
}
.sun-times .lbl {
  display: flex; flex-direction: column; gap: .25rem;
  font-size: .62rem; text-transform: uppercase; letter-spacing: .1em; color: var(--text-3);
}
.sun-times .lbl.right { text-align: right; align-items: flex-end; }
.sun-note { text-align: center; font-size: .72rem; color: var(--text-3); margin-top: .35rem; }

/* ── insight cards ── */
.insights { display: grid; grid-template-columns: repeat(3, 1fr); gap: .6rem; }
.insight {
  background: var(--card); border: 1px solid var(--line);
  border-radius: var(--radius); padding: .9rem .85rem;
}
.insight .lbl {
  display: flex; align-items: center; gap: .38rem;
  font-size: .63rem; font-weight: 650; text-transform: uppercase;
  letter-spacing: .1em; color: var(--text-3);
}
.insight .val {
  font-size: .95rem; font-weight: 650; margin-top: .5rem;
  font-family: var(--font-display);
}
.insight .bar {
  height: 3px; background: rgba(255,255,255,.07);
  border-radius: 99px; margin: .5rem 0 .45rem; overflow: hidden;
}
.insight .bar i { display: block; height: 100%; border-radius: 99px; }
.insight .tip { font-size: .66rem; color: var(--text-3); line-height: 1.45; }

/* ── compass ── */
.compass { display: flex; align-items: center; gap: .9rem; }
.compass .ring {
  width: 74px; height: 74px; border-radius: 50%;
  border: 1px solid var(--line-strong);
  position: relative; flex: 0 0 74px;
  background: radial-gradient(circle at 50% 40%, rgba(255,255,255,.04), transparent 70%);
}
.compass .n, .compass .e, .compass .s, .compass .w {
  position: absolute; font-size: .52rem; font-weight: 700; color: var(--text-3);
}
.compass .n { top: 4px; left: 50%; transform: translateX(-50%); color: var(--text-2); }
.compass .s { bottom: 4px; left: 50%; transform: translateX(-50%); }
.compass .e { right: 5px; top: 50%; transform: translateY(-50%); }
.compass .w { left: 5px; top: 50%; transform: translateY(-50%); }
.compass .needle {
  position: absolute; left: 50%; top: 50%; width: 2px; height: 56px;
  transform: translate(-50%, -50%) rotate(var(--deg));
  transition: transform .6s cubic-bezier(.3,1.4,.5,1);
}
.compass .needle::before {
  content: ''; position: absolute; top: 4px; left: 50%; transform: translateX(-50%);
  border-left: 4px solid transparent; border-right: 4px solid transparent;
  border-bottom: 22px solid var(--accent);
}
.compass .needle::after {
  content: ''; position: absolute; bottom: 4px; left: 50%; transform: translateX(-50%);
  border-left: 3px solid transparent; border-right: 3px solid transparent;
  border-top: 18px solid rgba(255,255,255,.22);
}
.compass .hub {
  position: absolute; left: 50%; top: 50%; width: 7px; height: 7px;
  background: var(--text); border-radius: 50%;
  transform: translate(-50%, -50%); z-index: 2;
}
.compass .info .deg { font-family: var(--font-display); font-size: 1.15rem; font-weight: 650; }
.compass .info .sub { font-size: .7rem; color: var(--text-3); margin-top: .2rem; line-height: 1.5; }

/* ── favorites bar ── */
.fav-bar {
  display: flex; align-items: center; gap: .5rem;
  overflow-x: auto; scrollbar-width: none; padding-bottom: .1rem;
}
.fav-bar::-webkit-scrollbar { display: none; }
.fav {
  display: inline-flex; align-items: center; gap: .45rem;
  background: var(--card); border: 1px solid var(--line);
  border-radius: var(--radius-sm); padding: .5rem .7rem;
  font-size: .78rem; color: var(--text-2); cursor: pointer;
  white-space: nowrap; transition: all .15s; flex: 0 0 auto;
}
.fav:hover, .fav.on {
  border-color: color-mix(in srgb, var(--accent) 45%, transparent);
  color: var(--text); background: var(--accent-soft);
}
.fav .t { font-weight: 650; font-variant-numeric: tabular-nums; }

/* ── empty state ── */
.empty {
  text-align: center; padding: 3.2rem 1rem 2.4rem;
}
.empty .mark { display: inline-flex; margin-bottom: 1.1rem; opacity: .95; }
.empty h1 {
  font-family: var(--font-display); font-size: 1.7rem; font-weight: 650;
  letter-spacing: -.02em; margin: 0;
}
.empty p {
  color: var(--text-3); font-size: .88rem; margin: .55rem 0 0;
  line-height: 1.6;
}
.try-row { display: flex; justify-content: center; gap: .5rem; flex-wrap: wrap; margin-top: 1.2rem; }

/* ── notices ── */
.notice {
  display: flex; align-items: flex-start; gap: .55rem;
  font-size: .74rem; line-height: 1.5;
  background: color-mix(in srgb, var(--warn) 8%, var(--card));
  border: 1px solid color-mix(in srgb, var(--warn) 28%, transparent);
  color: var(--text-2);
  border-radius: var(--radius-sm);
  padding: .65rem .8rem; margin-bottom: .8rem;
}
.notice b { color: var(--text); }
.notice.info {
  background: var(--accent-soft);
  border-color: color-mix(in srgb, var(--accent) 35%, transparent);
}

/* success / error streamlit toasts, minimal */
.stAlert { border-radius: var(--radius-sm) !important; font-size: .8rem !important; }
div[data-testid="stNotificationContent"] {
  background: var(--card) !important;
  border: 1px solid var(--line-strong) !important;
}

/* ── footer ── */
.ws-foot {
  margin-top: 2.2rem; padding-top: 1rem;
  border-top: 1px solid var(--line);
  display: flex; justify-content: space-between; gap: 1rem;
  font-size: .68rem; color: var(--text-3);
}
.ws-foot a { color: var(--text-2); text-decoration: none; }
.ws-foot a:hover { color: var(--text); }

/* ── temperature sparkline (inside rail) ── */
.spark { display: block; }

/* misc form helpers */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: transparent !important; border: none !important;
}
[data-testid="stSlider"] { display: none !important; }

/* narrow phones */
@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] { padding: 1rem .85rem 4rem !important; }
  .insights { grid-template-columns: 1fr; }
  .day { grid-template-columns: 46px 24px 34px 1fr 40px; gap: .5rem; padding: .7rem .8rem; }
}
</style>
"""


def inject() -> None:
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def set_accent(hex_color: str) -> None:
    """Paint the condition accent into the CSS variables."""
    import streamlit as st
    st.markdown(
        f"<style>:root{{--accent: {hex_color}; --accent-soft: {hex_color}29; }}</style>",
        unsafe_allow_html=True,
    )
