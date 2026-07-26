"""Semantic hooks — attach subject pack output onto ULI context without mutating curriculum."""

from __future__ import annotations

from typing import Any, Mapping

from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.subject_profile import detect_subject_from_uli


def run_subject_intelligence(
    uli: Any,
    *,
    subject_key: str | None = None,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Detect (or use) subject pack, run analyse_lesson, return enrichment dict for ``_meta``.

    Never modifies verified EngineResults or curriculum sources of truth.
    """
    detection = detect_subject_from_uli(uli)
    key = (subject_key or detection.subject_key or "general").strip().lower()
    pack = get_registry().get(key)
    analysis = pack.analyse_lesson(uli, context)
    return {
        "framework": "subject_intelligence_framework",
        "version": "1.0.0",
        "detection": detection.to_dict(),
        "subject_key": pack.subject.key,
        "subject_display_name": pack.subject.display_name,
        "pack_version": pack.version,
        "placeholder": bool(analysis.placeholder),
        "analysis": analysis.to_dict(),
        "capabilities": [c.to_dict() for c in pack.capabilities()],
        "mutates_curriculum": False,
        "mutates_engine_results": False,
    }
