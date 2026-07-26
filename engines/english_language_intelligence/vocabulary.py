"""Vocabulary intelligence metadata — scaffolds from source; no invented lexicon as curriculum."""

from __future__ import annotations

import re
from typing import Any, Mapping

_WORD = re.compile(r"\b[A-Za-z][A-Za-z'-]{2,}\b")

_ACADEMIC_HINTS = {
    "analyze",
    "analyse",
    "compare",
    "contrast",
    "evaluate",
    "infer",
    "interpret",
    "justify",
    "persuade",
    "significant",
    "evidence",
    "context",
    "theme",
    "structure",
}


def _candidate_words(text: str, *, limit: int = 20) -> list[str]:
    skip = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "from",
        "have",
        "will",
        "are",
        "was",
        "were",
        "their",
        "there",
        "about",
        "which",
        "when",
        "what",
        "your",
        "into",
        "students",
        "lesson",
        "subject",
        "english",
        "grade",
        "level",
    }
    seen: set[str] = set()
    out: list[str] = []
    for m in _WORD.finditer(text or ""):
        w = m.group(0)
        low = w.lower()
        if low in skip or low in seen:
            continue
        seen.add(low)
        out.append(w)
        if len(out) >= limit:
            break
    return out


def _tier(word: str) -> str:
    low = word.lower()
    if low in _ACADEMIC_HINTS or len(low) >= 10:
        return "tier_2"
    if low.endswith(("tion", "sion", "ment", "ology", "ity")):
        return "tier_2"
    return "tier_1"


def vocabulary_metadata(text: str, uli: Any | None = None) -> dict[str, Any]:
    words = _candidate_words(text)
    # Prefer ULI vocabulary when present
    if uli is not None:
        try:
            learn = dict(uli.learning_structure())
            for v in learn.get("vocabulary") or []:
                if isinstance(v, Mapping):
                    term = str(v.get("term") or "").strip()
                    if term and term not in words:
                        words.insert(0, term)
        except Exception:  # noqa: BLE001
            pass
    entries = []
    for w in words[:12]:
        entries.append(
            {
                "term": w,
                "tier": _tier(w),
                "definition_prompt": "Use the lesson glossary / context; do not invent definitions beyond source.",
                "simplified_meaning_prompt": "Offer a plain-language paraphrase after checking the verified meaning.",
                "synonyms_prompt": "List only synonyms supported by the lesson or dictionary policy.",
                "antonyms_prompt": "List only antonyms supported by the lesson.",
                "word_family_prompt": "Note related forms if present in the lesson.",
                "affixes_prompt": "Identify prefix/suffix/root only when morphologically clear.",
                "idiom_collocation_prompt": "Flag idioms/collocations if they appear in the source.",
                "context_clue_prompt": "Use surrounding sentences from the lesson for meaning.",
                "example_sentence_prompt": "Prefer example sentences from the verified text.",
                "frequency": "unknown",
                "reading_difficulty": "developing" if _tier(w) == "tier_2" else "accessible",
            }
        )
    return {
        "entries": entries,
        "tiers_supported": ["tier_1", "tier_2", "tier_3"],
        "features": [
            "definitions",
            "simplified_meanings",
            "academic_vocabulary",
            "synonyms",
            "antonyms",
            "word_families",
            "prefixes",
            "suffixes",
            "roots",
            "idioms",
            "collocations",
            "context_clues",
            "example_sentences",
            "reading_difficulty",
            "frequency_metadata",
        ],
        "provenance": "english_language_intelligence.vocabulary",
    }
