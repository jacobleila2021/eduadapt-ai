"""Learner state machine — deterministic transitions."""

from __future__ import annotations

from typing import Any

from engines.verified_learning_engine.event_registry import LEARNER_STATES

# event_type / stage → target state
TRANSITIONS: dict[tuple[str, str], str] = {
    ("preparing", "LessonOpened"): "reading",
    ("preparing", "LessonLoaded"): "reading",
    ("preparing", "SessionRestored"): "resuming",
    ("resuming", "SessionResumed"): "reading",
    ("reading", "AudioPlayed"): "listening",
    ("reading", "DiagramViewed"): "watching",
    ("listening", "LessonLoaded"): "reading",
    ("watching", "LessonLoaded"): "reading",
    ("reading", "HintRequested"): "requesting_help",
    ("practicing", "HintRequested"): "requesting_help",
    ("requesting_help", "TutorResponseReceived"): "practicing",
    ("requesting_help", "HintDelivered"): "practicing",
    ("reading", "AssessmentStarted"): "assessing",
    ("practicing", "AssessmentStarted"): "assessing",
    ("assessing", "AssessmentCompleted"): "reviewing",
    ("reviewing", "MasteryUpdated"): "reflecting",
    ("reflecting", "ReflectionCompleted"): "completed",
    ("reading", "LessonCompleted"): "reflecting",
    ("practicing", "LessonCompleted"): "reflecting",
    ("*", "SessionPaused"): "interrupted",
    ("interrupted", "SessionResumed"): "resuming",
    ("*", "SessionClosed"): "completed",
    ("reading", "TutorQuestionAsked"): "requesting_help",
    ("completed", "LessonOpened"): "reading",
}


class LearnerStateMachine:
    def __init__(self, initial: str = "preparing") -> None:
        if initial not in LEARNER_STATES:
            initial = "preparing"
        self.state = initial
        self.history: list[dict[str, Any]] = [{"state": initial, "event": "init"}]

    def transition(self, event_type: str) -> dict[str, Any]:
        key = (self.state, event_type)
        nxt = TRANSITIONS.get(key) or TRANSITIONS.get(("*", event_type))
        if not nxt:
            # stay — deterministic no-op
            return {"ok": True, "from": self.state, "to": self.state, "event": event_type, "changed": False}
        prev = self.state
        self.state = nxt
        row = {"from": prev, "to": nxt, "event": event_type, "changed": True}
        self.history.append(row)
        return {"ok": True, **row}

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "history": self.history[-50:], "states_available": list(LEARNER_STATES)}
