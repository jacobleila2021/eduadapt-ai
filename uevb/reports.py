"""UEVB report writers — Universal Educational Validation Report family."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from uevb.constants import UEVB_SCHEMA, UEVB_VERSION

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "reports" / "uevb"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_reports(
    *,
    suite_result: Mapping[str, Any],
    release_gate: Mapping[str, Any],
    dashboard: Mapping[str, Any],
) -> dict[str, str]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = _ts()
    paths: dict[str, str] = {}

    universal = {
        "schema": UEVB_SCHEMA,
        "report": "universal_educational_validation_report",
        "version": UEVB_VERSION,
        "generated_at": stamp,
        "suite": suite_result,
        "release_gate": release_gate,
        "dashboard": dashboard,
    }
    p = REPORT_ROOT / f"{stamp}_universal_educational_validation_report.json"
    p.write_text(json.dumps(universal, indent=2), encoding="utf-8")
    paths["universal"] = str(p)

    # Split reports
    fragments = {
        "engine_contribution_report": [
            (r.get("engine_contribution_report") or {})
            for r in (suite_result.get("validations") or [])
        ],
        "adaptation_differentiation_report": [
            (r.get("adaptation_differentiation_report") or {})
            for r in (suite_result.get("validations") or [])
        ],
        "publisher_benchmark_report": [
            (r.get("publisher_benchmark_report") or {})
            for r in (suite_result.get("validations") or [])
        ],
        "curriculum_consistency_report": suite_result.get("curriculum_consistency") or {},
        "visual_design_audit": [
            (r.get("visual_design_audit") or {})
            for r in (suite_result.get("validations") or [])
        ],
        "regression_summary": {
            "regressions": release_gate.get("regressions") or [],
            "pass_rate": release_gate.get("pass_rate"),
            "prior": dashboard.get("prior_pass_rate"),
        },
    }
    for name, payload in fragments.items():
        path = REPORT_ROOT / f"{stamp}_{name}.json"
        path.write_text(json.dumps({"schema": UEVB_SCHEMA, "report": name, "payload": payload}, indent=2), encoding="utf-8")
        paths[name] = str(path)

    dash_path = REPORT_ROOT / "dashboard_state.json"
    dash_path.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    paths["dashboard"] = str(dash_path)
    return paths
