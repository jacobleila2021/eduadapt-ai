"""Canonical LessonBundle — shared object for ULI pipeline (Milestone 2.3)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class LessonBundle:
    """
    Single package every downstream engine can read.

    Built when ENABLE_ULI_PIPELINE is on. Attached under adaptations ``_meta``;
    does not replace the adaptations dict returned to the UI.
    """

    raw_lesson: str = ""
    universal_lesson: dict[str, Any] = field(default_factory=dict)
    semantic_bundle: dict[str, Any] = field(default_factory=dict)
    validation_report: dict[str, Any] = field(default_factory=dict)
    certification: str = ""
    quality_score: float | None = None
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    subject_intelligence: dict[str, Any] = field(default_factory=dict)
    adaptation_payloads: dict[str, Any] = field(default_factory=dict)
    export_payloads: dict[str, Any] = field(default_factory=dict)
    source_envelope: dict[str, Any] = field(default_factory=dict)
    uli_schema_version: str = ""
    feature_flag: bool = False
    pipeline_version: str = "2.3.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> LessonBundle:
        data = data or {}
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})
