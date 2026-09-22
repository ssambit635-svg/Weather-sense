"""Small compatibility shims so WeatherSense runs on any supported Streamlit.

Streamlit's widget kwargs move around between releases (``use_container_width``
is deprecated in favour of ``width="stretch"``; ``st.segmented_control`` only
exists from 1.40; ``st.fragment`` only from 1.37). Detecting the capability at
import time keeps a single code path working everywhere instead of dying with
an ``AttributeError``/``TypeError`` on the first render.
"""

from __future__ import annotations

import importlib
import inspect
from typing import Any, Callable, Optional

import streamlit as st

__all__ = [
    "STREAMLIT_VERSION",
    "MIN_STREAMLIT",
    "version_ok",
    "stretch",
    "fragment",
    "control_flow_exceptions",
    "streamlit_api_exception",
    "has",
]


def _version_tuple(raw: str) -> tuple[int, ...]:
    parts = []
    for chunk in str(raw).split(".")[:3]:
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


STREAMLIT_VERSION = _version_tuple(getattr(st, "__version__", "0.0.0"))
MIN_STREAMLIT = (1, 37, 0)


def version_ok(minimum: tuple[int, ...] = MIN_STREAMLIT) -> bool:
    return STREAMLIT_VERSION >= minimum


def has(widget: str) -> bool:
    return hasattr(st, widget)


def _accepts(fn: Any, param: str) -> bool:
    try:
        return param in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


# st.button gained `width="stretch"` in 1.49; before that it was
# `use_container_width=True`. Both are still accepted by the versions we target,
# so pick whichever this install actually understands and never pass both.
_STRETCH_KWARGS: dict[str, Any] = (
    {"width": "stretch"} if _accepts(st.button, "width") else {"use_container_width": True}
)


def stretch() -> dict[str, Any]:
    """Keyword args that make a button/submit-button fill its column."""
    return dict(_STRETCH_KWARGS)


def fragment(run_every: Any = None) -> Callable:
    """``st.fragment`` where available, transparent no-op otherwise.

    Auto-refresh degrades to plain full-script reruns instead of crashing.
    """
    st_fragment = getattr(st, "fragment", None)
    if st_fragment is None:
        def _decorator(fn: Callable) -> Callable:
            return fn
        return _decorator

    try:
        return st_fragment(run_every=run_every) if run_every is not None else st_fragment()
    except Exception:  # pragma: no cover - very old/new signature mismatch
        def _decorator(fn: Callable) -> Callable:
            return fn
        return _decorator


def _resolve(name: str, modules: tuple[str, ...]) -> Optional[type]:
    for mod_name in modules:
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        exc = getattr(mod, name, None)
        if isinstance(exc, type) and issubclass(exc, BaseException):
            return exc
    return None


# st.rerun()/st.stop() unwind the script with control-flow exceptions. A global
# error boundary must let them through or navigation silently breaks.
_RERUN = _resolve("RerunException", (
    "streamlit.runtime.scriptrunner",
    "streamlit.runtime.scriptrunner_utils.exceptions",
))
_STOP = _resolve("StopException", (
    "streamlit.runtime.scriptrunner",
    "streamlit.runtime.scriptrunner_utils.exceptions",
))
_API = _resolve("StreamlitAPIException", ("streamlit.errors",))

control_flow_exceptions: tuple[type, ...] = tuple(
    e for e in (_RERUN, _STOP) if e is not None
)
streamlit_api_exception: Optional[type] = _API
