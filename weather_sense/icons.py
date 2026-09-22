"""Minimal stroke-based SVG icon set + the WeatherSense brand mark.

No emoji anywhere in the app — every glyph is purpose-drawn SVG.

The brand mark ("sky loop") is a single-line cloud with a small sun breaking
out above it: two strokes, no fill, drawn on a 24x24 grid so it scales from a
16px favicon to the 76px splash without a hint of padding drift.
"""

from __future__ import annotations

from urllib.parse import quote

# ---------------------------------------------------------------------------
# Generic UI icons (24x24, stroke style)
# ---------------------------------------------------------------------------
_UI = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "pin": '<path d="M12 21s7-5.1 7-11a7 7 0 1 0-14 0c0 5.9 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
    "locate": '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="1.6"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>',
    "bookmark": '<path d="M7 4h10a1 1 0 0 1 1 1v15l-6-3.6L6 20V5a1 1 0 0 1 1-1Z"/>',
    "bookmark-fill": '<path d="M7 4h10a1 1 0 0 1 1 1v15l-6-3.6L6 20V5a1 1 0 0 1 1-1Z" fill="currentColor" stroke="none"/>',
    "trash": '<path d="M4 7h16M10 7V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2M6.5 7l.8 12a1 1 0 0 0 1 .9h7.4a1 1 0 0 0 1-.9l.8-12M10 11v6M14 11v6"/>',
    "refresh": '<path d="M20 11a8 8 0 0 0-14.1-4.6L4 8.5"/><path d="M4 4v4.5h4.5"/><path d="M4 13a8 8 0 0 0 14.1 4.6L20 15.5"/><path d="M20 20v-4.5h-4.5"/>',
    "star": '<path d="m12 3.6 2.5 5.1 5.6.8-4.1 4 1 5.6-5-2.6-5 2.6 1-5.6-4.1-4 5.6-.8L12 3.6Z"/>',
    "star-fill": '<path d="m12 3.6 2.5 5.1 5.6.8-4.1 4 1 5.6-5-2.6-5 2.6 1-5.6-4.1-4 5.6-.8L12 3.6Z" fill="currentColor" stroke="none"/>',
    "alert": '<path d="M12 4.5 2.8 20h18.4L12 4.5Z"/><path d="M12 10v4.2M12 17.2v.4"/>',
    "thermometer": '<path d="M14 14.8V5a2 2 0 1 0-4 0v9.8a4.5 4.5 0 1 0 4 0Z"/><path d="M12 9.5v6.7"/>',
    "droplet": '<path d="M12 3.5s5.5 5.7 5.5 9.6a5.5 5.5 0 1 1-11 0C6.5 9.2 12 3.5 12 3.5Z"/>',
    "gauge": '<path d="M12 14.5 16 9"/><path d="M4.5 18a9 9 0 1 1 15 0"/><circle cx="12" cy="14.5" r="1.4"/>',
    "eye": '<path d="M2.5 12S6 6.5 12 6.5 21.5 12 21.5 12 18 17.5 12 17.5 2.5 12 2.5 12Z"/><circle cx="12" cy="12" r="2.6"/>',
    "wind": '<path d="M4 8.5h9.5a2.75 2.75 0 1 0-2.6-3.6M4 12.5h14a2.75 2.75 0 1 1-2.6 3.6M4 16.5h6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.2M12 19.3v2.2M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6"/>',
    "uv": '<circle cx="12" cy="12" r="3.6"/><path d="M12 3v2M12 19v2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M3 12h2M19 12h2M5.6 18.4 7 17M17 7l1.4-1.4"/>',
    "umbrella": '<path d="M12 4a8 8 0 0 1 8 7.5H4A8 8 0 0 1 12 4Z"/><path d="M12 11.5V17a2.2 2.2 0 0 0 4.4 0"/>',
    "arrow-up": '<path d="M12 19V5M6.5 10.5 12 5l5.5 5.5"/>',
    "arrow-down": '<path d="M12 5v14M6.5 13.5 12 19l5.5-5.5"/>',
    "sunrise": '<path d="M12 4v5M8.5 7.5 12 4l3.5 3.5"/><path d="M3 18h18M6.5 14.5a5.5 5.5 0 0 1 11 0"/><path d="M7 21h10"/>',
    "sunset": '<path d="M12 9V4M8.5 5.5 12 9l3.5-3.5"/><path d="M3 18h18M6.5 14.5a5.5 5.5 0 0 1 11 0"/><path d="M7 21h10"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "x": '<path d="m6 6 12 12M18 6 6 18"/>',
    "chevron": '<path d="m9 6 6 6-6 6"/>',
    "bug": '<path d="M8 9a4 4 0 0 1 8 0v3a4 4 0 0 1-8 0V9Z"/><path d="M8 10.5H4.5M8 14H4.8M16 10.5h3.5M16 14h3.2M12 9V5M9.5 5.5h5M9 18.5l-1.5 2M15 18.5l1.5 2M8.5 13 6.5 15M15.5 13l2 2M8.5 13l-2-2M15.5 13l2-2"/>',
    "bike": '<circle cx="6" cy="16.5" r="3.5"/><circle cx="18" cy="16.5" r="3.5"/><path d="M6 16.5 9.5 9h4.5l3.5 7.5M9.5 9 8 6h3M12.5 16.5H9.5l3-7.5"/>',
    "layers": '<path d="m12 3.5 8.5 4.5L12 12.5 3.5 8 12 3.5Z"/><path d="m4 12.5 8 4.3 8-4.3M4 16.5l8 4.3 8-4.3"/>',
    "spark": '<path d="m13 2.5-8 11h6l-2 8.5 8.5-12H11l2-7.5Z"/>',
    "map": '<path d="M9 4.5 3.5 6.8v13L9 17.2l6 2.6 5.5-2.3v-13L15 7.1 9 4.5Z"/><path d="M9 4.5v12.7M15 7.1v12.7"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.4 3.8 5.3 3.8 8.5S14.5 18.1 12 20.5c-2.5-2.4-3.8-5.3-3.8-8.5S9.5 5.9 12 3.5Z"/>',
    "wifi-off": '<path d="M3 3l18 18"/><path d="M8.6 15.4a5 5 0 0 1 6.8 0M5 11.8a10 10 0 0 1 4-2.5M19 11.8a10 10 0 0 0-6.6-2.9M2.5 8.2A15 15 0 0 1 9 4.6M21.5 8.2a15 15 0 0 0-4.4-2.6"/><path d="M12 19h.01"/>',
}


