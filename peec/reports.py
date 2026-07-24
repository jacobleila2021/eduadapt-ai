"""PEEC report writers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from peec.constants import PEEC_SCHEMA, PEEC_VERSION

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "reports" / "peec"


def write_peec_reports(audit: Mapping[str, Any]) -> dict[str, str]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    paths: dict[str, str] = {}

    master = {
        "schema": PEEC_SCHEMA,
        "version": PEEC_VERSION,
        "generated_at": stamp,
        "audit": audit,
    }
    master_path = REPORT_ROOT / f"{stamp}_product_excellence_pack.json"
    master_path.write_text(json.dumps(master, indent=2), encoding="utf-8")
    paths["pack"] = str(master_path)

    mapping = {
        "product_excellence_audit": (audit.get("audits") or {}).get("product_excellence_audit"),
        "ux_audit": (audit.get("audits") or {}).get("ux_audit"),
        "adaptation_quality_audit": (audit.get("audits") or {}).get("adaptation_quality_audit"),
        "visual_design_audit": (audit.get("audits") or {}).get("visual_design_audit"),
        "lesson_writing_audit": (audit.get("audits") or {}).get("lesson_writing_audit"),
        "accessibility_audit": (audit.get("audits") or {}).get("accessibility_audit"),
        "product_improvement_report": audit.get("product_improvement_report"),
        "remediation_plan": {"items": audit.get("remediation_plan") or []},
    }
    for name, payload in mapping.items():
        path = REPORT_ROOT / f"{stamp}_{name}.json"
        path.write_text(
            json.dumps({"schema": PEEC_SCHEMA, "report": name, "payload": payload}, indent=2),
            encoding="utf-8",
        )
        paths[name] = str(path)

    # Latest pointer for dashboards
    latest = REPORT_ROOT / "latest_product_excellence.json"
    latest.write_text(json.dumps(master, indent=2), encoding="utf-8")
    paths["latest"] = str(latest)
    return paths
