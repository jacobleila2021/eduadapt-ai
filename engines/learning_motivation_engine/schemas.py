"""LMAS schemas — motivation & achievement contracts (no curriculum mutation)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


LEVELS = (
    {"id": "explorer", "name": "Explorer", "min_xp": 0},
    {"id": "discoverer", "name": "Discoverer", "min_xp": 100},
    {"id": "learner", "name": "Learner", "min_xp": 300},
    {"id": "scholar", "name": "Scholar", "min_xp": 700},
    {"id": "expert", "name": "Expert", "min_xp": 1500},
    {"id": "master", "name": "Master", "min_xp": 3000},
    {"id": "innovator", "name": "Innovator", "min_xp": 6000},
)

XP_EVENTS = (
    "lesson_completed",
    "concept_mastered",
    "consistent_study",
    "reflection",
    "helping_classmate",
    "project_completed",
    "improvement",
    "revision",
    "tutor_session",
    "reading_completed",
)

# Base XP — evidence weighted later; guessing/repetition not rewarded
XP_BASE: dict[str, int] = {
    "lesson_completed": 25,
    "concept_mastered": 40,
    "consistent_study": 15,
    "reflection": 12,
    "helping_classmate": 20,  # teacher-approved only
    "project_completed": 50,
    "improvement": 30,
    "revision": 18,
    "tutor_session": 15,
    "reading_completed": 10,
}

ACHIEVEMENT_CATEGORIES = (
    "learning",
    "accessibility",
    "persistence",
    "reading",
    "science",
    "mathematics",
    "creativity",
    "executive_function",
    "collaboration",
    "critical_thinking",
    "reflection",
)

QUEST_TYPES = (
    "daily",
    "weekly",
    "revision",
    "project",
    "executive_function",
    "subject",
    "exam_preparation",
)

POLICY = {
    "intrinsic_before_extrinsic": True,
    "no_dark_patterns": True,
    "no_pay_to_win": True,
    "no_public_competitive_leaderboards": True,
    "no_punish_missed_days": True,
    "never_alter_curriculum_or_assessment": True,
    "anti_farming": True,
}


@dataclass
class LearnerMotivationState:
    learner_id: str
    xp_total: int = 0
    xp_log: list[dict[str, Any]] = field(default_factory=list)
    level_id: str = "explorer"
    badges: list[dict[str, Any]] = field(default_factory=list)
    achievements: list[dict[str, Any]] = field(default_factory=list)
    quests: list[dict[str, Any]] = field(default_factory=list)
    streaks: dict[str, Any] = field(default_factory=lambda: {
        "daily": 0, "weekly": 0, "monthly": 0, "grace_days_used": 0, "best_daily": 0
    })
    certificates: list[dict[str, Any]] = field(default_factory=list)
    skill_tree_progress: dict[str, Any] = field(default_factory=dict)
    journey: dict[str, Any] = field(default_factory=dict)
    last_event_hashes: list[str] = field(default_factory=list)  # anti-farming

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
