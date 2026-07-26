"""Weighted quality scoring and certification levels for ULIQE."""

from __future__ import annotations

from engines.universal_lesson_validation.schemas import (
    CATEGORY_WEIGHTS,
    CategoryScore,
    CertificationLevel,
    FindingSeverity,
    ValidationFinding,
)

_SCORE_CATEGORIES = (
    "curriculum_accuracy",
    "completeness",
    "pedagogy",
    "stem_accuracy",
    "accessibility",
    "assessment_coverage",
    "semantic_integrity",
)

_SEVERITY_PENALTY = {
    FindingSeverity.INFO: 0.0,
    FindingSeverity.WARNING: 4.0,
    FindingSeverity.ERROR: 12.0,
    FindingSeverity.CRITICAL: 25.0,
}


def _category_for_finding(finding: ValidationFinding) -> str:
    if finding.category in CATEGORY_WEIGHTS:
        return finding.category
    # Map non-scored pipeline categories into nearest scored bucket.
    mapping = {
        "schema": "completeness",
        "consistency": "semantic_integrity",
        "pedagogy": "pedagogy",
    }
    return mapping.get(finding.category, "completeness")


def score_findings(
    findings: list[ValidationFinding],
    *,
    stem_applicable: bool = False,
    official_curriculum: bool = False,
) -> tuple[float, float, list[CategoryScore]]:
    """
    Return overall_score (0–100), confidence (0–1), category_scores.

    STEM category is soft-weighted when not applicable (redistribute weight).
    Curriculum category is soft when uploaded_source and curriculum unknown.
    """
    by_cat: dict[str, list[ValidationFinding]] = {c: [] for c in _SCORE_CATEGORIES}
    for f in findings:
        by_cat[_category_for_finding(f)].append(f)

    weights = dict(CATEGORY_WEIGHTS)
    if not stem_applicable:
        freed = weights.pop("stem_accuracy", 0.0)
        # Redistribute to completeness + semantic
        weights["completeness"] = weights.get("completeness", 0.0) + freed * 0.5
        weights["semantic_integrity"] = weights.get("semantic_integrity", 0.0) + freed * 0.5
    if not official_curriculum:
        # Curriculum accuracy less punitive when enrichment is optional
        weights["curriculum_accuracy"] = weights.get("curriculum_accuracy", 0.0) * 0.5
        bump = CATEGORY_WEIGHTS["curriculum_accuracy"] * 0.5
        weights["completeness"] = weights.get("completeness", 0.0) + bump * 0.5
        weights["pedagogy"] = weights.get("pedagogy", 0.0) + bump * 0.5

    total_w = sum(weights.values()) or 1.0
    category_scores: list[CategoryScore] = []
    overall = 0.0

    for cat, weight in weights.items():
        rows = by_cat.get(cat, [])
        applicable = True
        if cat == "stem_accuracy" and not stem_applicable:
            applicable = False
            score = 100.0
        else:
            penalty = sum(_SEVERITY_PENALTY.get(f.severity, 0.0) for f in rows)
            # INFO-only inventory warnings for known ULI gaps shouldn't zero a category.
            score = max(0.0, 100.0 - penalty)
            # Cap penalty from pure warning floods (ULI is still maturing).
            warning_only = all(
                f.severity in (FindingSeverity.INFO, FindingSeverity.WARNING) for f in rows
            ) or not rows
            if warning_only and score < 55.0:
                score = 55.0
        norm_w = weight / total_w
        category_scores.append(
            CategoryScore(
                category=cat,
                weight=round(norm_w, 4),
                score=round(score, 2),
                applicable=applicable,
                findings_count=len(rows),
            )
        )
        overall += score * norm_w

    # Confidence: higher when fewer critical/errors and more INFO confirmations
    critical = sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL)
    errors = sum(1 for f in findings if f.severity == FindingSeverity.ERROR)
    confidence = max(0.2, min(0.95, 0.85 - 0.15 * critical - 0.05 * errors))
    return round(overall, 2), round(confidence, 3), category_scores


def certify(
    overall_score: float,
    findings: list[ValidationFinding],
) -> CertificationLevel:
    if any(f.severity == FindingSeverity.CRITICAL and f.category == "schema" for f in findings):
        return CertificationLevel.REJECTED
    if any(f.severity == FindingSeverity.CRITICAL for f in findings):
        return CertificationLevel.REJECTED
    if overall_score >= 90 and not any(f.severity == FindingSeverity.ERROR for f in findings):
        return CertificationLevel.PRODUCTION_READY
    if overall_score >= 80:
        return CertificationLevel.GOLD
    if overall_score >= 65:
        return CertificationLevel.SILVER
    return CertificationLevel.NEEDS_REVIEW
