"""Public service API for the Subject Intelligence Framework."""

from __future__ import annotations

from typing import Any, Mapping

from engines.subject_intelligence_framework.adapters import (
    to_aie_hints,
    to_ame_hints,
    to_atie_hints,
    to_lxp_hints,
)
from engines.subject_intelligence_framework.capability_matrix import (
    capability_matrix,
    lxp_hook_catalogue,
)
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.semantic_hooks import run_subject_intelligence
from engines.subject_intelligence_framework.validators import validate_pack_interface, validate_registry

SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK = True


def list_subject_packs() -> list[dict[str, Any]]:
    return get_registry().list_subjects()


def enrich_uli_with_subject_intelligence(
    uli: Any,
    *,
    subject_key: str | None = None,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Primary entry — attach SIF analysis for ULI pipeline / LessonBundle."""
    payload = run_subject_intelligence(uli, subject_key=subject_key, context=context)
    payload["atie"] = to_atie_hints(payload)
    payload["lxp"] = to_lxp_hints(payload)
    payload["ame"] = to_ame_hints(payload)
    payload["aie"] = to_aie_hints(payload)
    payload["lxp_hook_catalogue"] = lxp_hook_catalogue()
    return payload


__all__ = [
    "SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK",
    "list_subject_packs",
    "enrich_uli_with_subject_intelligence",
    "capability_matrix",
    "lxp_hook_catalogue",
    "validate_registry",
    "validate_pack_interface",
    "get_registry",
]
