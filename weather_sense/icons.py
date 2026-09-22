"""Minimal stroke-based SVG icon set. No emoji anywhere in the app."""

from __future__ import annotations

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
}


def icon(name: str, size: int = 16, cls: str = "", stroke: float = 1.7) -> str:
    """Return an inline <svg> for a UI icon name."""
    body = _UI.get(name)
    if body is None:
        return ""
    return (
        f'<svg class="ic {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


# ---------------------------------------------------------------------------
# Weather glyphs — richer, condition-specific marks
# ---------------------------------------------------------------------------
def _cloud(cx: float = 12, cy: float = 13.5, s: float = 1.0) -> str:
    """A soft filled/stroked cloud centered around (cx, cy), scale s."""
    return (
        f'<path d="M{cx - 6.4 * s} {cy + 3.6 * s}h{11.6 * s}'
        f'a{3.6 * s} {3.6 * s} 0 0 0 {0.4 * s} -{7.15 * s}'
        f'a{5.1 * s} {5.1 * s} 0 0 0 -{9.85 * s} -{1.7 * s}'
        f'a{3.9 * s} {3.9 * s} 0 0 0 -{2.15 * s} {8.85 * s}z"/>'
    )


def _sun_disc(cx: float = 12, cy: float = 12, r: float = 4) -> str:
    rays = []
    import math
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
    body = _W.get(key, _W["cloud"])
    return (
        f'<svg class="wic {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


# ---------------------------------------------------------------------------
# Brand mark
# ---------------------------------------------------------------------------
LOGO_SVG = """
<svg width="26" height="26" viewBox="0 0 32 32" fill="none" aria-hidden="true">
  <rect width="32" height="32" rx="9" fill="url(#wsg)"/>
  <circle cx="12.5" cy="12" r="4.1" stroke="#0B0D12" stroke-width="0"/>
  <circle cx="12.5" cy="12" r="4.1" fill="#0E1116" opacity="0"/>
  <path d="M9.2 20.6h11.2a3.5 3.5 0 0 0 .4-6.97 4.9 4.9 0 0 0-9.3-1.55
           3.75 3.75 0 0 0-2.3 8.52Z" fill="#0B0D12"/>
  <path d="M21.6 9.4a5.2 5.2 0 0 1 0 7.4" stroke="#0B0D12" stroke-width="1.7" stroke-linecap="round"/>
  <path d="M24.6 6.8a8.6 8.6 0 0 1 0 12.6" stroke="#0B0D12" stroke-width="1.7" stroke-linecap="round" opacity=".55"/>
  <defs>
    <linearGradient id="wsg" x1="0" y1="0" x2="32" y2="32">
      <stop stop-color="var(--accent-1, #7CB8FF)"/>
      <stop offset="1" stop-color="var(--accent-2, #4F8CF7)"/>
    </linearGradient>
  </defs>
</svg>
""".strip()

LOGO_ONLY_SVG = """
<svg width="20" height="20" viewBox="0 0 32 32" fill="none" aria-hidden="true">
  <rect width="32" height="32" rx="9" fill="url(#wsg2)"/>
  <path d="M9.2 20.6h11.2a3.5 3.5 0 0 0 .4-6.97 4.9 4.9 0 0 0-9.3-1.55
           3.75 3.75 0 0 0-2.3 8.52Z" fill="#0B0D12"/>
  <path d="M21.6 9.4a5.2 5.2 0 0 1 0 7.4" stroke="#0B0D12" stroke-width="1.7" stroke-linecap="round"/>
  <path d="M24.6 6.8a8.6 8.6 0 0 1 0 12.6" stroke="#0B0D12" stroke-width="1.7" stroke-linecap="round" opacity=".55"/>
  <defs>
    <linearGradient id="wsg2" x1="0" y1="0" x2="32" y2="32">
      <stop stop-color="#7CB8FF"/>
      <stop offset="1" stop-color="#4F8CF7"/>
    </linearGradient>
  </defs>
</svg>
""".strip()

# Plain favicon-safe data URI (dark tile, cloud glyph)
LOGO_DATA_URI = (
    "data:image/svg+xml,"
    + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='9' fill='%234F8CF7'/%3E"
    "%3Cpath d='M9.2 20.6h11.2a3.5 3.5 0 0 0 .4-6.97 4.9 4.9 0 0 0-9.3-1.55"
    " 3.75 3.75 0 0 0-2.3 8.52Z' fill='%230B0D12'/%3E"
    "%3Cpath d='M21.6 9.4a5.2 5.2 0 0 1 0 7.4' stroke='%230B0D12' stroke-width='1.7' stroke-linecap='round'/%3E"
    "%3Cpath d='M24.6 6.8a8.6 8.6 0 0 1 0 12.6' stroke='%230B0D12' stroke-width='1.7' stroke-linecap='round' opacity='.55'/%3E"
    "%3C/svg%3E"
)
