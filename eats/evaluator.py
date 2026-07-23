"""Educational Acceptance Testing System — evaluate adaptations (read-only)."""

from __future__ import annotations

from typing import Any, Mapping

from eats.checks import _blob, evaluate_adaptation
from eats.constants import EATS_ADAPTATION_KEYS, PUBLISHER_READY
from eats.golden_library import compare_to_eats_golden
from eats.scoring import PackageAcceptance, finalize_package


def _subject_from(adaptations: Mapping[str, Any], subject: str = "") -> str:
    if subject:
        return subject
    meta = adaptations.get("_meta") if isinstance(adaptations.get("_meta"), dict) else {}
    ctx = meta.get("lesson_context") or {}
    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    for candidate in (ctx.get("subject"), meta.get("subject"), std.get("subject")):
        if candidate:
            return str(candidate)
    return "general"


def evaluate_package(
    adaptations: Mapping[str, Any],
    *,
    subject: str = "",
    keys: tuple[str, ...] | list[str] | None = None,
) -> PackageAcceptance:
    """Evaluate every present adaptation independently."""
    keys = tuple(keys or EATS_ADAPTATION_KEYS)
    subject = _subject_from(adaptations, subject)
    mainstream = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    mainstream_blob = _blob(mainstream) if mainstream else ""

    by_adaptation = {}
    for key in keys:
        content = adaptations.get(key)
        if not isinstance(content, dict) or not content:
            continue
        by_adaptation[key] = evaluate_adaptation(
            content,
            adaptation_id=key,
            mainstream_blob=mainstream_blob,
            subject=subject,
        )

    sample = mainstream or next(
        (adaptations[k] for k in by_adaptation if isinstance(adaptations.get(k), dict)),
        {},
    )
    golden = compare_to_eats_golden(sample, subject=subject, overall_score=0.0)
    package = finalize_package(by_adaptation, golden_delta=float(golden.get("delta") or 0))
    if golden.get("matched") and package.overall and float(golden.get("golden_score") or 0) - package.overall > 8:
        package.weaknesses.append("Quality trails closest golden exemplar.")
    # Ensure threshold semantics align with publication readiness
    if package.overall < PUBLISHER_READY:
        package.publication_ready = False
        package.reject_rendering = True
    return package
