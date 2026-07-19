"""Accessibility Intelligence Engine schemas — functional supports only (no medical diagnoses)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Canonical profile keys (aligned with adaptation_specs + CIE + AME)
SUPPORTED_PROFILES = (
    "neurotypical",
    "dyslexia",
    "dysgraphia",
    "dyscalculia",
    "adhd",
    "autism",
    "executive_function",
    "processing_speed",
    "working_memory",
    "sld",
    "ell",
    "gifted",
    "twice_exceptional",
    "low_vision",
    "blind",
    "colour_vision_deficiency",
    "deaf",
    "hard_of_hearing",
    "motor",
    "adult",
    "professional",
    "visual",
    "auditory",
    "ld",
    "multisensory",
)

PRESENTATION_MODES = (
    "standard",
    "dyslexia",
    "visual",
    "auditory",
    "executive",
    "ell",
    "parent_summary",
    "teacher_guide",
    "exam_revision",
    "multisensory",
    "gifted",
    "university",
    "professional",
    "ld",
    "adhd",
    "autism",
    "dyscalculia",
    "dysgraphia",
)

WCAG_TARGET = "WCAG 2.2 AA"
UDL_VERSION = "UDL 3.0"


@dataclass
class LearnerAccessibilityProfile:
    learner_id: str
    age: int | None = None
    grade: str = ""
    reading_level: str = ""
    language_proficiency: str = ""  # e.g. ELL-A2, fluent
    vision_needs: list[str] = field(default_factory=list)
    hearing_needs: list[str] = field(default_factory=list)
    motor_accessibility: list[str] = field(default_factory=list)
    executive_function: str = ""  # low|typical|high_support
    working_memory: str = ""
    processing_speed: str = ""
    attention_profile: str = ""
    communication_profile: str = ""
    sensory_preferences: list[str] = field(default_factory=list)
    learning_preferences: list[str] = field(default_factory=list)
    preferred_modalities: list[str] = field(default_factory=list)
    preferred_font: str = ""
    preferred_colour_theme: str = ""
    preferred_line_spacing: float = 1.5
    preferred_paragraph_spacing: float = 1.2
    preferred_pacing: str = "standard"
    preferred_audio_speed: float = 1.0
    preferred_navigation_mode: str = "standard"
    preferred_assessment_format: str = "standard"
    active_profiles: list[str] = field(default_factory=list)
    teacher_accommodations: list[str] = field(default_factory=list)
    parent_accommodations: list[str] = field(default_factory=list)
    self_selected_preferences: dict[str, Any] = field(default_factory=dict)
    system_recommended_supports: list[str] = field(default_factory=list)
    accessibility_history: list[dict[str, Any]] = field(default_factory=list)
    # Explicit: never store medical diagnoses — functional preferences only
    stores_medical_diagnoses: bool = False

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnerAccessibilityProfile":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class AccessibilityRecommendation:
    support_id: str
    category: str  # reading|visual|audio|ef|assessment|navigation|interaction|language|sensory
    title: str
    reason: str
    evidence: str
    priority: int = 50
    expected_impact: str = "medium"
    confidence: float = 0.8
    presentation_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class InterfaceConfig:
    font: str = "system"
    font_size_px: int = 18
    colour_theme: str = "default"
    contrast: str = "aa"
    line_spacing: float = 1.5
    paragraph_spacing: float = 1.2
    margins: str = "comfortable"
    reading_ruler: bool = False
    focus_mode: bool = False
    animation_reduction: bool = False
    keyboard_navigation: bool = True
    touch_targets: str = "standard"  # standard|large
    icon_size: str = "standard"
    toolbar_layout: str = "full"
    navigation_complexity: str = "standard"
    distraction_level: str = "low"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
