"""Confidence model — blends self-report, mastery, and readiness."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import LearnerModel


def estimate_confidence(
    model: LearnerModel,
    *,
    ame: dict[str, Any] | None = None,
    self_reported: float | None = None,
) -> dict[str, Any]:
    ame = ame or {}
    parts = []
    if self_reported is not None:
        parts.append(("self_reported", float(self_reported), 0.35))
    ready = ame.get("exam_readiness") or {}
    if ready.get("confidence_level") is not None:
        parts.append(("exam_readiness", float(ready["confidence_level"]), 0.35))
    mastery = ame.get("mastery") or {}
    strong = mastery.get("strong_concepts") or []
    weak = mastery.get("weak_concepts") or []
    if strong or weak:
        ratio = len(strong) / max(1, len(strong) + len(weak))
        parts.append(("mastery_balance", ratio, 0.3))
    if not parts:
        parts.append(("baseline", float(model.confidence or 0.5), 1.0))

    total_w = sum(w for _, _, w in parts)
    score = sum(v * w for _, v, w in parts) / total_w
    band = "low" if score < 0.4 else "moderate" if score < 0.7 else "high"
    return {
        "confidence": round(score, 4),
        "band": band,
        "factors": [{"name": n, "value": v, "weight": w} for n, v, w in parts],
    }
