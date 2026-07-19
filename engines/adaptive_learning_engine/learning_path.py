"""Learning pathway builder — explainable, auditable pathways."""

from __future__ import annotations

import uuid
from typing import Any

from engines.adaptive_learning_engine.mastery import select_difficulty
from engines.adaptive_learning_engine.pacing import select_pacing
from engines.adaptive_learning_engine.schemas import ExplainableDecision, LearnerModel, PathwayStep, PATHWAY_TYPES
from engines.adaptive_learning_engine.sequencing import sequence_concepts


def build_learning_path(
    model: LearnerModel,
    *,
    cie: dict[str, Any] | None = None,
    aie: dict[str, Any] | None = None,
    pathway_type: str = "mastery",
    teacher_priorities: list[str] | None = None,
    allow_skip_prerequisites: bool = False,
    cognitive_load: str = "medium",
) -> dict[str, Any]:
    cie = cie or {}
    aie = aie or {}
    if pathway_type not in PATHWAY_TYPES:
        pathway_type = "mastery"

    # Teacher override check
    skip = allow_skip_prerequisites
    for ov in model.teacher_overrides or []:
        if ov.get("decision_type") == "sequencing" and ov.get("choice") == "allow_skip_prerequisites":
            skip = True

    steps, seq_decision = sequence_concepts(
        model,
        cie=cie,
        teacher_priorities=teacher_priorities,
        allow_skip_prerequisites=skip,
    )

    presentation = (aie.get("presentation") or {}).get("primary_mode") or (
        (aie.get("profiles_generated") or ["standard"])[0]
    )
    path_steps: list[dict[str, Any]] = []
    decisions: list[ExplainableDecision] = [seq_decision]

    for step in steps[:8]:
        diff, diff_dec = select_difficulty(model, concept_id=step.concept_id, cognitive_load=cognitive_load)
        pace, pace_dec = select_pacing(model, difficulty=diff, cognitive_load=cognitive_load)
        decisions.append(diff_dec)
        decisions.append(pace_dec)
        enriched = PathwayStep(
            step_id=step.step_id,
            concept_id=step.concept_id,
            title=step.title,
            activity_type=_activity_for_pathway(pathway_type, step),
            difficulty=diff,
            presentation_mode=presentation,
            rationale=step.rationale,
            prerequisites_ok=step.prerequisites_ok,
            estimated_minutes=int(pace.get("lesson_length_minutes") or step.estimated_minutes),
        )
        path_steps.append({**enriched.to_dict(), "pacing": pace})

    path_id = f"path_{uuid.uuid4().hex[:8]}"
    path_explanation = (
        f"Pathway '{pathway_type}' for learner {model.learner_id}: "
        f"{len(path_steps)} steps, presentation='{presentation}'. "
        f"Next activity: {path_steps[0]['concept_id'] if path_steps else 'none'} "
        f"at difficulty '{path_steps[0]['difficulty'] if path_steps else 'n/a'}' "
        f"because mastery/confidence and accessibility profile drove sequencing and pacing."
    )
    path_decision = ExplainableDecision(
        decision_id=path_id,
        decision_type="pathway",
        choice=pathway_type,
        explanation=path_explanation,
        evidence=[
            {"factor": "presentation_mode", "value": presentation},
            {"factor": "step_count", "value": len(path_steps)},
            {"factor": "accessibility_profiles", "value": model.accessibility_profiles},
            {"factor": "confidence", "value": model.confidence},
        ],
        confidence=0.86,
    )
    decisions.insert(0, path_decision)

    return {
        "path_id": path_id,
        "pathway_type": pathway_type,
        "learner_id": model.learner_id,
        "steps": path_steps,
        "next_activity": path_steps[0] if path_steps else None,
        "decisions": [d.to_dict() for d in decisions],
        "explainability": path_decision.to_dict(),
        "policy": {
            "does_not_generate_lessons": True,
            "uses_verified_engines_only": True,
            "prerequisites_enforced": not skip,
            "teacher_override_allowed": True,
        },
    }


def _activity_for_pathway(pathway_type: str, step: PathwayStep) -> str:
    if pathway_type == "remediation":
        return "remediation"
    if pathway_type == "enrichment":
        return "enrichment"
    if pathway_type == "adaptive_review":
        return "review"
    if step.activity_type:
        return step.activity_type
    return "lesson"
