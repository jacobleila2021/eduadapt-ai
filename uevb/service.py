"""UEVB public service API."""

from __future__ import annotations

from typing import Any, Mapping

from uevb.constants import (
    UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK,
    UEVB_VERSION,
)
from uevb.corpus import corpus_size, iter_corpus_specs
from uevb.dashboard import build_dashboard_state, render_dashboard_markdown
from uevb.release_gate import evaluate_release_gate, gate_package_for_production
from uevb.runner import run_uevb_suite
from uevb.validate import validate_composed_package


def pack_health() -> dict[str, Any]:
    return {
        "ok": UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK,
        "version": UEVB_VERSION,
        "smoke": UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK,
        "corpus": corpus_size(),
    }


def api_validate_package(package: Mapping[str, Any]) -> dict[str, Any]:
    return validate_composed_package(package)


def api_release_gate(package: Mapping[str, Any]) -> dict[str, Any]:
    return gate_package_for_production(package)


def api_run_suite(**kwargs: Any) -> dict[str, Any]:
    return run_uevb_suite(**kwargs)
