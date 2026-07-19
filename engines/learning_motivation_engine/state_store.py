"""Persistent LMAS learner state."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.learning_motivation_engine.schemas import LearnerMotivationState

STATE_DIR = DATA_DIR / "lmas" / "learners"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(learner_id: str) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in learner_id)[:80]
    return STATE_DIR / f"{safe}.json"


def load_state(learner_id: str) -> dict[str, Any]:
    p = _path(learner_id)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    doc = LearnerMotivationState(learner_id=learner_id).to_dict()
    doc["updated_at"] = _now()
    save_state(doc)
    return doc


def save_state(doc: dict[str, Any]) -> dict[str, Any]:
    doc["updated_at"] = _now()
    _path(str(doc["learner_id"])).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc
