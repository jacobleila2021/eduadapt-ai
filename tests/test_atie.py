"""AI Tutor Intelligence Engine tests."""

from __future__ import annotations

from engines.ai_tutor_engine import AITutorEngine
from engines.ai_tutor_intelligence_engine import atie_api
from engines.verified_learning_engine import reset_registry


def _ctx(**extra):
    base = {
        "learner_id": "atie_test_learner",
        "topic": "Force and Pressure",
        "grade": "8",
        "lesson_text": "Pressure is force per unit area. P = F/A.",
        "generate_turn": True,
        "start_session": True,
        "engine_outputs": {
            "curriculum": {
                "payload": {
                    "curriculum_intelligence": {
                        "primary_concept_id": "c8sci.pressure",
                        "matched_concepts": [
                            {
                                "concept_id": "c8sci.pressure",
                                "title": "Pressure",
                                "definition": "Force per unit area; P = F/A.",
                            }
                        ],
                        "learning_outcomes": [{"statement": "Apply P=F/A"}],
                    },
                    "knowledge": {
                        "citations": ["[NCERT Class 8 Science Ch.11]"],
                        "rag_hits": [
                            {
                                "text": "Pressure is force per unit area.",
                                "citation": "[NCERT Class 8 Science Ch.11]",
                                "score": 0.9,
                            }
                        ],
                    },
                }
            },
            "assessment": {
                "payload": {
                    "misconceptions": [
                        {
                            "misconception_id": "misc.force_eq_pressure",
                            "label": "Force and pressure are the same",
                            "concept_id": "c8sci.pressure",
                            "evidence": "Learner conflates force and pressure",
                            "intervention_ids": ["int.visual_pfa"],
                        }
                    ],
                    "official_mcqs": [{"item_id": "q1", "question": "What is pressure?"}],
                }
            },
            "accessibility": {
                "payload": {
                    "profiles_generated": ["dyslexia"],
                    "presentation": {"primary_mode": "dyslexia"},
                    "learner_profile": {"active_profiles": ["dyslexia", "adhd"]},
                }
            },
            "adaptive_learning": {
                "payload": {
                    "learner_model": {
                        "concepts_at_risk": ["c8sci.pressure"],
                        "confidence": 0.4,
                        "accessibility_profiles": ["dyslexia", "adhd"],
                    },
                    "next_activity": {"presentation_mode": "dyslexia", "estimated_minutes": 10},
                    "day_plan": {"goals": ["Review pressure"]},
                    "explainability": {"next_activity_explanation": "remediation"},
                }
            },
            "scientific_accuracy": {"payload": {"artifacts": []}},
        },
    }
    base.update(extra)
    return base


def test_grounded_tutor_turn():
    eng = AITutorEngine()
    out = eng.process(_ctx())
    assert out.ok
    assert out.payload.get("policy", {}).get("retrieve_before_generate") is True
    assert out.payload.get("grounding_packet", {}).get("ok") is True
    assert out.payload.get("session", {}).get("turn")
    assert "Pressure" in (out.payload.get("session", {}).get("turn", {}).get("content") or "") or out.payload.get(
        "session", {}
    ).get("response", {}).get("ok")


def test_refuse_without_evidence():
    eng = AITutorEngine()
    out = eng.process(
        {
            "learner_id": "atie_empty",
            "topic": "Unknown Topic XYZ",
            "lesson_text": "",
            "generate_turn": True,
            "engine_outputs": {},
        }
    )
    assert out.ok
    # May soft-retrieve from RAG; if still empty, insufficient flag
    gp = out.payload.get("grounding_packet") or {}
    if gp.get("insufficient_evidence"):
        content = (out.payload.get("session") or {}).get("turn", {}).get("content") or ""
        assert "cannot" in content.lower() or "confident" in content.lower() or "teacher" in content.lower()


def test_hint_api():
    h = atie_api.api_generate_hint(**_ctx(hint_level=2, generate_turn=False))
    assert h.get("ok") is True
    assert h.get("level") == 2
    assert "Hint 2" in h.get("content", "")


def test_registered():
    reg = reset_registry()
    assert "ai_tutor" in {e["engine_id"] for e in reg.list_engines()}
    assert AITutorEngine().health_check().ok
