"""Readability checks using ULI heuristics only (no text invention)."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_readability(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    a11y = obj.accessibility_structure()
    difficulty = dict(a11y.get("reading_level") or {})
    age = dict(a11y.get("age_estimate") or {})

    if not difficulty:
        findings.append(
            finding(
                "ULIQE.READ.001",
                "accessibility",
                FindingSeverity.ERROR,
                "No readability/difficulty block on ULI.",
                field_path="accessibility_structure.reading_level",
            )
        )
        return findings

    score = difficulty.get("score")
    band = difficulty.get("band")
    findings.append(
        finding(
            "ULIQE.READ.002",
            "accessibility",
            FindingSeverity.INFO,
            f"ULI readability heuristic band={band}, score={score}",
            evidence={"difficulty": difficulty, "age_estimate": age},
        )
    )

    # Soft sanity: extreme scores may indicate extraction noise.
    try:
        numeric = float(score) if score is not None else None
    except (TypeError, ValueError):
        numeric = None
    if numeric is not None and (numeric < 3 or numeric > 40):
        findings.append(
            finding(
                "ULIQE.READ.010",
                "accessibility",
                FindingSeverity.WARNING,
                f"Readability score {numeric} is outside typical heuristic range.",
                field_path="accessibility_structure.reading_level.score",
                recommendation="Review source text quality / OCR; do not replace with invented grade.",
            )
        )

    return findings
