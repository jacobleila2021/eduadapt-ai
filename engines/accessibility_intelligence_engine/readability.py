"""Readability engine — wraps analytics_engine; recommends presentation tweaks only."""

from __future__ import annotations

import re
from typing import Any


def readability_report(text: str) -> dict[str, Any]:
    raw = text or ""
    sentences = [s for s in re.split(r"[.!?]+", raw) if s.strip()]
    words = re.findall(r"[A-Za-z']+", raw)
    word_count = len(words)
    sent_count = max(len(sentences), 1)
    avg_sent_len = word_count / sent_count
    long_words = sum(1 for w in words if len(w) >= 8)
    vocab_complexity = (long_words / word_count) if word_count else 0.0
    passive = len(re.findall(r"\b(is|are|was|were|be|been)\s+\w+ed\b", raw, flags=re.I))
    passive_ratio = passive / sent_count

    complexity = None
    reading_level = None
    try:
        from analytics_engine import compute_lesson_complexity_score, estimate_reading_level

        complexity = compute_lesson_complexity_score(raw)
        reading_level = estimate_reading_level(raw)
    except Exception:  # noqa: BLE001
        complexity = int(min(100, avg_sent_len * 3 + vocab_complexity * 40))
        reading_level = "unknown"

    # Cognitive load heuristic
    load = "low"
    if avg_sent_len > 22 or vocab_complexity > 0.25 or (complexity or 0) > 70:
        load = "high"
    elif avg_sent_len > 16 or vocab_complexity > 0.15 or (complexity or 0) > 50:
        load = "medium"

    chunk_size = "standard"
    if load == "high":
        chunk_size = "small_2_3_sentences"
    elif load == "medium":
        chunk_size = "medium_paragraph"

    recommendations = []
    if load != "low":
        recommendations.append(
            {
                "action": "chunk_sentences",
                "detail": "Break long sentences for presentation; keep curriculum meaning",
                "preserves_meaning": True,
            }
        )
    if vocab_complexity > 0.2:
        recommendations.append(
            {
                "action": "glossary_highlight",
                "detail": "Highlight academic vocabulary with definitions (ELL/dyslexia)",
                "preserves_meaning": True,
            }
        )
    if passive_ratio > 0.3:
        recommendations.append(
            {
                "action": "prefer_active_voice_presentation",
                "detail": "Where equivalent, present in active voice without changing facts",
                "preserves_meaning": True,
            }
        )

    return {
        "word_count": word_count,
        "sentence_count": sent_count,
        "avg_sentence_length": round(avg_sent_len, 2),
        "vocabulary_complexity": round(vocab_complexity, 3),
        "passive_voice_ratio": round(passive_ratio, 3),
        "academic_density": round(vocab_complexity * 0.6 + min(avg_sent_len / 30, 1) * 0.4, 3),
        "cognitive_load": load,
        "recommended_chunk_size": chunk_size,
        "complexity_score": complexity,
        "reading_level": reading_level,
        "recommendations": recommendations,
        "policy": "presentation_improvements_only",
    }
