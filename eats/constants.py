"""Educational Acceptance Testing System — constants and pass bands."""

from __future__ import annotations

EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK = True

EATS_VERSION = "1.0.0"
EATS_SCHEMA = "alora.eats.v1"

# Pass criteria (overall publisher score / 100)
PUBLISHER_READY = 95
EXCELLENT_MIN = 90
GOOD_MIN = 85
NEEDS_IMPROVEMENT_MIN = 80
# Below 80 → Reject

MAX_REVISE_ATTEMPTS = 3
GOLDEN_PROMOTION_SCORE = 98

# Adaptations evaluated independently (product + LCE extras)
EATS_ADAPTATION_KEYS = (
    "standard",  # Mainstream
    "vocabulary",
    "visual",
    "auditory",
    "adhd",
    "autism",
    "dyslexia",
    "ell",
    "ld",
    "teacher",
    "parent",
    "worksheet",  # Exam Worksheet
)

SCORE_DIMENSIONS = (
    "writing_quality",
    "educational_quality",
    "visual_quality",
    "accessibility",
    "pedagogy",
    "vocabulary",
    "layout",
    "adaptation",
    "assessment",
    "diagram",
)

AI_PHRASES = (
    "delve",
    "dive into",
    "in conclusion",
    "as an ai",
    "certainly!",
    "great question",
    "let's explore",
    "in this lesson we will explore",
    "it is important to note that",
    "in today's fast-paced world",
    "without further ado",
    "in this article",
    "as previously mentioned",
)

ADAPTATION_SIGNATURES: dict[str, tuple[str, ...]] = {
    "adhd": ("chunk", "focus", "micro", "break", "short", "checkpoint", "movement", "pause"),
    "autism": ("predictable", "literal", "routine", "step", "clear", "structure", "same", "next"),
    "ell": ("key word", "sentence", "frame", "scaffold", "simple", "vocabulary", "model", "cognate"),
    "visual": ("diagram", "map", "flowchart", "icon", "see", "picture", "colour", "color", "look"),
    "auditory": ("listen", "say", "discuss", "oral", "hear", "speak", "narrat", "repeat"),
    "teacher": ("misconception", "differentiate", "pedagog", "assess", "note", "guidance", "teacher"),
    "parent": ("home", "conversation", "family", "practice at", "support", "ask your", "try asking"),
    "dyslexia": (
        "chunk",
        "font",
        "spacing",
        "phon",
        "read aloud",
        "decode",
        "syllable",
        "bold",
        "dyslexia",
        "reading support",
        "sound",
        "break the word",
    ),
    "vocabulary": ("pronunciation", "definition", "memory", "synonym", "word"),
    "worksheet": ("marks", "question", "exam", "revise", "practice", "answer"),
    "ld": ("scaffold", "step", "support", "chunk", "check", "guided"),
    "standard": ("example", "practice", "summary", "concept"),
}

VOCAB_REQUIRED_FIELDS = (
    "term",
    "pronunciation",
    "part_of_speech",
    "definition",
    "student_friendly_definition",
    "academic_definition",
    "example",
    "memory_tip",
)

SUBJECT_KEYS = (
    "math",
    "mathematics",
    "physics",
    "chemistry",
    "biology",
    "science",
    "english",
    "history",
    "geography",
    "economics",
    "computer_science",
    "cs",
    "languages",
    "general",
)


def band_for_score(score: float) -> str:
    if score >= PUBLISHER_READY:
        return "publisher_ready"
    if score >= EXCELLENT_MIN:
        return "excellent"
    if score >= GOOD_MIN:
        return "good"
    if score >= NEEDS_IMPROVEMENT_MIN:
        return "needs_improvement"
    return "reject"


def verdict_for_score(score: float) -> str:
    """Pass / Revise / Reject for the acceptance pipeline."""
    if score >= PUBLISHER_READY:
        return "pass"
    if score >= NEEDS_IMPROVEMENT_MIN:
        return "revise"
    return "reject"
