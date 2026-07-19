"""AI Learning Companion Intelligence System (ALCIS) tests."""

from __future__ import annotations

from engines.learning_companion_engine import LearningCompanionEngine
from engines.learning_companion_engine.avatars import list_companions
from engines.learning_companion_engine.dialogue import handoff_to_atie
from engines.learning_companion_engine.learner_memory import load_memory, save_memory
from engines.learning_companion_engine.motivation import craft_encouragement, motivation_profile
from engines.learning_companion_engine.personality import apply_style
from engines.learning_companion_engine.schemas import COMPANION_LIBRARY, PERSONALITY_STYLES
from engines.learning_companion_engine.service import (
    api_get_motivation_profile,
    api_list_companions,
    api_log_encouragement,
    api_record_celebration,
    api_retrieve_companion_analytics,
    api_retrieve_learner_memory,
    api_select_companion,
    api_update_goals,
    api_update_personality,
    api_wellbeing_support,
    api_ef_coach,
    api_handoff_atie,
)
from engines.learning_companion_engine.wellbeing import support
from engines.verified_learning_engine import get_registry, reset_registry


def test_companion_library():
    assert len(COMPANION_LIBRARY) >= 11
    assert "focus_fox" in COMPANION_LIBRARY
    assert "university_mentor" in COMPANION_LIBRARY
    assert len(PERSONALITY_STYLES) == 6
    assert len(list_companions()) == len(COMPANION_LIBRARY)


def test_registry_includes_learning_companion():
    reg = reset_registry()
    assert "learning_companion" in {e["engine_id"] for e in reg.list_engines()}
    assert reg.get("learning_companion").health_check().ok


def test_engine_never_teaches_policy():
    eng = LearningCompanionEngine()
    result = eng.process(
        {
            "learner_id": "alcis_u1",
            "progress_delta": 0.18,
            "engine_outputs": {
                "accessibility": {"payload": {"presentation": {"primary_mode": "auditory"}, "learner_profile": {"active_profiles": ["adhd"]}}},
                "adaptive_learning": {"payload": {"predictions": {"risk_of_disengagement": 0.2}, "learner_model": {"confidence": 0.6}}},
                "gamification": {"payload": {"xp": 10, "badges": ["starter"], "streaks": {"days": 3}}},
            },
        }
    )
    assert result.ok
    assert result.payload["policy"]["never_teach"] is True
    assert result.payload["policy"]["atie_for_explanations"] is True
    assert result.payload["encouragement"]["kind"] == "encouragement"
    assert result.payload["accessibility"]["presentation_only"] is True


def test_evidence_based_encouragement():
    profile = motivation_profile({"progress_delta": 0.18}, {"streaks": {"days": 4}})
    profile["challenges_completed"] = 3
    profile["persistence_signal"] = 0.8
    msg = craft_encouragement(profile, event="progress")
    assert msg["generic"] is False
    assert "18%" in msg["text"] or "improved" in msg["text"].lower()
    assert msg["evidence"]


def test_personality_consistency():
    a = apply_style("You finished the lesson.", "cheerful_friend")
    b = apply_style("You finished the lesson.", "calm_mentor")
    assert a["style"] == "cheerful_friend"
    assert b["style"] == "calm_mentor"
    assert a["text"] != b["text"]


def test_memory_persistence():
    learner = "alcis_mem_test"
    mem = load_memory(learner)
    mem["preferred_companion"] = "math_dragon"
    mem["favorite_subjects"] = ["mathematics"]
    save_memory(mem)
    again = load_memory(learner)
    assert again["preferred_companion"] == "math_dragon"
    assert "diagnosis" not in again


def test_wellbeing_no_clinical_advice():
    out = support(situation="frustrated", companion_id="study_panda")
    assert out["clinical_advice"] is False
    assert out["handoff_atie"] is True
    assert "mental health" not in out["message"]["text"].lower()


def test_atie_handoff():
    h = handoff_to_atie(companion_id="reading_owl", style="gentle_coach", topic="fractions")
    assert h["atie_required"] is True
    assert h["policy"] == "companion_never_teaches_independently"


def test_service_apis():
    learner = "alcis_api_user"
    assert api_list_companions()["ok"]
    sel = api_select_companion(learner, "focus_fox")
    assert sel["ok"]
    assert api_update_personality(learner, "calm_mentor")["ok"]
    mem = api_retrieve_learner_memory(learner)
    assert mem["memory"]["preferred_companion"] == "focus_fox"
    enc = api_log_encouragement(learner, context={"progress_delta": 0.1}, event="progress")
    assert enc["ok"]
    cel = api_record_celebration(learner, "lesson_completed", evidence={"detail": "Chapter 8 done."})
    assert cel["ok"]
    assert api_get_motivation_profile(learner)["ok"]
    assert api_update_goals(learner, [{"goal": "Master fractions", "by": "2026-08-01"}])["ok"]
    assert api_wellbeing_support(learner, "return_after_break")["ok"]
    assert api_ef_coach(learner, "planning", task="Revise Chapter 8")["ok"]
    assert api_handoff_atie(learner, topic="cells")["ok"]
    assert api_retrieve_companion_analytics(learner)["ok"]


def test_accessibility_adjustments():
    eng = LearningCompanionEngine()
    result = eng.process(
        {
            "learner_id": "a11y_user",
            "engine_outputs": {
                "accessibility": {
                    "payload": {
                        "presentation": {"primary_mode": "auditory", "reduced_motion": True},
                        "learner_profile": {"active_profiles": ["dyslexia"]},
                    }
                }
            },
        }
    )
    a11y = result.payload["accessibility"]
    assert a11y["pace"] == "slow"
    assert a11y["audio_usage"] is True
    assert a11y["no_medical_storage"] is True


def test_legacy_engines_remain():
    ids = {e["engine_id"] for e in get_registry().list_engines()}
    for required in (
        "curriculum",
        "ai_tutor",
        "voice_multimodal",
        "accessibility",
        "gamification",
        "learning_analytics",
        "learning_companion",
    ):
        assert required in ids


def test_alcis_smoke(capsys):
    """ALCIS_SMOKE_OK via standard pytest."""
    reg = reset_registry()
    assert reg.get("learning_companion")
    eng = LearningCompanionEngine()
    bundle = eng.process(
        {
            "learner_id": "smoke_companion",
            "progress_delta": 0.18,
            "persistence_score": 0.9,
            "engine_outputs": {
                "gamification": {"payload": {"xp": 5, "badges": [], "streaks": {"days": 2}}},
                "adaptive_learning": {"payload": {"predictions": {"risk_of_disengagement": 0.3}}},
            },
        }
    )
    assert bundle.ok
    assert bundle.payload["system"] == "ALCIS"
    assert api_select_companion("smoke_companion", "science_robot")["ok"]
    assert api_log_encouragement("smoke_companion", context={"progress_delta": 0.18})["ok"]
    assert api_record_celebration("smoke_companion", "daily_consistency")["ok"]

    with capsys.disabled():
        print("ALCIS_SMOKE_OK")
