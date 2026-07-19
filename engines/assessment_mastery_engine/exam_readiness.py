"""Exam readiness engine — coverage, gaps, predicted readiness."""

from __future__ import annotations

from typing import Any

from engines.assessment_mastery_engine.mastery import mastery_summary
from engines.assessment_mastery_engine.store import load_learner


def exam_readiness(
    learner_id: str,
    *,
    concept_ids: list[str] | None = None,
    topic: str = "",
    cie_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = load_learner(learner_id)
    mastery = state.get("mastery") or {}
    summary = mastery_summary(learner_id)

    # Target concept set from CIE match or explicit list
    targets = list(concept_ids or [])
    if not targets and cie_context:
        targets = [c.get("concept_id") for c in (cie_context.get("matched_concepts") or []) if c.get("concept_id")]
    if not targets:
        targets = list(mastery.keys())

    covered = []
    weak = []
    missing = []
    scores = []
    for cid in targets:
        row = mastery.get(cid)
        if not row:
            missing.append(cid)
            scores.append(0.0)
            continue
        pct = float(row.get("mastery_pct") or 0)
        scores.append(pct)
        if pct >= 0.75:
            covered.append({"concept_id": cid, "mastery_pct": pct, "level": row.get("level")})
        else:
            weak.append({"concept_id": cid, "mastery_pct": pct, "level": row.get("level")})

    avg = sum(scores) / len(scores) if scores else 0.0
    # Evidence volume factor
    evid_n = len(state.get("evidence") or [])
    confidence = min(0.95, 0.35 + 0.05 * min(evid_n, 10) + 0.4 * avg)

    predicted = "ready" if avg >= 0.8 and not missing and evid_n >= 3 else (
        "nearly_ready" if avg >= 0.65 else "needs_revision"
    )

    revision = [w["concept_id"] for w in sorted(weak, key=lambda x: x["mastery_pct"])] + missing

    return {
        "learner_id": learner_id,
        "topic": topic,
        "concept_coverage": {
            "targets": targets,
            "covered": covered,
            "weaknesses": weak,
            "missing": missing,
            "coverage_ratio": (len(covered) / len(targets)) if targets else 0.0,
        },
        "strengths": summary.get("strong_concepts") or [],
        "weaknesses": weak,
        "knowledge_gaps": missing,
        "predicted_readiness": predicted,
        "readiness_score": round(avg, 4),
        "confidence_level": round(confidence, 4),
        "recommended_revision": revision[:12],
        "policy": "multi_evidence_exam_readiness",
    }
