"""Live validation dashboard state for UEVB."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "reports" / "uevb"
DASHBOARD_PATH = REPORT_ROOT / "dashboard_state.json"


def build_dashboard_state(
    validations: list[Mapping[str, Any]],
    *,
    release_gate: Mapping[str, Any] | None = None,
    corpus_meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    subject_scores: dict[str, list[float]] = defaultdict(list)
    curriculum_notes: dict[str, int] = defaultdict(int)
    adaptation_scores: list[float] = []
    visual_scores: list[float] = []
    editorial_scores: list[float] = []
    engine_failures: dict[str, int] = defaultdict(int)
    golden_ok = 0
    total = len(validations)
    passed = 0

    for row in validations:
        if row.get("ok"):
            passed += 1
        subject = str(row.get("subject") or "general")
        pub = float((row.get("publisher_benchmark_report") or {}).get("publisher_quality_score") or 0)
        subject_scores[subject].append(pub)
        adaptation_scores.append(
            float((row.get("adaptation_differentiation_report") or {}).get("adaptation_differentiation_score") or 0)
        )
        visual_scores.append(float((row.get("visual_design_audit") or {}).get("visual_quality_score") or 0))
        editorial_scores.append(pub)
        for eng in (row.get("engine_contribution_report") or {}).get("core_integration_failures") or []:
            engine_failures[str(eng)] += 1
        if (row.get("golden_benchmark") or {}).get("ok"):
            golden_ok += 1

    def _avg(vals: list[float]) -> float:
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    prior = {}
    if DASHBOARD_PATH.exists():
        try:
            prior = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            prior = {}

    state = {
        "schema": "alora.uevb.dashboard.v1",
        "pass_rate": round((passed / total), 4) if total else 0.0,
        "prior_pass_rate": prior.get("pass_rate"),
        "total_lessons": total,
        "passed": passed,
        "subject_quality": {k: _avg(v) for k, v in subject_scores.items()},
        "curriculum_quality": dict(curriculum_notes) or {"status": "see_consistency_report"},
        "adaptation_quality": _avg(adaptation_scores),
        "visual_quality": _avg(visual_scores),
        "editorial_quality": _avg(editorial_scores),
        "engine_contribution_failures": dict(engine_failures),
        "golden_benchmark_status": {
            "passed": golden_ok,
            "total": total,
            "rate": round(golden_ok / total, 4) if total else 0.0,
        },
        "release_gate": release_gate or {},
        "corpus": corpus_meta or {},
        "regression_trends": {
            "pass_rate_delta": round(
                ((passed / total) if total else 0.0) - float(prior.get("pass_rate") or 0.0),
                4,
            )
        },
    }
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def render_dashboard_markdown(state: Mapping[str, Any]) -> str:
    lines = [
        "# UEVB Validation Dashboard",
        "",
        f"- Pass rate: **{float(state.get('pass_rate') or 0):.1%}**",
        f"- Lessons: {state.get('passed')}/{state.get('total_lessons')}",
        f"- Adaptation quality: {state.get('adaptation_quality')}",
        f"- Visual quality: {state.get('visual_quality')}",
        f"- Editorial quality: {state.get('editorial_quality')}",
        f"- Golden benchmark rate: {((state.get('golden_benchmark_status') or {}).get('rate') or 0):.1%}",
        "",
        "## Subject quality",
    ]
    for subject, score in sorted((state.get("subject_quality") or {}).items()):
        lines.append(f"- {subject}: {score}")
    lines.append("")
    lines.append("## Engine contribution failures")
    fails = state.get("engine_contribution_failures") or {}
    if not fails:
        lines.append("- None")
    else:
        for eng, n in sorted(fails.items()):
            lines.append(f"- {eng}: {n}")
    rg = state.get("release_gate") or {}
    lines.extend(
        [
            "",
            "## Release gate",
            f"- Permitted: **{rg.get('release_permitted')}**",
            f"- Regressions: {rg.get('regressions') or []}",
        ]
    )
    return "\n".join(lines)
