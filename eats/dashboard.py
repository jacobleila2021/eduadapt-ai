"""Educational Acceptance Dashboard — aggregate metrics (data API + optional Streamlit)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "reports" / "eats"
DASHBOARD_PATH = REPORT_ROOT / "dashboard_state.json"


def _load_reports() -> list[dict[str, Any]]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for path in sorted(REPORT_ROOT.glob("*_publisher_quality_report.json")):
        try:
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return rows


def build_dashboard_state() -> dict[str, Any]:
    reports = _load_reports()
    if not reports:
        state = {
            "pass_rate": 0.0,
            "average_scores": {},
            "rejected_lessons": 0,
            "publisher_quality_index": 0.0,
            "trend": [],
            "subject_performance": {},
            "adaptation_performance": {},
            "vocabulary_performance": 0.0,
            "diagram_performance": 0.0,
            "accessibility_compliance": 0.0,
            "total_lessons": 0,
        }
        DASHBOARD_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state

    totals = 0
    passes = 0
    rejected = 0
    overalls: list[float] = []
    dim_sums: dict[str, list[float]] = defaultdict(list)
    subjects: dict[str, list[float]] = defaultdict(list)
    adaptations: dict[str, list[float]] = defaultdict(list)
    trend: list[dict[str, Any]] = []

    for rep in reports:
        summary = rep.get("lesson_summary") or {}
        overall = float(summary.get("overall_publisher_score") or 0)
        totals += 1
        overalls.append(overall)
        if summary.get("publication_ready") or summary.get("verdict") == "pass":
            passes += 1
        if summary.get("verdict") == "reject" or not summary.get("publication_ready"):
            if summary.get("verdict") == "reject":
                rejected += 1
        for k, v in (rep.get("scores") or {}).items():
            dim_sums[k].append(float(v))
        sub = str((summary.get("subject") or "general")).lower() or "general"
        subjects[sub].append(overall)
        for aid, acc in (rep.get("by_adaptation") or {}).items():
            adaptations[aid].append(float(acc.get("overall") or 0))
        trend.append(
            {
                "run_id": rep.get("run_id"),
                "score": overall,
                "verdict": summary.get("verdict"),
                "topic": summary.get("topic"),
            }
        )

    def avg(vals: list[float]) -> float:
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    state = {
        "pass_rate": round(100.0 * passes / max(1, totals), 2),
        "average_scores": {k: avg(v) for k, v in dim_sums.items()},
        "rejected_lessons": rejected,
        "publisher_quality_index": avg(overalls),
        "trend": trend[-50:],
        "subject_performance": {k: avg(v) for k, v in subjects.items()},
        "adaptation_performance": {k: avg(v) for k, v in adaptations.items()},
        "vocabulary_performance": avg(dim_sums.get("vocabulary") or []),
        "diagram_performance": avg(dim_sums.get("diagram") or []),
        "accessibility_compliance": avg(dim_sums.get("accessibility") or []),
        "total_lessons": totals,
    }
    DASHBOARD_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def render_dashboard_streamlit() -> None:
    """Optional Streamlit panel — safe no-op if streamlit unavailable."""
    try:
        import streamlit as st
    except Exception:
        return
    state = build_dashboard_state()
    st.subheader("Educational Acceptance Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pass rate", f"{state['pass_rate']}%")
    c2.metric("Publisher Quality Index", state["publisher_quality_index"])
    c3.metric("Rejected lessons", state["rejected_lessons"])
    c4.metric("Lessons evaluated", state["total_lessons"])
    st.write("### Average dimension scores")
    st.json(state.get("average_scores") or {})
    st.write("### Adaptation performance")
    st.json(state.get("adaptation_performance") or {})
    st.write("### Subject performance")
    st.json(state.get("subject_performance") or {})
