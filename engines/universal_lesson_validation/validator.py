"""ULIQE validation pipeline orchestrator."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, stem_applicable
from engines.universal_lesson_validation.accessibility import validate_accessibility
from engines.universal_lesson_validation.assessment import validate_assessment
from engines.universal_lesson_validation.biology import validate_biology
from engines.universal_lesson_validation.chemistry import validate_chemistry
from engines.universal_lesson_validation.completeness import validate_completeness
from engines.universal_lesson_validation.computer_science import validate_computer_science
from engines.universal_lesson_validation.consistency import validate_consistency
from engines.universal_lesson_validation.commerce_economics import validate_commerce_economics
from engines.universal_lesson_validation.curriculum import validate_curriculum
from engines.universal_lesson_validation.diagrams import validate_diagrams
from engines.universal_lesson_validation.english import validate_english
from engines.universal_lesson_validation.mathematics import validate_mathematics
from engines.universal_lesson_validation.pedagogy import validate_pedagogy
from engines.universal_lesson_validation.physics import validate_physics
from engines.universal_lesson_validation.readability import validate_readability
from engines.universal_lesson_validation.reporting import assemble_report, compare_reports
from engines.universal_lesson_validation.schema_check import validate_schema
from engines.universal_lesson_validation.schemas import (
    CertificationLevel,
    FindingSeverity,
    ULIQEReport,
    ValidationFinding,
)
from engines.universal_lesson_validation.scoring import certify, score_findings
from engines.universal_lesson_validation.semantic import validate_semantic
from engines.universal_lesson_validation.social_science import validate_social_science
from engines.universal_lesson_validation.universal_visual import validate_universal_visual
from engines.universal_lesson_validation.world_languages import validate_world_languages

PIPELINE_STAGES: tuple[tuple[str, Any], ...] = (
    ("schema", validate_schema),
    ("semantic", validate_semantic),
    ("curriculum", validate_curriculum),
    ("pedagogy", validate_pedagogy),
    ("accessibility", validate_accessibility),
    ("readability", validate_readability),
    ("diagrams", validate_diagrams),
    ("universal_visual", validate_universal_visual),
    ("mathematics", validate_mathematics),
    ("chemistry", validate_chemistry),
    ("physics", validate_physics),
    ("biology", validate_biology),
    ("english", validate_english),
    ("social_science", validate_social_science),
    ("computer_science", validate_computer_science),
    ("commerce_economics", validate_commerce_economics),
    ("world_languages", validate_world_languages),
    ("assessment", validate_assessment),
    ("completeness", validate_completeness),
    ("consistency", validate_consistency),
)


def list_validation_rules() -> list[dict[str, str]]:
    """Enumerate known rule id prefixes / stages for API consumers."""
    return [
        {"stage": stage, "module": fn.__module__, "entry": fn.__name__}
        for stage, fn in PIPELINE_STAGES
    ]


def run_pipeline(uli: Any) -> ULIQEReport:
    """
    Full ULIQE sequence. Stops early only on schema CRITICAL malformed object
    (cannot coerce ULI). Otherwise runs all stages and certifies.
    """
    schema_findings = validate_schema(uli)
    if any(
        f.severity == FindingSeverity.CRITICAL and f.rule_id == "ULIQE.SCHEMA.001"
        for f in schema_findings
    ):
        return assemble_report(
            findings=schema_findings,
            category_scores=[],
            overall_score=0.0,
            confidence=0.0,
            certification=CertificationLevel.REJECTED,
            rules_executed=["schema"],
            uli_source_id="",
            uli_schema_version="",
            grounding_mode="unknown",
        )

    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    rules_executed: list[str] = []
    for stage, fn in PIPELINE_STAGES:
        rules_executed.append(stage)
        if stage == "schema":
            findings.extend(schema_findings)
            continue
        findings.extend(fn(uli))

    official = obj.grounding_mode == "official_curriculum_publish"
    overall, confidence, category_scores = score_findings(
        findings,
        stem_applicable=stem_applicable(obj),
        official_curriculum=official,
    )
    certification = certify(overall, findings)
    return assemble_report(
        findings=findings,
        category_scores=category_scores,
        overall_score=overall,
        confidence=confidence,
        certification=certification,
        rules_executed=rules_executed,
        uli_source_id=obj.source_id,
        uli_schema_version=obj.schema_version,
        grounding_mode=obj.grounding_mode,
    )


def validate_uli(uli: Any) -> ULIQEReport:
    return run_pipeline(uli)


def score_uli(uli: Any) -> dict[str, Any]:
    report = run_pipeline(uli)
    return {
        "overall_score": report.overall_score,
        "confidence": report.confidence,
        "category_scores": [c.to_dict() for c in report.category_scores],
        "certification": report.certification.value,
    }


def certify_uli(uli: Any) -> dict[str, Any]:
    report = run_pipeline(uli)
    return {
        "certification": report.certification.value,
        "downstream_allowed": report.downstream_allowed,
        "overall_score": report.overall_score,
        "pass_fail": report.pass_fail,
    }


def generate_report(uli: Any) -> dict[str, Any]:
    return run_pipeline(uli).to_dict()


def compare_versions(uli_a: Any, uli_b: Any) -> dict[str, Any]:
    return compare_reports(run_pipeline(uli_a), run_pipeline(uli_b))
