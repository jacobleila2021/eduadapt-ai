"""REST-shaped API facade for AI Learning Companion Intelligence System (ALCIS)."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine import analytics
from engines.learning_companion_engine.avatars import list_companions
from engines.learning_companion_engine.companion_manager import run_companion_action
from engines.learning_companion_engine.learner_memory import load_memory, save_memory, update_goals, append_reflection
from engines.learning_companion_engine.motivation import motivation_profile
from engines.learning_companion_engine.personality import update_personality
from engines.learning_companion_engine.encouragement import encourage
from engines.learning_companion_engine.celebration import celebrate


def api_select_companion(learner_id: str, companion_id: str, **kwargs: Any) -> dict[str, Any]:
    return run_companion_action("select_companion", learner_id=learner_id, companion_id=companion_id, **kwargs)


def api_update_personality(learner_id: str, style: str) -> dict[str, Any]:
    mem = load_memory(learner_id)
    mem = update_personality(mem, style)
    save_memory(mem)
    return {"ok": True, "memory": mem}


def api_retrieve_learner_memory(learner_id: str) -> dict[str, Any]:
    return {"ok": True, "memory": load_memory(learner_id)}


def api_log_encouragement(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    return run_companion_action("encourage", learner_id=learner_id, **kwargs)


def api_record_celebration(learner_id: str, trigger: str, **kwargs: Any) -> dict[str, Any]:
    return run_companion_action("celebrate", learner_id=learner_id, trigger=trigger, **kwargs)


def api_get_motivation_profile(learner_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    mem = load_memory(learner_id)
    return {"ok": True, "profile": motivation_profile(context or {}, mem)}


def api_update_goals(learner_id: str, goals: list[dict[str, Any]]) -> dict[str, Any]:
    mem = update_goals(learner_id, goals)
    analytics.record("goal_update", learner_id=learner_id, payload={"count": len(goals)})
    return {"ok": True, "memory": mem}


def api_retrieve_companion_analytics(learner_id: str = "") -> dict[str, Any]:
    return {"ok": True, "analytics": analytics.summary(learner_id)}


def api_list_companions() -> dict[str, Any]:
    return {"ok": True, "companions": list_companions()}


def api_wellbeing_support(learner_id: str, situation: str, **kwargs: Any) -> dict[str, Any]:
    return run_companion_action("wellbeing", learner_id=learner_id, situation=situation, **kwargs)


def api_ef_coach(learner_id: str, need: str, **kwargs: Any) -> dict[str, Any]:
    return run_companion_action("ef_coach", learner_id=learner_id, need=need, **kwargs)


def api_handoff_atie(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    return run_companion_action("handoff_atie", learner_id=learner_id, **kwargs)


def api_start_companion_session(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    return run_companion_action("start_session", learner_id=learner_id, **kwargs)


def api_record_reflection(learner_id: str, reflection: dict[str, Any]) -> dict[str, Any]:
    mem = append_reflection(learner_id, reflection)
    analytics.record("reflection", learner_id=learner_id, payload=reflection)
    return {"ok": True, "memory": mem}


# Convenience re-exports for tests
api_encourage = api_log_encouragement
api_celebrate = api_record_celebration
