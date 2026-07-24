"""Beta Readiness Score — commercial release report."""

from __future__ import annotations

from typing import Any, Mapping

from pobr.audits import (
    audit_accessibility,
    audit_educational_consistency,
    audit_exports,
    audit_performance,
    audit_rendering,
    audit_ux,
    audit_workflows,
)
from pobr.constants import BETA_READY_MIN, POBR_SCHEMA, POBR_VERSION


def _score_from_audit(audit: Mapping[str, Any], *, base: float = 70.0) -> dict[str, Any]:
    strengths = list(audit.get("strengths") or [])
    weaknesses = list(audit.get("weaknesses") or audit.get("missing") or [])
    score = base + min(25.0, len(strengths) * 3.0) - min(40.0, len(weaknesses) * 8.0)
    score = max(0.0, min(100.0, score))
    return {
        "score": round(score, 1),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommended_actions": list(audit.get("recommended_actions") or weaknesses),
        "ok": bool(audit.get("ok")),
    }


def build_beta_readiness_report(
    package: Mapping[str, Any] | None = None,
    *,
    peec: Mapping[str, Any] | None = None,
    uevb: Mapping[str, Any] | None = None,
    pmes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    package = package or {}
    peec = peec or package.get("peec") or {}
    uevb = uevb or package.get("uevb") or {}
    pmes = pmes or package.get("pmes") or {}

    workflow = _score_from_audit(audit_workflows(), base=75)
    ux = _score_from_audit(audit_ux(), base=72)
    performance = _score_from_audit(audit_performance(), base=78)
    accessibility = _score_from_audit(audit_accessibility(), base=74)
    rendering = _score_from_audit(audit_rendering(), base=72)
    exports = _score_from_audit(audit_exports(), base=70)
    consistency = _score_from_audit(audit_educational_consistency(package), base=76)

    # Map product excellence signals into category scores
    educational = {
        "score": 95.0 if package.get("ok") else (88.0 if pmes.get("approved") else 70.0),
        "strengths": ["PMES/UEVB/PEEC compose gates active"] if pmes or uevb or peec else [],
        "weaknesses": [] if package.get("ok") else ["Package not marked publication-ready."],
        "recommended_actions": [] if package.get("ok") else ["Re-run compose until publication_ready."],
        "ok": bool(package.get("ok") or pmes.get("approved")),
    }
    writing = {
        "score": 92.0 if (peec.get("ok") or peec.get("smoke_ok")) else 80.0,
        "strengths": ["PEEC writing remediation available."],
        "weaknesses": [] if peec.get("ok") else ["PEEC writing audit still has open items."],
        "recommended_actions": list((peec.get("remediation_plan") or [])[:5]),
        "ok": bool(peec.get("ok") or peec.get("smoke_ok")),
    }
    visual = rendering
    adaptation = {
        "score": 90.0 if (uevb.get("ok") or (uevb.get("validation") or {}).get("ok")) else 75.0,
        "strengths": ["UEVB differentiation gate."],
        "weaknesses": [] if uevb.get("ok") else ["UEVB adaptation gate not green."],
        "recommended_actions": [],
        "ok": bool(uevb.get("ok") or (uevb.get("validation") or {}).get("gates", {}).get("adaptation_differentiation")),
    }
    reliability = {
        "score": 90.0 if package.get("ok") else 78.0,
        "strengths": ["Publication gate fail-closed for quarantine."],
        "weaknesses": [] if package.get("ok") else ["Reliability blocked until publication_ready."],
        "recommended_actions": [],
        "ok": bool(package.get("ok")),
    }
    commercial = {
        "score": round(
            (
                workflow["score"]
                + exports["score"]
                + ux["score"]
                + educational["score"]
            )
            / 4.0,
            1,
        ),
        "strengths": workflow["strengths"][:3] + exports["strengths"][:3],
        "weaknesses": workflow["weaknesses"] + exports["weaknesses"],
        "recommended_actions": workflow["recommended_actions"] + exports["recommended_actions"],
        "ok": workflow["ok"] and exports["ok"],
    }

    categories = {
        "educational_quality": educational,
        "writing_quality": writing,
        "visual_quality": visual,
        "adaptation_quality": adaptation,
        "accessibility": accessibility,
        "performance": performance,
        "rendering": rendering,
        "reliability": reliability,
        "commercial_readiness": commercial,
        "ux": ux,
        "exports": exports,
        "educational_consistency": consistency,
        "workflows": workflow,
    }
    scores = [float(v["score"]) for v in categories.values()]
    overall = round(sum(scores) / len(scores), 1) if scores else 0.0

    remediation: list[dict[str, str]] = []
    for name, row in categories.items():
        for action in row.get("recommended_actions") or []:
            if isinstance(action, dict):
                remediation.append({"area": name, "action": str(action.get("action") or action), "priority": "high"})
            else:
                remediation.append({"area": name, "action": str(action), "priority": "high"})

    # Dedupe
    seen = set()
    plan = []
    for row in remediation:
        if row["action"] in seen:
            continue
        seen.add(row["action"])
        plan.append(row)

    beta_ready = overall >= BETA_READY_MIN and workflow["ok"] and exports["ok"] and rendering["ok"]

    return {
        "schema": POBR_SCHEMA,
        "version": POBR_VERSION,
        "report": "beta_readiness_report",
        "overall_beta_readiness": overall,
        "threshold": BETA_READY_MIN,
        "beta_ready": beta_ready,
        "categories": categories,
        "product_optimisation_report": {
            "status": "beta_ready" if beta_ready else "needs_optimisation",
            "overall": overall,
            "top_strengths": educational["strengths"] + ux["strengths"][:2],
            "top_gaps": plan[:8],
        },
        "final_remediation_plan": plan[:24],
        "release_rule": {
            "workflows_ok": workflow["ok"],
            "exports_ok": exports["ok"],
            "rendering_ok": rendering["ok"],
            "overall_meets_threshold": overall >= BETA_READY_MIN,
        },
    }
