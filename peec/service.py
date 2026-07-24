"""PEEC orchestration — audit → remediate → re-audit."""

from __future__ import annotations

from typing import Any, Mapping

from peec.audit import run_product_excellence_audit
from peec.constants import PEEC_VERSION, PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK
from peec.remediate import remediate_for_product_excellence
from peec.reports import write_peec_reports


def apply_peec(
    adaptations: dict[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
    pmes_report: Mapping[str, Any] | None = None,
    write_reports: bool = False,
    max_passes: int = 2,
) -> dict[str, Any]:
    """
    Product Excellence & Experience Completion pass.
    Not a new engine — experience polish + audit deliverables.
    """
    working = dict(adaptations)
    audit = run_product_excellence_audit(working, board=board, pmes_report=pmes_report)
    history = [{"pass": 0, "ok": audit.get("ok"), "open_items": len(audit.get("remediation_plan") or [])}]

    for i in range(max_passes):
        if audit.get("ok"):
            break
        working = remediate_for_product_excellence(working, board=board, audit=audit)
        audit = run_product_excellence_audit(working, board=board, pmes_report=pmes_report)
        history.append(
            {"pass": i + 1, "ok": audit.get("ok"), "open_items": len(audit.get("remediation_plan") or [])}
        )

    paths = write_peec_reports(audit) if write_reports else {}
    working["_peec_audit"] = {
        "ok": audit.get("ok"),
        "version": PEEC_VERSION,
        "history": history,
    }
    return {
        "adaptations": working,
        "audit": audit,
        "ok": bool(audit.get("ok")),
        "report_paths": paths,
        "smoke_ok": PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK,
        "version": PEEC_VERSION,
        "regression_verification": {
            "passes": history,
            "final_ok": bool(audit.get("ok")),
            "note": "PEEC remediations must not reintroduce mechanical language.",
        },
    }
