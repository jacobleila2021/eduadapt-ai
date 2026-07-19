"""Session memory — resume checkpoints, tutor context, pending interventions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from engines.verified_learning_engine.session_manager import SessionManager


class SessionMemory:
    """Thin facade over SessionManager for orchestration memory fields."""

    def __init__(self, sessions: SessionManager | None = None) -> None:
        self.sessions = sessions or SessionManager()

    def snapshot(self, session_id: str) -> dict[str, Any] | None:
        doc = self.sessions.load(session_id)
        if not doc:
            return None
        meta = doc.get("meta") or {}
        memory = meta.get("memory") or {}
        return {
            "session_id": doc.get("session_id"),
            "workflow_state": {
                "workflow_id": doc.get("workflow_id"),
                "workflow": doc.get("workflow"),
                "status": "closed" if doc.get("closed") else ("paused" if doc.get("paused") else "active"),
            },
            "current_lesson": doc.get("lesson_id"),
            "learner_state": (doc.get("state_machine") or {}).get("state"),
            "stage": doc.get("stage"),
            "ai_tutor_context": memory.get("ai_tutor_context") or {},
            "mastery_updates": memory.get("mastery_updates") or [],
            "accessibility_settings": meta.get("accessibility") or {},
            "pending_interventions": doc.get("pending_interventions") or [],
            "resume_checkpoint": (doc.get("checkpoints") or [{}])[-1] if doc.get("checkpoints") else {},
            "offline": bool(meta.get("offline")),
        }

    def _mutate_memory(self, session_id: str, mutator) -> dict[str, Any]:
        doc = self.sessions.load(session_id)
        if not doc:
            raise FileNotFoundError(session_id)
        meta = dict(doc.get("meta") or {})
        memory = dict(meta.get("memory") or {})
        mutator(doc, meta, memory)
        meta["memory"] = memory
        doc["meta"] = meta
        self.sessions._save(doc)
        return doc

    def update_tutor_context(self, session_id: str, ctx: dict[str, Any]) -> dict[str, Any]:
        def mut(_doc, _meta, memory):
            memory["ai_tutor_context"] = {**(memory.get("ai_tutor_context") or {}), **ctx}

        return self._mutate_memory(session_id, mut)

    def append_mastery(self, session_id: str, update: dict[str, Any]) -> dict[str, Any]:
        def mut(_doc, _meta, memory):
            lst = list(memory.get("mastery_updates") or [])
            lst.append(update)
            memory["mastery_updates"] = lst[-50:]

        return self._mutate_memory(session_id, mut)

    def queue_intervention(self, session_id: str, intervention: dict[str, Any]) -> dict[str, Any]:
        def mut(doc, _meta, _memory):
            doc.setdefault("pending_interventions", []).append(intervention)

        return self._mutate_memory(session_id, mut)

    def restore_offline(self, session_id: str) -> dict[str, Any] | None:
        doc = self.sessions.load(session_id)
        if not doc:
            return None
        meta = dict(doc.get("meta") or {})
        meta["offline"] = False
        doc["meta"] = meta
        doc["stage"] = "session_restored"
        doc.setdefault("stage_timestamps", {})["session_restored"] = datetime.now(timezone.utc).isoformat()
        self.sessions._save(doc)
        return self.sessions.apply_state_event(session_id, "SessionRestored")["session"]
