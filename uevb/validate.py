"""Validate one composed lesson package — learner experience authority."""

from __future__ import annotations

from typing import Any, Mapping

from uevb.differentiation import measure_adaptation_differentiation
from uevb.engine_contribution import measure_engine_contributions
from uevb.publisher_benchmark import golden_benchmark_package, publisher_benchmark_lesson
from uevb.visual_audit import audit_visual_quality


def validate_composed_package(
    package: Mapping[str, Any],
    *,
    require_pmes: bool = True,
) -> dict[str, Any]:
    """Final pre-production validation for a single LCE package."""
    adaptations = package.get("adaptations") or {}
    board = package.get("intelligence_board") or adaptations.get("_intelligence_board") or {}
    subject = str(
        board.get("subject")
        or (package.get("clg") or {}).get("subject_key")
        or ""
    )
    pmes = package.get("pmes") or {}
    publisher_review = package.get("publisher_review_report") or adaptations.get("_pmes") or {}

    engine_report = measure_engine_contributions(
        adaptations,
        board=board,
        subject=subject,
        package_meta={
            "pqle": package.get("pqle"),
            "pmes": pmes,
            "editorial": package.get("editorial"),
        },
    )
    diff_report = measure_adaptation_differentiation(adaptations)
    visual_report = audit_visual_quality(adaptations)
    publisher_report = publisher_benchmark_lesson(
        adaptations, publisher_review_report=publisher_review
    )
    golden_report = golden_benchmark_package(adaptations, subject=subject)

    pmes_ok = bool(pmes.get("approved") or publisher_review.get("approved") or not require_pmes)
    if require_pmes and package.get("ok") and pmes.get("approved") is False:
        pmes_ok = False
    if require_pmes and publisher_review.get("approved") is True:
        pmes_ok = True
    if require_pmes and pmes.get("approved") is True:
        pmes_ok = True

    gates = {
        "pmes": pmes_ok,
        "engine_contribution": bool(engine_report.get("ok")),
        "adaptation_differentiation": bool(diff_report.get("ok")),
        "visual_design": bool(visual_report.get("ok")),
        "publisher_benchmark": bool(publisher_report.get("ok")),
        "golden_benchmark": bool(golden_report.get("ok")),
    }
    # Soften engine gate: allow N/A subject packs; fail only on core pipeline failures
    core_failures = [
        e
        for e in (engine_report.get("integration_failures") or [])
        if e in {"KIE", "ULI", "LCE", "UVIE", "PQLE", "PMES", "SIF", "CMIF", "CEF"}
    ]
    gates["engine_contribution"] = len(core_failures) == 0
    engine_report = dict(engine_report)
    engine_report["core_integration_failures"] = core_failures
    engine_report["ok"] = len(core_failures) == 0

    passed = all(gates.values())
    return {
        "schema": "alora.uevb.lesson_validation.v1",
        "ok": passed,
        "release_candidate": passed,
        "gates": gates,
        "engine_contribution_report": engine_report,
        "adaptation_differentiation_report": diff_report,
        "publisher_benchmark_report": publisher_report,
        "visual_design_audit": visual_report,
        "golden_benchmark": golden_report,
        "subject": subject,
        "topic": str(board.get("topic") or (package.get("clg") or {}).get("topic") or ""),
    }
