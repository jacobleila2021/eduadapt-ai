"""REST-shaped API facade for VLIE Learning Session Orchestrator."""

from __future__ import annotations

from typing import Any

from engines.verified_learning_engine.orchestrator import VerifiedLearningOrchestrator
from engines.verified_learning_engine.workflow_manager import WorkflowManager

_ORCH: VerifiedLearningOrchestrator | None = None


def _orch() -> VerifiedLearningOrchestrator:
    global _ORCH
    if _ORCH is None:
        _ORCH = VerifiedLearningOrchestrator()
    return _ORCH


def reset_service_orchestrator() -> None:
    global _ORCH
    _ORCH = None


# ── Session lifecycle ─────────────────────────────────────────────────────


def api_create_session(**kwargs: Any) -> dict[str, Any]:
    return {"ok": True, "session": _orch().create_session(**kwargs)}


def api_resume_session(session_id: str) -> dict[str, Any]:
    return {"ok": True, "session": _orch().resume_session(session_id)}


def api_pause_session(session_id: str) -> dict[str, Any]:
    return {"ok": True, "session": _orch().pause_session(session_id)}


def api_close_session(session_id: str) -> dict[str, Any]:
    return {"ok": True, "session": _orch().close_session(session_id)}


# ── Events & timeline ─────────────────────────────────────────────────────


def api_publish_event(event_type: str, session_id: str, **kwargs: Any) -> dict[str, Any]:
    return {"ok": True, "event": _orch().publish_event(event_type, session_id=session_id, **kwargs)}


def api_retrieve_event_history(session_id: str | None = None, limit: int = 200) -> dict[str, Any]:
    return {"ok": True, "events": _orch().event_history(session_id=session_id, limit=limit)}


def api_retrieve_session_timeline(session_id: str) -> dict[str, Any]:
    return {"ok": True, **_orch().session_timeline(session_id)}


# ── Workflow & decisions ──────────────────────────────────────────────────


def api_retrieve_workflow(session_id: str | None = None, workflow_id: str | None = None) -> dict[str, Any]:
    if session_id:
        doc = _orch().sessions.load(session_id)
        if not doc:
            return {"ok": False, "error": "session_not_found"}
        return {"ok": True, "workflow": doc.get("workflow"), "templates": WorkflowManager.list_templates()}
    return {
        "ok": True,
        "workflow": WorkflowManager(workflow_id or "lesson_learning").to_dict(),
        "templates": WorkflowManager.list_templates(),
    }


def api_advance_workflow(session_id: str) -> dict[str, Any]:
    return {"ok": True, **_orch().advance_workflow(session_id)}


def api_retrieve_orchestration_decisions(session_id: str) -> dict[str, Any]:
    doc = _orch().sessions.load(session_id)
    if not doc:
        return {"ok": False, "error": "session_not_found"}
    return {"ok": True, "decisions": doc.get("decisions") or []}


def api_orchestrate(session_id: str, engine_outputs: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": True, **_orch().orchestrate_from_engines(session_id, engine_outputs, context=context)}


# ── Health, audit, recommendations ────────────────────────────────────────


def api_retrieve_engine_status() -> dict[str, Any]:
    return {"ok": True, "engines": _orch().integrations.list_all()}


def api_retrieve_health_report() -> dict[str, Any]:
    return {"ok": True, "health": _orch().health_report()}


def api_retrieve_audit_logs(session_id: str | None = None, limit: int = 200) -> dict[str, Any]:
    logs = _orch().audit.search(session_id=session_id, limit=limit) if session_id else _orch().audit.export()[-limit:]
    return {"ok": True, "audit": logs}


def api_retrieve_recommendations(session_id: str) -> dict[str, Any]:
    doc = _orch().sessions.load(session_id)
    if not doc:
        return {"ok": False, "error": "session_not_found"}
    return {"ok": True, "recommendations": doc.get("recommendations") or []}


def api_retrieve_session_memory(session_id: str) -> dict[str, Any]:
    snap = _orch().memory.snapshot(session_id)
    if not snap:
        return {"ok": False, "error": "session_not_found"}
    return {"ok": True, "memory": snap}


def api_retrieve_config() -> dict[str, Any]:
    return {"ok": True, "config": _orch().config.export(), "policies": _orch().policies.export()}
