"""Pronunciation coaching — listen / repeat / compare; no invented IPA."""

from __future__ import annotations

from typing import Any
import re

from engines.voice_multimodal_learning.schemas import PronunciationAttempt

# Curated stress hints for common STEM terms (verified resources / pedagogy lists)
_STRESS_HINTS: dict[str, dict[str, Any]] = {
    "chloroplast": {"syllables": ["chlo", "ro", "plast"], "stress": 0},
    "photosynthesis": {"syllables": ["pho", "to", "syn", "the", "sis"], "stress": 3},
    "mitochondria": {"syllables": ["mi", "to", "chon", "dri", "a"], "stress": 2},
    "hypotenuse": {"syllables": ["hy", "pot", "e", "nuse"], "stress": 1},
    "coefficient": {"syllables": ["co", "ef", "fi", "cient"], "stress": 2},
    "stoichiometry": {"syllables": ["stoi", "chi", "om", "e", "try"], "stress": 2},
    "acceleration": {"syllables": ["ac", "cel", "er", "a", "tion"], "stress": 3},
}


def syllable_breakdown(word: str) -> list[str]:
    key = (word or "").strip().lower()
    if key in _STRESS_HINTS:
        return list(_STRESS_HINTS[key]["syllables"])
    # Heuristic split on vowel groups — presentation aid only, not invented phonetics claim
    parts = re.findall(r"[^aeiouy]*[aeiouy]+[^aeiouy]*", key, flags=re.I) or [key]
    return [p for p in parts if p]


def stress_pattern(word: str) -> dict[str, Any]:
    key = (word or "").strip().lower()
    syllables = syllable_breakdown(key)
    if key in _STRESS_HINTS:
        return {"syllables": syllables, "primary_stress_index": _STRESS_HINTS[key]["stress"], "source": "curated"}
    return {"syllables": syllables, "primary_stress_index": 0 if syllables else None, "source": "heuristic"}


def coach(
    word: str,
    *,
    heard: str = "",
    slow_mode: bool = False,
) -> PronunciationAttempt:
    target = (word or "").strip()
    heard_n = (heard or "").strip()
    syllables = syllable_breakdown(target)
    accuracy = _compare(target, heard_n)
    feedback = _feedback(accuracy, slow_mode=slow_mode)
    return PronunciationAttempt(
        word=target,
        heard=heard_n,
        accuracy=accuracy,
        syllables=syllables,
        feedback=feedback,
        slow_mode=slow_mode,
    )


def _compare(target: str, heard: str) -> float:
    if not target:
        return 0.0
    if not heard:
        return 0.0
    t = re.sub(r"[^a-z]", "", target.lower())
    h = re.sub(r"[^a-z]", "", heard.lower())
    if t == h:
        return 1.0
    # simple character overlap ratio
    shared = sum(1 for a, b in zip(t, h) if a == b)
    return round(shared / max(len(t), len(h), 1), 3)


def _feedback(accuracy: float, *, slow_mode: bool) -> str:
    if accuracy >= 0.9:
        return "Great pronunciation!"
    if accuracy >= 0.7:
        return "Close — try again, focusing on stressed syllables." + (" (slow mode on)" if slow_mode else "")
    if accuracy > 0:
        return "Listen again, then repeat slowly."
    return "Tap Listen, then Repeat when ready."


def practice_card(word: str, *, category: str = "vocabulary") -> dict[str, Any]:
    stress = stress_pattern(word)
    return {
        "word": word,
        "category": category,  # vocabulary|scientific|math|chemical|historical|foreign
        "actions": ["listen", "repeat", "compare"],
        "syllables": stress["syllables"],
        "stress": stress,
        "slow_pronunciation_mode": True,
        "policy": "use_curated_or_heuristic_only_never_llm_invented_ipa",
    }
