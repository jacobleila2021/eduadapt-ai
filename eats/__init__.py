"""Educational Acceptance Testing System (EATS).

Editor-in-chief gate above ULI → SIF → UVIE → LCE → PQLE → Render.
Validates lesson outputs. Does not generate curriculum. Does not modify engines.
"""

from __future__ import annotations

from eats.constants import (
    EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK,
    EATS_ADAPTATION_KEYS,
    EATS_VERSION,
    PUBLISHER_READY,
)
from eats.dashboard import build_dashboard_state, render_dashboard_streamlit
from eats.evaluator import evaluate_package
from eats.hooks import attach_eats_to_adaptations, eats_block_reason
from eats.pipeline import accept_lesson
from eats.service import pack_health, score_summary

__all__ = [
    "EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK",
    "EATS_ADAPTATION_KEYS",
    "EATS_VERSION",
    "PUBLISHER_READY",
    "accept_lesson",
    "attach_eats_to_adaptations",
    "build_dashboard_state",
    "eats_block_reason",
    "evaluate_package",
    "pack_health",
    "render_dashboard_streamlit",
    "score_summary",
]
