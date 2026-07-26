"""Contract tests for Teaching Policy Pack (Phase 1 Steps 1–3)."""

from __future__ import annotations

import ai_generator
from knowledge.prompts import (
    AUDITORY_SECTION_RULES,
    BULLET_SECTION_RULES,
    DEPTH_RULES,
    DIFFERENTIATION_RULES,
    ENGINE_RULES,
    RAG_CITATION_RULES,
    RAG_RULES,
    SECTION_TITLE_RULES,
    TEACHER_ANSWER_RULES,
    VISUAL_PRACTICE_RULES,
    enrichment_policy_header,
)


def test_policy_pack_strings_are_non_empty_and_stable():
    """Byte-stable markers for relocated teaching policies."""
    assert "DEPTH REQUIREMENTS (critical):" in DEPTH_RULES
    assert "VERIFIED KNOWLEDGE FIRST" in ENGINE_RULES
    assert "SOURCE GROUNDING:" in RAG_CITATION_RULES
    assert "RETRIEVED_SOURCES are optional enrichment" in RAG_CITATION_RULES
    assert "DIFFERENTIATION (minimum 80% unique" in DIFFERENTIATION_RULES
    assert "SECTION TITLES (critical" in SECTION_TITLE_RULES
    assert "DYSLEXIA SMART FORMAT" in BULLET_SECTION_RULES
    assert "AUDITORY LEARNER FORMAT" in AUDITORY_SECTION_RULES
    assert "VISUAL LEARNER PRACTICE FORMAT" in VISUAL_PRACTICE_RULES
    assert "TEACHER VERSION (teacher adaptation only):" in TEACHER_ANSWER_RULES
    assert "KNOWLEDGE LAYER — RETRIEVED SOURCES (mandatory when provided):" in RAG_RULES


def test_ai_generator_reexports_pack_without_local_duplicates():
    """ai_generator must consume the pack — not redefine policy bodies."""
    assert ai_generator.DEPTH_RULES is DEPTH_RULES
    assert ai_generator.ENGINE_RULES is ENGINE_RULES
    assert ai_generator.RAG_CITATION_RULES is RAG_CITATION_RULES
    assert ai_generator.DIFFERENTIATION_RULES is DIFFERENTIATION_RULES
    assert ai_generator.SECTION_TITLE_RULES is SECTION_TITLE_RULES
    assert ai_generator.BULLET_SECTION_RULES is BULLET_SECTION_RULES
    assert ai_generator.AUDITORY_SECTION_RULES is AUDITORY_SECTION_RULES
    assert ai_generator.VISUAL_PRACTICE_RULES is VISUAL_PRACTICE_RULES
    assert ai_generator.TEACHER_ANSWER_RULES is TEACHER_ANSWER_RULES


def test_lesson_prompt_embeds_canonical_pack():
    prompt = ai_generator._lesson_prompt("standard", "Standard", "hint")
    assert DEPTH_RULES in prompt
    assert ENGINE_RULES in prompt
    assert RAG_CITATION_RULES in prompt
    assert DIFFERENTIATION_RULES in prompt
    # Must not embed the strict official RAG_RULES header in default lesson prompts
    assert "KNOWLEDGE LAYER — RETRIEVED SOURCES (mandatory when provided):" not in prompt


def test_enrichment_policy_header_mode_aware():
    assert enrichment_policy_header("uploaded_source") is RAG_CITATION_RULES
    assert enrichment_policy_header() is RAG_CITATION_RULES
    assert enrichment_policy_header("official_curriculum_publish") is RAG_RULES


def test_prepare_knowledge_out_of_scope_uses_optional_header():
    from knowledge.service import prepare_knowledge_for_lesson

    result = prepare_knowledge_for_lesson(
        "Grade Level: 6 | Subject: Earth Science\nThe water cycle includes evaporation.",
        {
            "topic": "The Water Cycle",
            "grade_level": "Grade 6",
            "vocabulary_terms": ["evaporation", "condensation"],
        },
        grounding_mode="uploaded_source",
    )
    assert result["scope_matched"] is False
    assert result["external_enrichment"]["required"] is False
    assert result["prompt_block"] == RAG_CITATION_RULES
    assert "mandatory when provided" not in result["prompt_block"]


def test_prepare_knowledge_official_mode_uses_strict_header_when_out_of_scope():
    from knowledge.service import prepare_knowledge_for_lesson

    result = prepare_knowledge_for_lesson(
        "Grade Level: 6 | Subject: Earth Science\nThe water cycle includes evaporation.",
        {"topic": "The Water Cycle", "grade_level": "Grade 6"},
        grounding_mode="official_curriculum_publish",
    )
    assert result["prompt_block"] == RAG_RULES
    assert result["grounding_mode"] == "official_curriculum_publish"


def test_prepare_knowledge_available_block_aligned_with_system_policy(monkeypatch):
    """When enrichment is available under uploaded_source, header must not contradict RAG_CITATION_RULES."""
    from knowledge import service as knowledge_service
    from knowledge.types import RagHit

    class FakeRag:
        def ensure_index(self):
            return {"indexed": 1, "backend": "test"}

        def retrieve(self, query, k=6):
            return [
                RagHit(
                    chunk_id="c1",
                    citation="[NCERT Class 8 Science Ch.1 p.1]",
                    chapter_title="Crop Production",
                    text="Crop production and management overview for class 8.",
                    score=0.9,
                    metadata={},
                )
            ]

    monkeypatch.setattr(knowledge_service, "_rag_singleton", FakeRag())
    monkeypatch.setattr(knowledge_service, "_scope_matches", lambda *a, **k: True)
    monkeypatch.setattr(knowledge_service, "match_official_mcqs", lambda *a, **k: [])
    monkeypatch.setattr(knowledge_service, "match_exam_bundle", lambda *a, **k: {})

    result = knowledge_service.prepare_knowledge_for_lesson(
        "Grade Level: 8 | Subject: Science\nCrop production.",
        {"topic": "Crop Production", "grade_level": "8", "vocabulary_terms": ["crop"]},
        grounding_mode="uploaded_source",
    )
    assert result["external_enrichment"]["status"] == "available"
    assert result["external_enrichment"]["required"] is False
    assert result["prompt_block"].startswith(RAG_CITATION_RULES.strip()) or result[
        "prompt_block"
    ].startswith(RAG_CITATION_RULES)
    assert "KNOWLEDGE LAYER — RETRIEVED SOURCES (mandatory when provided):" not in result[
        "prompt_block"
    ]
    assert "RETRIEVED_SOURCES" in result["prompt_block"]
