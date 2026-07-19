"""Pacing engine — lesson length, chunks, practice frequency."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import ExplainableDecision, LearnerModel


def select_pacing(
    model: LearnerModel,
    *,
    difficulty: str = "standard",
    cognitive_load: str = "medium",
) -> tuple[dict[str, Any], ExplainableDecision]:
    profiles = set(model.accessibility_profiles or [])
    base_minutes = {"foundation": 20, "guided": 18, "standard": 15, "advanced": 12, "extension": 14, "challenge": 16}.get(
        difficulty, 15
    )
    chunk = "medium"
    examples = 2
    practice_freq = "normal"
    reflection_min = 3
    review_freq = "standard"
    tutor_freq = "as_needed"

    evidence: list[dict[str, Any]] = [{"factor": "difficulty", "value": difficulty}]

    if profiles.intersection({"adhd", "executive_function", "processing_speed"}):
        base_minutes = min(base_minutes, 10)
        chunk = "small_2min"
        examples = 3
        practice_freq = "high"
        tutor_freq = "frequent"
        evidence.append({"factor": "attention_ef_support", "value": True})

    if "dyslexia" in profiles or "ell" in profiles:
        examples = max(examples, 3)
        reflection_min = 4
        evidence.append({"factor": "reading_language_support", "value": True})

    if cognitive_load == "high":
        chunk = "small_2min"
        base_minutes = min(base_minutes, 12)
        evidence.append({"factor": "high_cognitive_load", "value": True})

    if profiles.intersection({"gifted", "twice_exceptional"}) and difficulty in ("extension", "challenge", "advanced"):
        # Faster through known material, deeper on extension
        if model.concepts_at_risk:
            practice_freq = "high"
        else:
            base_minutes = max(8, base_minutes - 3)
            tutor_freq = "socratic_depth"
        evidence.append({"factor": "gifted_pacing", "value": True})

    if "adult" in profiles or "professional" in profiles:
        reflection_min = 2
        chunk = "self_paced"
        evidence.append({"factor": "adult_professional", "value": True})

    if model.concepts_at_risk:
        practice_freq = "high"
        review_freq = "elevated"
        evidence.append({"factor": "at_risk_concepts", "count": len(model.concepts_at_risk)})

    pacing = {
        "lesson_length_minutes": base_minutes,
        "chunk_size": chunk,
        "examples_count": examples,
        "practice_frequency": practice_freq,
        "reflection_minutes": reflection_min,
        "review_frequency": review_freq,
        "ai_tutor_frequency": tutor_freq,
        "policy": "presentation_pacing_only",
    }
    explanation = (
        f"Pacing: {base_minutes} min lessons, chunk={chunk}, {examples} examples, "
        f"practice={practice_freq}, tutor={tutor_freq} based on accessibility={sorted(profiles) or ['neurotypical']} "
        f"and {len(model.concepts_at_risk)} at-risk concepts."
    )
    decision = ExplainableDecision(
        decision_id=f"pace_{difficulty}_{chunk}",
        decision_type="pacing",
        choice=json_safe(pacing),
        explanation=explanation,
        evidence=evidence,
        confidence=0.85,
    )
    # choice should be string for schema - store summary
    decision.choice = f"{base_minutes}min/{chunk}/{practice_freq}"
    return pacing, decision


def json_safe(obj: Any) -> str:
    return str(obj)
