"""RC1 Beta / Production Readiness Report writer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from release import RC_TAG, RC_VERSION, RELEASE_CANDIDATE_PRODUCTION_READINESS_SMOKE_OK

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "reports" / "release"


def build_rc1_report(campaign: Mapping[str, Any], *, pobr: Mapping[str, Any] | None = None) -> dict[str, Any]:
    defects = campaign.get("defects") or {}
    perf = campaign.get("performance") or {}
    pobr = pobr or {}
    critical = defects.get("critical_open_count") or 0
    high = defects.get("high_open_count") or 0

    return {
        "schema": "alora.release.rc1_report.v1",
        "tag": RC_TAG,
        "version": RC_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "smoke_ok": RELEASE_CANDIDATE_PRODUCTION_READINESS_SMOKE_OK,
        "executive_summary": {
            "rc1_ready": bool(campaign.get("rc1_ready")),
            "packages_ok": campaign.get("packages_ok"),
            "packages_targeted": campaign.get("packages_targeted"),
            "critical_open": critical,
            "high_open": high,
            "architecture_frozen": True,
            "statement": (
                "Alora AI RC1 is ready for controlled beta when Critical and High defects are zero "
                "and ≥90% of campaign packages publish cleanly."
                if campaign.get("rc1_ready")
                else "RC1 not yet ready — Critical/High defects remain or package pass rate is below 90%."
            ),
        },
        "known_issues": {
            "critical": defects.get("critical_open") or [],
            "high": defects.get("high_open") or [],
            "medium": defects.get("medium_documented") or [],
            "low": defects.get("low_documented") or [],
        },
        "resolved_issues": defects.get("resolved") or [],
        "performance_metrics": perf,
        "educational_quality_metrics": {
            "subjects_covered": campaign.get("subjects") or [],
            "curricula_covered": campaign.get("curricula") or [],
            "gates": ["PMES", "PQLE", "UEVB", "PEEC", "Publisher", "Accessibility"],
        },
        "accessibility_metrics": {
            "profiles": ["adhd", "autism", "ell", "visual", "auditory", "ld", "dyslexia", "parent", "teacher"],
            "note": "Accessibility defects surface as missing/thin adaptations or scaffold leaks.",
        },
        "publisher_quality_metrics": {
            "pmes_required": True,
            "cream_background": "#FFF9EE",
            "exports": ["DOCX", "HTML", "Print", "PDF", "Save pack"],
        },
        "beta_readiness": {
            "pobr_overall": pobr.get("overall_beta_readiness"),
            "pobr_beta_ready": pobr.get("beta_ready"),
        },
        "release_risks": _risks(campaign),
        "recommendations": _recommendations(campaign),
        "stop_condition": {
            "critical_and_high_resolved": critical == 0 and high == 0,
            "tag": RC_TAG,
            "development_frozen": bool(campaign.get("rc1_ready")),
            "future_work": "maintenance, feature requests, educational enhancements",
        },
    }


def _risks(campaign: Mapping[str, Any]) -> list[str]:
    risks: list[str] = []
    defects = campaign.get("defects") or {}
    if defects.get("critical_open_count"):
        risks.append("Critical learner-facing defects remain open.")
    if defects.get("high_open_count"):
        risks.append("High-impact defects remain open.")
    avg = float((campaign.get("performance") or {}).get("avg_package_seconds") or 0)
    if avg > 120:
        risks.append("Average package generation exceeds 2 minutes — classroom demos need caching.")
    if int(campaign.get("packages_ok") or 0) < int(campaign.get("packages_targeted") or 1):
        risks.append("Not all campaign packages published cleanly.")
    if not risks:
        risks.append("No blocking risks identified in this campaign snapshot.")
    return risks


def _recommendations(campaign: Mapping[str, Any]) -> list[str]:
    recs: list[str] = []
    if not campaign.get("rc1_ready"):
        recs.append("Re-run `python -m release --target 100 --auto-fix` until Critical/High are zero.")
        recs.append("Prioritise scaffold leaks, missing adaptations, and broken PDF/export paths.")
    else:
        recs.append("Tag build ALORA-AI-RC1 and freeze architecture.")
        recs.append("Limit future work to maintenance, feature requests, and educational enhancements.")
        recs.append("Keep UEVB/PEEC/POBR regression smoke in CI for every release.")
    return recs


def write_rc1_report(report: Mapping[str, Any]) -> dict[str, str]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    paths: dict[str, str] = {}
    master = REPORT_ROOT / f"{stamp}_rc1_beta_readiness_report.json"
    master.write_text(json.dumps(report, indent=2), encoding="utf-8")
    paths["rc1_report"] = str(master)
    latest = REPORT_ROOT / "latest_rc1_report.json"
    latest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    paths["latest"] = str(latest)
    # Executive markdown
    md = REPORT_ROOT / f"{stamp}_RC1_EXECUTIVE_SUMMARY.md"
    exe = report.get("executive_summary") or {}
    lines = [
        f"# {RC_TAG} — Executive Summary",
        "",
        f"- Ready: **{exe.get('rc1_ready')}**",
        f"- Packages OK: {exe.get('packages_ok')}/{exe.get('packages_targeted')}",
        f"- Critical open: {exe.get('critical_open')}",
        f"- High open: {exe.get('high_open')}",
        f"- Architecture frozen: {exe.get('architecture_frozen')}",
        "",
        str(exe.get("statement") or ""),
        "",
        "## Release risks",
    ]
    for r in report.get("release_risks") or []:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## Recommendations")
    for r in report.get("recommendations") or []:
        lines.append(f"- {r}")
    md.write_text("\n".join(lines), encoding="utf-8")
    paths["executive_summary_md"] = str(md)
    return paths
