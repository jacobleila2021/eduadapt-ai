"""
ULI Milestone 2.3 — feature-flagged pipeline wiring.

When ENABLE_ULI_PIPELINE is off: no-op (current behaviour).
When on: build/enrich ULI, run non-blocking ULIQE, attach LessonBundle metadata.
Never changes prompts, never regenerates lessons, never rejects generation.
"""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_lesson_intelligence.bundle import LessonBundle
from engines.universal_lesson_intelligence.facade import (
    ULI_SCHEMA_VERSION,
    UniversalLessonIntelligence,
    build_universal_lesson_intelligence,
)

ULI_MILESTONE_2_3_SMOKE_OK = True


def is_uli_pipeline_enabled() -> bool:
    try:
        from config import ENABLE_ULI_PIPELINE

        return bool(ENABLE_ULI_PIPELINE)
    except Exception:  # noqa: BLE001
        return False


def build_uli_context(
    *,
    source_envelope: Mapping[str, Any],
    universal_profile: Mapping[str, Any] | None = None,
    stem_metadata: Mapping[str, Any] | None = None,
    classifications: list[Any] | None = None,
    enrich: bool = True,
) -> dict[str, Any]:
    """
    Build enriched ULI + non-blocking ULIQE report.

    Returns a plain dict for ``_meta["uli"]``. Does not raise on validation soft fails.
    """
    uli = build_universal_lesson_intelligence(
        source_envelope,
        universal_profile,
        stem_metadata=stem_metadata,
        classifications=classifications,
        enrich=enrich,
    )
    if enrich and not uli.enriched:
        uli = uli.ensure_enriched()

    # Subject Intelligence Framework (placeholders) — between enrichment and ULIQE
    sif_payload: dict[str, Any] = {}
    try:
        from engines.subject_intelligence_framework import (
            enrich_uli_with_subject_intelligence,
        )

        sif_payload = enrich_uli_with_subject_intelligence(uli)
    except Exception as exc:  # noqa: BLE001 — never block generation
        sif_payload = {
            "framework": "subject_intelligence_framework",
            "ok": False,
            "error": str(exc),
            "placeholder": True,
        }

    validation_report: dict[str, Any] = {}
    certification = ""
    quality_score = None
    warnings: list[str] = []
    recommendations: list[str] = []
    try:
        from engines.universal_lesson_validation import validate_uli

        report = validate_uli(uli)
        validation_report = report.to_dict()
        certification = report.certification.value
        quality_score = report.overall_score
        warnings = list(report.warnings)
        recommendations = list(report.recommendations)
    except Exception as exc:  # noqa: BLE001 — never block generation
        validation_report = {
            "ok": False,
            "error": str(exc),
            "pass_fail": "skipped",
            "certification": "Needs Review",
        }
        certification = "Needs Review"
        warnings = [f"ULIQE skipped: {exc}"]

    semantic = dict(uli.semantic_bundle())
    sif_warnings = list((sif_payload.get("analysis") or {}).get("warnings") or [])
    if sif_warnings:
        warnings = list(dict.fromkeys([*warnings, *sif_warnings]))
    return {
        "enabled": True,
        "uli_schema_version": uli.schema_version,
        "source_id": uli.source_id,
        "enriched": uli.enriched,
        "universal_lesson": uli.to_dict(),
        "semantic_bundle": semantic,
        "subject_intelligence": sif_payload,
        "accessors": {
            "educational_structure": dict(uli.educational_structure()),
            "learning_structure": dict(uli.learning_structure()),
            "assessment_structure": dict(uli.assessment_structure()),
            "diagram_structure": dict(uli.diagram_structure()),
            "knowledge_graph_structure": dict(uli.knowledge_graph_structure()),
            "voice_structure": dict(uli.voice_structure()),
            "analytics_structure": dict(uli.analytics_structure()),
            "accessibility_structure": dict(uli.accessibility_structure()),
            "stem_structure": dict(uli.stem_structure()),
        },
        "validation_report": validation_report,
        "certification": certification,
        "quality_score": quality_score,
        "warnings": warnings,
        "recommendations": recommendations,
        # Non-blocking: generation always continues
        "blocks_generation": False,
        "downstream_allowed_hint": validation_report.get("downstream_allowed"),
    }


