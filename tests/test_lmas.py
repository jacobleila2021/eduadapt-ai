"""Learning Motivation & Achievement System (LMAS) tests."""

from __future__ import annotations

from engines.learning_motivation_engine import LearningMotivationEngine
from engines.learning_motivation_engine.certificates import issue_certificate, verify_certificate
from engines.learning_motivation_engine.levels import level_for_xp
from engines.learning_motivation_engine.quests import generate_quests
from engines.learning_motivation_engine.schemas import LEVELS, POLICY
from engines.learning_motivation_engine.service import (
    api_award_xp,
    api_complete_quest,
    api_get_achievements,
    api_get_analytics,
    api_get_journey,
    api_get_quests,
    api_get_rewards,
    api_get_skill_tree,
    api_get_streaks,
    api_get_xp,
    api_issue_certificate,
    api_learner_dashboard,
)
from engines.learning_motivation_engine.state_store import load_state
from engines.learning_motivation_engine.streaks import record_activity
from engines.learning_motivation_engine.xp import compute_xp
from engines.verified_learning_engine import get_registry, reset_registry


def test_policy_healthy_motivation():
    assert POLICY["intrinsic_before_extrinsic"] is True
    assert POLICY["no_public_competitive_leaderboards"] is True
    assert POLICY["no_punish_missed_days"] is True
    assert len(LEVELS) == 7


def test_registry_lmas_and_gamification_facade():
    reg = reset_registry()
    ids = {e["engine_id"] for e in reg.list_engines()}
    assert "learning_motivation" in ids
    assert "gamification" in ids
    assert reg.get("learning_motivation").health_check().ok
    assert reg.get("gamification").health_check().ok


def test_xp_formulas_and_anti_farming():
    calc = compute_xp("lesson_completed", difficulty="hard", subject="science")
    assert calc["ok"] and calc["xp"] > 0
    blocked = compute_xp("helping_classmate", teacher_approved=False)
    assert blocked["ok"] is False
    neg = compute_xp("improvement", improvement_delta=-0.2)
    assert neg["ok"] is False

    import uuid

    learner = f"lmas_xp_user_{uuid.uuid4().hex[:8]}"
    key = f"lesson:ch8:{uuid.uuid4().hex[:8]}"
    r1 = api_award_xp(learner, "lesson_completed", evidence_key=key, signals={"lessons_completed": 1})
    assert r1["ok"] and r1["xp_awarded"] > 0
    r2 = api_award_xp(learner, "lesson_completed", evidence_key=key)
    assert r2["ok"] is False  # anti-farming


def test_levels_reflect_growth():
    assert level_for_xp(0)["level"]["id"] == "explorer"
    assert level_for_xp(700)["level"]["id"] == "scholar"
    assert level_for_xp(6000)["level"]["id"] == "innovator"


def test_engine_process_payload():
    eng = LearningMotivationEngine()
    result = eng.process(
        {
            "learner_id": "lmas_eng",
            "topic": "cells",
            "feature_flags": {"gamification": True},
            "engine_outputs": {
                "curriculum": {"payload": {"concepts": ["cell", "organelle", "photosynthesis"]}},
                "assessment": {"payload": {"mastery": {"concepts_mastered": ["cell"], "concepts_at_risk": ["photosynthesis"]}}},
                "accessibility": {"payload": {"learner_profile": {"active_profiles": ["adhd"]}}},
                "adaptive_learning": {"payload": {"learner_model": {"concepts_mastered": ["cell"]}}},
            },
        }
    )
    assert result.ok
    assert result.payload["system"] == "LMAS"
    assert result.payload["policy"]["no_dark_patterns"] is True
    assert result.payload["skill_tree"]["nodes"]
    assert result.payload["personalization"]["presentation_only"] is True


def test_gamification_mirrors_lmas():
    reg = reset_registry()
    ctx = {
        "learner_id": "lmas_mirror",
        "engine_outputs": {},
        "feature_flags": {"gamification": True},
    }
    lmas = reg.get("learning_motivation").process(ctx)
    ctx["engine_outputs"] = {"learning_motivation": {"ok": True, "payload": lmas.payload}}
    game = reg.get("gamification").process(ctx)
    assert game.ok
    assert game.payload.get("xp") == lmas.payload.get("xp")
    assert game.payload.get("system") == "LMAS"


def test_quests_streaks_certificates():
    learner = "lmas_quest"
    qs = api_get_quests(learner, refresh=True, subject="science")
    assert qs["ok"] and qs["quests"]
    qid = qs["quests"][0]["quest_id"]
    # Use unique evidence via complete_quest path
    state = load_state(learner)
    streak = record_activity(state)
    assert streak["streaks"]["policy"] == "no_punish_missed_days"
    cert = api_issue_certificate(learner, "milestone", "First Science Milestone")
    assert cert["ok"] and cert["verify"]["ok"]
    assert "qr_verification" in cert["certificate"]


def test_service_surfaces():
    learner = "lmas_api"
    api_award_xp(learner, "reflection", evidence_key="ref:1", signals={"reflections": 1})
    assert api_get_xp(learner)["ok"]
    assert api_get_achievements(learner)["ok"]
    assert api_get_skill_tree(context={"concepts": ["a", "b", "c"]})["ok"]
    assert api_get_journey(learner)["ok"]
    assert api_get_streaks(learner)["ok"]
    assert api_get_rewards(learner)["ok"]
    assert api_get_analytics(learner)["ok"]
    assert api_learner_dashboard(learner)["ok"]
    dash = api_learner_dashboard(learner)["dashboard"]
    assert dash["no_public_leaderboard"] is True


def test_legacy_engines_remain():
    ids = {e["engine_id"] for e in get_registry().list_engines()}
    for required in ("curriculum", "ai_tutor", "voice_multimodal", "learning_companion", "learning_motivation", "gamification"):
        assert required in ids


def test_lmas_smoke(capsys):
    """LMAS_SMOKE_OK via standard pytest."""
    import uuid

    reg = reset_registry()
    assert reg.get("learning_motivation")
    eng = LearningMotivationEngine()
    learner = f"smoke_lmas_{uuid.uuid4().hex[:8]}"
    bundle = eng.process({"learner_id": learner, "topic": "fractions", "feature_flags": {"gamification": True}})
    assert bundle.ok and bundle.payload["enabled"] is True
    award = api_award_xp(
        learner,
        "concept_mastered",
        evidence_key=f"smoke:c1:{uuid.uuid4().hex[:8]}",
        improvement_delta=0.2,
        signals={"concepts_mastered": 1},
    )
    assert award["ok"]
    assert generate_quests({"subject": "math"})
    state = load_state(learner)
    issued = issue_certificate(state, kind="competency", title="Smoke Competency")
    assert verify_certificate(issued["certificate"])["ok"]

    with capsys.disabled():
        print("LMAS_SMOKE_OK")
