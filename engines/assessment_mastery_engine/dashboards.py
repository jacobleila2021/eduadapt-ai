"""Dashboard payloads — teacher, student, parent, school (data only; UI later)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from engines.assessment_mastery_engine.exam_readiness import exam_readiness
from engines.assessment_mastery_engine.interventions import interventions_for_weak_concepts
from engines.assessment_mastery_engine.mastery import mastery_summary, recompute_all_mastery
from engines.assessment_mastery_engine.revision import generate_revision_plan
from engines.assessment_mastery_engine.store import list_learners, load_learner


def student_dashboard(learner_id: str, *, topic: str = "") -> dict[str, Any]:
    recompute_all_mastery(learner_id)
    summary = mastery_summary(learner_id)
    ready = exam_readiness(learner_id, topic=topic)
    plan = generate_revision_plan(learner_id, topic=topic)
    state = load_learner(learner_id)
    return {
        "role": "student",
        "learner_id": learner_id,
        "mastery_map": state.get("mastery") or {},
        "competencies": state.get("competencies") or {},
        "achievements": [
            c for c, r in (state.get("mastery") or {}).items() if (r.get("level") in ("proficient", "advanced", "mastered"))
        ],
        "current_goals": (summary.get("weak_concepts") or [])[:3],
        "recommended_next_lesson": (plan.get("priority_topics") or [None])[0],
        "revision_plan": plan,
        "confidence_tracker": state.get("confidence") or {},
        "exam_readiness": ready,
    }


def teacher_dashboard(learner_ids: list[str] | None = None, *, topic: str = "") -> dict[str, Any]:
    ids = learner_ids or list_learners()
    class_mastery = []
    need_support = []
    ready_extension = []
    gap_heat: dict[str, list[float]] = defaultdict(list)

    for lid in ids:
        recompute_all_mastery(lid)
        s = mastery_summary(lid)
        class_mastery.append({"learner_id": lid, **{k: s[k] for k in ("by_level", "concept_count", "weak_concepts")}})
        weak = s.get("weak_concepts") or []
        if weak:
            need_support.append({"learner_id": lid, "weak": weak[:3]})
            for w in weak:
                gap_heat[w.get("concept_id") or "?"].append(float(w.get("mastery_pct") or 0))
        strong = s.get("strong_concepts") or []
        if strong and not weak:
            ready_extension.append({"learner_id": lid, "strong": strong[:2]})

    heatmap = {
        cid: {"avg": round(sum(v) / len(v), 3), "n": len(v)}
        for cid, v in gap_heat.items()
    }
    top_gaps = sorted(heatmap.items(), key=lambda kv: kv[1]["avg"])[:8]
    interventions = interventions_for_weak_concepts([g[0] for g in top_gaps if g[0] != "?"])

    return {
        "role": "teacher",
        "class_size": len(ids),
        "class_mastery": class_mastery,
        "learning_gaps": [{"concept_id": c, **meta} for c, meta in top_gaps],
        "competency_heatmaps": heatmap,
        "students_requiring_support": need_support,
        "students_ready_for_extension": ready_extension,
        "intervention_recommendations": interventions[:8],
        "topic": topic,
    }


def parent_dashboard(learner_id: str) -> dict[str, Any]:
    s = student_dashboard(learner_id)
    weak = s.get("current_goals") or []
    return {
        "role": "parent",
        "learner_id": learner_id,
        "progress_summary": {
            "mastery_levels": mastery_summary(learner_id).get("by_level"),
            "exam_readiness": (s.get("exam_readiness") or {}).get("predicted_readiness"),
        },
        "strengths": (mastery_summary(learner_id).get("strong_concepts") or [])[:5],
        "areas_requiring_support": weak,
        "recommended_home_activities": [
            i
            for i in (s.get("revision_plan") or {}).get("interventions") or []
            if i.get("kind") in ("concrete_activity", "parent_support", "additional_practice")
        ][:5],
        "learning_habits": {
            "evidence_count": len(load_learner(learner_id).get("evidence") or []),
            "attempt_count": len(load_learner(learner_id).get("attempts") or []),
        },
        "upcoming_assessments": [],
    }


def school_dashboard(learner_ids: list[str] | None = None) -> dict[str, Any]:
    teacher = teacher_dashboard(learner_ids)
    ids = learner_ids or list_learners()
    readiness = []
    for lid in ids:
        r = exam_readiness(lid)
        readiness.append(r.get("readiness_score") or 0)
    avg_ready = sum(readiness) / len(readiness) if readiness else 0.0
    return {
        "role": "school",
        "learners": len(ids),
        "year_level_mastery": teacher.get("class_mastery"),
        "school_wide_gaps": teacher.get("learning_gaps"),
        "intervention_effectiveness": {
            "note": "Track by comparing mastery_pct before/after intervention ids in evidence notes (future).",
            "recommended_now": teacher.get("intervention_recommendations"),
        },
        "assessment_quality": {
            "official_bank_policy": True,
            "avg_exam_readiness": round(avg_ready, 4),
        },
        "accessibility_metrics": {
            "note": "Join with AccessibilityEngine profiles when learner roster includes a11y flags.",
        },
    }
