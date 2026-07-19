"""Coordinate interventions — records trigger/engine/reason/evidence/outcome hooks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InterventionManager:
    KINDS = (
        "reading_support",
        "executive_function_prompt",
        "worked_example",
        "visual_explanation",
        "audio_explanation",
        "spaced_review",
        "retrieval_practice",
        "teacher_notification",
        "parent_recommendation",
    )

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def from_decisions(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for d in decisions:
            action = d.get("action") or {}
            if not (action.get("intervention") or d.get("decision_type") in ("misconception_intervention", "remediation", "presentation_adjust")):
                continue
            kind = "retrieval_practice"
            if d.get("decision_type") == "presentation_adjust":
                kind = "reading_support"
            elif d.get("decision_type") == "misconception_intervention":
                kind = "worked_example"
            elif d.get("decision_type") == "remediation":
                kind = "spaced_review"
            row = {
                "intervention_id": f"iv_{uuid.uuid4().hex[:8]}",
                "kind": kind,
                "trigger": d.get("decision_type"),
                "engine_involved": d.get("responsible_engine"),
                "reason": d.get("reason"),
                "evidence": d.get("evidence") or [],
                "outcome": None,
                "ts": _now(),
            }
            self.records.append(row)
            out.append(row)
        return out

    def record_outcome(self, intervention_id: str, outcome: str) -> dict[str, Any] | None:
        for r in self.records:
            if r["intervention_id"] == intervention_id:
                r["outcome"] = outcome
                r["outcome_ts"] = _now()
                return r
        return None

    def export(self) -> list[dict[str, Any]]:
        return list(self.records)
