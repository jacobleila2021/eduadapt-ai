"""Misconception detection — curated patterns + response evidence."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from engines.assessment_mastery_engine.schemas import MisconceptionHit

DATA = Path(__file__).resolve().parent / "data" / "misconceptions_class8_science.json"


@lru_cache(maxsize=1)
def load_misconception_bank() -> dict[str, Any]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def list_misconceptions(concept_id: str | None = None) -> list[dict[str, Any]]:
    rows = list(load_misconception_bank().get("misconceptions") or [])
    if concept_id:
        rows = [
            m
            for m in rows
            if m.get("concept_id") == concept_id or concept_id in (m.get("related_concepts") or [])
        ]
    return rows


def detect_from_text(
    text: str,
    *,
    concept_ids: list[str] | None = None,
) -> list[MisconceptionHit]:
    blob = (text or "").strip().lower()
    if not blob:
        return []
    hits: list[MisconceptionHit] = []
    for m in list_misconceptions():
        if concept_ids:
            related = set(m.get("related_concepts") or []) | {m.get("concept_id")}
            if not related.intersection(concept_ids):
                continue
        patterns = [p.lower() for p in (m.get("patterns") or [])]
        matched = [p for p in patterns if p in blob]
        if not matched:
            continue
        conf = min(0.95, 0.45 + 0.15 * len(matched))
        hits.append(
            MisconceptionHit(
                misconception_id=m["misconception_id"],
                label=m["label"],
                concept_id=m.get("concept_id") or "",
                evidence=m.get("evidence_template") or f"Matched patterns: {matched}",
                confidence=round(conf, 3),
                intervention_ids=list(m.get("intervention_ids") or []),
            )
        )
    hits.sort(key=lambda h: -h.confidence)
    return hits


def detect_from_attempt(
    *,
    response: str,
    correct: bool | None,
    concept_id: str = "",
    question: str = "",
) -> list[MisconceptionHit]:
    """If incorrect, score response + question against misconception patterns."""
    if correct is True:
        return []
    blob = f"{response}\n{question}"
    cids = [concept_id] if concept_id else None
    hits = detect_from_text(blob, concept_ids=cids)
    # boost confidence slightly for confirmed wrong answers
    for h in hits:
        h.confidence = min(0.98, h.confidence + 0.1)
    return hits
