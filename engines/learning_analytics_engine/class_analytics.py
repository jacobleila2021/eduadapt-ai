"""Class / teacher analytics aggregations."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from engines.learning_analytics_engine.learner_analytics import learner_analytics


def class_analytics(learner_sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate per-learner source bundles into class view."""
    rows = [learner_analytics(s) for s in learner_sources]
    heat: dict[str, list[float]] = defaultdict(list)
    misconceptions: Counter[str] = Counter()
    need_intervention = []
    ready_enrichment = []
    profiles: Counter[str] = Counter()

    for row in rows:
        lid = row.get("learner_id")
        progress = row.get("learning_progress") or {}
        for cid in progress.get("at_risk") or []:
            heat[str(cid)].append(0.3)
        for cid in progress.get("mastered") or []:
            heat[str(cid)].append(0.9)
        for m in (row.get("assessment_history") or {}).get("misconceptions") or []:
            if isinstance(m, dict):
                misconceptions[m.get("label") or m.get("misconception_id") or "unknown"] += 1
        risk = (row.get("risk_indicators") or {}).get("risk_of_failure") or 0
        if risk >= 0.5 or progress.get("at_risk_count", 0) > 0:
            need_intervention.append(lid)
        elif progress.get("mastered_count", 0) > 0 and progress.get("at_risk_count", 0) == 0:
            ready_enrichment.append(lid)
        for p in (row.get("accessibility_usage") or {}).get("profiles") or []:
            profiles[p] += 1

    heatmap = {
        cid: {"avg_proxy": round(sum(v) / len(v), 3), "n": len(v)}
        for cid, v in heat.items()
    }
    return {
        "class_size": len(rows),
        "mastery_heatmaps": heatmap,
        "common_misconceptions": misconceptions.most_common(10),
        "students_requiring_intervention": need_intervention,
        "students_ready_for_enrichment": ready_enrichment,
        "accessibility_profile_distribution": dict(profiles),
        "learners": rows,
    }


def teacher_analytics(sources: dict[str, Any], class_bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    cie = sources.get("cie") or {}
    ame = sources.get("ame") or {}
    ale = sources.get("ale") or {}
    lesson = sources.get("lesson") or {}
    class_bundle = class_bundle or {}

    return {
        "class_overview": {
            "size": class_bundle.get("class_size") or 1,
            "topic": (sources.get("context") or {}).get("topic"),
        },
        "mastery_heatmaps": class_bundle.get("mastery_heatmaps") or {},
        "curriculum_coverage": {
            "outcomes": len(cie.get("learning_outcomes") or []),
            "concepts": len(cie.get("matched_concepts") or []),
            "graph_stats": cie.get("graph_stats") or {},
        },
        "assessment_quality": {
            "official_items": len(ame.get("official_mcqs") or []),
            "exam_bundle_keys": list((ame.get("exam_bundle") or {}).keys()),
            "policy": "official_answers_only",
        },
        "accessibility_effectiveness": class_bundle.get("accessibility_profile_distribution") or {},
        "learning_gaps": (cie.get("learning_gaps") or {}),
        "common_misconceptions": class_bundle.get("common_misconceptions")
        or [(m.get("label"), 1) for m in (ame.get("misconceptions") or [])[:5] if isinstance(m, dict)],
        "students_requiring_intervention": class_bundle.get("students_requiring_intervention")
        or ((ale.get("recommendations") or {}).get("teacher") or []),
        "students_ready_for_enrichment": class_bundle.get("students_ready_for_enrichment")
        or (ale.get("enrichment") or []),
        "lesson_effectiveness": {
            "complexity_score": lesson.get("complexity_score"),
            "reading_level": lesson.get("reading_level"),
            "objective_count": lesson.get("objective_count"),
        },
        "question_effectiveness": {
            "note": "Requires longitudinal attempt data from AME store",
            "bank_items_available": len(ame.get("official_mcqs") or []),
        },
        "time_on_task": (ale.get("learner_model") or {}).get("time_on_task_min"),
        "assignment_completion": (ale.get("learner_model") or {}).get("completion_rate"),
        "explainability": (ale.get("explainability") or {}),
    }
