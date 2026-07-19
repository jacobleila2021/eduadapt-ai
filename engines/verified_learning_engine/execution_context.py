"""VLIE execution context — shared state across engine steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class ExecutionContext:
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    schema_version: str = "3.0.0"
    lesson_text: str = ""
    topic: str = ""
    board: str = "unknown"
    grade: str = ""
    subject: str = ""
    api_key: str = ""
    feature_flags: dict[str, bool] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    engine_outputs: dict[str, Any] = field(default_factory=dict)
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    source_envelope: dict[str, Any] = field(default_factory=dict)
    source_id: str = ""
    classifications: list[dict[str, Any]] = field(default_factory=list)
    universal_profile: dict[str, Any] = field(default_factory=dict)
    curriculum_resolution: dict[str, Any] = field(default_factory=dict)
    grounding_policy: dict[str, Any] = field(
        default_factory=lambda: {
            "mode": "uploaded_source",
            "external_citations_required": False,
        }
    )
    stage_status: dict[str, dict[str, Any]] = field(default_factory=dict)
    stage_input_hashes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "schema_version": self.schema_version,
            "lesson_text": self.lesson_text,
            "topic": self.topic,
            "board": self.board,
            "grade": self.grade,
            "subject": self.subject,
            "feature_flags": self.feature_flags,
            "meta": self.meta,
            "engine_outputs": self.engine_outputs,
            "audit_trail": self.audit_trail,
            "source_envelope": self.source_envelope,
            "source_id": self.source_id,
            "classifications": self.classifications,
            "universal_profile": self.universal_profile,
            "curriculum_resolution": self.curriculum_resolution,
            "grounding_policy": self.grounding_policy,
            "stage_status": self.stage_status,
            "stage_input_hashes": self.stage_input_hashes,
        }

    @classmethod
    def from_lesson(
        cls,
        lesson_text: str,
        *,
        api_key: str = "",
        feature_flags: dict[str, bool] | None = None,
        **kwargs: Any,
    ) -> "ExecutionContext":
        return cls(
            lesson_text=lesson_text or "",
            api_key=api_key or "",
            feature_flags=feature_flags or {},
            **kwargs,
        )
