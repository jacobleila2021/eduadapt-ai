"""Companion manager — orchestrates ALCIS turn without teaching."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine import analytics
from engines.learning_companion_engine.accessibility import companion_a11y
from engines.learning_companion_engine.avatars import get_companion, select_companion
from engines.learning_companion_engine.celebration import celebrate
from engines.learning_companion_engine.dialogue import greeting, handoff_to_atie
from engines.learning_companion_engine.encouragement import encourage
from engines.learning_companion_engine.engagement import engagement_state
from engines.learning_companion_engine.executive_function import coach_ef
from engines.learning_companion_engine.learner_memory import load_memory, merge_accessibility_from_aie, save_memory
from engines.learning_companion_engine.motivation import motivation_profile
from engines.learning_companion_engine.recommendations import recommend
from engines.learning_companion_engine.rewards import sync_gamification_rewards
from engines.learning_companion_engine.session_memory import append_message, start_session
from engines.learning_companion_engine.wellbeing import support


def _publish_vlie(action: str, vlie_session_id: str, payload: dict[str, Any] | None = None) -> None:
    if not vlie_session_id:
        return
    try:
        from engines.verified_learning_engine.service import api_publish_event

        event_map = {
            "encouragement": "CompanionEncouraged",
            "celebration": "CompanionCelebrated",
            "handoff": "TutorQuestionAsked",
            "check_in": "CompanionCheckIn",
        }
        api_publish_event(event_map.get(action, "CompanionEncouraged"), vlie_session_id, payload=payload or {})
    except Exception:  # noqa: BLE001
        pass


def analyze_companion_context(context: dict[str, Any]) -> dict[str, Any]:
    learner_id = str(context.get("learner_id") or context.get("user_id") or "anonymous")
    memory = load_memory(learner_id)
    outputs = context.get("engine_outputs") or {}
    aie = (outputs.get("accessibility") or {}).get("payload") or {}
    if aie:
        memory = merge_accessibility_from_aie(memory, aie)

    companion_id = context.get("companion_id") or memory.get("preferred_companion") or "study_panda"
    style = context.get("communication_style") or memory.get("communication_style") or "gentle_coach"
    companion = get_companion(companion_id)

    a11y = companion_a11y(context, memory)
    eng = engagement_state(context, memory)
    profile = motivation_profile(context, memory)
    recs = recommend(context, memory)

    game = (outputs.get("gamification") or {}).get("payload") or {}
    greet = greeting(companion_id=companion_id, style=style, learner_name=str(context.get("learner_name") or ""))
    enc = encourage(companion_id=companion_id, style=style, context=context, memory=memory, event=str(context.get("event") or "progress"))

    voice_hook = {
        "integrates": "voice_multimodal",
        "speakable_messages": [greet["message"], enc["message"]],
        "voice_preference": memory.get("voice_preference") or "Female",
    }

    return {
        "engine": "learning_companion",
        "system": "ALCIS",
        "version": "1.0.0",
        "companion": companion,
        "style": style,
        "memory_summary": {
            "preferred_companion": memory.get("preferred_companion"),
            "streaks": memory.get("streaks"),
            "goals": memory.get("long_term_goals"),
            "achievements_count": len(memory.get("achievements") or []),
        },
        "motivation_profile": profile,
        "engagement": eng,
        "accessibility": a11y,
        "greeting": greet["message"],
        "encouragement": enc["message"],
        "recommendations": recs,
        "gamification_bridge": {"xp": game.get("xp"), "badges": game.get("badges"), "streaks": game.get("streaks")},
        "voice": voice_hook,
        "dashboards": analytics.summary(learner_id).get("dashboards"),
        "policy": {
            "never_teach": True,
            "atie_for_explanations": True,
            "no_clinical_advice": True,
            "no_medical_diagnoses_stored": True,
            "curriculum_unchanged": True,
        },
    }


def run_companion_action(
    action: str,
    *,
    learner_id: str,
    companion_id: str | None = None,
    style: str | None = None,
    context: dict[str, Any] | None = None,
    session_id: str | None = None,
    vlie_session_id: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    memory = load_memory(learner_id)
    companion_id = companion_id or memory.get("preferred_companion") or "study_panda"
    style = style or memory.get("communication_style") or "gentle_coach"
    context = context or {}

    if action == "select_companion":
        out = select_companion(learner_id, kwargs.get("companion_id") or companion_id, teacher_allowed=kwargs.get("teacher_allowed"))
        if out.get("ok"):
            memory["preferred_companion"] = out["companion"]["id"]
            save_memory(memory)
        return out

    if action == "encourage":
        out = encourage(companion_id=companion_id, style=style, context=context, memory=memory, event=kwargs.get("event") or "progress")
        analytics.record("encouragement", learner_id=learner_id, session_id=session_id or "", payload=out["message"])
        _publish_vlie("encouragement", vlie_session_id, out["message"])
        if session_id:
            append_message(session_id, out["message"])
        return out

    if action == "celebrate":
        game = ((context.get("engine_outputs") or {}).get("gamification") or {}).get("payload") or kwargs.get("gamification") or {}
        out = celebrate(
            learner_id=learner_id,
            trigger=str(kwargs.get("trigger") or "skill_milestone"),
            companion_id=companion_id,
            style=style,
            evidence=kwargs.get("evidence"),
            gamification=game,
        )
        analytics.record("celebration", learner_id=learner_id, session_id=session_id or "", payload=out["message"])
        _publish_vlie("celebration", vlie_session_id, out["message"])
        return out

    if action == "wellbeing":
        out = support(situation=str(kwargs.get("situation") or "struggle"), companion_id=companion_id, style=style)
        analytics.record("wellbeing", learner_id=learner_id, payload=out["message"])
        if out.get("handoff_atie"):
            handoff = handoff_to_atie(companion_id=companion_id, style=style, topic=str(kwargs.get("topic") or ""))
            out["atie_handoff"] = handoff
            _publish_vlie("handoff", vlie_session_id, handoff["message"])
        return out

    if action == "ef_coach":
        out = coach_ef(need=str(kwargs.get("need") or "planning"), companion_id=companion_id, style=style, task=str(kwargs.get("task") or ""))
        analytics.record("ef_coach", learner_id=learner_id, payload=out)
        return out

    if action == "handoff_atie":
        out = handoff_to_atie(companion_id=companion_id, style=style, topic=str(kwargs.get("topic") or ""))
        _publish_vlie("handoff", vlie_session_id, out["message"])
        return out

    if action == "sync_rewards":
        game = ((context.get("engine_outputs") or {}).get("gamification") or {}).get("payload") or kwargs.get("gamification") or {}
        return sync_gamification_rewards(learner_id=learner_id, gamification_payload=game, companion_id=companion_id, style=style)

    if action == "start_session":
        doc = start_session(learner_id, companion_id=companion_id, vlie_session_id=vlie_session_id)
        analytics.record("dialogue", learner_id=learner_id, session_id=doc["session_id"], payload={"phase": "start"})
        return {"ok": True, "session": doc}

    return {"ok": False, "error": "unknown_action", "action": action}
