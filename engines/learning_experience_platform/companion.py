"""ALCIS companion hooks — non-interruptive encouragement."""

from __future__ import annotations

from typing import Any


def companion_presence(
    learner_id: str,
    *,
    progress_pct: float = 0.0,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    messages = []
    try:
        from engines.learning_companion_engine.service import (
            api_log_encouragement,
            api_record_celebration,
            api_ef_coach,
        )

        if progress_pct >= 100:
            messages.append(api_record_celebration(learner_id, "lesson_completed", evidence={"detail": "Lesson finished."}))
        elif progress_pct >= 50:
            messages.append(api_log_encouragement(learner_id, context={"progress_delta": progress_pct / 100.0}, event="progress"))
        elif progress_pct > 0 and progress_pct < 15:
            messages.append(api_ef_coach(learner_id, "initiation", task="Continue reading"))
    except Exception as exc:  # noqa: BLE001
        messages.append({"ok": False, "error": str(exc)})

    return {
        "ok": True,
        "interrupt": False,
        "messages": messages,
        "behaviors": ["celebrate_progress", "encourage", "recommend_breaks", "milestones", "suggest_revision"],
        "policy": "never_interrupt_unnecessarily",
        "source": "alcis",
    }
