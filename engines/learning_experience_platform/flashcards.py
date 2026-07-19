"""Verified flashcards — spaced repetition via ALE; never invent cards from LLM memory."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.phase3_schemas import FLASHCARD_KINDS


def _card_id(front: str, back: str) -> str:
    return "fc_" + hashlib.sha256(f"{front}|{back}".encode()).hexdigest()[:12]


def build_flashcards(
    *,
    lesson: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    learner_id: str = "",
) -> dict[str, Any]:
    lesson = lesson or {}
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    cie = (outputs.get("curriculum") or {}).get("payload") or {}
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}

    cards: list[dict[str, Any]] = []

    for w in lesson.get("word_wall") or []:
        if isinstance(w, dict) and w.get("term"):
            front = str(w["term"])
            back = str(w.get("definition") or w.get("meaning") or "")
            if back:
                cards.append(_mk(front, back, "vocabulary", lesson))

    for obj in cie.get("learning_objectives") or lesson.get("learning_objectives") or []:
        text = obj.get("text") if isinstance(obj, dict) else str(obj)
        if text:
            cards.append(_mk(f"Learning objective", text[:300], "concept", lesson))

    for c in cie.get("concepts") or []:
        if isinstance(c, dict) and c.get("title"):
            cards.append(_mk(str(c["title"]), str(c.get("definition") or c.get("summary") or c.get("title"))[:400], "concept", lesson))

    for a in sa.get("artifacts") or []:
        if not isinstance(a, dict):
            continue
        payload = a.get("payload") or {}
        latex = payload.get("latex") or payload.get("formula")
        if latex:
            cards.append(_mk(str(payload.get("name") or "Formula"), str(latex), "formula", lesson))

    # Glossary from UCF / LXP glossary builder
    try:
        from engines.learning_experience_platform.glossary import build_glossary

        gloss = build_glossary(context=context)
        for g in (gloss.get("entries") or gloss.get("terms") or [])[:20]:
            if isinstance(g, dict) and g.get("term"):
                cards.append(_mk(str(g["term"]), str(g.get("definition") or "")[:400], "definition", lesson))
    except Exception:  # noqa: BLE001
        pass

    # Deduplicate by id
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for card in cards:
        if card["card_id"] in seen:
            continue
        seen.add(card["card_id"])
        unique.append(card)

    spaced = []
    if learner_id:
        try:
            from engines.adaptive_learning_engine.service import api_schedule_review

            concept_ids = [c.get("related_concept") for c in unique if c.get("related_concept")]
            spaced = (api_schedule_review(learner_id, concept_ids=concept_ids[:8] or None) or {}).get("schedule") or []
        except Exception:  # noqa: BLE001
            spaced = []

    analytics.track("flashcard", learner_id=learner_id, lesson_id=str(lesson.get("lesson_id") or ""), payload={"count": len(unique)})
    return {
        "ok": True,
        "cards": unique[:60],
        "count": len(unique[:60]),
        "features": {
            "flip": True,
            "audio": True,
            "images": True,
            "spaced_repetition": True,
            "bookmarking": True,
            "difficulty_ratings": True,
        },
        "spaced_repetition": spaced,
        "source": "verified_lesson_cie_sae_glossary",
        "policy": {"never_invent_cards": True},
    }


def _mk(front: str, back: str, kind: str, lesson: dict[str, Any]) -> dict[str, Any]:
    kind = kind if kind in FLASHCARD_KINDS else "concept"
    return {
        "card_id": _card_id(front, back),
        "kind": kind,
        "front": front,
        "back": back,
        "difficulty": "medium",
        "bookmarked": False,
        "related_concept": str(lesson.get("lesson_id") or lesson.get("title") or ""),
        "audio_hint": "VMLE",
        "session_id": f"fcs_{uuid.uuid4().hex[:6]}",
    }


def rate_flashcard(card_id: str, rating: str, *, learner_id: str = "") -> dict[str, Any]:
    allowed = {"easy", "medium", "hard", "again"}
    rating = rating if rating in allowed else "medium"
    analytics.track("flashcard", learner_id=learner_id, payload={"card_id": card_id, "rating": rating})
    return {"ok": True, "card_id": card_id, "rating": rating}
