"""Reading progress — estimates + LAIE-shaped telemetry."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.session_store import list_recent_lessons, load_progress, save_progress


def estimate_reading_minutes(text: str, *, wpm: float = 180.0) -> float:
    words = max(len((text or "").split()), 1)
    return round(words / max(wpm, 60.0), 1)


def update_progress(
    learner_id: str,
    lesson_id: str,
    *,
    reading_pct: float | None = None,
    delta_seconds: float = 0.0,
    resume_offset: int | None = None,
    resume_anchor: str | None = None,
    lesson_text: str = "",
) -> dict[str, Any]:
    current = load_progress(learner_id, lesson_id)
    pct = float(reading_pct if reading_pct is not None else current.get("reading_pct") or 0)
    pct = max(0.0, min(100.0, pct))
    spent = float(current.get("time_spent_seconds") or 0) + max(delta_seconds, 0)
    patch = {
        "reading_pct": pct,
        "completion_pct": pct,
        "time_spent_seconds": spent,
        "estimated_minutes": estimate_reading_minutes(lesson_text) if lesson_text else current.get("estimated_minutes") or 0,
    }
    if resume_offset is not None:
        patch["resume_offset"] = int(resume_offset)
    if resume_anchor is not None:
        patch["resume_anchor"] = resume_anchor
    row = save_progress(learner_id, lesson_id, patch)
    return {"ok": True, "progress": row, "recent": list_recent_lessons(learner_id)}


def laie_reader_payload(learner_id: str, lesson_id: str) -> dict[str, Any]:
    """Shape expected by LAIE lesson_reader analytics."""
    from engines.learning_experience_platform.session_store import list_bookmarks, list_highlights, list_notes

    return {
        "lesson_id": lesson_id,
        "progress": load_progress(learner_id, lesson_id),
        "bookmarks": list_bookmarks(learner_id),
        "highlights_count": len(list_highlights(learner_id, lesson_id)),
        "notes_count": len(list_notes(learner_id, lesson_id)),
        "destination": "learning_analytics",
    }
