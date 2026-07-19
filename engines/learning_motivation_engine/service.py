"""REST-shaped API facade for Learning Motivation & Achievement System (LMAS)."""

from __future__ import annotations

from typing import Any

from engines.learning_motivation_engine import analytics
from engines.learning_motivation_engine.achievements import list_achievements
from engines.learning_motivation_engine.certificates import issue_certificate, verify_certificate
from engines.learning_motivation_engine.competency_maps import build_competency_map
from engines.learning_motivation_engine.dashboards import (
    learner_dashboard,
    parent_dashboard,
    special_educator_dashboard,
    teacher_dashboard,
)
from engines.learning_motivation_engine.learning_journey import build_journey
from engines.learning_motivation_engine.levels import level_for_xp
from engines.learning_motivation_engine.notifications import notify
from engines.learning_motivation_engine.personalization import personalize
from engines.learning_motivation_engine.progression import apply_progress_event
from engines.learning_motivation_engine.quests import complete_quest, generate_quests
from engines.learning_motivation_engine.rewards import summarize_rewards, vmle_announcements
from engines.learning_motivation_engine.skill_tree import build_skill_tree
from engines.learning_motivation_engine.state_store import load_state, save_state
from engines.learning_motivation_engine.xp import compute_xp


def _publish(learner_id: str, event_type: str, payload: dict[str, Any], vlie_session_id: str = "") -> None:
    analytics.record(event_type, learner_id=learner_id, payload=payload)
    if not vlie_session_id:
        return
    try:
        from engines.verified_learning_engine.service import api_publish_event

        api_publish_event(event_type, vlie_session_id, payload=payload)
    except Exception:  # noqa: BLE001
        pass


def api_award_xp(learner_id: str, event: str, evidence_key: str, **kwargs: Any) -> dict[str, Any]:
    state = load_state(learner_id)
    result = apply_progress_event(
        state,
        event,
        evidence_key=evidence_key,
        signals=kwargs.get("signals") or {},
        difficulty=kwargs.get("difficulty") or "medium",
        subject=kwargs.get("subject") or "default",
        improvement_delta=float(kwargs.get("improvement_delta") or 0),
        teacher_approved=bool(kwargs.get("teacher_approved")),
        bonus_multiplier=float(kwargs.get("bonus_multiplier") or 1.0),
    )
    if result.get("ok") and result.get("state"):
        save_state(result["state"])
        _publish(learner_id, "MotivationXPAwarded", {"xp": result.get("xp_awarded")}, kwargs.get("vlie_session_id") or "")
        # ALCIS celebration hook
        try:
            from engines.learning_companion_engine.service import api_record_celebration

            if result.get("newly_earned_badges") or result.get("xp_awarded"):
                api_record_celebration(
                    learner_id,
                    "skill_milestone" if result.get("newly_earned_badges") else "daily_consistency",
                    evidence={"detail": f"+{result.get('xp_awarded')} XP"},
                    gamification={"xp": result["state"].get("xp_total"), "badges": result["state"].get("badges"), "streaks": result["state"].get("streaks")},
                )
        except Exception:  # noqa: BLE001
            pass
    return result


def api_get_xp(learner_id: str) -> dict[str, Any]:
    state = load_state(learner_id)
    return {"ok": True, "xp_total": state.get("xp_total"), "log": (state.get("xp_log") or [])[-20:], "level": level_for_xp(int(state.get("xp_total") or 0))}


def api_compute_xp_preview(event: str, **kwargs: Any) -> dict[str, Any]:
    return compute_xp(event, **{k: kwargs[k] for k in ("difficulty", "subject", "improvement_delta", "teacher_approved", "bonus_multiplier") if k in kwargs})


def api_get_achievements(learner_id: str = "") -> dict[str, Any]:
    if learner_id:
        state = load_state(learner_id)
        return {"ok": True, "earned": state.get("achievements") or [], "catalog": list_achievements()}
    return {"ok": True, "catalog": list_achievements()}


def api_get_quests(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    state = load_state(learner_id)
    if not state.get("quests") or kwargs.get("refresh"):
        state["quests"] = generate_quests(kwargs.get("context") or {"subject": kwargs.get("subject")})
        save_state(state)
    return {"ok": True, "quests": state.get("quests")}


def api_complete_quest(learner_id: str, quest_id: str) -> dict[str, Any]:
    state = load_state(learner_id)
    out = complete_quest(state, quest_id)
    if out.get("ok"):
        save_state(out["state"])
        # award revision/lesson-style XP for quest completion via evidence
        award = api_award_xp(learner_id, "revision", evidence_key=f"quest:{quest_id}")
        out["xp"] = award
    return out


def api_get_skill_tree(**kwargs: Any) -> dict[str, Any]:
    return {"ok": True, "skill_tree": build_skill_tree(kwargs.get("context") or kwargs)}


def api_get_journey(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    state = load_state(learner_id)
    return {"ok": True, "journey": build_journey(state, kwargs.get("context"))}


def api_get_certificates(learner_id: str) -> dict[str, Any]:
    state = load_state(learner_id)
    return {"ok": True, "certificates": state.get("certificates") or []}


def api_issue_certificate(learner_id: str, kind: str, title: str, **kwargs: Any) -> dict[str, Any]:
    state = load_state(learner_id)
    out = issue_certificate(state, kind=kind, title=title, metadata=kwargs.get("metadata"))
    save_state(out["state"])
    _publish(learner_id, "MotivationCertificateIssued", out["certificate"])
    return {"ok": True, "certificate": out["certificate"], "verify": verify_certificate(out["certificate"])}


def api_get_streaks(learner_id: str) -> dict[str, Any]:
    return {"ok": True, "streaks": load_state(learner_id).get("streaks")}


def api_get_rewards(learner_id: str) -> dict[str, Any]:
    return {"ok": True, "rewards": summarize_rewards(load_state(learner_id))}


def api_get_analytics(learner_id: str = "") -> dict[str, Any]:
    state = load_state(learner_id) if learner_id else {}
    return {"ok": True, "analytics": analytics.summary(learner_id, state)}


def api_get_competency_map(**kwargs: Any) -> dict[str, Any]:
    return {"ok": True, "map": build_competency_map(kwargs.get("context") or kwargs)}


def api_learner_dashboard(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    state = load_state(learner_id)
    return {"ok": True, "dashboard": learner_dashboard(state, kwargs.get("context"))}


def api_parent_dashboard(learner_id: str) -> dict[str, Any]:
    return {"ok": True, "dashboard": parent_dashboard(load_state(learner_id))}


def api_teacher_dashboard(learner_ids: list[str] | None = None) -> dict[str, Any]:
    ids = learner_ids or []
    states = [load_state(i) for i in ids]
    return {"ok": True, "dashboard": teacher_dashboard(states)}


def api_special_educator_dashboard(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    return {
        "ok": True,
        "dashboard": special_educator_dashboard(load_state(learner_id), personalize(kwargs.get("context"))),
    }


def api_notify(learner_id: str, kind: str, title: str, body: str, **kwargs: Any) -> dict[str, Any]:
    return {"ok": True, "notification": notify(learner_id=learner_id, kind=kind, title=title, body=body, personalization=kwargs.get("personalization"))}


def api_vmle_announcements(learner_id: str) -> dict[str, Any]:
    state = load_state(learner_id)
    return {"ok": True, "announcements": vmle_announcements({"badges": (state.get("badges") or [])[-1:], "certificates": (state.get("certificates") or [])[-1:]})}
