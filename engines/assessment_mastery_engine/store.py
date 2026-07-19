"""Learner evidence + mastery store (JSON-backed, curriculum-agnostic)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.assessment_mastery_engine.schemas import (
    CompetencyProgress,
    EvidenceRecord,
    MasteryRecord,
)

AME_DIR = DATA_DIR / "ame"
LEARNERS_DIR = AME_DIR / "learners"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _learner_path(learner_id: str) -> Path:
    LEARNERS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in learner_id)[:80]
    return LEARNERS_DIR / f"{safe}.json"


def load_learner(learner_id: str) -> dict[str, Any]:
    path = _learner_path(learner_id)
    if not path.is_file():
        return {
            "learner_id": learner_id,
            "evidence": [],
            "mastery": {},
            "competencies": {},
            "attempts": [],
            "confidence": {},
            "created_at": _now(),
            "updated_at": _now(),
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_learner(state: dict[str, Any]) -> Path:
    state["updated_at"] = _now()
    path = _learner_path(str(state["learner_id"]))
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def add_evidence(learner_id: str, record: EvidenceRecord) -> dict[str, Any]:
    state = load_learner(learner_id)
    if not record.evidence_id:
        record.evidence_id = f"ev_{uuid.uuid4().hex[:10]}"
    if not record.timestamp:
        record.timestamp = _now()
    state["evidence"].append(record.to_dict())
    save_learner(state)
    return state


def upsert_mastery(learner_id: str, record: MasteryRecord) -> dict[str, Any]:
    state = load_learner(learner_id)
    record.last_updated = _now()
    state["mastery"][record.concept_id] = record.to_dict()
    save_learner(state)
    return state


def upsert_competency(learner_id: str, record: CompetencyProgress) -> dict[str, Any]:
    state = load_learner(learner_id)
    record.last_updated = _now()
    state["competencies"][record.competency_id] = record.to_dict()
    save_learner(state)
    return state


def append_attempt(learner_id: str, attempt: dict[str, Any]) -> dict[str, Any]:
    state = load_learner(learner_id)
    state.setdefault("attempts", []).append(attempt)
    save_learner(state)
    return state


def list_learners() -> list[str]:
    LEARNERS_DIR.mkdir(parents=True, exist_ok=True)
    return [p.stem for p in LEARNERS_DIR.glob("*.json")]
