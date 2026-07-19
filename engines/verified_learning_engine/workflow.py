"""Standard VLIE workflow stages (ordered pipeline)."""

from __future__ import annotations

# Engine IDs in default execution order (priority also set on engines)
WORKFLOW_STAGES = (
    "knowledge_ingestion",
    "universal_curriculum",
    "curriculum",
    "scientific_accuracy",
    "assessment",
    "accessibility",
    "adaptive_learning",
    "ai_tutor",
    "voice_multimodal",
    "learning_analytics",
    "learning_motivation",
    "gamification",
    "learning_companion",
    "multi_agent",
    "quality_assurance",
    "learning_experience",
)


def stage_description(engine_id: str) -> str:
    return {
        "knowledge_ingestion": "Validate and extract the uploaded source",
        "universal_curriculum": "Build a curriculum-neutral source profile",
        "curriculum": "Resolve optional curriculum enrichment",
        "scientific_accuracy": "Route STEM claims through deterministic engines",
        "assessment": "Match official questions and exam bundles",
        "accessibility": "Prepare accessibility / neurodiversity profiles",
        "adaptive_learning": "Personalize presentation pathways",
        "ai_tutor": "Prepare tutor resources (grounded)",
        "voice_multimodal": "Prepare source-grounded audio and multimodal supports",
        "learning_analytics": "Compute complexity / insights metadata",
        "gamification": "Motivation hooks (accessibility-first)",
        "learning_motivation": "Prepare accessible motivation supports",
        "learning_companion": "Prepare source-grounded companion supports",
        "multi_agent": "Named teaching agents coordinate presentation",
        "quality_assurance": "Hard publish gate + scorecard",
        "learning_experience": "Package validated adaptations for the reader",
    }.get(engine_id, engine_id)
