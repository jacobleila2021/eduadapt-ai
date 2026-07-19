"""Misconception bridge — wraps AME detectors; links to interventions."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import LearnerModel


def detect_misconceptions(
    model: LearnerModel,
    *,
    lesson_text: str = "",
    ame: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    ame = ame or {}
    hits = list(ame.get("misconceptions") or [])
    # Also scan lesson/topic text via AME detector
    try:
        from engines.assessment_mastery_engine.misconceptions import detect_from_text

        cids = model.concepts_at_risk + model.concepts_developing
        extra = detect_from_text(lesson_text, concept_ids=cids or None)
        for h in extra:
            row = h.to_dict() if hasattr(h, "to_dict") else h
            if row.get("misconception_id") not in {x.get("misconception_id") for x in hits}:
                hits.append(row)
    except Exception:  # noqa: BLE001
        pass
    return hits
