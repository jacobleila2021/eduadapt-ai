"""Streamlit shell smoke tests without network or AI generation."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_loads_without_runtime_exception():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=60).run()
    assert not app.exception
    assert any(item.value == "1. Upload Your Lesson" for item in app.subheader)
    assert app.button
