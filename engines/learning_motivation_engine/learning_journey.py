"""Interactive learning journey — milestones, goals, certificates."""

from __future__ import annotations

from typing import Any

from engines.learning_motivation_engine.levels import level_for_xp


def build_journey(state: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    ale = ((context.get("engine_outputs") or {}).get("adaptive_learning") or {}).get("payload") or {}
    level = level_for_xp(int(state.get("xp_total") or 0))
    milestones = [
        {"id": "start", "label": "Began journey", "done": True},
        {"id": "first_badge", "label": "First badge", "done": bool(state.get("badges"))},
        {"id": "scholar", "label": "Reach Scholar", "done": int(state.get("xp_total") or 0) >= 700},
        {"id": "certificate", "label": "Earn a certificate", "done": bool(state.get("certificates"))},
    ]
    return {
        "milestones": milestones,
        "completed_competencies": (ale.get("learner_model") or {}).get("concepts_mastered") or [],
        "current_progress": level,
        "upcoming_goals": state.get("goals") or context.get("goals") or [{"goal": "Complete next recommended skill"}],
        "adaptive_recommendations": (ale.get("next_activity") or ale.get("pathway") or {}),
        "certificates_earned": state.get("certificates") or [],
        "quests_active": [q for q in (state.get("quests") or []) if q.get("status") == "active"][:5],
    }
