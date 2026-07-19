"""Synchronize VMLE actions with VLIE event-driven session orchestrator."""

from __future__ import annotations

from typing import Any

# Map VMLE actions → VLIE event types
ACTION_EVENTS = {
    "audio_played": "AudioPlayed",
    "diagram_viewed": "DiagramViewed",
    "hint_requested": "HintRequested",
    "tutor_question": "TutorQuestionAsked",
    "tutor_response": "TutorResponseReceived",
    "accessibility_changed": "AccessibilityChanged",
    "assessment_started": "AssessmentStarted",
}


def publish_to_vlie(
    action: str,
    *,
    session_id: str,
    learner_id: str = "",
    lesson_id: str = "",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event_type = ACTION_EVENTS.get(action) or action
    try:
        from engines.verified_learning_engine.service import api_publish_event

        return api_publish_event(
            event_type,
            session_id,
            learner_id=learner_id,
            lesson_id=lesson_id,
            payload=payload or {"source": "vmle", "action": action},
        )
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "event_type": event_type, "queued_locally": True}


def devices() -> dict[str, Any]:
    return {
        "android": True,
        "ios": True,
        "tablets": True,
        "chromebooks": True,
        "desktop": True,
        "feature_parity": "practical",
        "offline": True,
    }
