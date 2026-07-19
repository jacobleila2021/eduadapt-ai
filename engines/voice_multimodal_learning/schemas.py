"""VMLE schemas — multimodal session contracts (presentation layer only)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PLAYBACK_SPEEDS = (0.75, 1.0, 1.25, 1.5, 1.75, 2.0)

VOICE_COMMANDS = (
    "read_this_page",
    "explain_this_concept",
    "slow_down",
    "speed_up",
    "repeat_that",
    "translate_this",
    "show_the_diagram",
    "open_glossary",
    "start_quiz",
    "next_question",
    "previous_page",
    "highlight_keywords",
    "show_examples",
    "ask_my_tutor",
)

HIGHLIGHT_MODES = ("word", "sentence", "paragraph")

SUPPORTED_LANGUAGES = ("en", "hi", "en-IN")


@dataclass
class VoiceSession:
    session_id: str
    learner_id: str = ""
    lesson_id: str = ""
    vlie_session_id: str = ""
    language: str = "en"
    speed: float = 1.0
    voice_style: str = "Female"
    highlight_mode: str = "sentence"
    offline: bool = False
    accessibility: dict[str, Any] = field(default_factory=dict)
    teacher_controls: dict[str, Any] = field(default_factory=dict)
    parent_controls: dict[str, Any] = field(default_factory=dict)
    bookmark: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NarrationPlan:
    text: str
    sentences: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    speed: float = 1.0
    language: str = "en"
    voice_style: str = "Female"
    source: str = "verified_lesson"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PronunciationAttempt:
    word: str
    heard: str = ""
    accuracy: float = 0.0
    syllables: list[str] = field(default_factory=list)
    feedback: str = ""
    slow_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
