"""POBR — Product Optimisation & Beta Readiness tests."""

from __future__ import annotations

from lesson_pack import build_lesson_save_pack
from pdf_exporter import export_tab_pdf
from pobr import (
    PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK,
    apply_pobr,
    build_beta_readiness_report,
)
from pobr.audits import audit_exports, audit_rendering, audit_workflows


def test_pobr_smoke_marker():
    assert PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK is True


def test_workflows_and_exports_present():
    wf = audit_workflows()
    assert wf["checks"]["teacher_export_pdf"] is True
    assert wf["checks"]["teacher_save_pack"] is True
    ex = audit_exports()
    assert "PDF exporter missing." not in (ex.get("weaknesses") or [])
    rend = audit_rendering()
    assert "Picture:" not in str(rend.get("weaknesses") or [])


def test_pdf_and_save_pack_bytes():
    lesson = {
        "topic": "Force and Pressure",
        "big_idea": "Force is a push or a pull.",
        "sections": [
            {"title": "Concept: Force", "role": "concept", "body": "Force changes motion."},
            {"title": "Summary", "role": "summary", "body": "You can explain force clearly."},
        ],
    }
    pdf = export_tab_pdf("Force and Pressure", lesson, "standard")
    assert isinstance(pdf, (bytes, bytearray))
    assert pdf[:4] == b"%PDF"
    pack = build_lesson_save_pack(adaptations={"standard": lesson}, topic="Force and Pressure")
    assert b"alora.lesson_save_pack" in pack


def test_beta_readiness_report_structure():
    report = build_beta_readiness_report({"ok": True, "pmes": {"approved": True}, "peec": {"ok": True}, "uevb": {"ok": True}})
    assert "overall_beta_readiness" in report
    assert "categories" in report
    assert "final_remediation_plan" in report
    result = apply_pobr({"ok": True, "pmes": {"approved": True}}, write_reports=False)
    assert result.get("smoke_ok") is True
    assert "overall_beta_readiness" in result
    print("PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK")
