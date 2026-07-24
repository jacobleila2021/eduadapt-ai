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
from engines.lesson_composition_engine.content_fidelity import (
    CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK,
    apply_content_fidelity,
)
from engines.lesson_composition_engine.publisher_remediation import (
    ALORA_PUBLISHER_REMEDIATION_SMOKE_OK,
)
from engines.lesson_composition_engine.intelligence_board import (
    PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK,
    build_lesson_intelligence_board,
)
from engines.lesson_composition_engine.editorial_board import review_package_editorial
from engines.lesson_composition_engine.publisher_style_guide import (
    PHASE_OMEGA_2_PMES_SMOKE_OK,
    STYLE_GUIDE,
    style_guide_css,
)
from engines.lesson_composition_engine.pmes import critique_adaptation, run_pmes

__all__ = [
    "LESSON_COMPOSITION_ENGINE_SMOKE_OK",
    "LCE_SMOKE_OK",
    "PUBLISHER_QUALITY_LESSON_EXCELLENCE_SMOKE_OK",
    "ALORA_PUBLISHER_REMEDIATION_SMOKE_OK",
    "CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK",
    "PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK",
    "PHASE_OMEGA_2_PMES_SMOKE_OK",
    "PUBLISHER_QUALITY_THRESHOLD",
    "LCE_ENGINE_ID",
    "LCE_SCHEMA_VERSION",
    "PACK_VERSION",
    "PRODUCTION_THRESHOLD",
    "ADAPTIVE_VERSION_IDS",
    "STYLE_GUIDE",
    "LessonCompositionEngine",
    "compose_lesson_package",
    "attach_lce_to_adaptations",
    "apply_content_fidelity",
    "build_canonical_lesson_graph",
    "build_lesson_intelligence_board",
    "review_adaptation",
    "review_package",
    "review_package_editorial",
    "critique_adaptation",
    "run_pmes",
    "style_guide_css",
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
