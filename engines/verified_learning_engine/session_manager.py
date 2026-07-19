"""Learning session manager — lifecycle + persistence."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.verified_learning_engine.event_registry import SESSION_STAGES
from engines.verified_learning_engine.state_machine import LearnerStateMachine
from engines.verified_learning_engine.workflow_manager import WorkflowManager

SESSIONS_DIR = DATA_DIR / "vlie" / "sessions"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(session_id: str) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)[:80]
    return SESSIONS_DIR / f"{safe}.json"


class SessionManager:
    def create(
        self,
        *,
        learner_id: str = "anonymous",
        lesson_id: str = "",
        topic: str = "",
        workflow_id: str = "lesson_learning",
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        sid = f"ls_{uuid.uuid4().hex[:12]}"
        sm = LearnerStateMachine("preparing")
        wf = WorkflowManager(workflow_id)
        doc = {
            "session_id": sid,
            "learner_id": learner_id,
            "lesson_id": lesson_id or topic or "lesson",
            "topic": topic,
            "stage": "session_created",
            "stage_timestamps": {"session_created": _now()},
            "state_machine": sm.to_dict(),
            "workflow": wf.to_dict(),
            "workflow_id": workflow_id,
            "paused": False,
            "closed": False,
            "engine_outputs_summary": {},
            "pending_interventions": [],
            "recommendations": [],
            "decisions": [],
            "checkpoints": [],
            "meta": meta or {},
            "created_at": _now(),
            "updated_at": _now(),
            "stages_available": list(SESSION_STAGES),
        }
        self._save(doc)
        return doc

    def load(self, session_id: str) -> dict[str, Any] | None:
        path = _path(session_id)
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, doc: dict[str, Any]) -> Path:
        doc["updated_at"] = _now()
        path = _path(doc["session_id"])
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def set_stage(self, session_id: str, stage: str) -> dict[str, Any]:
        doc = self.load(session_id)
        if not doc:
            raise FileNotFoundError(session_id)
        if stage not in SESSION_STAGES:
            raise ValueError(f"Unknown stage: {stage}")
        doc["stage"] = stage
        doc.setdefault("stage_timestamps", {})[stage] = _now()
        self._save(doc)
        return doc

    def apply_state_event(self, session_id: str, event_type: str) -> dict[str, Any]:
        doc = self.load(session_id)
        if not doc:
            raise FileNotFoundError(session_id)
        sm = LearnerStateMachine((doc.get("state_machine") or {}).get("state") or "preparing")
        # restore history lightly
        result = sm.transition(event_type)
        doc["state_machine"] = sm.to_dict()
        self._save(doc)
        return {"session": doc, "transition": result}

    def pause(self, session_id: str) -> dict[str, Any]:
        doc = self.set_stage(session_id, "lesson_paused")
        doc["paused"] = True
        self._save(doc)
        return self.apply_state_event(session_id, "SessionPaused")["session"]

    def resume(self, session_id: str) -> dict[str, Any]:
        doc = self.load(session_id)
        if not doc:
            raise FileNotFoundError(session_id)
        doc["paused"] = False
        doc["stage"] = "lesson_resumed"
        doc.setdefault("stage_timestamps", {})["lesson_resumed"] = _now()
        doc.setdefault("stage_timestamps", {})["session_restored"] = _now()
        self._save(doc)
        self.apply_state_event(session_id, "SessionRestored")
        return self.apply_state_event(session_id, "SessionResumed")["session"]

    def close(self, session_id: str) -> dict[str, Any]:
        doc = self.set_stage(session_id, "session_closed")
        doc["closed"] = True
        self._save(doc)
        return self.apply_state_event(session_id, "SessionClosed")["session"]

    def checkpoint(self, session_id: str, label: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        doc = self.load(session_id)
        if not doc:
            raise FileNotFoundError(session_id)
        doc.setdefault("checkpoints", []).append({"at": _now(), "label": label, "data": data or {}})
        self._save(doc)
        return doc

    def timeline(self, session_id: str) -> dict[str, Any]:
        doc = self.load(session_id)
        if not doc:
            raise FileNotFoundError(session_id)
        stamps = doc.get("stage_timestamps") or {}
        ordered = sorted(stamps.items(), key=lambda kv: kv[1])
        return {
            "session_id": session_id,
            "stage": doc.get("stage"),
            "state": (doc.get("state_machine") or {}).get("state"),
            "timeline": [{"stage": s, "ts": t} for s, t in ordered],
            "workflow": doc.get("workflow"),
        }
