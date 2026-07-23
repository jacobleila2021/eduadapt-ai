"""EATS acceptance pipeline — evaluate → revise → re-evaluate → report → gate."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from eats.constants import (
    EATS_ADAPTATION_KEYS,
    EATS_VERSION,
    MAX_REVISE_ATTEMPTS,
    PUBLISHER_READY,
    band_for_score,
)
from eats.dashboard import build_dashboard_state
from eats.evaluator import _subject_from, evaluate_package
from eats.golden_library import promote_to_golden
from eats.reports import write_publisher_quality_report
from eats.revise_gate import attempt_revise
from eats.screenshots import capture_adaptation_snapshots


def _topic_from(adaptations: Mapping[str, Any], topic: str = "") -> str:
    if topic:
        return topic
    meta = adaptations.get("_meta") if isinstance(adaptations.get("_meta"), dict) else {}
    ctx = meta.get("lesson_context") or {}
    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    return str(
        ctx.get("topic")
        or std.get("topic")
        or std.get("title")
        or std.get("big_idea")
        or "Lesson"
    )


def accept_lesson(
    adaptations: dict[str, Any],
    *,
    subject: str = "",
    topic: str = "",
    clg: Mapping[str, Any] | None = None,
    capture_screenshots: bool = True,
    try_png: bool = False,
    auto_revise: bool = True,
    max_attempts: int = MAX_REVISE_ATTEMPTS,
    promote_golden: bool = True,
) -> dict[str, Any]:
    """Full Educational Acceptance pipeline (editor-in-chief gate)."""
    working = {k: (dict(v) if isinstance(v, dict) else v) for k, v in adaptations.items()}
    subject = _subject_from(working, subject)
    topic = _topic_from(working, topic)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    attempts = 0
    revise_log: list[dict[str, Any]] = []

    package = evaluate_package(working, subject=subject)

    while (
        auto_revise
        and not package.publication_ready
        and package.overall >= 60
        and attempts < max_attempts
    ):
        attempts += 1
        revised = attempt_revise(working, clg=clg, max_passes=1)
        working = revised["adaptations"]
        revise_log.append({"attempt": attempts, **(revised.get("revise_meta") or {})})
        package = evaluate_package(working, subject=subject)
        package.attempts = attempts

    package.attempts = attempts

    if package.overall < PUBLISHER_READY:
        package.publication_ready = False
        package.reject_rendering = True
        if package.verdict == "pass":
            package.verdict = "revise" if package.overall >= 80 else "reject"
            package.band = band_for_score(package.overall)

    screenshots: dict[str, Any] = {}
    if capture_screenshots:
        keys = [k for k in EATS_ADAPTATION_KEYS if isinstance(working.get(k), dict)]
        screenshots = capture_adaptation_snapshots(
            working, run_id=run_id, keys=keys, try_png=try_png
        )
        package.screenshot_dir = str(screenshots.get("dir") or "")

    report_info = write_publisher_quality_report(
        package, topic=topic, subject=subject, run_id=run_id
    )
    package.report_path = str(report_info.get("json") or "")

    if promote_golden and package.publication_ready and package.overall >= 98:
        promote_to_golden(
            working,
            subject=subject,
            topic=topic,
            publisher_score=package.overall,
            lesson_id=f"eats_{subject}_{topic}",
        )

    dashboard = build_dashboard_state()
    eats_meta = {
        "version": EATS_VERSION,
        "run_id": run_id,
        "verdict": package.verdict,
        "overall": package.overall,
        "band": package.band,
        "publication_ready": package.publication_ready,
        "reject_rendering": package.reject_rendering,
        "attempts": attempts,
        "revise_log": revise_log,
        "report_path": package.report_path,
        "screenshot_dir": package.screenshot_dir,
        "scores": package.scores,
        "rejected_adaptations": package.rejected_adaptations,
        "threshold": PUBLISHER_READY,
    }

    meta = dict(working.get("_meta") or {}) if isinstance(working.get("_meta"), dict) else {}
    meta["eats"] = eats_meta
    working["_meta"] = meta

    return {
        "ok": bool(package.publication_ready),
        "verdict": package.verdict,
        "package": package.to_dict(),
        "adaptations": working,
        "report": report_info.get("report"),
        "report_paths": {"json": report_info.get("json"), "markdown": report_info.get("markdown")},
        "screenshots": screenshots,
        "dashboard": dashboard,
        "eats_meta": eats_meta,
    }
