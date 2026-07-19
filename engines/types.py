"""Shared types for the Computation Layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIPPED = "skipped"


class TaskKind(str, Enum):
    SOLVE_MATH = "solve_math"
    PLOT_GRAPH = "plot_graph"
    BALANCE_EQUATION = "balance_equation"
    RENDER_CHEMISTRY = "render_chemistry"
    MOLECULE_SMILES = "molecule_smiles"
    CALCULATE_FORCE = "calculate_force"
    DRAW_CIRCUIT = "draw_circuit"
    PHYSICS_DIAGRAM = "physics_diagram"
    GEOMETRY = "geometry"
    STATISTICS = "statistics"
    TABLE = "table"
    OFFICIAL_ANSWER = "official_answer"
    ASSERTION_REASON = "assertion_reason"
    EXPLAIN_RAG = "explain_rag"
    COMPARE_CONCEPTS = "compare_concepts"
    ESSAY_RAG = "essay_rag"


@dataclass
class ToolTask:
    kind: TaskKind
    payload: dict[str, Any]
    subject: str | None = None
    grade: str | None = None


@dataclass
class EngineResult:
    """Deterministic or knowledge-backed result. Teaching must not mutate payload."""

    engine_id: str
    layer: str  # "computation" | "knowledge" | "teaching"
    task_kind: TaskKind
    payload: dict[str, Any]
    latex: str | None = None
    asset_paths: list[str] = field(default_factory=list)
    validation: ValidationStatus = ValidationStatus.SKIPPED
    validation_detail: str = ""
    provenance: dict[str, str] = field(default_factory=dict)
    deterministic: bool = True
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.validation != ValidationStatus.FAIL
