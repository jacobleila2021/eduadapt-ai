"""Sequencing — prerequisite-safe order from CIE + AME mastery."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import ExplainableDecision, LearnerModel, PathwayStep


def sequence_concepts(
    model: LearnerModel,
    *,
    cie: dict[str, Any] | None = None,
    candidate_ids: list[str] | None = None,
    teacher_priorities: list[str] | None = None,
    allow_skip_prerequisites: bool = False,
) -> tuple[list[PathwayStep], ExplainableDecision]:
    """
    Do not allow skipping essential prerequisites unless explicitly overridden.
    """
    cie = cie or {}
    mastered = set(model.concepts_mastered or [])
    at_risk = list(model.concepts_at_risk or [])
    developing = list(model.concepts_developing or [])

    # Candidates: teacher priorities > at_risk > developing > CIE matched > recommend_next
    candidates: list[str] = []
    for src in (teacher_priorities or [], at_risk, developing, candidate_ids or []):
        for cid in src:
            if cid and cid not in candidates and cid not in mastered:
                candidates.append(cid)

    matched = cie.get("matched_concepts") or []
    for m in matched:
        cid = m.get("concept_id") if isinstance(m, dict) else None
        if cid and cid not in candidates and cid not in mastered:
            candidates.append(cid)

    next_recs = cie.get("next_concepts") or []
    for n in next_recs:
        cid = n.get("concept_id") if isinstance(n, dict) else n
        if cid and cid not in candidates and cid not in mastered:
            candidates.append(cid)

    # Prerequisite check via CIE gaps / graph
    steps: list[PathwayStep] = []
    blocked: list[str] = []
    for cid in candidates[:12]:
        missing = _missing_prereqs(cid, mastered, cie)
        if missing and not allow_skip_prerequisites:
            # Insert missing prereqs first
            for mid in missing:
                if mid not in mastered and all(s.concept_id != mid for s in steps):
                    title = _title(mid, cie)
                    steps.append(
                        PathwayStep(
                            step_id=f"seq_{mid}",
                            concept_id=mid,
                            title=title,
                            activity_type="remediation",
                            rationale=f"Prerequisite for {cid}",
                            prerequisites_ok=True,
                            estimated_minutes=12,
                        )
                    )
                    blocked.append(cid)
            # Then the target if prereqs will be covered
            steps.append(
                PathwayStep(
                    step_id=f"seq_{cid}",
                    concept_id=cid,
                    title=_title(cid, cie),
                    activity_type="lesson",
                    rationale="Queued after prerequisites",
                    prerequisites_ok=False if missing else True,
                    estimated_minutes=15,
                )
            )
        else:
            steps.append(
                PathwayStep(
                    step_id=f"seq_{cid}",
                    concept_id=cid,
                    title=_title(cid, cie),
                    activity_type="lesson" if cid not in at_risk else "practice",
                    rationale="Ready — prerequisites satisfied" if not missing else "Teacher override skip allowed",
                    prerequisites_ok=not missing or allow_skip_prerequisites,
                    estimated_minutes=15,
                )
            )

    # Dedupe preserving order
    seen = set()
    unique: list[PathwayStep] = []
    for s in steps:
        if s.concept_id in seen:
            continue
        seen.add(s.concept_id)
        unique.append(s)

    explanation = (
        f"Sequenced {len(unique)} steps prioritizing at-risk ({len(at_risk)}) and developing concepts; "
        f"prerequisites enforced={not allow_skip_prerequisites}. "
        f"Teacher priorities={teacher_priorities or []}."
    )
    decision = ExplainableDecision(
        decision_id="seq_primary",
        decision_type="sequencing",
        choice=" → ".join(s.concept_id for s in unique[:5]) or "none",
        explanation=explanation,
        evidence=[
            {"factor": "at_risk", "value": at_risk},
            {"factor": "mastered_count", "value": len(mastered)},
            {"factor": "allow_skip_prerequisites", "value": allow_skip_prerequisites},
        ],
        confidence=0.88,
    )
    return unique, decision


def _missing_prereqs(concept_id: str, mastered: set[str], cie: dict[str, Any]) -> list[str]:
    gaps = cie.get("learning_gaps") or {}
    if gaps.get("target") == concept_id:
        return [m for m in (gaps.get("missing_prerequisites") or []) if m not in mastered]
    prereq = cie.get("prerequisites") or {}
    chain = prereq.get("chain") or []
    missing = []
    for row in chain:
        cid = row.get("concept_id") if isinstance(row, dict) else row
        if cid and cid not in mastered:
            missing.append(cid)
    # Also try live CIE graph
    try:
        from engines.curriculum_intelligence_engine.intelligence import get_runtime

        g = get_runtime()["graph"]
        for mid in g.missing_prerequisites(concept_id, mastered):
            if mid not in missing:
                missing.append(mid)
    except Exception:  # noqa: BLE001
        pass
    return missing


def _title(concept_id: str, cie: dict[str, Any]) -> str:
    for m in cie.get("matched_concepts") or []:
        if isinstance(m, dict) and m.get("concept_id") == concept_id:
            return m.get("title") or concept_id
    try:
        from engines.curriculum_intelligence_engine.intelligence import get_runtime

        n = get_runtime()["graph"].get_concept(concept_id)
        return n.title if n else concept_id
    except Exception:  # noqa: BLE001
        return concept_id
