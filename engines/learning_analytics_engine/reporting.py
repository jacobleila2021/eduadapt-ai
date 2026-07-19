"""Reporting engine — JSON-first exports (PDF/Excel via existing infra when available)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

REPORTS_DIR = DATA_DIR / "laie" / "reports"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_report(
    report_type: str,
    payload: dict[str, Any],
    *,
    learner_id: str = "",
    fmt: str = "json",
) -> dict[str, Any]:
    """
    Supported report_type: student|parent|teacher|iep_support|progress|
    curriculum|assessment|accessibility|executive|investor
    fmt: json|csv|excel|pdf (json always; others best-effort)
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    doc = {
        "report_type": report_type,
        "generated_at": _now(),
        "learner_id": learner_id,
        "payload": payload,
        "policy": {
            "insights_only": True,
            "no_content_mutation": True,
            "no_medical_diagnoses": True,
            "educator_final_authority": True,
        },
    }
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (learner_id or "aggregate"))[:40]
    path = REPORTS_DIR / f"{report_type}_{safe}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json"
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

    exports: dict[str, Any] = {"json": str(path)}
    if fmt == "csv":
        exports["csv"] = _try_csv(doc, path.with_suffix(".csv"))
    elif fmt == "excel":
        exports["excel"] = _try_excel(doc, path.with_suffix(".xlsx"))
    elif fmt == "pdf":
        exports["pdf"] = {"status": "deferred", "note": "Use existing PDF exporters when wiring UI"}

    return {"ok": True, "report": doc, "exports": exports}


def _try_csv(doc: dict[str, Any], path: Path) -> dict[str, Any]:
    try:
        import csv

        flat = doc.get("payload") or {}
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["key", "value"])
            for k, v in flat.items():
                w.writerow([k, json.dumps(v, ensure_ascii=False) if not isinstance(v, (str, int, float)) else v])
        return {"path": str(path), "ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def _try_excel(doc: dict[str, Any], path: Path) -> dict[str, Any]:
    try:
        import openpyxl  # type: ignore

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "report"
        ws.append(["key", "value"])
        for k, v in (doc.get("payload") or {}).items():
            ws.append([k, json.dumps(v, ensure_ascii=False) if not isinstance(v, (str, int, float)) else v])
        wb.save(path)
        return {"path": str(path), "ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "fallback": "json"}
