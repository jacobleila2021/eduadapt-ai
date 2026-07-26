"""Report assembly helpers for ULIQE."""

from __future__ import annotations

from engines.universal_lesson_validation.schemas import (
    CertificationLevel,
    FindingSeverity,
    ULIQEReport,
    ValidationFinding,
)


def assemble_report(
    *,
    findings: list[ValidationFinding],
    category_scores,
    overall_score: float,
    confidence: float,
    certification: CertificationLevel,
    rules_executed: list[str],
    uli_source_id: str,
    uli_schema_version: str,
    grounding_mode: str,
) -> ULIQEReport:
    missing = [
        f.field_path or f.message
        for f in findings
        if f.category == "completeness"
        and f.severity in (FindingSeverity.WARNING, FindingSeverity.ERROR, FindingSeverity.CRITICAL)
    ]
    inconsistencies = [
        f.message
        for f in findings
        if f.category == "consistency"
        and f.severity in (FindingSeverity.WARNING, FindingSeverity.ERROR)
    ]
    recommendations = [f.recommendation for f in findings if f.recommendation]
    warnings = [
        f.message for f in findings if f.severity == FindingSeverity.WARNING
    ]
    curriculum_gaps = [
        f.message for f in findings if f.category == "curriculum_accuracy"
        and f.severity != FindingSeverity.INFO
    ]
    accessibility_gaps = [
        f.message for f in findings if f.category == "accessibility"
        and f.severity != FindingSeverity.INFO
    ]
    assessment_gaps = [
        f.message for f in findings if f.category == "assessment_coverage"
        and f.severity != FindingSeverity.INFO
    ]
    semantic_issues = [
        f.message for f in findings if f.category == "semantic_integrity"
        and f.severity != FindingSeverity.INFO
    ]
    stem_issues = [
        f.message for f in findings if f.category == "stem_accuracy"
        and f.severity in (FindingSeverity.WARNING, FindingSeverity.ERROR, FindingSeverity.CRITICAL)
    ]

    rejected = certification == CertificationLevel.REJECTED
    ok = certification in {
        CertificationLevel.PRODUCTION_READY,
        CertificationLevel.GOLD,
        CertificationLevel.SILVER,
    } and not rejected

    return ULIQEReport(
        ok=ok,
        certification=certification,
        overall_score=overall_score,
        confidence=confidence,
        pass_fail="pass" if ok else "fail",
        findings=findings,
        category_scores=list(category_scores),
        missing_elements=list(dict.fromkeys(missing)),
        inconsistencies=list(dict.fromkeys(inconsistencies)),
        recommendations=list(dict.fromkeys(recommendations)),
        warnings=list(dict.fromkeys(warnings)),
        curriculum_gaps=list(dict.fromkeys(curriculum_gaps)),
        accessibility_gaps=list(dict.fromkeys(accessibility_gaps)),
        assessment_gaps=list(dict.fromkeys(assessment_gaps)),
        semantic_issues=list(dict.fromkeys(semantic_issues)),
        stem_issues=list(dict.fromkeys(stem_issues)),
        rules_executed=list(rules_executed),
        uli_source_id=uli_source_id,
        uli_schema_version=uli_schema_version,
        grounding_mode=grounding_mode,
    )


def compare_reports(a: ULIQEReport, b: ULIQEReport) -> dict:
    """Diff two validation reports (version compare)."""
    return {
        "score_delta": round(b.overall_score - a.overall_score, 2),
        "certification_from": a.certification.value,
        "certification_to": b.certification.value,
        "new_errors": [
            f.to_dict()
            for f in b.findings
            if f.severity in (FindingSeverity.ERROR, FindingSeverity.CRITICAL)
            and f.rule_id not in {x.rule_id for x in a.findings}
        ],
        "resolved_errors": [
            f.to_dict()
            for f in a.findings
            if f.severity in (FindingSeverity.ERROR, FindingSeverity.CRITICAL)
            and f.rule_id not in {x.rule_id for x in b.findings}
        ],
    }