def icon(name: str, size: int = 16, cls: str = "", stroke: float = 1.7) -> str:
    """Return an inline <svg> for a UI icon name (empty string if unknown)."""
    body = _UI.get(name)
    if body is None:
        return ""
    cls = (cls or "").strip()
    return (
        f'<svg class="ic {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


# ---------------------------------------------------------------------------
# Weather glyphs — richer, condition-specific marks
# ---------------------------------------------------------------------------
def _cloud_d(cx: float = 12.0, cy: float = 13.5, s: float = 1.0) -> str:
    """Path data for a soft cloud; the arcs close exactly back on the start."""
    return (
        f"M{cx - 6.4 * s:.3f} {cy + 3.6 * s:.3f}h{11.6 * s:.3f}"
        f"a{3.6 * s:.3f} {3.6 * s:.3f} 0 0 0 {0.4 * s:.3f} {-7.15 * s:.3f}"
        f"a{5.1 * s:.3f} {5.1 * s:.3f} 0 0 0 {-9.85 * s:.3f} {-1.7 * s:.3f}"
        f"a{3.9 * s:.3f} {3.9 * s:.3f} 0 0 0 {-2.15 * s:.3f} {8.85 * s:.3f}Z"
    )


def _cloud(cx: float = 12, cy: float = 13.5, s: float = 1.0) -> str:
    """A soft filled/stroked cloud centered around (cx, cy), scale s."""
    return f'<path d="{_cloud_d(cx, cy, s)}"/>'


def _sun_disc(cx: float = 12, cy: float = 12, r: float = 4) -> str:
    import math
    rays = []
    for i in range(8):
        a = math.radians(i * 45)
        x1, y1 = cx + (r + 1.6) * math.cos(a), cy + (r + 1.6) * math.sin(a)
        x2, y2 = cx + (r + 3.8) * math.cos(a), cy + (r + 3.8) * math.sin(a)
        rays.append(f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}"/>')
    return f'<circle cx="{cx}" cy="{cy}" r="{r}"/>' + "".join(rays)


_W = {
    "clear-day": _sun_disc(12, 12, 4.6),
    "clear-night": '<path d="M20.5 13.5A8.5 8.5 0 1 1 10.5 3.5a7 7 0 1 0 10 10Z"/>',
    "mostly-day": (
        '<circle cx="15.5" cy="8.5" r="3.4"/>'
        '<path d="M15.5 2.6v1.6M9.6 8.5H8M20.9 8.5h-1.6M11.3 4.3l1.1 1.1"/>'
        + _cloud(11, 15, 0.82)
    ),
    "mostly-night": (
        '<path d="M18.5 10A6.5 6.5 0 1 1 11 3.6a5.3 5.3 0 1 0 7.5 6.4Z"/>'
        + _cloud(11, 15, 0.82)
    ),
    "partly-day": (
        '<circle cx="15" cy="8" r="3.6"/>'
        '<path d="M15 1.8v1.7M8.8 8H7.2M20.8 8h-1.6M10.6 3.4l1.2 1.2"/>'
        + _cloud(11.5, 14.5, 0.95)
    ),
    "partly-night": (
        '<path d="M18.2 9.8A6.6 6.6 0 1 1 10.6 3a5.4 5.4 0 1 0 7.6 6.8Z"/>'
        + _cloud(11.5, 14.5, 0.95)
    ),
    "cloud": _cloud(12, 13, 1.08),
    "overcast": (
        '<path d="M5.5 13.2a3.4 3.4 0 0 1 1.6-5.9 5 5 0 0 1 8.6-1.1" opacity=".6"/>'
        + _cloud(12.5, 14.5, 1.02)
    ),
    "fog": (
        '<path d="M7 13.5h10a3.4 3.4 0 0 0 .4-6.78A4.9 4.9 0 0 0 7.8 6.15'
        ' 3.7 3.7 0 0 0 7 13.5Z"/>'
        '<path d="M5.5 17h13M7.5 20.2h9"/>'
    ),
    "drizzle": (
        _cloud(12, 11.5, 1.0)
        + '<path d="M9 16.5v1.8M12 17v2.4M15 16.5v1.8M10.5 20.4v1M13.5 20.4v1"/>'
    ),
    "rain": (
        _cloud(12, 11.5, 1.0)
        + '<path d="M9 16.5v2.6M12 17v3.4M15 16.5v2.6"/>'
    ),
    "heavy-rain": (
        _cloud(12, 11, 1.05)
        + '<path d="M8.4 16.2 7 20.4M11.6 16.2l-1.4 4.2M14.8 16.2l-1.4 4.2M17.4 16.5l-1 3"/>'
    ),
    "snow": (
        _cloud(12, 11.5, 1.0)
        + '<path d="M9 17.4h.01M12 18.4h.01M15 17.4h.01M10.5 20.6h.01M13.5 20.6h.01"'
        ' stroke-width="2.4"/>'
    ),
    "sleet": (
        _cloud(12, 11.5, 1.0)
        + '<path d="M9.2 16.8v2.4M14.8 16.8v2.4M10.6 20.8h.01M13.4 20.8h.01" stroke-width="2.2"/>'
    ),
    "thunder": (
        _cloud(12, 11, 1.05)
        + '<path d="m12.6 15.5 3.6 0-2.7 3.5h2.3l-4.2 4.8 1.3-3.8h-2.2l2-4.5Z" '
        'fill="currentColor" stroke="none"/>'
    ),
    "hail": (
        _cloud(12, 11.5, 1.0)
        + '<circle cx="9.5" cy="18.4" r="1.1" fill="currentColor" stroke="none"/>'
        '<circle cx="13" cy="20" r="1.1" fill="currentColor" stroke="none"/>'
        '<circle cx="15.8" cy="17.8" r="1.1" fill="currentColor" stroke="none"/>'
    ),
}


def weather_icon(key: str, size: int = 24, cls: str = "", stroke: float = 1.5) -> str:
    """Return an inline <svg> weather glyph."""
    body = _W.get(key) or _W["cloud"]
    cls = (cls or "").strip()
    return (
        f'<svg class="wic {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


# ---------------------------------------------------------------------------
# Brand mark — "sky loop"
# ---------------------------------------------------------------------------
# Geometry lives in one place so the header mark, the favicon, the empty state
# and the splash loader are always the exact same drawing.
#
# Validated numerically (path sampling): ink bbox 1.32,2.78 → 21.73,19.66
# inside the 24x24 box, optical centre (11.52, 11.22), 2.0u clearance between
# the sun disc and the cloud stroke, 4.5u to the ray tips — nothing touches.
_LOGO_CLOUD_D = _cloud_d(10.8, 16.2, 0.96)
_LOGO_SUN = (18.6, 7.2, 2.4)          # cx, cy, r — breaks out above the cloud
_LOGO_RAYS_D = "M18.6 4.18V2.78M16.46 5.06l-.99-.99M20.74 5.06l.99-.99"
# centres the 24-box ink inside the 32-box tile (4 + optical offset)
_LOGO_TILE_SHIFT = "translate(4.48 4.78)"

_GRAD_FROM = "#8CC4FF"
_GRAD_TO = "#4F8CF7"


def _logo_gradient(uid: str) -> str:
    return (
        f'<defs><linearGradient id="wslogo-{uid}" x1="3" y1="3" x2="21" y2="20" '
        f'gradientUnits="userSpaceOnUse">'
        f'<stop stop-color="{_GRAD_FROM}"/><stop offset="1" stop-color="{_GRAD_TO}"/>'
        f"</linearGradient></defs>"
    )


def _clean_uid(uid: str, fallback: str = "h") -> str:
    return "".join(ch for ch in str(uid) if ch.isalnum()) or fallback


def _logo_glyph(uid: str, stroke: float, color: str = "", animated: bool = False) -> str:
    """Inner drawing of the mark (no wrapping <svg>), 24x24 user units.

    When ``animated`` is set, both stroked paths carry ``pathLength="1"`` so the
    CSS draw-in can work in normalised units (``stroke-dasharray: 1``) no matter
    how long the real path is.
    """
    paint = color or f"url(#wslogo-{uid})"
    cls = "ws-logo-glyph" + (" ws-logo-anim" if animated else "")
    plen = ' pathLength="1"' if animated else ""
    cx, cy, r = _LOGO_SUN
    return (
        ("" if color else _logo_gradient(uid))
        + f'<g class="{cls}" fill="none" stroke="{paint}" stroke-width="{stroke}" '
        + 'stroke-linecap="round" stroke-linejoin="round">'
        + f'<g class="ws-logo-sun"><circle cx="{cx}" cy="{cy}" r="{r}"/>'
        + f'<path class="ws-logo-rays" d="{_LOGO_RAYS_D}"{plen}/></g>'
        + f'<path class="ws-logo-cloud" d="{_LOGO_CLOUD_D}"{plen}/></g>'
    )


def logo_mark(size: int = 26, uid: str = "h", stroke: float = 1.6,
              color: str = "", animated: bool = False,
              title: str = "WeatherSense") -> str:
    """The bare line-art mark on a transparent background.

    ``animated=True`` adds the stroke-draw / sun-pop classes used by the splash
    loader; ``color`` overrides the gradient with a solid stroke.
    """
    uid = _clean_uid(uid, "h")
    return (
        f'<svg class="ws-logo" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" role="img" aria-label="{title}">'
        + _logo_glyph(uid, stroke, color=color, animated=animated)
        + "</svg>"
    )


def logo_tile(size: int = 32, uid: str = "t", animated: bool = False) -> str:
    """Mark on a dark rounded tile — favicon, splash badge, app icon."""
    uid = _clean_uid(uid, "t")
    return (
        f'<svg class="ws-logo-tile" width="{size}" height="{size}" viewBox="0 0 32 32" '
        f'fill="none" role="img" aria-label="WeatherSense">'
        f'<rect width="32" height="32" rx="9.5" fill="#0B0D12"/>'
        f'<rect x=".5" y=".5" width="31" height="31" rx="9" stroke="rgba(255,255,255,.10)"/>'
        f'<g transform="{_LOGO_TILE_SHIFT}">'
        + _logo_glyph(uid + "i", 1.75, animated=animated)
        + "</g></svg>"
    )


def _data_uri(svg: str) -> str:
    return "data:image/svg+xml," + quote(svg, safe="")


# Header mark, standalone mark and favicon — all the same drawing.
LOGO_SVG = logo_mark(26, uid="hdr")
LOGO_ONLY_SVG = logo_mark(20, uid="only")
LOGO_TILE_SVG = logo_tile(32)

# Favicon: a dark tile carries the mark at 16px on any browser chrome.
# Solid stroke (no gradient refs) so it survives being inlined as a data URI.
LOGO_DATA_URI = _data_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none">'
    '<rect width="32" height="32" rx="9.5" fill="#0B0D12"/>'
    f'<g transform="{_LOGO_TILE_SHIFT}" fill="none" stroke="#8CC4FF" stroke-width="1.9" '
    'stroke-linecap="round" stroke-linejoin="round">'
    f'<circle cx="{_LOGO_SUN[0]}" cy="{_LOGO_SUN[1]}" r="{_LOGO_SUN[2]}"/>'
    f'<path d="{_LOGO_RAYS_D}"/>'
    f'<path d="{_LOGO_CLOUD_D}"/>'
    "</g></svg>"
)
