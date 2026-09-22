"""Regression tests for WeatherSense.

Run with:  python -m unittest discover -s tests -v
(or:       pytest tests/  — both work, no network access required)

These exist because of real failures that were fixed:

* hourly/daily arrays were truncated to zero length by a bad pad helper, so the
  forecast sections silently rendered "unavailable";
* ``None`` values from the weather API crashed formatters (``wind_dir_name``)
  or leaked the literal string "None" into the UI;
* exceptions raised inside an ``st.fragment`` bypass the page-level error
  boundary and surface as Streamlit's raw red traceback box.
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit.testing.v1 import AppTest  # noqa: E402

from weather_sense import components as ui  # noqa: E402
from weather_sense import sample  # noqa: E402
from weather_sense.api import (  # noqa: E402
    code_info, fmt_int, fmt_t, normalize_aqi, normalize_forecast, num, valid_place,
    wind_dir_full, wind_dir_name,
)
from weather_sense.compat import stretch  # noqa: E402
from weather_sense.icons import LOGO_DATA_URI, LOGO_SVG, icon, logo_mark  # noqa: E402

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


class TestNormalization(unittest.TestCase):
    def test_sample_payload_keeps_every_slot(self):
        """The regression: `_pad(times, 0)` used to empty these lists."""
        data = normalize_forecast(sample.forecast(51.5, -0.12))
        self.assertEqual(48, len(data["hourly"]["time"]))
        self.assertEqual(7, len(data["daily"]["time"]))
        for key, values in data["hourly"].items():
            self.assertEqual(len(data["hourly"]["time"]), len(values), key)
        for key, values in data["daily"].items():
            self.assertEqual(len(data["daily"]["time"]), len(values), key)

    def test_empty_and_garbage_payloads_are_safe(self):
        for raw in ({}, None, "junk", {"current": 5, "hourly": [], "daily": {}}):
            data = normalize_forecast(raw)
            self.assertIsInstance(data["current"], dict)
            self.assertIn("temperature_2m", data["current"])
            self.assertIsInstance(data["hourly"]["time"], list)
            self.assertIsInstance(data["daily"]["time"], list)
            self.assertTrue(data["timezone"])

    def test_short_arrays_are_padded_not_index_error(self):
        raw = {
            "current": {"time": "2026-09-22T12:00", "temperature_2m": 10, "weather_code": 61},
            "hourly": {"time": ["2026-09-22T12:00", "2026-09-22T13:00"],
                       "temperature_2m": [10], "weather_code": [61]},
            "daily": {"time": ["2026-09-22"], "temperature_2m_max": [None]},
        }
        data = normalize_forecast(raw)
        self.assertEqual(2, len(data["hourly"]["temperature_2m"]))
        self.assertIsNone(data["hourly"]["temperature_2m"][1])
        self.assertEqual(1, len(data["daily"]["temperature_2m_min"]))

    def test_strings_nan_and_inf_are_coerced(self):
        data = normalize_forecast({"current": {"temperature_2m": "21.5",
                                               "wind_speed_10m": float("nan"),
                                               "cloud_cover": float("inf")}})
        self.assertEqual(21.5, data["current"]["temperature_2m"])
        self.assertIsNone(data["current"]["wind_speed_10m"])
        self.assertIsNone(data["current"]["cloud_cover"])

    def test_aqi_normalization(self):
        self.assertEqual({"us_aqi": None, "pm2_5": None, "pm10": None},
                         {k: normalize_aqi({})["current"][k] for k in ("us_aqi", "pm2_5", "pm10")})
        self.assertEqual(42.0, normalize_aqi({"current": {"us_aqi": "42"}})["current"]["us_aqi"])


class TestFormatters(unittest.TestCase):
    def test_none_never_reaches_the_ui(self):
        self.assertEqual("--", fmt_t(None, "C"))
        self.assertEqual("--", wind_dir_name(None))
        self.assertEqual("unknown direction", wind_dir_full(None))
        self.assertEqual("--", fmt_int(None, "%"))
        self.assertEqual("7%", fmt_int("7.4", "%"))
        self.assertIsNone(num(None))
        self.assertIsNone(num("abc"))
        self.assertIsNone(num(float("nan")))

    def test_wind_directions(self):
        self.assertEqual("N", wind_dir_name(0))
        self.assertEqual("SW", wind_dir_name(225))
        self.assertEqual("N", wind_dir_name(359))
        self.assertEqual("south-west", wind_dir_full(225))

    def test_units(self):
        self.assertEqual("0°", fmt_t(0, "C"))
        self.assertEqual("32°", fmt_t(0, "F"))

    def test_code_info_defaults(self):
        for code in (None, "x", 999, -1):
            label, key, accent = code_info(code)
            self.assertTrue(label and key and accent.startswith("#"))


class TestPlaces(unittest.TestCase):
    def test_valid_place(self):
        self.assertTrue(valid_place({"lat": 1.0, "lon": 2.0}))
        self.assertFalse(valid_place({"lat": None, "lon": 2.0}))
        self.assertFalse(valid_place({"lat": 999, "lon": 2.0}))
        self.assertFalse(valid_place(None))
        self.assertFalse(valid_place("London"))


class TestBrand(unittest.TestCase):
    def test_logo_is_well_formed_svg(self):
        for svg in (LOGO_SVG, logo_mark(78, uid="splash", animated=True), icon("clock", 13)):
            self.assertTrue(svg.startswith("<svg"), svg[:40])
            self.assertTrue(svg.endswith("</svg>"))
            self.assertEqual(svg.count("<svg"), svg.count("</svg>"))

    def test_unknown_icon_is_blank_not_crash(self):
        self.assertEqual("", icon("does-not-exist"))
        self.assertIn("<svg", ui.loader_svg(20))

    def test_favicon_is_a_data_uri(self):
        self.assertTrue(LOGO_DATA_URI.startswith("data:image/svg+xml,"))
        self.assertNotIn("<", LOGO_DATA_URI)      # fully percent-encoded
        self.assertNotIn("#", LOGO_DATA_URI)

    def test_gradient_ids_are_unique_per_instance(self):
        a, b = logo_mark(26, uid="one"), logo_mark(26, uid="two")
        self.assertIn("wslogo-one", a)
        self.assertIn("wslogo-two", b)

    def test_animated_logo_carries_pathlength(self):
        """The CSS draw-in uses normalised dash units, so pathLength is required."""
        animated = logo_mark(78, uid="splash", animated=True)
        static = logo_mark(26, uid="hdr")
        self.assertEqual(2, animated.count('pathLength="1"'))   # cloud + rays
        self.assertNotIn("pathLength", static)

    def test_splash_states(self):
        loading = ui.splash_html("Reading the sky")
        ready = ui.splash_html("Ready", ready=True, fade=True)
        self.assertIn("ws-logo-anim", loading)
        self.assertIn("ws-ring-a", loading)
        self.assertIn("ws-dots", loading)
        self.assertIn("ws-ready", ready)
        self.assertIn("ws-out", ready)
        self.assertNotIn("ws-dots", ready)        # dots stop once data landed


class TestCompat(unittest.TestCase):
    def test_stretch_returns_one_mechanism(self):
        kw = stretch()
        self.assertEqual(1, len(kw))
        self.assertIn(next(iter(kw)), ("width", "use_container_width"))


class TestAppEndToEnd(unittest.TestCase):
    """Whole-app runs through Streamlit's own harness (offline sample data)."""

    def _run(self, **kwargs):
        at = AppTest.from_file(APP, default_timeout=240)
        for key, value in kwargs.items():
            at.query_params[key] = value
        at.run()
        return at

    def test_first_run_renders_the_full_dashboard(self):
        at = self._run()
        self.assertEqual([], [str(e.value) for e in at.exception])
        body = self._body(at)
        self.assertEqual(24, body.count('class="rail-col"'), "24 hourly cells")
        self.assertEqual(7, body.count('<div class="day"'), "7 forecast rows")
        self.assertEqual(6, body.count('class="metric"'), "6 condition metrics")
        self.assertEqual(3, body.count('class="insight"'), "3 insight cards")
        self.assertIn("ws-header", body)
        self.assertIn("ws-foot", body)
        self.assertNotIn("unavailable", body.split("Air quality data")[0])
        self.assertNotIn(">None<", body)
        self.assertNotIn("None%", body)

    @staticmethod
    def _body(at):
        """Rendered markup, minus <style> blocks (CSS mentions every class)."""
        return "\n".join(str(m.value) for m in at.markdown
                         if not str(m.value).lstrip().startswith("<style"))

    def test_splash_is_shown_once_then_removed(self):
        at = self._run()
        self.assertNotIn('class="ws-splash"', self._body(at))   # cleared before reveal
        self.assertIn("ws-header", self._body(at))              # app really rendered
        at.run()                                                # any later interaction
        self.assertNotIn("ws-splash-badge", self._body(at))
        self.assertNotIn("ws-ring-a", self._body(at))

    def test_city_search_updates_the_place(self):
        at = self._run()
        at.text_input(key="city_input").input("Tokyo").run()
        [b for b in at.button if b.label == "Search"][0].click().run()
        self.assertEqual([], [str(e.value) for e in at.exception])
        self.assertEqual("Tokyo", at.session_state["place"]["name"])
        self.assertEqual("Tokyo", at.session_state["city_input"])

    def test_unit_toggle_switches_to_fahrenheit(self):
        at = self._run()
        at.session_state["unit_seg"] = "°F"
        at.run()
        self.assertEqual("F", at.session_state["unit"])
        self.assertEqual([], [str(e.value) for e in at.exception])

    def test_favorites_round_trip(self):
        at = self._run()
        [b for b in at.button if b.label == "Save city"][0].click().run()
        self.assertEqual(1, len(at.session_state["favorites"]))
        self.assertTrue(any(b.label.startswith("London") for b in at.button))
        [b for b in at.button if b.label == "Clear"][0].click().run()
        self.assertEqual([], at.session_state["favorites"])

    def test_query_param_bootstrap(self):
        at = self._run(city="Paris", cc="FR")
        self.assertEqual([], [str(e.value) for e in at.exception])
        self.assertEqual("Paris", at.session_state["place"]["name"])

    def test_fragment_errors_show_a_card_not_a_traceback_box(self):
        """An exception inside st.fragment must not become Streamlit's red box."""
        def boom(*args, **kwargs):
            raise RuntimeError("synthetic failure")

        # patched only for this run, so later tests see the real component
        with mock.patch.object(ui, "hero", boom):
            at = self._run()
        body = self._body(at)
        self.assertEqual([], [str(e.value) for e in at.exception],
                         "Streamlit must not render its own traceback box")
        self.assertIn("ws-fatal", body)
        self.assertIn("synthetic failure", body)
        self.assertTrue(any(b.label == "Retry" for b in at.button))

    def test_page_level_errors_show_a_card_too(self):
        """Same guarantee for failures outside any fragment."""
        def boom():
            raise RuntimeError("shell failure")

        with mock.patch.object(ui, "unit_toggle", boom):
            at = self._run()
        body = self._body(at)
        self.assertEqual([], [str(e.value) for e in at.exception])
        self.assertIn("ws-fatal", body)
        self.assertIn("shell failure", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
