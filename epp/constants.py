"""EPP constants — product perfection markers only."""

from __future__ import annotations

ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK = True
EPP_VERSION = "1.0.0"
EPP_SCHEMA = "alora.epp.v1"

# Phrases that make a lesson feel AI/template/mechanical to a publisher reader
ROBOTIC_TRANSITIONS = (
    "in this section",
    "as mentioned above",
    "it is important to note",
    "let us now",
    "we will now",
    "moving forward",
    "furthermore",
    "moreover",
    "in conclusion",
    "without further ado",
    "delve",
    "dive into",
    "in today's world",
    "as an ai",
    "great question",
)

SCAFFOLD_LEAKS = (
    "notice how",
    "students will",
    "learners will",
    "worth mastering",
    "memory tip",
    "picture:",
    "checkpoint:",
    "core idea in this lesson",
    "learning objective",
)

# Board fields that must become learner-visible somewhere in the package
BOARD_TO_LEARNER = (
    ("examples", "example"),
    ("misconceptions", "misconception"),
    ("verified_claims", "explanation"),
    ("vocabulary", "vocabulary"),
    ("visual_opportunities", "diagram"),
    ("learning_goals", "practice"),
)

PERSONA_INTENTS = {
    "standard": "clear master-teacher explanation with one vivid example",
    "adhd": "short missions, movement, checklist energy",
    "autism": "predictable steps, literal language, calm sequence",
    "ell": "simple words, say-it-aloud, cognate-friendly",
    "visual": "see-label-trace diagram language",
    "auditory": "listen-say-retell language",
    "ld": "step-by-step chunks with one check",
    "dyslexia": "short lines, high-frequency words, oral check",
    "teacher": "teachable moves and exit tickets (adult page)",
    "parent": "warm home conversation, no jargon",
    "vocabulary": "memorable flashcards that teach retention",
    "worksheet": "practice that measures learning",
}

PUBLISHER_BENCHMARKS = (
    "Pearson",
    "Oxford",
    "Cambridge",
    "National Geographic Learning",
    "Scholastic",
)
