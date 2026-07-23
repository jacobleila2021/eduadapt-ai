"""EATS Publisher Quality Report writer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from eats.scoring import PackageAcceptance

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "reports" / "eats"


def write_publisher_quality_report(
    package: PackageAcceptance,
    *,
    topic: str = "",
    subject: str = "",
    run_id: str = "",
) -> dict[str, Any]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    data = package.to_dict()
    report = {
        "title": "Publisher Quality Report",
        "schema": "alora.eats.report.v1",
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lesson_summary": {
            "topic": topic,
            "subject": subject,
            "overall_publisher_score": data["overall"],
            "band": data["band"],
            "verdict": data["verdict"],
            "publication_ready": data["publication_ready"],
            "attempts": data["attempts"],
        },
        "scores": data["scores"],
        "strengths": data["strengths"],
        "weaknesses": data["weaknesses"],
        "rejected_pages": data["rejected_adaptations"],
        "revise_pages": data["revise_adaptations"],
        "visual_issues": _collect_issues(package, ("visual_quality", "diagram", "layout")),
        "writing_issues": _collect_issues(package, ("writing_quality",)),
        "accessibility_issues": _collect_issues(package, ("accessibility",)),
        "vocabulary_issues": _collect_issues(package, ("vocabulary",)),
        "improvement_recommendations": _recommendations(package),
        "by_adaptation": data["by_adaptation"],
        "screenshot_dir": data.get("screenshot_dir") or "",
        "golden_delta": data.get("golden_delta") or 0,
    }

    json_path = REPORT_ROOT / f"{run_id}_publisher_quality_report.json"
    md_path = REPORT_ROOT / f"{run_id}_publisher_quality_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(_to_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "report": report}


def _collect_issues(package: PackageAcceptance, dims: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for aid, acc in package.by_adaptation.items():
        for dim_name in dims:
            dim = acc.dimensions.get(dim_name)
            if not dim:
                continue
            for issue in dim.issues:
                out.append(f"[{aid}/{dim_name}] {issue}")
    return out[:40]


def _recommendations(package: PackageAcceptance) -> list[str]:
    recs: list[str] = []
    if package.overall < 95:
        recs.append("Run the revise pipeline and re-evaluate before publishing.")
    for aid in package.rejected_adaptations:
        recs.append(f"Rewrite {aid} with a genuine educational personality and richer pedagogy.")
    for aid in package.revise_adaptations:
        recs.append(f"Polish {aid}: strengthen examples, diagrams, and transitions.")
    for issue in package.weaknesses[:8]:
        recs.append(f"Address: {issue}")
    if not recs:
        recs.append("Maintain publisher-ready standard; consider promoting to golden_lessons/ (98+).")
    return recs[:20]


def _to_markdown(report: Mapping[str, Any]) -> str:
    summary = report.get("lesson_summary") or {}
    lines = [
        "# Publisher Quality Report",
        "",
        f"**Topic:** {summary.get('topic') or '—'}  ",
        f"**Subject:** {summary.get('subject') or '—'}  ",
        f"**Overall Publisher Score:** {summary.get('overall_publisher_score')}  ",
        f"**Band:** {summary.get('band')}  ",
        f"**Verdict:** {summary.get('verdict')}  ",
        f"**Publication ready:** {summary.get('publication_ready')}  ",
        "",
        "## Scores",
        "",
    ]
    for k, v in (report.get("scores") or {}).items():
        lines.append(f"- **{k}:** {v}")
    lines += ["", "## Strengths", ""]
    lines += [f"- {s}" for s in (report.get("strengths") or ["—"])]
    lines += ["", "## Weaknesses", ""]
    lines += [f"- {s}" for s in (report.get("weaknesses") or ["—"])]
    lines += ["", "## Improvement recommendations", ""]
    lines += [f"- {s}" for s in (report.get("improvement_recommendations") or ["—"])]
    lines += ["", "## Rejected pages", ""]
    rejected = report.get("rejected_pages") or []
    lines += [f"- {s}" for s in rejected] if rejected else ["- None"]
    return "\n".join(lines) + "\n"
