"""
Universal Lesson Intelligence (ULI) — Milestones 2.1–2.3.

2.1 Facade · 2.2 Semantic enrichment · 2.3 Feature-flagged pipeline wiring
"""

from __future__ import annotations

from engines.universal_lesson_intelligence.bundle import LessonBundle
from engines.universal_lesson_intelligence.facade import (
    ULI_MILESTONE_2_2_SMOKE_OK,
    ULI_SCHEMA_VERSION,
    UniversalLessonIntelligence,
    build_enriched_universal_lesson_intelligence,
    build_universal_lesson_intelligence,
)
from engines.universal_lesson_intelligence.pipeline import (
    ULI_MILESTONE_2_3_SMOKE_OK,
    attach_uli_pipeline,
    build_uli_context,
    finalize_lesson_bundle,
    get_uli_from_adaptations,
    is_uli_pipeline_enabled,
)

__all__ = [
    "ULI_SCHEMA_VERSION",
    "ULI_MILESTONE_2_2_SMOKE_OK",
    "ULI_MILESTONE_2_3_SMOKE_OK",
    "LessonBundle",
    "UniversalLessonIntelligence",
    "build_universal_lesson_intelligence",
    "build_enriched_universal_lesson_intelligence",
    "is_uli_pipeline_enabled",
    "build_uli_context",
    "attach_uli_pipeline",
    "finalize_lesson_bundle",
    "get_uli_from_adaptations",
]
