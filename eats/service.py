"""Educational Acceptance Testing System (EATS) — public service API."""

from __future__ import annotations

from eats.constants import (
    EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK,
    EATS_VERSION,
    PUBLISHER_READY,
)
from eats.dashboard import build_dashboard_state, render_dashboard_streamlit
from eats.evaluator import evaluate_package
from eats.hooks import attach_eats_to_adaptations, eats_block_reason
from eats.pipeline import accept_lesson


def score_summary(adaptations: dict, **kwargs):
    package = evaluate_package(adaptations, **kwargs)
    return package.to_dict()


def pack_health() -> dict:
    return {
        "ok": True,
        "name": "Educational Acceptance Testing System",
        "version": EATS_VERSION,
        "threshold": PUBLISHER_READY,
        "smoke": EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK,
    }


__all__ = [
    "EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK",
    "accept_lesson",
    "attach_eats_to_adaptations",
    "build_dashboard_state",
    "eats_block_reason",
    "evaluate_package",
    "pack_health",
    "render_dashboard_streamlit",
    "score_summary",
]
