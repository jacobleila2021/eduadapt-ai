"""VLIE Learning Session Orchestrator — unit, workflow, recovery, smoke tests."""

from __future__ import annotations

from engines.verified_learning_engine import (
    EVENT_TYPES,
    LEARNER_STATES,
    SESSION_STAGES,
    VerifiedLearningOrchestrator,
    WorkflowManager,
    reset_registry,
)
from engines.verified_learning_engine.event_bus import reset_event_bus
from engines.verified_learning_engine.policy_engine import PolicyEngine
from engines.verified_learning_engine.service import (
    api_close_session,
    api_create_session,
    api_orchestrate,
    api_pause_session,
    api_publish_event,
    api_retrieve_audit_logs,
    api_retrieve_engine_status,
    api_retrieve_event_history,
    api_retrieve_health_report,
    api_retrieve_recommendations,
    api_retrieve_session_timeline,
    api_retrieve_workflow,
    api_resume_session,
    reset_service_orchestrator,
)
from engines.verified_learning_engine.state_machine import LearnerStateMachine


def _fresh() -> VerifiedLearningOrchestrator:
    reset_registry()
    reset_event_bus()
    reset_service_orchestrator()
    return VerifiedLearningOrchestrator()


def test_event_catalogue_complete():
    for required in (
        "LessonOpened",
        "LessonCompleted",
        "HintRequested",
        "MisconceptionDetected",
        "AssessmentCompleted",
        "MasteryUpdated",
        "RecommendationGenerated",
    ):
        assert required in EVENT_TYPES
    assert "session_created" in SESSION_STAGES
    assert "preparing" in LEARNER_STATES


def test_state_machine_deterministic():
    sm = LearnerStateMachine("preparing")
    r1 = sm.transition("LessonOpened")
    assert r1["to"] == "reading" and r1["changed"]
    r2 = sm.transition("AssessmentStarted")
    assert r2["to"] == "assessing"
    r3 = sm.transition("SessionPaused")
    assert r3["to"] == "interrupted"


def test_workflow_templates():
    templates = {t["id"] for t in WorkflowManager.list_templates()}
    assert {"lesson_learning", "exam_revision", "homework"} <= templates
    wf = WorkflowManager("lesson_learning")
    assert wf.current_step() == "lesson"
    adv = wf.advance()
    assert adv["completed_step"] == "lesson"
    assert adv["next_step"] == "tutor"


def test_session_lifecycle_and_events():
    vlie = _fresh()
    session = vlie.create_session(learner_id="learner_a", lesson_id="ch1", topic="Cells")
    sid = session["session_id"]
    assert session["stage"] == "session_created"
    assert "session_created" in session["stage_timestamps"]

    vlie.publish_event("LessonLoaded", session_id=sid)
    vlie.publish_event("LessonOpened", session_id=sid)
    paused = vlie.pause_session(sid)
    assert paused["paused"] is True
    resumed = vlie.resume_session(sid)
    assert resumed["paused"] is False
    closed = vlie.close_session(sid)
    assert closed["closed"] is True

    hist = vlie.event_history(session_id=sid)
    types = {e["event_type"] for e in hist}
    assert "SessionCreated" in types
    assert "LessonLoaded" in types
    assert "SessionClosed" in types

    timeline = vlie.session_timeline(sid)
    assert timeline["timeline"]
    assert any(x["stage"] == "session_created" for x in timeline["timeline"])


def test_orchestration_decisions_interventions_recommendations():
    vlie = _fresh()
    session = vlie.create_session(learner_id="learner_b", lesson_id="ch2")
    sid = session["session_id"]
    engine_outputs = {
        "adaptive_learning": {
            "ok": True,
            "payload": {
                "learner_model": {"concepts_at_risk": ["photosynthesis"], "confidence": 0.3},
                "confidence": {"confidence": 0.3},
                "predictions": {"risk_of_failure": 0.7, "risk_of_disengagement": 0.6},
                "misconceptions": [{"id": "misc1"}],
                "next_activity": {"concept_id": "chloroplast", "activity_type": "practice"},
                "spaced_repetition": [{"concept_id": "cells", "sessions": [{"day_offset": 1}]}],
            },
        },
        "assessment": {"ok": True, "payload": {"misconceptions": [{"id": "m1"}]}},
        "accessibility": {"ok": True, "payload": {"learner_profile": {"active_profiles": ["dyslexia"]}}},
    }
    result = vlie.orchestrate_from_engines(sid, engine_outputs, context={"help_requests": 4})
    assert result["decisions"]
    assert result["recommendations"]
    assert any(d["decision_type"] == "remediation" for d in result["decisions"])
    assert result["interventions"]
    mem = vlie.memory.snapshot(sid)
    assert mem and mem["pending_interventions"]


