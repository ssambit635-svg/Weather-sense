"""WeatherSense design system — hairlines, quiet surfaces, one accent.

Every colour in the app comes from a CSS custom property, so the whole UI can be
re-painted at runtime by swapping one token map (:func:`apply_theme`) — no
component re-renders, no duplicated stylesheets:

* **dark** — the original night palette; the condition accent is used as
  authored, on near-black surfaces;
* **light** — warm *cream* surfaces with *beige* elevation, warm ink type and
  the same condition accents, darkened just enough to stay legible on paper
  (:func:`accent_for`).

Tokens that describe a *role* rather than a colour (hairlines, tracks, tints,
the knob, text-on-accent) are tokens too, so nothing in this file hard-codes a
value that only works on one background.
"""

from __future__ import annotations

from typing import Any, Optional

DEFAULT_THEME = "dark"
THEMES = ("dark", "light")
DEFAULT_ACCENT = "#5B8DEF"

# ---------------------------------------------------------------------------
# palettes
# ---------------------------------------------------------------------------
DARK: dict[str, str] = {
    "bg": "#0A0C10",
    "bg-elev": "#10131A",
    "card": "#12151C",
    "card-hi": "#171B24",
    "line": "rgba(255,255,255,.075)",
    "line-strong": "rgba(255,255,255,.13)",
    "text": "#EDEFF4",
    "text-hi": "#FFFFFF",
    "text-2": "rgba(237,239,244,.62)",
    "text-3": "rgba(237,239,244,.38)",
    "on-text": "#0B0D12",
    "track": "rgba(255,255,255,.07)",
    "tint": "rgba(255,255,255,.05)",
    "tint-strong": "rgba(255,255,255,.22)",
    "good": "#34C759",
    "good-soft": "#7BC96F",
    "warn": "#E5B83E",
    "warn-soft": "#F08C2E",
    "bad": "#EF5B5B",
    "neutral": "#8B97A8",
    "violet": "#8B7CF6",
    "purple": "#A45BF0",
    "purple-deep": "#8B4BF0",
    "precip": "#6EA8FE",
    "knob": "#FFFFFF",
    "shadow": "rgba(0,0,0,.45)",
    "logo-from": "#8CC4FF",
    "logo-to": "#4F8CF7",
    "wash": "9%",
}

# cream + beige: warm paper surfaces, warm ink, no pure black anywhere
LIGHT: dict[str, str] = {
    "bg": "#FAF6EE",
    "bg-elev": "#F3EADC",
    "card": "#FFFCF6",
    "card-hi": "#F7EFE1",
    "line": "rgba(74,58,36,.14)",
    "line-strong": "rgba(74,58,36,.26)",
    "text": "#241E15",
    "text-hi": "#120E08",
    "text-2": "rgba(36,30,21,.70)",
    "text-3": "rgba(36,30,21,.50)",
    "on-text": "#FFFCF6",
    "track": "rgba(74,58,36,.10)",
    "tint": "rgba(74,58,36,.05)",
    "tint-strong": "rgba(74,58,36,.26)",
    "good": "#177A3C",
    "good-soft": "#2F7D3A",
    "warn": "#8F6209",
    "warn-soft": "#A3560A",
    "bad": "#C0392B",
    "neutral": "#5F6B7E",
    "violet": "#4B3BC8",
    "purple": "#7A2FD0",
    "purple-deep": "#6A28C0",
    "precip": "#2F6FC4",
    "knob": "#FFFFFF",
    "shadow": "rgba(74,58,36,.20)",
    "logo-from": "#5C9AEB",
    "logo-to": "#1C58B4",
    "wash": "13%",
}

PALETTES: dict[str, dict[str, str]] = {"dark": DARK, "light": LIGHT}

# how strongly the *soft* accent tint is applied, per palette
_SOFT_ALPHA = {"dark": "29", "light": "1F"}

# ---------------------------------------------------------------------------
# colour maths — only needed to tune the condition accent per palette
# ---------------------------------------------------------------------------


def parse_hex(value: Any) -> Optional[tuple[int, int, int]]:
    """``#RGB``/``#RRGGBB`` -> (r, g, b); ``None`` for anything else."""
    if not isinstance(value, str):
        return None
    raw = value.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        return None
    try:
        return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    except ValueError:
        return None


