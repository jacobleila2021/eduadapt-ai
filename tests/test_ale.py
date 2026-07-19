"""Adaptive Learning Engine tests."""

from __future__ import annotations

from engines.adaptive_learning_engine import AdaptiveLearningEngine, ale_api
from engines.adaptive_learning_engine.learner_model import save_learner_model
from engines.adaptive_learning_engine.schemas import LearnerModel
from engines.verified_learning_engine import reset_registry


def test_pathway_and_explainability():
    lid = "ale_test_learner"
    save_learner_model(
        LearnerModel(
            learner_id=lid,
            concepts_at_risk=["c8sci.pressure"],
            concepts_developing=["c8sci.force"],
            concepts_mastered=["c8sci.motion_intro"],
            accessibility_profiles=["dyslexia", "adhd"],
            confidence=0.45,
        )
    )
    eng = AdaptiveLearningEngine()
    out = eng.process(
        {
            "learner_id": lid,
            "topic": "Force and Pressure",
            "lesson_text": "Force is pressure so they are the same. P=F/A.",
            "grade": "8",
            "engine_outputs": {
                "accessibility": {
                    "payload": {
                        "profiles_generated": ["dyslexia", "adhd"],
                        "presentation": {"primary_mode": "dyslexia"},
                        "readability": {"cognitive_load": "high"},
                        "learner_profile": {"active_profiles": ["dyslexia", "adhd"]},
                    }
                },
                "curriculum": {
                    "payload": {
                        "curriculum_intelligence": {
                            "primary_concept_id": "c8sci.pressure",
                            "matched_concepts": [
                                {"concept_id": "c8sci.pressure", "title": "Pressure"},
                                {"concept_id": "c8sci.force", "title": "Force"},
                            ],
                            "learning_gaps": {
                                "target": "c8sci.pressure",
                                "missing_prerequisites": [],
                            },
                        }
                    }
                },
                "assessment": {
                    "payload": {
                        "mastery": {
                            "weak_concepts": [{"concept_id": "c8sci.pressure", "mastery_pct": 0.4}],
                            "strong_concepts": [],
                        },
                        "misconceptions": [
                            {
                                "misconception_id": "misc.force_eq_pressure",
                                "label": "Force and pressure are the same",
                                "concept_id": "c8sci.pressure",
                                "confidence": 0.8,
                                "intervention_ids": ["int.visual_pfa"],
                            }
                        ],
                    }
                },
            },
        }
    )
    assert out.ok
    assert out.payload.get("policy", {}).get("does_not_generate_lessons") is True
    assert out.payload.get("next_activity")
    assert out.payload.get("explainability")
    assert "explanation" in (out.payload.get("explainability") or {}) or out.payload[
        "explainability"
    ].get("next_activity_explanation")
    assert out.payload.get("difference_target") == 0.80


def test_teacher_override_api():
    lid = "ale_test_learner"
    r = ale_api.api_teacher_override(
        lid,
        decision_type="sequencing",
        choice="allow_skip_prerequisites",
        reason="Teacher confirmed prior mastery offline",
    )
    assert r["ok"]
    assert r["model"]["teacher_overrides"]


def test_predictions():
    pred = ale_api.api_predict_learner_outcomes("ale_test_learner")
    assert "risk_of_failure" in pred
    assert "explanatory_factors" in pred


def test_dashboards():
    d = ale_api.api_dashboards("student", learner_id="ale_test_learner")
    assert d["role"] == "student"
    assert d.get("next_recommended_lesson") is not None


def test_registered():
    reg = reset_registry()
    rows = {e["engine_id"]: e for e in reg.list_engines()}
    assert "adaptive_learning" in rows
    h = AdaptiveLearningEngine().health_check()
    assert h.ok
