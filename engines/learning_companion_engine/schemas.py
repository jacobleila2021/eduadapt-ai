"""ALCIS schemas — companion personalities, memory, motivation (never curriculum)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PERSONALITY_STYLES = (
    "gentle_coach",
    "cheerful_friend",
    "curious_explorer",
    "calm_mentor",
    "energetic_motivator",
    "professional_mentor",
)

COMPANION_LIBRARY: dict[str, dict[str, Any]] = {
    "reading_owl": {
        "name": "Reading Owl",
        "traits": ["calm", "encouraging", "literacy_focused"],
        "default_style": "gentle_coach",
        "focus": "literacy",
    },
    "science_robot": {
        "name": "Science Robot",
        "traits": ["curious", "logical", "experiment_driven"],
        "default_style": "curious_explorer",
        "focus": "science",
    },
    "math_dragon": {
        "name": "Math Dragon",
        "traits": ["confident", "problem_solving", "step_by_step"],
        "default_style": "energetic_motivator",
        "focus": "mathematics",
    },
    "focus_fox": {
        "name": "Focus Fox",
        "traits": ["executive_function", "time_management", "organization", "planning"],
        "default_style": "calm_mentor",
        "focus": "executive_function",
    },
    "history_explorer": {
        "name": "History Explorer",
        "traits": ["storytelling", "curious", "context_rich"],
        "default_style": "curious_explorer",
        "focus": "history",
    },
    "nature_guardian": {
        "name": "Nature Guardian",
        "traits": ["calm", "caring", "ecology_minded"],
        "default_style": "gentle_coach",
        "focus": "environment",
    },
    "coding_penguin": {
        "name": "Coding Penguin",
        "traits": ["playful", "logical", "debug_minded"],
        "default_style": "cheerful_friend",
        "focus": "computing",
    },
    "language_parrot": {
        "name": "Language Parrot",
        "traits": ["expressive", "multilingual", "practice_oriented"],
        "default_style": "cheerful_friend",
        "focus": "languages",
    },
    "study_panda": {
        "name": "Study Panda",
        "traits": ["steady", "habit_building", "balanced"],
        "default_style": "gentle_coach",
        "focus": "study_habits",
    },
    "university_mentor": {
        "name": "University Mentor",
        "traits": ["professional", "reflective", "goal_oriented"],
        "default_style": "professional_mentor",
        "focus": "higher_ed",
    },
    "career_coach": {
        "name": "Career Coach",
        "traits": ["practical", "aspirational", "skills_focused"],
        "default_style": "professional_mentor",
        "focus": "career",
    },
}


@dataclass
class LearnerCompanionMemory:
    learner_id: str
    preferred_companion: str = "study_panda"
    communication_style: str = "gentle_coach"
    motivation_preferences: list[str] = field(default_factory=lambda: ["effort", "progress"])
    achievements: list[dict[str, Any]] = field(default_factory=list)
    streaks: dict[str, Any] = field(default_factory=lambda: {"days": 0, "best": 0})
    favorite_subjects: list[str] = field(default_factory=list)
    confidence_areas: list[str] = field(default_factory=list)
    support_areas: list[str] = field(default_factory=list)
    accessibility_preferences: dict[str, Any] = field(default_factory=dict)
    encouragement_style: str = "specific_evidence"
    preferred_pacing: str = "steady"
    reflection_history: list[dict[str, Any]] = field(default_factory=list)
    long_term_goals: list[dict[str, Any]] = field(default_factory=list)
    interaction_frequency: str = "medium"  # low|medium|high
    avatar_customization: dict[str, Any] = field(default_factory=dict)
    voice_preference: str = "Female"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompanionMessage:
    text: str
    kind: str  # greeting|encouragement|celebration|ef_coach|wellbeing|handoff_tutor
    companion_id: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    speakable: bool = True
    refer_to_atie: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
