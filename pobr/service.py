"""POBR service — run beta readiness + optional report write."""

from __future__ import annotations

from typing import Any, Mapping

from pobr.beta_readiness import build_beta_readiness_report
from pobr.constants import (
    POBR_VERSION,
    PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK,
)
from pobr.reports import write_pobr_reports


def apply_pobr(
    package: Mapping[str, Any] | None = None,
    *,
    write_reports: bool = True,
) -> dict[str, Any]:
    package = package or {}
    report = build_beta_readiness_report(
        package,
        peec=package.get("peec"),
        uevb=package.get("uevb"),
        pmes=package.get("pmes"),
    )
    paths = write_pobr_reports(report) if write_reports else {}
    return {
        "ok": bool(report.get("beta_ready")),
        "version": POBR_VERSION,
        "smoke_ok": PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK,
        "report": report,
        "report_paths": paths,
        "overall_beta_readiness": report.get("overall_beta_readiness"),
        "beta_ready": report.get("beta_ready"),
    }
