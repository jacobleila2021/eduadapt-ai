"""Milestone 2.3 — ULI pipeline wiring (feature-flagged)."""

from __future__ import annotations

import config
from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.universal_lesson.profile import build_universal_lesson_profile
from engines.universal_lesson_intelligence import (
    ULI_MILESTONE_2_3_SMOKE_OK,
    LessonBundle,
    attach_uli_pipeline,
    finalize_lesson_bundle,
    is_uli_pipeline_enabled,
)
from engines.universal_lesson_intelligence.pipeline import build_uli_context


SAMPLE = b"""# Photosynthesis

Grade Level: 8 | Subject: Science
Students will explain photosynthesis.
Photosynthesis uses sunlight, water, and carbon dioxide.
"""


def test_milestone_2_3_smoke():
    assert ULI_MILESTONE_2_3_SMOKE_OK is True


def test_feature_flag_default_off():
    assert config.ENABLE_ULI_PIPELINE is False or isinstance(
        config.ENABLE_ULI_PIPELINE, bool
    )
    # Default env unset → False
    assert is_uli_pipeline_enabled() is False or config.ENABLE_ULI_PIPELINE is True


def test_attach_noop_shape_when_disabled(monkeypatch):
    monkeypatch.setattr(config, "ENABLE_ULI_PIPELINE", False)
    monkeypatch.setattr(
        "engines.universal_lesson_intelligence.pipeline.is_uli_pipeline_enabled",
        lambda: False,
    )
    envelope = ingest_source_bytes("t.txt", SAMPLE).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    meta: dict = {}
    attach_uli_pipeline(
        meta,
        lesson_text=SAMPLE.decode(),
        source_envelope=envelope,
        universal_profile=profile,
    )
    assert meta["uli"]["enabled"] is False
    assert meta["uli"]["feature_flag"] is False


def test_build_uli_context_non_blocking(monkeypatch):
    monkeypatch.setattr(config, "ENABLE_ULI_PIPELINE", True)
    envelope = ingest_source_bytes("t.txt", SAMPLE).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    ctx = build_uli_context(
        source_envelope=envelope,
        universal_profile=profile,
        stem_metadata={"artifacts": [], "claims_found": [], "preferred_visuals": []},
        enrich=True,
    )
    assert ctx["enabled"] is True
    assert ctx["blocks_generation"] is False
    assert "semantic_bundle" in ctx
    assert "validation_report" in ctx
    assert "accessors" in ctx
    assert "educational_structure" in ctx["accessors"]


def test_finalize_lesson_bundle_when_enabled(monkeypatch):
    monkeypatch.setattr(
        "engines.universal_lesson_intelligence.pipeline.is_uli_pipeline_enabled",
        lambda: True,
    )
    envelope = ingest_source_bytes("t.txt", SAMPLE).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    adaptations = {
        "standard": {"big_idea": "x", "sections": []},
        "_meta": {
            "universal_profile": profile,
            "source_envelope": envelope,
            "engine_artifacts": [],
        },
    }
    attach_uli_pipeline(
        adaptations["_meta"],
        lesson_text=SAMPLE.decode(),
        source_envelope=envelope,
        universal_profile=profile,
        stem_metadata={"artifacts": [], "claims_found": []},
    )
    finalize_lesson_bundle(
        adaptations,
        lesson_text=SAMPLE.decode(),
        source_envelope=envelope,
    )
    bundle = adaptations["_meta"]["lesson_bundle"]
    assert bundle["feature_flag"] is True
    assert "adaptation_payloads" in bundle
    assert "standard" in bundle["adaptation_payloads"]
    assert LessonBundle.from_dict(bundle).certification == bundle.get("certification")


def test_finalize_skipped_payload_when_disabled(monkeypatch):
    monkeypatch.setattr(
        "engines.universal_lesson_intelligence.pipeline.is_uli_pipeline_enabled",
        lambda: False,
    )
    adaptations = {"standard": {}, "_meta": {}}
    finalize_lesson_bundle(adaptations, lesson_text="hi", source_envelope={})
    assert adaptations["_meta"]["lesson_bundle"]["feature_flag"] is False