def to_hex(rgb: tuple[float, float, float]) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb)


def rgb_to_hsl(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (c / 255 for c in rgb)
    hi, lo = max(r, g, b), min(r, g, b)
    l = (hi + lo) / 2
    if hi == lo:
        return 0.0, 0.0, l
    d = hi - lo
    s = d / (2 - hi - lo) if l > 0.5 else d / (hi + lo)
    if hi == r:
        h = ((g - b) / d) % 6
    elif hi == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h / 6, s, l


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[float, float, float]:
    def channel(p: float, q: float, t: float) -> float:
        t = t % 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    if s == 0:
        return l * 255, l * 255, l * 255
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    return tuple(channel(p, q, h + off) * 255 for off in (1 / 3, 0, -1 / 3))  # type: ignore[return-value]


def _relative_luminance(rgb: tuple[float, float, float]) -> float:
    def channel(value: float) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    """WCAG contrast ratio between two RGB colours (1.0 … 21.0)."""
    la, lb = _relative_luminance(a), _relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# accents are used as graphics (icons, arcs, hairlines, needles) on cream;
# WCAG asks for 3:1 there, we hold 3.6 so they stay crisp, not muddy.
_LIGHT_MIN_CONTRAST = 3.6
_LIGHT_MIN_LIGHTNESS = 0.30


def accent_soft(hex_color: str, theme: str = DEFAULT_THEME) -> str:
    """Translucent wash of the accent, tuned per palette."""
    rgb = parse_hex(hex_color)
    if rgb is None:
        return "rgba(91,141,239,.16)"
    alpha = _SOFT_ALPHA.get(theme, _SOFT_ALPHA[DEFAULT_THEME])
    return to_hex(rgb) + alpha


def accent_for(hex_color: str, theme: str = DEFAULT_THEME) -> str:
    """Condition accent, tuned for the palette it will sit on.

    Dark surfaces take the colour exactly as authored — it was drawn for them.
    Cream is twelve times brighter than near-black, so the same hue is walked
    down in lightness until it clears :data:`_LIGHT_MIN_CONTRAST` against the
    page (the hue and chroma are preserved: a sunny amber stays amber, it just
    stops glowing).
    """
    rgb = parse_hex(hex_color)
    if rgb is None:
        return DEFAULT_ACCENT
    if theme != "light":
        return to_hex(rgb)

    hue, sat, light = rgb_to_hsl(rgb)
    sat = min(1.0, sat * 1.05)
    page = parse_hex(PALETTES["light"]["bg"]) or (250, 246, 238)
    candidate = min(light, 0.46)
    while candidate > _LIGHT_MIN_LIGHTNESS:
        tuned = hsl_to_rgb(hue, sat, candidate)
        if contrast_ratio(tuned, page) >= _LIGHT_MIN_CONTRAST:
            return to_hex(tuned)
        candidate -= 0.01
    return to_hex(hsl_to_rgb(hue, sat, _LIGHT_MIN_LIGHTNESS))


# ---------------------------------------------------------------------------
# theme plumbing
# ---------------------------------------------------------------------------


def current_theme() -> str:
    """The palette the session is on (falls back to the default)."""
    try:
        import streamlit as st

        theme = st.session_state.get("theme", DEFAULT_THEME)
    except Exception:                     # bare import / tests
        theme = DEFAULT_THEME
    return theme if theme in THEMES else DEFAULT_THEME


def theme_css(theme: str = DEFAULT_THEME, accent: Optional[str] = None) -> str:
    """One ``<style>`` block carrying the palette *and* the condition accent.

    Everything is written to ``:root`` so every surface, widget and icon in the
    app — including Streamlit's own chrome — follows in a single swap.
    """
    tokens = dict(PALETTES.get(theme, DARK))
    accent = accent or DEFAULT_ACCENT
    tokens["accent"] = accent_for(accent, theme)
    tokens["accent-soft"] = accent_soft(tokens["accent"], theme)
    scheme = "light" if theme == "light" else "dark"

    body = "\n".join(f"  --{name}: {value};" for name, value in tokens.items())
    return (
        "<style>\n"
        f":root {{\n{body}\n  color-scheme: {scheme};\n}}\n"
        f"html, body {{ background: {tokens['bg']} !important; color-scheme: {scheme}; }}\n"
        "</style>"
    )


def apply_theme(theme: Optional[str] = None, accent: Optional[str] = None) -> None:
    """Paint the active palette (and accent) into the document."""
    import streamlit as st

    st.markdown(theme_css(theme or current_theme(), accent), unsafe_allow_html=True)


def set_accent(hex_color: str) -> None:
    """Re-paint the condition accent, keeping the palette the user chose."""
    apply_theme(None, hex_color)


# ---------------------------------------------------------------------------
# the stylesheet (structure only — every value is a token)
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ── tokens: defaults for the dark palette; apply_theme() overrides them ── */
:root {
  --bg: #0A0C10;
  --bg-elev: #10131A;
  --card: #12151C;
  --card-hi: #171B24;
  --line: rgba(255,255,255,.075);
  --line-strong: rgba(255,255,255,.13);
  --text: #EDEFF4;
  --text-hi: #FFFFFF;
  --text-2: rgba(237,239,244,.62);
  --text-3: rgba(237,239,244,.38);
  --on-text: #0B0D12;
  --track: rgba(255,255,255,.07);
  --tint: rgba(255,255,255,.05);
  --tint-strong: rgba(255,255,255,.22);
  --accent: #5B8DEF;
  --accent-soft: rgba(91,141,239,.16);
  --good: #34C759;
  --good-soft: #7BC96F;
  --warn: #E5B83E;
  --warn-soft: #F08C2E;
  --bad: #EF5B5B;
  --neutral: #8B97A8;
  --violet: #8B7CF6;
  --purple: #A45BF0;
  --purple-deep: #8B4BF0;
  --precip: #6EA8FE;
  --knob: #FFFFFF;
  --shadow: rgba(0,0,0,.45);
  --logo-from: #8CC4FF;
  --logo-to: #4F8CF7;
  --wash: 9%;
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
    radial-gradient(1100px 500px at 50% -160px, color-mix(in srgb, var(--accent) var(--wash), transparent), transparent 70%),
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

/* palette swaps should glide, never flash */
[data-testid="stAppViewContainer"], .stApp, .ws-header, .panel, .metrics, .metric,
.days, .day, .rail-wrap, .insight, .alert, .notice, .ws-fatal, .empty, .compass .ring,
.range, .aqi-bar, .aqi-knob, .fav, .sec-title, .hero-temp, .hero-cond, .metric-val,
.caption, [data-testid="stTextInput"] input, .stAlert, .ws-foot {
  transition: background-color .28s ease, border-color .28s ease,
              color .28s ease, box-shadow .28s ease;
}

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
.ws-logo, .ws-logo-tile { display: block; flex-shrink: 0; }
.ws-anchor { display: none; }
/* the brand mark's gradient follows the palette (CSS beats the stop attribute) */
.ws-stop-from { stop-color: var(--logo-from); }
.ws-stop-to { stop-color: var(--logo-to); }

/* search field sits flush against the action row */
div[data-testid="stTextInput"] { margin-bottom: 0 !important; }

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
/* primary = ink pill on the current canvas */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-primary"],
button[data-testid="baseButton-primary"] {
  background: var(--text) !important;
  color: var(--on-text) !important;
  border-color: transparent !important;
}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
  background: var(--text-hi) !important;
  color: var(--on-text) !important;
  border-color: transparent !important;
}

/* ── the two view settings: unit pill + theme pill ── */
[data-testid="stColumn"]:has(.ws-anchor) [data-testid="stButton"],
[data-testid="column"]:has(.ws-anchor) [data-testid="stButton"] { width: 100%; }
[data-testid="stColumn"]:has(.ws-anchor) button,
[data-testid="column"]:has(.ws-anchor) button {
  position: relative !important;
  width: 100% !important;
  height: 34px !important; min-height: 34px !important;
  padding: 0 12px !important;
  border-radius: 999px !important;
  background: var(--card) !important;
  border: 1px solid var(--line) !important;
  color: var(--text-2) !important;
  font-size: .77rem !important; font-weight: 600 !important;
  letter-spacing: .01em !important;
  transition: color .16s, border-color .16s, background-color .16s !important;
}
[data-testid="stColumn"]:has(.ws-anchor) button:hover,
[data-testid="column"]:has(.ws-anchor) button:hover {
  background: var(--card-hi) !important;
  border-color: var(--line-strong) !important;
  color: var(--text) !important;
}
/* the theme pill carries a sun/moon mask that follows currentColor */
[data-testid="stColumn"]:has(.ws-theme-anchor) button,
[data-testid="column"]:has(.ws-theme-anchor) button {
  padding-left: 33px !important;
  justify-content: flex-start !important;
  text-align: left !important;
}
[data-testid="stColumn"]:has(.ws-theme-anchor) button p,
[data-testid="column"]:has(.ws-theme-anchor) button p { text-align: left !important; }
[data-testid="stColumn"]:has(.ws-theme-anchor) button::before,
[data-testid="column"]:has(.ws-theme-anchor) button::before {
  content: ''; position: absolute; left: 13px; top: 50%;
  width: 14px; height: 14px; margin-top: -7px;
  background-color: currentColor; opacity: .82;
  -webkit-mask: var(--ws-mode-icon) center / contain no-repeat;
  mask: var(--ws-mode-icon) center / contain no-repeat;
  transition: transform .5s cubic-bezier(.3,1.4,.5,1), opacity .2s;
}
[data-testid="stColumn"]:has(.ws-theme-anchor) button:hover::before,
[data-testid="column"]:has(.ws-theme-anchor) button:hover::before {
  transform: rotate(22deg) scale(1.05); opacity: 1;
}
[data-testid="stColumn"]:has(.ws-go-light) button::before,
[data-testid="column"]:has(.ws-go-light) button::before { --ws-mode-icon: __ICON_SUN__; }
[data-testid="stColumn"]:has(.ws-go-dark) button::before,
[data-testid="column"]:has(.ws-go-dark) button::before { --ws-mode-icon: __ICON_MOON__; }

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
.rail-p { font-size: .6rem; color: var(--precip); font-variant-numeric: tabular-nums; min-height: .8em; }
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
.day-pop { font-size: .66rem; color: var(--precip); text-align: right; font-variant-numeric: tabular-nums; }
.day-lo, .day-hi {
  font-size: .84rem; font-weight: 600; font-variant-numeric: tabular-nums;
  text-align: center;
}
.day-lo { color: var(--text-3); }
.day-hi { color: var(--text); }
.range {
  position: relative; height: 4px; border-radius: 99px;
  background: var(--track);
}
.range .fill {
  position: absolute; top: 0; bottom: 0; border-radius: 99px;
  background: linear-gradient(90deg, var(--precip), var(--accent));
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
  background: linear-gradient(90deg, var(--good), var(--warn), var(--warn-soft),
              var(--bad), var(--purple), var(--purple-deep));
  opacity: .95;
}
.aqi-knob {
  position: absolute; top: 50%; width: 13px; height: 13px; border-radius: 50%;
  background: var(--knob); border: 3px solid var(--bg-elev);
  transform: translate(-50%, -50%);
  box-shadow: 0 1px 6px var(--shadow);
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
  height: 3px; background: var(--track);
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
  background: radial-gradient(circle at 50% 40%, var(--tint), transparent 70%);
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
  border-top: 18px solid var(--tint-strong);
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

/* streamlit's own chrome, re-skinned from the tokens so it survives any palette */
.stAlert { border-radius: var(--radius-sm) !important; font-size: .8rem !important; }
div[data-testid="stAlert"], div[data-testid="stAlertContainer"] {
  background: var(--card) !important;
  border: 1px solid var(--line-strong) !important;
  color: var(--text-2) !important;
}
div[data-testid="stAlert"] p { color: var(--text-2) !important; }
/* the alert glyph keeps Streamlit's semantic colour — it reads on both palettes */
div[data-testid="stNotificationContent"] {
  background: var(--card) !important;
  border: 1px solid var(--line-strong) !important;
}
div[data-testid="stExpander"] details { background: var(--card) !important; border-color: var(--line) !important; }
div[data-testid="stExpander"] summary { color: var(--text-2) !important; font-size: .8rem !important; }
div[data-testid="stExpander"] summary svg { fill: var(--text-2) !important; }
pre, code, div[data-testid="stCode"] {
  background: var(--bg-elev) !important;
  color: var(--text-2) !important;
}
div[data-testid="stSpinner"] div, div[data-testid="stSpinner"] p { color: var(--text-2) !important; }
div[data-testid="stSpinner"] svg { color: var(--accent) !important; }
div[data-testid="stCaptionContainer"] p, .stCaption { color: var(--text-3) !important; }
div[data-baseweb="tooltip"] > div {
  background: var(--text) !important;
  color: var(--bg) !important;
  font-family: var(--font) !important;
  font-size: .72rem !important;
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

/* ── opening splash: brand mark draws itself, loader spins ── */
.ws-splash {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 1rem; min-height: 56vh; padding: 3.6rem 1rem 3rem; text-align: center;
}
.ws-splash-badge {
  position: relative; display: inline-flex;
  align-items: center; justify-content: center;
}
/* soft accent halo breathing behind the mark */
.ws-splash-badge::before {
  content: ''; position: absolute; inset: -26px; border-radius: 50%;
  background: radial-gradient(circle,
              color-mix(in srgb, var(--accent) 30%, transparent), transparent 68%);
  filter: blur(8px); opacity: .6;
  animation: ws-halo 2.8s ease-in-out infinite;
}
@keyframes ws-halo {
  0%, 100% { opacity: .45; transform: scale(.92); }
  50%      { opacity: .9;  transform: scale(1.07); }
}
.ws-splash-badge .ws-logo { position: relative; z-index: 1; }

/* stroke draw-in (paths carry pathLength="1" when animated) */
.ws-logo-anim .ws-logo-cloud {
  stroke-dasharray: 1; stroke-dashoffset: 1;
  animation: ws-draw 1.25s cubic-bezier(.62,.02,.34,1) .12s forwards;
}
.ws-logo-anim .ws-logo-rays {
  stroke-dasharray: 1; stroke-dashoffset: 1;
  animation: ws-draw .55s ease-out 1.02s forwards;
}
.ws-logo-anim .ws-logo-sun {
  transform-box: fill-box; transform-origin: center;
  opacity: 0; animation: ws-pop .8s cubic-bezier(.34,1.52,.5,1) .58s forwards;
}
@keyframes ws-draw { to { stroke-dashoffset: 0; } }
@keyframes ws-pop {
  0%   { opacity: 0; transform: scale(.35) rotate(-18deg); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); }
}

.ws-word {
  font-family: var(--font-display); font-size: 1.14rem; font-weight: 600;
  letter-spacing: .34em; text-indent: .34em; color: var(--text);
  opacity: 0; animation: ws-rise .7s ease .3s forwards;
}
.ws-tag {
  font-size: .63rem; letter-spacing: .18em; text-transform: uppercase;
  color: var(--text-3); opacity: 0; animation: ws-rise .7s ease .5s forwards;
}
@keyframes ws-rise {
  from { opacity: 0; transform: translateY(7px); }
  to   { opacity: 1; transform: none; }
}

/* the loader itself: counter-rotating arcs + a sliding shimmer bar */
.ws-loader { display: flex; align-items: center; gap: .6rem; height: 22px; }
.ws-ring { display: block; }
.ws-ring-track { stroke: var(--track); }
.ws-ring-a, .ws-ring-b { transform-box: fill-box; transform-origin: center; }
.ws-ring-a { stroke: var(--accent); animation: ws-spin 1.15s linear infinite; }
.ws-ring-b { stroke: var(--tint-strong); animation: ws-spin 1.9s linear infinite reverse; }
@keyframes ws-spin { to { transform: rotate(360deg); } }

.ws-status {
  font-size: .66rem; font-weight: 600; letter-spacing: .18em;
  text-transform: uppercase; color: var(--text-3);
}
.ws-dots i { font-style: normal; opacity: .18; animation: ws-dot 1.4s infinite; }
.ws-dots i:nth-child(2) { animation-delay: .18s; }
.ws-dots i:nth-child(3) { animation-delay: .36s; }
@keyframes ws-dot { 0%, 60%, 100% { opacity: .18; } 30% { opacity: 1; } }

.ws-bar {
  position: relative; width: 152px; height: 2px; border-radius: 99px;
  background: var(--track); overflow: hidden;
}
.ws-bar i {
  position: absolute; top: 0; bottom: 0; left: 0; width: 42%;
  border-radius: 99px; transition: width .3s ease, background .3s ease;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  animation: ws-slide 1.25s cubic-bezier(.45,0,.55,1) infinite;
}
@keyframes ws-slide {
  0%   { transform: translateX(-115%); }
  100% { transform: translateX(345%); }
}
/* data landed: bar completes, loader holds still, card fades away */
.ws-splash.ws-ready .ws-bar i {
  width: 100%; animation: none;
  background: color-mix(in srgb, var(--accent) 70%, transparent);
}
.ws-splash.ws-ready .ws-ring-a, .ws-splash.ws-ready .ws-ring-b { animation: none; }
.ws-splash.ws-ready .ws-status { color: var(--text-2); }
.ws-splash.ws-out { animation: ws-fade-out .42s cubic-bezier(.4,0,.2,1) forwards; }
@keyframes ws-fade-out {
  to { opacity: 0; transform: translateY(-9px) scale(.988); filter: blur(2px); }
}

/* ── fatal-error card (replaces a blank screen / raw traceback) ── */
.ws-fatal {
  background: var(--card); border: 1px solid var(--line);
  border-left: 2px solid var(--bad); border-radius: var(--radius);
  padding: 1.1rem 1.15rem; margin-top: 1rem;
}
.ws-fatal .ttl {
  display: flex; align-items: center; gap: .5rem;
  font-size: .95rem; font-weight: 650; color: var(--text);
}
.ws-fatal .ttl svg { color: var(--bad); }
.ws-fatal .body { font-size: .78rem; color: var(--text-2); line-height: 1.55; margin-top: .45rem; }
.ws-fatal code {
  display: inline-block; margin-top: .5rem; padding: .18rem .4rem;
  background: var(--tint); border-radius: 6px;
  font-size: .72rem; color: var(--text);
}

/* honour the OS "reduce motion" setting everywhere */
@media (prefers-reduced-motion: reduce) {
  .hero-icon, .live-dot, .ws-splash-badge::before,
  .ws-ring-a, .ws-ring-b, .ws-bar i, .ws-dots i { animation: none !important; }
  .ws-logo-anim .ws-logo-cloud, .ws-logo-anim .ws-logo-rays {
    stroke-dashoffset: 0 !important; animation: none !important;
  }
  .ws-logo-anim .ws-logo-sun, .ws-word, .ws-tag { opacity: 1 !important; animation: none !important; }
  .ws-splash.ws-out { animation: none !important; opacity: 0 !important; }
  [data-testid="stColumn"]:has(.ws-theme-anchor) button::before { transition: none !important; }
}

/* narrow phones */
@media (max-width: 480px) {
  /* keep the "Light mode" pill legible when the row gets cramped */
  [data-testid="stColumn"]:has(.ws-anchor) button,
  [data-testid="column"]:has(.ws-anchor) button {
    font-size: .72rem !important;
    padding-left: 10px !important; padding-right: 9px !important;
  }
  [data-testid="stColumn"]:has(.ws-theme-anchor) button,
  [data-testid="column"]:has(.ws-theme-anchor) button { padding-left: 28px !important; }
  [data-testid="stColumn"]:has(.ws-theme-anchor) button::before,
  [data-testid="column"]:has(.ws-theme-anchor) button::before { left: 10px; width: 13px; height: 13px; margin-top: -6.5px; }
}

@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] { padding: 1rem .85rem 4rem !important; }
  .insights { grid-template-columns: 1fr; }
  .day { grid-template-columns: 46px 24px 34px 1fr 40px; gap: .5rem; padding: .7rem .8rem; }
  .ws-splash { min-height: 48vh; padding: 2.6rem .8rem 2.2rem; gap: .85rem; }
  .ws-word { font-size: 1rem; letter-spacing: .28em; text-indent: .28em; }
  .ws-bar { width: 128px; }
}
</style>
"""


def stylesheet() -> str:
    """CSS with the sun/moon mask data URIs resolved from the icon set."""
    from weather_sense.icons import symbol_uri

    sun = symbol_uri("sun", stroke=1.9)
    moon = symbol_uri("moon", stroke=1.9)
    return (
        CSS.replace("__ICON_SUN__", f'url("{sun}")')
        .replace("__ICON_MOON__", f'url("{moon}")')
    )


def inject() -> None:
    """Static structure CSS (palette-independent)."""
    import streamlit as st

    st.markdown(stylesheet(), unsafe_allow_html=True)
