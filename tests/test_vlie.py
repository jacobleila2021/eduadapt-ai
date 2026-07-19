"""VLIE unit tests — registry, enrichment pipeline, package schema."""

from __future__ import annotations

from engines.verified_learning_engine import (
    WORKFLOW_STAGES,
    VerifiedLearningOrchestrator,
    get_registry,
    reset_registry,
)


def test_registry_has_core_engines():
    reg = reset_registry()
    ids = {e["engine_id"] for e in reg.list_engines()}
    for required in (
        "curriculum",
        "scientific_accuracy",
        "assessment",
        "accessibility",
        "adaptive_learning",
        "ai_tutor",
        "learning_analytics",
        "gamification",
        "multi_agent",
        "quality_assurance",
    ):
        assert required in ids


def test_workflow_stages_documented():
    assert "curriculum" in WORKFLOW_STAGES
    assert "quality_assurance" in WORKFLOW_STAGES


def test_vlie_enrichment_without_openai():
    vlie = VerifiedLearningOrchestrator()
    result = vlie.process_lesson(
        "Plant cell has chloroplast. Solve 2*x + 3 = 11.",
        generate_adaptations=False,
    )
    assert result["run_id"]
    assert result["package"]["schema_version"] == "3.0.0"
    assert result["package"]["grounding_mode"] == "uploaded_source"
    assert "persisted_path" in result["package"]
    assert result["merged"]["engines"]
    assert "scientific_accuracy" in result["merged"]["engines"]


def test_engine_health():
    reg = get_registry()
    health = reg.health_all()
    assert len(health) >= 8
    assert any(h.engine_id == "curriculum" for h in health)
