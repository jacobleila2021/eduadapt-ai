"""POBR report writers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from pobr.constants import POBR_SCHEMA, POBR_VERSION

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "reports" / "pobr"


def write_pobr_reports(report: Mapping[str, Any]) -> dict[str, str]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    paths: dict[str, str] = {}
    master = {"schema": POBR_SCHEMA, "version": POBR_VERSION, "generated_at": stamp, "report": report}
    master_path = REPORT_ROOT / f"{stamp}_beta_readiness_pack.json"
    master_path.write_text(json.dumps(master, indent=2), encoding="utf-8")
    paths["pack"] = str(master_path)

    fragments = {
        "product_optimisation_report": report.get("product_optimisation_report"),
        "ux_audit": (report.get("categories") or {}).get("ux"),
        "performance_audit": (report.get("categories") or {}).get("performance"),
        "accessibility_audit": (report.get("categories") or {}).get("accessibility"),
        "rendering_audit": (report.get("categories") or {}).get("rendering"),
        "export_audit": (report.get("categories") or {}).get("exports"),
        "beta_readiness_report": {
            "overall": report.get("overall_beta_readiness"),
            "beta_ready": report.get("beta_ready"),
            "categories": report.get("categories"),
        },
        "final_remediation_plan": {"items": report.get("final_remediation_plan") or []},
    }
    for name, payload in fragments.items():
        path = REPORT_ROOT / f"{stamp}_{name}.json"
        path.write_text(
            json.dumps({"schema": POBR_SCHEMA, "report": name, "payload": payload}, indent=2),
            encoding="utf-8",
        )
        paths[name] = str(path)

    latest = REPORT_ROOT / "latest_beta_readiness.json"
    latest.write_text(json.dumps(master, indent=2), encoding="utf-8")
    paths["latest"] = str(latest)
    return paths
