"""Adaptive difficulty — deterministic levels from mastery/confidence/load."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import DIFFICULTY_LEVELS, ExplainableDecision, LearnerModel


def select_difficulty(
    model: LearnerModel,
    *,
    concept_id: str = "",
    cognitive_load: str = "medium",
    error_rate: float | None = None,
    recent_progress: float | None = None,
) -> tuple[str, ExplainableDecision]:
    pct_hint = None
    # Infer from risk/mastered lists
    if concept_id and concept_id in model.concepts_at_risk:
        pct_hint = 0.3
    elif concept_id and concept_id in model.concepts_developing:
        pct_hint = 0.55
    elif concept_id and concept_id in model.concepts_mastered:
        pct_hint = 0.85

    confidence = float(model.confidence or 0.5)
    err = float(error_rate if error_rate is not None else (0.5 if pct_hint and pct_hint < 0.5 else 0.2))
    progress = float(recent_progress if recent_progress is not None else confidence)

    # Deterministic scoring (no randomness)
    score = 0.0
    evidence: list[dict[str, Any]] = []
    if pct_hint is not None:
        score += pct_hint * 0.45
        evidence.append({"factor": "concept_mastery_band", "value": pct_hint})
    else:
        score += 0.5 * 0.45
        evidence.append({"factor": "concept_mastery_band", "value": "unknown_default_0.5"})
    score += confidence * 0.25
    evidence.append({"factor": "confidence", "value": confidence})
    score += (1.0 - err) * 0.15
    evidence.append({"factor": "error_pattern", "value": err})
    score += progress * 0.1
    evidence.append({"factor": "recent_progress", "value": progress})

    load_pen = {"low": 0.05, "medium": 0.0, "high": -0.1}.get((cognitive_load or "medium").lower(), 0.0)
    score += load_pen
    evidence.append({"factor": "cognitive_load", "value": cognitive_load, "penalty": load_pen})

    if score < 0.35:
        level = "foundation"
    elif score < 0.5:
        level = "guided"
    elif score < 0.7:
        level = "standard"
    elif score < 0.82:
        level = "advanced"
    elif score < 0.92:
        level = "extension"
    else:
        level = "challenge"

    # Gifted / 2e nudge toward extension when mastery allows
    if "gifted" in model.accessibility_profiles or "twice_exceptional" in model.accessibility_profiles:
        if level in ("standard", "advanced") and score >= 0.65:
            level = "extension"
            evidence.append({"factor": "gifted_enrichment_nudge", "value": True})

    explanation = (
        f"Difficulty set to '{level}' because mastery band={pct_hint if pct_hint is not None else 'unknown'}, "
        f"confidence={confidence:.0%}, error_rate={err:.0%}, cognitive_load={cognitive_load}, "
        f"composite_score={score:.2f}. Presentation only — curriculum facts unchanged."
    )
    decision = ExplainableDecision(
        decision_id=f"diff_{concept_id or 'general'}_{level}",
        decision_type="difficulty",
        choice=level,
        explanation=explanation,
        evidence=evidence,
        confidence=min(0.95, 0.55 + abs(score - 0.5)),
    )
    return level, decision


def difficulty_catalog() -> list[str]:
    return list(DIFFICULTY_LEVELS)
