"""
Universal Lesson Intelligence Validation & Quality Engine (ULIQE).

Deterministic quality gate for ULI objects. Never invents educational content.
Does not modify VLIE, ULI facade, or other intelligence engines.
"""

from __future__ import annotations

from engines.universal_lesson_validation.engine import UniversalLessonValidationEngine
from engines.universal_lesson_validation.schemas import (
    CATEGORY_WEIGHTS,
    CertificationLevel,
    ULIQEReport,
)
from engines.universal_lesson_validation.service import (
    certify_uli,
    compare_versions,
    gate_for_downstream,
    generate_report,
    list_validation_rules,
    score_uli,
    validate_uli,
)

ULIQE_SMOKE_OK = True

__all__ = [
    "ULIQE_SMOKE_OK",
    "CATEGORY_WEIGHTS",
    "CertificationLevel",
    "ULIQEReport",
    "UniversalLessonValidationEngine",
    "validate_uli",
    "score_uli",
    "certify_uli",
    "generate_report",
    "compare_versions",
    "list_validation_rules",
    "gate_for_downstream",
]
