"""Role dashboards — learner, teacher, parent, special educator, school, district."""

from __future__ import annotations

from typing import Any

from engines.learning_motivation_engine.analytics import summary
from engines.learning_motivation_engine.learning_journey import build_journey
from engines.learning_motivation_engine.rewards import summarize_rewards


def learner_dashboard(state: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "role": "learner",
        "rewards": summarize_rewards(state),
        "journey": build_journey(state, context),
        "quests": [q for q in (state.get("quests") or []) if q.get("status") == "active"][:7],
        "badges": state.get("badges") or [],
        "no_public_leaderboard": True,
    }


def teacher_dashboard(states: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "role": "teacher",
        "class_xp_avg": round(sum(int(s.get("xp_total") or 0) for s in states) / max(len(states), 1), 1),
        "quest_completion_rate": _quest_rate(states),
        "motivation_trends": "aggregate_only_no_public_ranking",
        "learners_count": len(states),
    }


def parent_dashboard(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "parent",
        "streaks": state.get("streaks"),
        "achievements": (state.get("achievements") or [])[-5:],
        "certificates": state.get("certificates") or [],
        "habits": {"daily_streak": (state.get("streaks") or {}).get("daily")},
        "home_tips": ["Celebrate effort", "Short consistent sessions beat cramming"],
    }


def special_educator_dashboard(state: dict[str, Any], a11y: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "role": "special_educator",
        "accessibility_personalization": a11y or {},
        "celebration_intensity": (a11y or {}).get("celebration_intensity"),
        "progress": summarize_rewards(state),
        "note": "Functional supports only — no medical labels",
    }


def school_leader_dashboard(states: list[dict[str, Any]]) -> dict[str, Any]:
    return {"role": "school_leader", "engagement_summary": teacher_dashboard(states), "certificates_issued": sum(len(s.get("certificates") or []) for s in states)}


def district_dashboard(schools: list[dict[str, Any]]) -> dict[str, Any]:
    return {"role": "district_admin", "schools": len(schools), "policy": "privacy_preserving_aggregates_only"}


def _quest_rate(states: list[dict[str, Any]]) -> float:
    done = total = 0
    for s in states:
        for q in s.get("quests") or []:
            total += 1
            if q.get("status") == "completed":
                done += 1
    return round(done / total, 3) if total else 0.0


def analytics_panel(learner_id: str, state: dict[str, Any]) -> dict[str, Any]:
    return summary(learner_id, state)
