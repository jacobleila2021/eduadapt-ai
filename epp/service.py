"""EPP service — surface → polish (learner-visible only)."""

from __future__ import annotations

from typing import Any, Mapping

from epp.constants import (
    ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK,
    EPP_SCHEMA,
    EPP_VERSION,
    PUBLISHER_BENCHMARKS,
)
from epp.personas import persona_notes
from epp.polish import polish_adaptations
from epp.surface import surface_board_into_adaptations


def apply_epp(
    adaptations: dict[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Educational Product Perfection pass.

    Does not gate publication — UEVB / PMES / PEEC remain the authorities.
    Only improves what the learner reads, sees, and practices.
    """
    board = board or adaptations.get("_intelligence_board") or {}
    working, surface_notes = surface_board_into_adaptations(dict(adaptations), board=board)
    working = polish_adaptations(working, board=board)
    notes = surface_notes + [
        {"kind": "persona", "detail": n["adaptation"] + ": " + n["intent"]}
        for n in persona_notes(working)
    ]

    working["_epp"] = {
        "version": EPP_VERSION,
        "schema": EPP_SCHEMA,
        "notes": notes,
        "publisher_benchmarks": list(PUBLISHER_BENCHMARKS),
        "smoke_ok": ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK,
    }
    return {
        "adaptations": working,
        "ok": True,
        "version": EPP_VERSION,
        "smoke_ok": ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK,
        "notes": notes,
        "regression_guard": {
            "rule": "No future commit may reduce lesson, adaptation, publisher, accessibility, visual quality, or performance.",
            "benchmarks": list(PUBLISHER_BENCHMARKS),
        },
    }
