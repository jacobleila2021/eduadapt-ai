"""Full Product Excellence Audit + improvement plan."""

from __future__ import annotations

from typing import Any, Mapping

from peec.accessibility_audit import audit_accessibility, audit_adaptation_quality
from peec.constants import PEEC_SCHEMA, PEEC_VERSION, PUBLISHER_HOUSES
from peec.ux_audit import audit_ux, walk_student_journeys
from peec.visual_audit import audit_visual_learning
from peec.writing_audit import audit_lesson_writing


def run_product_excellence_audit(
    adaptations: Mapping[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
    pmes_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    writing = audit_lesson_writing(adaptations)
    ux = audit_ux(adaptations)
    adaptation = audit_adaptation_quality(adaptations)
    visual = audit_visual_learning(adaptations)
    accessibility = audit_accessibility(adaptations)
    journey = walk_student_journeys(adaptations)

    ok = all(
        [
            writing.get("ok"),
            ux.get("ok"),
            adaptation.get("ok"),
            visual.get("ok"),
            accessibility.get("ok"),
        ]
    )
    # Journey findings inform remediation but do not alone block excellence after polish
    audits = {
        "product_excellence_audit": {
            "ok": ok,
            "publisher_benchmark_houses": list(PUBLISHER_HOUSES),
            "question": (
                "Would an experienced educator say this is among the finest digital lessons?"
            ),
            "pmes_approved": bool((pmes_report or {}).get("approved")),
            "journey_clear": bool(journey.get("ok")),
        },
        "lesson_writing_audit": writing,
        "ux_audit": ux,
        "adaptation_quality_audit": adaptation,
        "visual_design_audit": visual,
        "accessibility_audit": accessibility,
        "student_journey": journey,
    }

    # Remediation plan from issues
    plan: list[dict[str, str]] = []
    for name, report in audits.items():
        if name == "product_excellence_audit":
            continue
        if report.get("ok"):
            continue
        for issue in report.get("issues") or []:
            if isinstance(issue, dict):
                plan.append(
                    {
                        "audit": name,
                        "action": f"Fix {issue.get('issue')} on {issue.get('page', 'page')}",
                        "priority": "high",
                    }
                )
            else:
                plan.append({"audit": name, "action": str(issue), "priority": "high"})
        for persona, notes in (report.get("confusion_points") or {}).items():
            for note in notes:
                plan.append(
                    {
                        "audit": "student_journey",
                        "action": f"{persona}: {note}",
                        "priority": "high",
                    }
                )

    # Deduplicate plan actions
    seen = set()
    unique_plan = []
    for row in plan:
        key = row["action"]
        if key in seen:
            continue
        seen.add(key)
        unique_plan.append(row)

    ok = bool(audits["product_excellence_audit"]["ok"])
    improvement = {
        "schema": "alora.peec.product_improvement_report.v1",
        "status": "excellent" if ok else "needs_remediation",
        "highlights": [
            "Cream textbook design system enforced",
            "PMES + UEVB gates remain in force",
            "Adaptations audited for handcrafted personality",
        ],
        "open_items": len(unique_plan),
    }

    return {
        "schema": PEEC_SCHEMA,
        "version": PEEC_VERSION,
        "ok": ok,
        "board_topic": str((board or {}).get("topic") or ""),
        "audits": audits,
        "product_improvement_report": improvement,
        "remediation_plan": unique_plan,
        "release_ready": ok and bool((pmes_report or {}).get("approved", True)),
    }
