"""Accessibility Intelligence Engine tests."""

from __future__ import annotations

from engines.accessibility_engine import AccessibilityEngine
from engines.accessibility_intelligence_engine.learner_profile import (
    save_profile,
    update_preferences,
)
from engines.accessibility_intelligence_engine.readability import readability_report
from engines.accessibility_intelligence_engine.schemas import LearnerAccessibilityProfile
from engines.accessibility_intelligence_engine import service as aie_api
from engines.verified_learning_engine import reset_registry


def test_dyslexia_recommendations():
    lid = "aie_test_dyslexia"
    p = LearnerAccessibilityProfile(learner_id=lid, active_profiles=["dyslexia", "adhd"])
    save_profile(p)
    recs = aie_api.api_generate_recommendations(lid)["recommendations"]
    ids = {r["support_id"] for r in recs}
    assert "dyslexia_font_spacing" in ids
    assert "task_chunking" in ids or "focus_mode" in ids


def test_interface_and_presentation():
    lid = "aie_test_dyslexia"
    p = LearnerAccessibilityProfile(learner_id=lid, active_profiles=["dyslexia", "adhd"])
    save_profile(p)
    pkg = aie_api.api_apply_accommodations(lid)
    assert pkg["policy"]["presentation_only"] is True
    assert pkg["policy"]["no_medical_diagnoses_stored"] is True
    assert "ld" in pkg["prioritized_adaptation_specs"]


def test_readability():
    report = readability_report(
        "Photosynthesis is a process. " * 5
        + "The complex biochemical pathway utilized by autotrophic organisms is remarkable."
    )
    assert "cognitive_load" in report
    assert report["policy"] == "presentation_improvements_only"


def test_preferences_update():
    lid = "aie_test_prefs"
    update_preferences(
        lid,
        {
            "active_profiles": ["ell"],
            "preferred_font": "Atkinson",
            "self_selected_preferences": {"focus_mode": True},
        },
    )
    profile = aie_api.api_get_learner_profile(lid)["profile"]
    assert "ell" in profile["active_profiles"]
    assert profile["preferred_font"] == "Atkinson"
    assert profile["stores_medical_diagnoses"] is False


def test_accessibility_engine_aie_payload():
    eng = AccessibilityEngine()
    out = eng.process(
        {
            "learner_id": "aie_test_dyslexia",
            "accessibility_profiles": ["dyslexia", "ell"],
            "lesson_text": "Force is a push or pull. Pressure is force per unit area.",
            "grade": "8",
        }
    )
    assert out.ok
    assert out.payload.get("facts_immutable") is True
    assert "learner_profile" in out.payload
    assert "tutor_brief" in out.payload
    assert out.payload["tutor_brief"]["never_alter_curriculum_accuracy"] is True
    assert out.payload.get("profiles_generated")


def test_dashboards():
    d = aie_api.api_dashboards("student", learner_id="aie_test_dyslexia")
    assert d["role"] == "student"
    t = aie_api.api_dashboards("teacher", learner_id="aie_test_dyslexia")
    assert t["role"] == "teacher"


def test_registered():
    reg = reset_registry()
    assert "accessibility" in {e["engine_id"] for e in reg.list_engines()}
    h = AccessibilityEngine().health_check()
    assert h.ok
