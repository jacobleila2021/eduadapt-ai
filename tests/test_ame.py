"""Assessment & Mastery Engine tests."""

from __future__ import annotations

from engines.assessment_engine import AssessmentEngine
from engines.assessment_mastery_engine.evidence import evaluate_response, submit_answer
from engines.assessment_mastery_engine.mastery import compute_concept_mastery, recompute_all_mastery
from engines.assessment_mastery_engine.misconceptions import detect_from_text
from engines.assessment_mastery_engine.revision import generate_revision_plan
from engines.assessment_mastery_engine import service as ame_api
from engines.verified_learning_engine import reset_registry


def test_evaluate_official_mcq():
    r = evaluate_response(response="C", official_answer="C", question_type="mcq")
    assert r["correct"] is True
    r2 = evaluate_response(response="A", official_answer="C", question_type="mcq")
    assert r2["correct"] is False


def test_misconception_force_pressure():
    hits = detect_from_text("I think force is pressure so they are the same")
    assert hits
    assert any("force" in h.label.lower() or "pressure" in h.label.lower() for h in hits)


def test_submit_updates_mastery(tmp_path=None):
    lid = "ame_test_learner_force"
    out = submit_answer(
        learner_id=lid,
        assessment_id="as_test",
        item_id="exemplar-demo",
        response="wrong",
        official_answer="C",
        question_type="mcq",
        concept_id="c8sci.pressure",
        question="What is pressure?",
    )
    assert out["evaluation"]["correct"] is False
    # second evidence (correct) still needed for proficient
    submit_answer(
        learner_id=lid,
        assessment_id="as_test",
        item_id="exemplar-demo2",
        response="C",
        official_answer="C",
        question_type="mcq",
        concept_id="c8sci.pressure",
    )
    m = compute_concept_mastery(lid, "c8sci.pressure")
    assert m.evidence_count >= 2
    assert m.mastery_pct > 0


def test_revision_and_readiness():
    lid = "ame_test_learner_force"
    recompute_all_mastery(lid)
    plan = generate_revision_plan(lid, topic="Force and Pressure")
    assert "weak_concepts" in plan
    ready = ame_api.api_retrieve_exam_readiness(lid, topic="Force and Pressure")
    assert "predicted_readiness" in ready


def test_assessment_engine_ame_payload():
    eng = AssessmentEngine()
    out = eng.process(
        {
            "topic": "Force and Pressure",
            "lesson_text": "Pressure is force per unit area. Force is pressure.",
            "learner_id": "ame_test_learner_force",
            "assessment_type": "diagnostic",
        }
    )
    assert out.ok
    assert "official_mcqs" in out.payload or "exam_bundle" in out.payload
    assert "assessment_package" in out.payload
    assert out.payload.get("policy", {}).get("official_answers_only") is True


def test_dashboards():
    d = ame_api.api_dashboards("student", learner_id="ame_test_learner_force")
    assert d["role"] == "student"
    t = ame_api.api_dashboards("teacher", learner_ids=["ame_test_learner_force"])
    assert t["role"] == "teacher"


def test_assessment_registered():
    reg = reset_registry()
    rows = {e["engine_id"]: e for e in reg.list_engines()}
    assert "assessment" in rows
    h = AssessmentEngine().health_check()
    assert h.ok
