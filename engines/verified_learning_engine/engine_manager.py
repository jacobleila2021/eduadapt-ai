"""Register default VLIE engines (facades over existing modules)."""

from __future__ import annotations

from engines.accessibility_engine import AccessibilityEngine
from engines.adaptive_learning_engine import AdaptiveLearningEngine
from engines.ai_tutor_engine import AITutorEngine
from engines.assessment_engine import AssessmentEngine
from engines.curriculum_engine import CurriculumEngine
from engines.gamification_engine import GamificationEngine
from engines.knowledge_ingestion_engine import KnowledgeIngestionEngine
from engines.learning_analytics_engine import LearningAnalyticsEngine
from engines.learning_companion_engine import LearningCompanionEngine
from engines.learning_experience_platform import LearningExperienceEngine
from engines.learning_motivation_engine import LearningMotivationEngine
from engines.multi_agent_engine import MultiAgentEngine
from engines.quality_assurance_engine import QualityAssuranceEngine
from engines.scientific_accuracy_engine import ScientificAccuracyEngine
from engines.universal_curriculum_framework import UniversalCurriculumEngine
from engines.curriculum_expansion_framework import CurriculumExpansionEngine
from engines.curriculum_migration_framework import CurriculumMigrationEngine
from engines.voice_multimodal_learning import VoiceMultimodalEngine
from engines.verified_learning_engine.engine_registry import EngineRegistry


def register_default_engines(registry: EngineRegistry) -> None:
    """Plug-and-play default set. Feature flags can disable any engine."""
    registry.register(KnowledgeIngestionEngine(), enabled=True, depends_on=[])
    registry.register(UniversalCurriculumEngine(), depends_on=["knowledge_ingestion"])
    registry.register(CurriculumExpansionEngine(), depends_on=["universal_curriculum"])
    registry.register(CurriculumMigrationEngine(), depends_on=["universal_curriculum", "curriculum_expansion"])
    registry.register(CurriculumEngine(), depends_on=["universal_curriculum"])
    registry.register(ScientificAccuracyEngine(), depends_on=["curriculum"])
    registry.register(AssessmentEngine(), depends_on=["curriculum"])
    registry.register(AccessibilityEngine(), depends_on=[])
    registry.register(AdaptiveLearningEngine(), depends_on=["accessibility", "curriculum", "assessment"])
    registry.register(AITutorEngine(), depends_on=["scientific_accuracy", "adaptive_learning", "assessment", "accessibility"])
    registry.register(
        VoiceMultimodalEngine(),
        depends_on=["accessibility", "ai_tutor", "scientific_accuracy"],
    )
    registry.register(
        LearningExperienceEngine(),
        depends_on=[
            "accessibility",
            "ai_tutor",
            "voice_multimodal",
            "curriculum",
            "multi_agent",
            "quality_assurance",
        ],
    )
    registry.register(LearningAnalyticsEngine(), depends_on=["adaptive_learning", "assessment", "accessibility", "curriculum", "ai_tutor"])
    registry.register(
        LearningMotivationEngine(),
        depends_on=["curriculum", "assessment", "accessibility", "adaptive_learning", "universal_curriculum"],
    )
    registry.register(GamificationEngine(), enabled=True, depends_on=["learning_motivation"])
    registry.register(
        LearningCompanionEngine(),
        depends_on=["accessibility", "ai_tutor", "adaptive_learning", "gamification", "voice_multimodal"],
    )
    registry.register(MultiAgentEngine(), depends_on=["accessibility", "scientific_accuracy"])
    registry.register(
        QualityAssuranceEngine(),
        depends_on=["scientific_accuracy", "curriculum", "multi_agent"],
    )
