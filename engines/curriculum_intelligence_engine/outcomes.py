"""Learning outcome + Bloom / Webb DOK helpers."""

from __future__ import annotations

from typing import Any

BLOOM_LEVELS = ("remember", "understand", "apply", "analyze", "evaluate", "create")
WEBB_DOK = {
    "1": "Recall and reproduction",
    "2": "Skills and concepts",
    "3": "Strategic thinking",
    "4": "Extended thinking",
}


def normalize_bloom(raw: str) -> str:
    key = (raw or "").strip().lower()
    aliases = {
        "knowledge": "remember",
        "comprehension": "understand",
        "application": "apply",
        "analysis": "analyze",
        "analyse": "analyze",
        "synthesis": "create",
        "evaluation": "evaluate",
    }
    key = aliases.get(key, key)
    return key if key in BLOOM_LEVELS else "understand"


def normalize_dok(raw: str | int) -> str:
    s = str(raw or "").strip()
    if s in WEBB_DOK:
        return s
    return "2"


def map_equivalent_outcomes(
    outcomes: list[dict[str, Any]],
    *,
    concept_id: str | None = None,
) -> list[dict[str, Any]]:
    """Group outcomes that share concept_ids as cross-curriculum equivalents."""
    filtered = outcomes
    if concept_id:
        filtered = [o for o in outcomes if concept_id in (o.get("concept_ids") or [])]
    by_concept: dict[str, list[dict[str, Any]]] = {}
    for o in filtered:
        for cid in o.get("concept_ids") or ["_"]:
            by_concept.setdefault(cid, []).append(o)
    return [
        {"concept_id": cid, "outcomes": rows, "count": len(rows)}
        for cid, rows in by_concept.items()
    ]


def outcome_coverage(concept_ids: list[str], outcomes: list[dict[str, Any]]) -> dict[str, Any]:
    covered = {
        cid
        for o in outcomes
        for cid in (o.get("concept_ids") or [])
        if cid in concept_ids
    }
    missing = [c for c in concept_ids if c not in covered]
    return {
        "requested": concept_ids,
        "covered": sorted(covered),
        "missing": missing,
        "coverage_ratio": (len(covered) / len(concept_ids)) if concept_ids else 0.0,
    }
