"""Learning Analytics & Insights Engine tests."""

from __future__ import annotations

from engines.learning_analytics_engine import LearningAnalyticsEngine, laie_api
from engines.verified_learning_engine import reset_registry


def _ctx():
    return {
        "learner_id": "laie_test_learner",
        "topic": "Force and Pressure",
        "grade": "8",
        "lesson_text": "Pressure is force per unit area. Students will explain P=F/A.",
        "analytics_role": "teacher",
        "engine_outputs": {
            "curriculum": {
                "payload": {
                    "curriculum_intelligence": {
                        "matched_concepts": [{"concept_id": "c8sci.pressure", "title": "Pressure"}],
                        "learning_outcomes": [{"outcome_id": "lo1", "bloom": "apply", "dok": "3"}],
                        "learning_gaps": {"missing_prerequisites": []},
                        "graph_stats": {"concepts": 19},
                    }
                }
            },
            "assessment": {
                "payload": {
                    "official_mcqs": [{"item_id": "x"}],
                    "mastery": {"weak_concepts": [{"concept_id": "c8sci.pressure", "mastery_pct": 0.4}]},
                    "misconceptions": [{"label": "Force equals pressure", "misconception_id": "m1"}],
                    "exam_readiness": {"readiness_score": 0.4, "predicted_readiness": "needs_revision", "confidence_level": 0.5},
                }
            },
            "accessibility": {
                "payload": {
                    "profiles_generated": ["dyslexia"],
                    "wcag_target": "WCAG 2.2 AA",
                    "learner_profile": {"active_profiles": ["dyslexia"]},
                    "accommodations": {"functional_supports": ["tts"], "recommendations": []},
                    "interface": {"font": "OpenDyslexic", "focus_mode": True},
                }
            },
            "adaptive_learning": {
                "payload": {
                    "learner_model": {
                        "concepts_at_risk": ["c8sci.pressure"],
                        "concepts_mastered": [],
                        "confidence": 0.4,
                        "accessibility_profiles": ["dyslexia"],
                    },
                    "predictions": {
                        "risk_of_failure": 0.7,
                        "risk_of_disengagement": 0.5,
                        "probability_of_mastery": 0.3,
                        "recommended_intervention_timing": "immediate",
                        "confidence": 0.8,
                        "explanatory_factors": [{"factor": "at_risk", "value": 1}],
                    },
                    "interventions": [{"title": "Visual P=F/A", "priority": 10, "intervention_id": "int.visual_pfa"}],
                    "explainability": {"next_activity_explanation": "guided remediation"},
                    "recommendations": {"student": [], "teacher": [], "parent": []},
                }
            },
            "ai_tutor": {"payload": {"modes": ["socratic"], "verified_artifact_count": 1}},
            "gamification": {"payload": {"xp": 0, "streaks": {"days": 2}, "quests": ["Review"]}},
        },
    }


def test_laie_insights_payload():
    eng = LearningAnalyticsEngine()
    out = eng.process(_ctx())
    assert out.ok
    assert "report" in out.payload
    assert out.payload.get("policy", {}).get("insights_only") is True
    assert out.payload.get("what_happened")
    assert out.payload.get("predictions")
    assert out.payload.get("recommendations")
    assert out.payload.get("alerts")


def test_apis():
    ctx = _ctx()
    learner = laie_api.api_learner_analytics(**ctx)
    assert learner.get("learning_progress")
    pred = laie_api.api_predictive_insights(**ctx)
    assert "risk_of_falling_behind" in pred
    dash = laie_api.api_dashboard_summaries("parent", **ctx)
    assert dash["role"] == "parent"
    rep = laie_api.api_reporting("student", **ctx)
    assert rep["ok"]


def test_registered():
    reg = reset_registry()
    assert "learning_analytics" in {e["engine_id"] for e in reg.list_engines()}
    h = LearningAnalyticsEngine().health_check()
    assert h.ok
