"""Emotion tags for companion responses — pedagogical affect, not clinical diagnosis."""

from __future__ import annotations

from typing import Any


def infer_affect(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    conf = float(context.get("confidence") or 0.5)
    frustration = float(context.get("frustration") or 0)
    if frustration >= 0.6 or conf < 0.35:
        affect = "needs_support"
    elif conf >= 0.75:
        affect = "confident"
    else:
        affect = "steady"
    return {
        "affect": affect,
        "confidence": conf,
        "frustration": frustration,
        "note": "Affect tags are learning-state heuristics — not mental-health assessments",
        "clinical": False,
    }
