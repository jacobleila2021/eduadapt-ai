"""Shared assessment metadata builders — AME remains assessment owner."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from engines.subject_intelligence_core.utilities import learning_structure_dict

ExtraFieldsFn = Callable[[int, str | None], dict[str, Any]]


def extract_learning_objectives(uli: Any) -> list[Any]:
    learn = learning_structure_dict(uli)
    return list(learn.get("learning_objectives") or [])


def build_assessment_hints(
    uli: Any,
    domains: list[dict[str, Any]],
    *,
    provenance: str,
    default_domain: str = "general",
    extra_fields: ExtraFieldsFn | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    objectives = extract_learning_objectives(uli)
    diagnostic = domains[0]["domain"] if domains else default_domain
    hints: list[dict[str, Any]] = []
    for i, obj in enumerate(objectives[:limit]):
        text = obj.get("objective") if isinstance(obj, Mapping) else str(obj)
        row: dict[str, Any] = {
            "objective_ref": text,
            "bloom_hint": "apply" if i % 2 == 0 else "understand",
            "dok_hint": "2" if i < 4 else "3",
            "cognitive_demand": "medium",
            "difficulty_estimate": "developing",
            "diagnostic_focus": diagnostic,
            "owner": "AME",
            "provenance": provenance,
        }
        if extra_fields:
            row.update(extra_fields(i, text if isinstance(text, str) else None))
        hints.append(row)
    if not hints:
        row = {
            "objective_ref": None,
            "bloom_hint": "understand",
            "dok_hint": "2",
            "cognitive_demand": "medium",
            "difficulty_estimate": "developing",
            "diagnostic_focus": diagnostic,
            "owner": "AME",
            "provenance": provenance,
        }
        if extra_fields:
            row.update(extra_fields(0, None))
        hints.append(row)
    return hints


def build_revision_summary(
    domains: list[dict[str, Any]],
    misconceptions: list[dict[str, Any]],
    *,
    retrieval_prompts: list[str],
    provenance: str,
    intervals: list[int] | None = None,
) -> dict[str, Any]:
    return {
        "focus_domains": [d["domain"] for d in domains[:4]],
        "retrieval_prompts": list(retrieval_prompts),
        "spaced_practice": {
            "recommended_intervals_days": list(intervals or [1, 3, 7]),
            "interleave": True,
        },
        "misconception_review_ids": [m.get("misconception_id") for m in misconceptions[:6]],
        "provenance": provenance,
    }
