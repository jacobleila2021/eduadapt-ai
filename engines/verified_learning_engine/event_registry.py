"""Strongly typed learning-session event catalogue (immutable records)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid

# Session lifecycle stages
SESSION_STAGES = (
    "session_created",
    "session_restored",
    "lesson_loaded",
    "lesson_started",
    "lesson_paused",
    "lesson_resumed",
    "lesson_completed",
    "reflection_completed",
    "assessment_started",
    "assessment_submitted",
    "mastery_updated",
    "recommendation_generated",
    "session_closed",
)

# Runtime learner states
LEARNER_STATES = (
    "preparing",
    "reading",
    "listening",
    "watching",
    "practicing",
    "requesting_help",
    "reflecting",
    "assessing",
    "reviewing",
    "completed",
    "interrupted",
    "offline",
    "resuming",
)

EVENT_TYPES = (
    "LessonOpened",
    "LessonLoaded",
    "LessonCompleted",
    "HintRequested",
    "HintDelivered",
    "TutorQuestionAsked",
    "TutorResponseReceived",
    "DiagramViewed",
    "AudioPlayed",
    "AccessibilityChanged",
    "ConfidenceChanged",
    "MisconceptionDetected",
    "InterventionTriggered",
    "AssessmentStarted",
    "AssessmentCompleted",
    "MasteryUpdated",
    "GoalAchieved",
    "XPAwarded",
    "BadgeUnlocked",
    "ReflectionCompleted",
    "ParentViewed",
    "TeacherReviewed",
    "SessionCreated",
    "SessionRestored",
    "SessionPaused",
    "SessionResumed",
    "SessionClosed",
    "EngineScheduled",
    "OrchestrationDecision",
    "RecommendationGenerated",
    "WorkflowAdvanced",
    "HealthAlert",
    "VoiceCommandReceived",
    "PronunciationScored",
    "ReadAlongProgress",
    "OfflineSynced",
    "CompanionEncouraged",
    "CompanionCelebrated",
    "CompanionCheckIn",
    "MotivationXPAwarded",
    "MotivationCertificateIssued",
    "MotivationQuestCompleted",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class LearningEvent:
    """Immutable, timestamped orchestration event."""

    event_type: str
    session_id: str
    learner_id: str = ""
    lesson_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    ts: str = field(default_factory=_now)
    source: str = "vlie"

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "session_id": self.session_id,
            "learner_id": self.learner_id,
            "lesson_id": self.lesson_id,
            "payload": dict(self.payload),
            "ts": self.ts,
            "source": self.source,
            "immutable": True,
        }


def make_event(
    event_type: str,
    *,
    session_id: str,
    learner_id: str = "",
    lesson_id: str = "",
    payload: dict[str, Any] | None = None,
    source: str = "vlie",
) -> LearningEvent:
    if event_type not in EVENT_TYPES:
        # Allow extension events but tag them
        payload = {**(payload or {}), "_extended_type": True}
    return LearningEvent(
        event_type=event_type,
        session_id=session_id,
        learner_id=learner_id,
        lesson_id=lesson_id,
        payload=dict(payload or {}),
        source=source,
    )
