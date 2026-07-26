"""English language misconception library — pattern detection via SICS."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

ENGLISH_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "eng.main_idea_first_sentence",
        "label": "Main idea is always the first sentence",
        "domain": "reading",
        "patterns": [
            r"main\s*idea\s*(is\s*)?(always\s*)?(the\s*)?first\s*sentence",
            r"topic\s*sentence\s*(is\s*)?(always\s*)?main\s*idea",
        ],
        "correction": "Main idea can be stated or implied and may appear anywhere; verify with supporting details.",
        "related_concepts": ["main_idea", "supporting_details"],
    },
    {
        "misconception_id": "eng.synonym_exact",
        "label": "Synonyms are always interchangeable",
        "domain": "vocabulary",
        "patterns": [
            r"synonyms?\s*(are\s*)?(always\s*)?(the\s*)?same",
            r"any\s*synonym\s*works\s*in\s*any\s*sentence",
        ],
        "correction": "Synonyms share related meanings but differ in register, collocation, and nuance.",
        "related_concepts": ["synonym", "collocation", "register"],
    },
    {
        "misconception_id": "eng.passive_always_wrong",
        "label": "Passive voice is always incorrect",
        "domain": "grammar",
        "patterns": [
            r"passive\s*voice\s*(is\s*)?(always\s*)?(wrong|incorrect|bad)",
            r"never\s*use\s*passive",
        ],
        "correction": "Passive voice is a choice for focus/agency; teach when it is appropriate, not ban it.",
        "related_concepts": ["voice", "agency", "style"],
    },
    {
        "misconception_id": "eng.longer_better",
        "label": "Longer sentences/essays are always better",
        "domain": "writing",
        "patterns": [
            r"longer\s*(essays?|sentences?)\s*(are\s*)?(always\s*)?better",
            r"more\s*words\s*means\s*better\s*writing",
        ],
        "correction": "Clarity, organisation, and evidence matter more than length; revise for purpose and audience.",
        "related_concepts": ["clarity", "organisation", "revision"],
    },
    {
        "misconception_id": "eng.theme_equals_topic",
        "label": "Theme equals topic",
        "domain": "literature",
        "patterns": [
            r"theme\s*(is\s*)?(the\s*)?same\s*as\s*topic",
            r"theme\s*(is\s*)?just\s*what\s*happens",
        ],
        "correction": "Topic is what the text is about; theme is the insight or message developed through the text.",
        "related_concepts": ["theme", "topic", "motif"],
    },
    {
        "misconception_id": "eng.reading_aloud_only_fluency",
        "label": "Reading aloud alone proves comprehension",
        "domain": "reading",
        "patterns": [
            r"reading\s*aloud\s*(means|proves)\s*comprehension",
            r"fluency\s*(is\s*)?(the\s*)?same\s*as\s*understanding",
        ],
        "correction": "Fluency supports comprehension but is not the same; check with retell, inference, and evidence.",
        "related_concepts": ["fluency", "comprehension"],
    },
    {
        "misconception_id": "eng.pronunciation_accent_wrong",
        "label": "Any non-native accent is incorrect pronunciation",
        "domain": "pronunciation",
        "patterns": [
            r"accent\s*(is\s*)?(always\s*)?wrong",
            r"only\s*(british|american)\s*accent\s*is\s*correct",
        ],
        "correction": "Focus on intelligibility and phoneme clarity; accents are varieties, not errors.",
        "related_concepts": ["intelligibility", "phonics", "stress"],
    },
)


def detect_english_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    return detect_from_catalogue(
        ENGLISH_MISCONCEPTIONS,
        text,
        provenance="english_language_intelligence.misconceptions",
        limit=limit,
    )
