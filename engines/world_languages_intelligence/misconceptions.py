"""World languages misconceptions — SICS catalogue detection."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

WORLD_LANGUAGES_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "wl.word_for_word",
        "label": "Translation is always word-for-word",
        "domain": "translation",
        "patterns": [
            r"word[\s-]*for[\s-]*word\s*(is\s*)?(always|best)",
            r"translate\s*(each|every)\s*word\s*(literally|exactly)",
            r"literal\s*translation\s*(is\s*)?(always\s*)?(correct|best)",
        ],
        "correction": "Prefer meaning and register in context; literal calques often break grammar or culture.",
        "related_concepts": ["register", "contextual_meaning", "idioms"],
    },
    {
        "misconception_id": "wl.pronounce_like_english",
        "label": "Pronounce every language like English spelling",
        "domain": "pronunciation",
        "patterns": [
            r"pronounce\s*(it\s*)?(like|as)\s*english",
            r"pronounce\s*.{0,40}like\s*english",
            r"like\s*english\s*spelling",
            r"spelling\s*(always\s*)?(shows|equals)\s*sound",
            r"read\s*(foreign|other)\s*words?\s*(as\s*)?english",
        ],
        "correction": "Use target-language sound systems, IPA/script cues, and minimal pairs—not English orthography transfer.",
        "related_concepts": ["ipa", "phonemes", "script"],
    },
    {
        "misconception_id": "wl.grammar_same_as_english",
        "label": "Other languages use English word order/rules",
        "domain": "grammar",
        "patterns": [
            r"same\s*(grammar|word\s*order)\s*as\s*english",
            r"all\s*languages?\s*(use|follow)\s*svo",
            r"grammar\s*(is\s*)?(the\s*)?same\s*(in\s*)?every\s*language",
        ],
        "correction": "Map target-language patterns (order, agreement, cases, particles) explicitly against the learner’s L1.",
        "related_concepts": ["word_order", "agreement", "cases"],
    },
    {
        "misconception_id": "wl.vocab_one_meaning",
        "label": "Each word has only one meaning",
        "domain": "vocabulary",
        "patterns": [
            r"each\s*word\s*(has\s*)?(only\s*)?one\s*meaning",
            r"words?\s*(never|don't)\s*change\s*meaning",
        ],
        "correction": "Teach senses, collocations, and register; use context clues from the verified lesson.",
        "related_concepts": ["polysemy", "collocation", "context_clues"],
    },
    {
        "misconception_id": "wl.accent_equals_wrong",
        "label": "Any accent means incorrect speaking",
        "domain": "speaking",
        "patterns": [
            r"accent\s*(means|is)\s*(wrong|incorrect|bad)",
            r"must\s*sound\s*(exactly\s*)?(like\s*)?(a\s*)?native",
        ],
        "correction": "Prioritise intelligibility and communicative success; accents are normal in multilingual speakers.",
        "related_concepts": ["intelligibility", "fluency", "pronunciation"],
    },
    {
        "misconception_id": "wl.reading_aloud_only",
        "label": "Reading aloud is the only way to learn reading",
        "domain": "reading",
        "patterns": [
            r"reading\s*aloud\s*(is\s*)?(the\s*)?only\s*(way|method)",
            r"silent\s*reading\s*(does\s*not|doesn't)\s*(count|help)",
        ],
        "correction": "Balance fluency reading, silent comprehension, and strategy instruction from the lesson.",
        "related_concepts": ["fluency", "comprehension", "strategies"],
    },
)


def detect_world_languages_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    return detect_from_catalogue(
        WORLD_LANGUAGES_MISCONCEPTIONS,
        text,
        provenance="world_languages_intelligence.misconceptions",
        limit=limit,
    )