def test_policy_never_official_answers():
    pe = PolicyEngine()
    assert pe.assert_allowed("generate_official_answer")["allowed"] is False
    assert pe.assert_allowed("mutate_curriculum")["allowed"] is False


def test_dependency_no_cycles():
    vlie = _fresh()
    dep = vlie.dependencies.validate_no_cycles()
    assert dep["ok"] is True


def test_event_replay():
    vlie = _fresh()
    session = vlie.create_session(learner_id="replay")
    sid = session["session_id"]
    vlie.publish_event("LessonOpened", session_id=sid)
    hist = vlie.event_history(session_id=sid)
    reset_event_bus()
    vlie.bus = reset_event_bus()
    count = vlie.bus.replay(hist)
    assert count >= 1
    assert vlie.bus.history(session_id=sid)


def test_offline_restore():
    vlie = _fresh()
    session = vlie.create_session(learner_id="offline_user", meta={"offline": True})
    sid = session["session_id"]
    restored = vlie.memory.restore_offline(sid)
    assert restored
    assert (restored.get("meta") or {}).get("offline") is False


def test_service_apis():
    reset_registry()
    reset_event_bus()
    reset_service_orchestrator()
    created = api_create_session(learner_id="api_user", lesson_id="L1")
    assert created["ok"]
    sid = created["session"]["session_id"]
    assert api_publish_event("LessonLoaded", sid)["ok"]
    assert api_pause_session(sid)["ok"]
    assert api_resume_session(sid)["ok"]
    assert api_retrieve_event_history(sid)["ok"]
    assert api_retrieve_session_timeline(sid)["ok"]
    assert api_retrieve_workflow(session_id=sid)["ok"]
    orch = api_orchestrate(
        sid,
        {"adaptive_learning": {"ok": True, "payload": {"learner_model": {"concepts_mastered": ["x"], "confidence": 0.9}}}},
    )
    assert orch["ok"]
    assert api_retrieve_recommendations(sid)["ok"]
    assert api_retrieve_audit_logs(session_id=sid)["ok"]
    assert api_retrieve_engine_status()["ok"]
    assert api_retrieve_health_report()["ok"]
    assert api_close_session(sid)["ok"]


def test_process_lesson_uses_v3_with_legacy_projection_available():
    """Regression: the public entry point remains stable after the v3 cutover."""
    vlie = _fresh()
    result = vlie.process_lesson(
        "Plant cell has chloroplast. Solve 2*x + 3 = 11.",
        generate_adaptations=False,
    )
    assert result["run_id"]
    assert result["package"]["schema_version"] == "3.0.0"
    assert result["package"]["grounding_mode"] == "uploaded_source"
    assert "scientific_accuracy" in result["merged"]["engines"]


def test_vlie_orchestration_smoke(capsys):
    """Comprehensive smoke — emits VLIE_ORCHESTRATION_SMOKE_OK via standard pytest."""
    vlie = _fresh()
    # Engines still registered
    ids = {e["engine_id"] for e in vlie.registry.list_engines()}
    for required in (
        "curriculum",
        "assessment",
        "accessibility",
        "adaptive_learning",
        "ai_tutor",
        "learning_analytics",
    ):
        assert required in ids

    session = vlie.create_session(
        learner_id="smoke_learner",
        lesson_id="smoke_lesson",
        workflow_id="lesson_learning",
    )
    sid = session["session_id"]
    for et in ("LessonLoaded", "LessonOpened", "TutorQuestionAsked", "AssessmentStarted", "AssessmentCompleted"):
        vlie.publish_event(et, session_id=sid)

    out = vlie.orchestrate_from_engines(
        sid,
        {
            "adaptive_learning": {
                "ok": True,
                "payload": {
                    "learner_model": {"concepts_at_risk": ["c1"], "confidence": 0.4},
                    "predictions": {"risk_of_failure": 0.6},
                },
            },
            "assessment": {"ok": True, "payload": {}},
        },
    )
    assert out["decisions"] and out["recommendations"]
    assert vlie.advance_workflow(sid)["engines_ordered"] is not None
    health = vlie.health_report()
    assert health["dependency_status"]["ok"]
    assert vlie.policies.get("never_generate_official_answers") is True

    # Legacy path
    pkg = vlie.process_lesson("H2 + O2 -> water. 1+1=2", generate_adaptations=False)
    assert pkg["validation"]

    # Visible under normal pytest capture (no -s / no importlib hack required)
    with capsys.disabled():
        print("VLIE_ORCHESTRATION_SMOKE_OK")
