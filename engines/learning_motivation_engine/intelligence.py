"""LMAS intelligence aggregator — builds motivation payload for VLIE."""

from __future__ import annotations

from typing import Any

from engines.learning_motivation_engine import analytics
from engines.learning_motivation_engine.competency_maps import build_competency_map
from engines.learning_motivation_engine.learning_journey import build_journey
from engines.learning_motivation_engine.personalization import personalize
from engines.learning_motivation_engine.quests import generate_quests
from engines.learning_motivation_engine.rewards import alcis_celebration_payload, atie_context_snippet, summarize_rewards, vmle_announcements
from engines.learning_motivation_engine.schemas import POLICY
from engines.learning_motivation_engine.skill_tree import build_skill_tree
from engines.learning_motivation_engine.state_store import load_state, save_state
from engines.learning_motivation_engine.dashboards import learner_dashboard


def build_motivation_payload(context: dict[str, Any]) -> dict[str, Any]:
    learner_id = str(context.get("learner_id") or context.get("user_id") or "anonymous")
    state = load_state(learner_id)
    prefs = personalize(context)

    if not state.get("quests"):
        state["quests"] = generate_quests(context)
        save_state(state)

    skill_tree = build_skill_tree(context)
    competency = build_competency_map(context)
    journey = build_journey(state, context)
    state["skill_tree_progress"] = {"recommended": skill_tree.get("recommended_next")}
    state["journey"] = journey
    save_state(state)

    analytics.record("motivation_plan", learner_id=learner_id, payload={"xp": state.get("xp_total")})

    enabled = bool((context.get("feature_flags") or {}).get("gamification", True))
    # Back-compat keys expected by ALCIS / LAIE under gamification payload shape
    return {
        "system": "LMAS",
        "engine": "learning_motivation",
        "enabled": enabled,
        "xp": int(state.get("xp_total") or 0),
        "badges": state.get("badges") or [],
        "streaks": state.get("streaks") or {"days": (state.get("streaks") or {}).get("daily") or 0},
        "quests": [q.get("title") for q in (state.get("quests") or []) if q.get("status") == "active"]
        or ["Complete Exam Practice (Official)", "Review verified visuals"],
        "quest_objects": state.get("quests") or [],
        "certificates": state.get("certificates") or [],
        "level": state.get("level") or {"level": {"id": state.get("level_id")}},
        "achievements": state.get("achievements") or [],
        "skill_tree": skill_tree,
        "learning_journey": journey,
        "competency_map": competency,
        "personalization": prefs,
        "rewards_summary": summarize_rewards(state),
        "alcis": alcis_celebration_payload(state),
        "atie": atie_context_snippet(state),
        "vmle": {"announcements": vmle_announcements()},
        "dashboard": learner_dashboard(state, context),
        "analytics": analytics.summary(learner_id, state),
        "design": "accessibility-first intrinsic motivation",
        "policy": POLICY,
        "note": "LMAS owns motivation economy; curriculum/assessment unchanged",
    }