def attach_uli_pipeline(
    meta: dict[str, Any],
    *,
    lesson_text: str,
    source_envelope: Mapping[str, Any],
    universal_profile: Mapping[str, Any] | None = None,
    stem_metadata: Mapping[str, Any] | None = None,
    classifications: list[Any] | None = None,
) -> dict[str, Any]:
    """
    If feature flag enabled, populate ``meta["uli"]``. Always returns meta.
    """
    if not is_uli_pipeline_enabled():
        meta["uli"] = {"enabled": False, "feature_flag": False}
        return meta

    uli_ctx = build_uli_context(
        source_envelope=source_envelope,
        universal_profile=universal_profile,
        stem_metadata=stem_metadata,
        classifications=classifications,
        enrich=True,
    )
    uli_ctx["feature_flag"] = True
    uli_ctx["raw_lesson_chars"] = len(lesson_text or "")
    meta["uli"] = uli_ctx
    return meta


def finalize_lesson_bundle(
    adaptations: dict[str, Any],
    *,
    lesson_text: str,
    source_envelope: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Attach ``LessonBundle`` under ``_meta["lesson_bundle"]`` when flag is on.
    Strips nested ``_meta`` from adaptation payloads to keep the bundle lean.
    """
    meta = adaptations.setdefault("_meta", {})
    if not is_uli_pipeline_enabled():
        meta["lesson_bundle"] = LessonBundle(
            feature_flag=False,
            raw_lesson=(lesson_text or "")[:2000],
        ).to_dict()
        return adaptations

    uli_ctx = meta.get("uli") or {}
    if not uli_ctx.get("enabled"):
        # Flag turned on mid-flight — build now
        attach_uli_pipeline(
            meta,
            lesson_text=lesson_text,
            source_envelope=source_envelope or meta.get("source_envelope") or {},
            universal_profile=meta.get("universal_profile"),
            stem_metadata={
                "artifacts": meta.get("engine_artifacts") or [],
                "claims_found": meta.get("stem_claims_found"),
                "preferred_visuals": meta.get("preferred_visuals") or [],
                "routing_warnings": meta.get("routing_warnings") or [],
                "biology_figures": meta.get("biology_figures") or [],
            },
        )
        uli_ctx = meta.get("uli") or {}

    adaptation_payloads = {
        key: value
        for key, value in adaptations.items()
        if not str(key).startswith("_")
    }
    bundle = LessonBundle(
        raw_lesson=lesson_text or "",
        universal_lesson=dict(uli_ctx.get("universal_lesson") or {}),
        semantic_bundle=dict(uli_ctx.get("semantic_bundle") or {}),
        validation_report=dict(uli_ctx.get("validation_report") or {}),
        certification=str(uli_ctx.get("certification") or ""),
        quality_score=uli_ctx.get("quality_score"),
        warnings=list(uli_ctx.get("warnings") or []),
        recommendations=list(uli_ctx.get("recommendations") or []),
        subject_intelligence=dict(uli_ctx.get("subject_intelligence") or {}),
        adaptation_payloads=adaptation_payloads,
        export_payloads={},
        source_envelope=dict(source_envelope or meta.get("source_envelope") or {}),
        uli_schema_version=str(
            uli_ctx.get("uli_schema_version") or ULI_SCHEMA_VERSION
        ),
        feature_flag=True,
    )
    meta["lesson_bundle"] = bundle.to_dict()
    return adaptations


def get_uli_from_adaptations(
    adaptations: Mapping[str, Any] | None,
) -> UniversalLessonIntelligence | None:
    """Rehydrate ULI from adaptations ``_meta`` when present."""
    meta = (adaptations or {}).get("_meta") or {}
    uli_blob = (meta.get("uli") or {}).get("universal_lesson")
    if not isinstance(uli_blob, Mapping):
        return None
    envelope = uli_blob.get("source_envelope") or meta.get("source_envelope") or {}
    profile = uli_blob.get("universal_profile")
    stem = uli_blob.get("stem_metadata")
    classes = list(uli_blob.get("classifications") or [])
    enrichment = uli_blob.get("enrichment")
    if not envelope:
        return None
    return UniversalLessonIntelligence.from_artifacts(
        envelope,
        profile,
        stem_metadata=stem,
        classifications=classes,
        enrichment=enrichment,
        enrich=False,
    )
