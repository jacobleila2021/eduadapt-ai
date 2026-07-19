"""Mastery engine — multi-evidence levels (never a single test score)."""

from __future__ import annotations

from typing import Any

from engines.assessment_mastery_engine.schemas import MASTERY_LEVELS, MasteryRecord
from engines.assessment_mastery_engine.store import load_learner, upsert_mastery


# Weights by evidence source (sum normalized later)
SOURCE_WEIGHTS = {
    "assessment": 1.0,
    "official_exam_practice": 1.2,
    "worksheet": 0.9,
    "practice": 0.8,
    "assignment": 1.0,
    "project": 1.1,
    "ai_tutor": 0.7,
    "reflection": 0.5,
    "teacher_observation": 1.0,
}


def _level_from_pct(pct: float) -> str:
    if pct >= 0.95:
        return "mastered"
    if pct >= 0.85:
        return "advanced"
    if pct >= 0.75:
        return "proficient"
    if pct >= 0.60:
        return "approaching_proficiency"
    if pct >= 0.40:
        return "developing"
    return "beginning"


def compute_concept_mastery(learner_id: str, concept_id: str) -> MasteryRecord:
    state = load_learner(learner_id)
    rows = [e for e in state.get("evidence") or [] if e.get("concept_id") == concept_id]
    if not rows:
        rec = MasteryRecord(learner_id=learner_id, concept_id=concept_id, level="beginning", mastery_pct=0.0)
        upsert_mastery(learner_id, rec)
        return rec

    num = 0.0
    den = 0.0
    evid_ids = []
    for e in rows:
        w = float(e.get("weight") or SOURCE_WEIGHTS.get(e.get("source") or "assessment", 1.0))
        score = e.get("score")
        if score is None and e.get("correct") is not None:
            score = 1.0 if e["correct"] else 0.0
        score = float(score or 0.0)
        # blend self-confidence lightly if present
        conf = e.get("confidence")
        if conf is not None:
            score = 0.85 * score + 0.15 * float(conf)
        num += w * score
        den += w
        if e.get("evidence_id"):
            evid_ids.append(e["evidence_id"])

    pct = (num / den) if den else 0.0
    # Require multiple evidence points for proficient+
    if len(rows) < 2 and pct >= 0.75:
        pct = min(pct, 0.74)  # cap at approaching until more evidence
    level = _level_from_pct(pct)
    rec = MasteryRecord(
        learner_id=learner_id,
        concept_id=concept_id,
        level=level,
        mastery_pct=round(pct, 4),
        evidence_count=len(rows),
        evidence_ids=evid_ids[-20:],
        recommended_next="" if level in ("proficient", "advanced", "mastered") else concept_id,
    )
    upsert_mastery(learner_id, rec)
    return rec


def recompute_all_mastery(learner_id: str) -> dict[str, Any]:
    state = load_learner(learner_id)
    concepts = {e.get("concept_id") for e in state.get("evidence") or [] if e.get("concept_id")}
    out = {}
    for cid in concepts:
        out[cid] = compute_concept_mastery(learner_id, cid).to_dict()
    return {"learner_id": learner_id, "mastery": out, "levels": list(MASTERY_LEVELS)}


def mastery_summary(learner_id: str) -> dict[str, Any]:
    state = load_learner(learner_id)
    mastery = state.get("mastery") or {}
    if not mastery and state.get("evidence"):
        return recompute_all_mastery(learner_id)
    by_level: dict[str, int] = {lv: 0 for lv in MASTERY_LEVELS}
    for row in mastery.values():
        lv = row.get("level") or "beginning"
        by_level[lv] = by_level.get(lv, 0) + 1
    weak = sorted(
        (r for r in mastery.values() if float(r.get("mastery_pct") or 0) < 0.6),
        key=lambda r: float(r.get("mastery_pct") or 0),
    )
    strong = sorted(
        (r for r in mastery.values() if float(r.get("mastery_pct") or 0) >= 0.75),
        key=lambda r: -float(r.get("mastery_pct") or 0),
    )
    return {
        "learner_id": learner_id,
        "by_level": by_level,
        "weak_concepts": weak[:10],
        "strong_concepts": strong[:10],
        "concept_count": len(mastery),
        "policy": "multi_evidence_never_single_score",
    }
