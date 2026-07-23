"""
Lesson Composition Engine (LCE) 1.0 — Production Quality Adaptive Lesson Composer.

Final educational authoring layer before ULIQE / rendering.
Composes verified ULI · SIF · UVIE · Subject Pack knowledge into premium lessons.
Never invents curriculum. Never alters EngineResult payloads.
"""

from __future__ import annotations

from engines.lesson_composition_engine.engine import LessonCompositionEngine
from engines.lesson_composition_engine.service import (
    LESSON_COMPOSITION_ENGINE_SMOKE_OK,
    LCE_SMOKE_OK,
    api_attach_to_adaptations,
    api_build_blueprint,
    api_compose_lesson,
    api_compose_vocabulary,
    api_evaluate_quality,
    api_narrative_contract,
    attach_lce_to_adaptations,
    compose_lesson_package,
    pack_health,
)
from engines.lesson_composition_engine.schemas import (
    ADAPTIVE_VERSION_IDS,
    LCE_ENGINE_ID,
    LCE_SCHEMA_VERSION,
    PACK_VERSION,
    PRODUCTION_THRESHOLD,
)
from engines.lesson_composition_engine.clg import build_canonical_lesson_graph
from engines.lesson_composition_engine.eerl import review_adaptation, review_package
from engines.lesson_composition_engine.publisher_quality import (
    PUBLISHER_QUALITY_LESSON_EXCELLENCE_SMOKE_OK,
    PUBLISHER_QUALITY_THRESHOLD,
    score_package,
    score_publisher_quality,
)

__all__ = [
    "LESSON_COMPOSITION_ENGINE_SMOKE_OK",
    "LCE_SMOKE_OK",
    "PUBLISHER_QUALITY_LESSON_EXCELLENCE_SMOKE_OK",
    "PUBLISHER_QUALITY_THRESHOLD",
    "LCE_ENGINE_ID",
    "LCE_SCHEMA_VERSION",
    "PACK_VERSION",
    "PRODUCTION_THRESHOLD",
    "ADAPTIVE_VERSION_IDS",
    "LessonCompositionEngine",
    "compose_lesson_package",
    "attach_lce_to_adaptations",
    "build_canonical_lesson_graph",
    "review_adaptation",
    "review_package",
    "score_publisher_quality",
    "score_package",
    "api_compose_lesson",
    "api_build_blueprint",
    "api_compose_vocabulary",
    "api_evaluate_quality",
    "api_attach_to_adaptations",
    "api_narrative_contract",
    "pack_health",
]
