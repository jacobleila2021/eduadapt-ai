"""
Universal Educational Validation & Benchmarking (UEVB).

Final authority before production. Validates learner experience — not a new
intelligence engine.
"""

from __future__ import annotations

from uevb.constants import (
    UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK,
    UEVB_VERSION,
)
from uevb.corpus import corpus_size, iter_corpus_specs
from uevb.dashboard import build_dashboard_state, render_dashboard_markdown
from uevb.release_gate import evaluate_release_gate, gate_package_for_production
from uevb.runner import run_uevb_suite
from uevb.service import api_release_gate, api_run_suite, api_validate_package, pack_health
from uevb.validate import validate_composed_package

__all__ = [
    "UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK",
    "UEVB_VERSION",
    "corpus_size",
    "iter_corpus_specs",
    "validate_composed_package",
    "gate_package_for_production",
    "evaluate_release_gate",
    "run_uevb_suite",
    "build_dashboard_state",
    "render_dashboard_markdown",
    "api_validate_package",
    "api_release_gate",
    "api_run_suite",
    "pack_health",
]
