"""Shared helpers for ULIQE validators — resolve ULI without inventing content."""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_lesson_intelligence import UniversalLessonIntelligence
from engines.universal_lesson_intelligence.facade import build_universal_lesson_intelligence
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def coerce_uli(uli: Any) -> UniversalLessonIntelligence:
    """Accept UniversalLessonIntelligence, to_dict() snapshot, or envelope+profile dict."""
    if isinstance(uli, UniversalLessonIntelligence):
        return uli
    if not isinstance(uli, Mapping):
        raise TypeError("ULIQE requires a UniversalLessonIntelligence or mapping snapshot")
    if "source_envelope" in uli and "universal_profile" in uli:
        return build_universal_lesson_intelligence(
            uli["source_envelope"],
            uli["universal_profile"],
            stem_metadata=uli.get("stem_metadata"),
            classifications=list(uli.get("classifications") or []),
        )
    if "educational_structure" in uli and "learning_structure" in uli:
        # Semantic-only bundle cannot rebuild full ULI — reject for schema stage.
        raise ValueError(
            "ULIQE requires full ULI (envelope + profile). Pass UniversalLessonIntelligence "
            "or to_dict() snapshot, not semantic_bundle alone."
        )
    raise ValueError("Unrecognized ULI payload for ULIQE")


def finding(
    rule_id: str,
    category: str,
    severity: FindingSeverity,
    message: str,
    *,
    field_path: str = "",
    recommendation: str = "",
    evidence: dict[str, Any] | None = None,
) -> ValidationFinding:
    return ValidationFinding(
        rule_id=rule_id,
        category=category,
        severity=severity,
        message=message,
        field_path=field_path,
        recommendation=recommendation,
        evidence=evidence or {},
    )


def nonempty_list(value: Any) -> bool:
    return isinstance(value, (list, tuple)) and len(value) > 0


def stem_applicable(uli: UniversalLessonIntelligence) -> bool:
    stem = uli.stem_structure()
    if stem.get("claims_found") or stem.get("artifacts"):
        return True
    for row in uli.classifications:
        kind = ""
        if isinstance(row, Mapping):
            kind = str(row.get("content_type") or row.get("kind") or "")
        else:
            kind = str(getattr(row, "content_type", "") or "")
        if any(
            token in kind
            for token in (
                "math",
                "chemical",
                "physics",
                "circuit",
                "geometry",
                "molecule",
                "plot",
                "statistics",
                "chart",
            )
        ):
            return True
    return False
