"""Adaptive assessment — select items by mastery + accessibility (presentation rigor preserved)."""

from __future__ import annotations

from typing import Any

from engines.assessment_mastery_engine.assessments import generate_assessment
from engines.assessment_mastery_engine.store import load_learner


DIFFICULTY_ORDER = ("easy", "medium", "hard")


def _target_difficulty(mastery_pct: float) -> str:
    if mastery_pct < 0.4:
        return "easy"
    if mastery_pct < 0.7:
        return "medium"
    return "hard"


def adaptive_assessment(
    *,
    learner_id: str,
    topic: str = "",
    lesson_text: str = "",
    concept_id: str = "",
    accessibility_profiles: list[str] | None = None,
    reading_level: str = "",
    limit: int = 5,
    cie_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = load_learner(learner_id)
    mastery = (state.get("mastery") or {}).get(concept_id) or {}
    pct = float(mastery.get("mastery_pct") or 0.0)
    target = _target_difficulty(pct)

    base = generate_assessment(
        assessment_type="adaptive",
        topic=topic,
        lesson_text=lesson_text,
        concept_ids=[concept_id] if concept_id else None,
        limit=limit * 2,
        learner_id=learner_id,
        cie_context=cie_context,
    )
    items = base.get("items") or []
    # filter toward target difficulty when tagged
    preferred = [i for i in items if (i.get("difficulty") or "medium").lower() == target]
    if len(preferred) < limit:
        preferred = preferred + [i for i in items if i not in preferred]
    selected = preferred[:limit]

    profiles = accessibility_profiles or []
    accommodations = []
    if any(p in profiles for p in ("dyslexia", "ell")):
        accommodations.append("extra_time_factor_1.5")
        accommodations.append("glossary_support")
        accommodations.append("dyslexia_friendly_font_hint")
    if "adhd" in profiles or "executive_function" in profiles:
        accommodations.append("chunked_items")
        accommodations.append("progress_checklist")
    if "autism" in profiles:
        accommodations.append("predictable_item_order")
        accommodations.append("explicit_success_criteria")
    if "dyscalculia" in profiles:
        accommodations.append("formula_card_allowed")
        accommodations.append("concrete_examples")
    if "gifted" in profiles:
        accommodations.append("extension_hots_optional")

    return {
        **base,
        "assessment_type": "adaptive",
        "items": selected,
        "item_count": len(selected),
        "adaptive": {
            "mastery_pct": pct,
            "target_difficulty": target,
            "reading_level": reading_level,
            "accessibility_profiles": profiles,
            "accommodations": accommodations,
            "academic_rigor_preserved": True,
            "note": "Presentation/time accommodations only — official items and answers unchanged.",
        },
    }
