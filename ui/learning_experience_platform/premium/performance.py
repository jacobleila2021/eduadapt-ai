"""Client-side performance hints for Streamlit LXP."""

from __future__ import annotations

from typing import Any
import time


def performance_plan() -> dict[str, Any]:
    return {
        "lazy_load_diagrams": True,
        "virtual_scroll_threshold": 40,
        "memoize_ai_panel": True,
        "image_max_width": 1200,
        "prefetch_next_lesson": True,
        "progressive_sections": True,
        "cache_formulae": True,
        "cache_diagrams": True,
    }


def mark_page_load(start_monotonic: float, *, learner_id: str = "") -> dict[str, Any]:
    elapsed_ms = max(0.0, (time.monotonic() - start_monotonic) * 1000)
    try:
        from engines.learning_experience_platform.phase4_analytics import track_experience

        track_experience("page_load", learner_id=learner_id, payload={"ms": round(elapsed_ms, 1)})
    except Exception:  # noqa: BLE001
        pass
    return {"ok": True, "load_ms": round(elapsed_ms, 1)}
