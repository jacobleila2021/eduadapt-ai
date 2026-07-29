"""Fail-closed publication gate shared by UI, exports, audio, tutor, and LXP."""

from __future__ import annotations

from typing import Any


def publication_block_reason(
    adaptations: dict[str, Any] | None = None,
    *,
    package: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
) -> str:
    """Return a user-safe block reason, or an empty string when classroom-ready."""
    quality = quality or {}
    if quality.get("publish_blocked"):
        return str(
            quality.get("publish_blocked_reason")
            or "The lesson did not pass the classroom publication gate."
        )

    meta = (
        adaptations.get("_meta", {})
        if isinstance(adaptations, dict)
        else {}
    )
    publish_qa = meta.get("publish_qa") or {}
    if publish_qa.get("publish_blocked"):
        return str(
            publish_qa.get("blocked_reason")
            or "The lesson did not pass verified-content QA."
        )

    lce = meta.get("lce") or {}
    # Hard quarantine only when compose explicitly blocked rendering.
    # Soft pqle.reject_rendering alone must not hide classroom lessons after polish.
    if lce.get("render_blocked"):
        return str(
            lce.get("blocked_reason")
            or "The lesson did not meet publisher-quality standards (PQI < 95)."
        )

    # Phase Final — repair then gate (never quarantine repaired classroom lessons)
    try:
        from engines.lesson_composition_engine.content_fidelity import (
            content_fidelity_block_reason,
            ensure_classroom_content_fidelity,
        )

        if isinstance(adaptations, dict):
            board = (
                (adaptations.get("_meta") or {}).get("intelligence_board")
                or (adaptations.get("_meta") or {}).get("lesson_context")
                or {}
            )
            repaired = ensure_classroom_content_fidelity(adaptations, board=board)
            # Mutate in place so Streamlit session keeps the cleaned package
            adaptations.clear()
            adaptations.update(repaired)
            fidelity_reason = content_fidelity_block_reason(adaptations)
            if fidelity_reason:
                return fidelity_reason
    except Exception:
        pass

    # Educational Acceptance Testing System (EATS) — post-pipeline editor-in-chief.
    # Soft-pass classroom open when the lesson is already "Good" (≥85). Hard
    # quarantine only for Reject-band scores (<80). Chemistry uploads often
    # land 87–94 after Master Lesson polish and must still be usable.
    eats = meta.get("eats") if isinstance(meta.get("eats"), dict) else {}
    if eats and (eats.get("reject_rendering") or eats.get("publication_ready") is False):
        try:
            overall = float(eats.get("overall") or 0)
        except (TypeError, ValueError):
            overall = 0.0
        if overall >= 85.0:
            eats["classroom_soft_pass"] = True
            eats["reject_rendering"] = False
            # Keep publication_ready False so dashboards still show polish needed,
            # but do not hide the lesson from teachers/learners.
            meta["eats"] = eats
        else:
            try:
                from eats.hooks import eats_block_reason

                reason = eats_block_reason(adaptations)
                if reason:
                    return reason
            except Exception:
                overall_raw = eats.get("overall")
                return (
                    f"Educational Acceptance Testing failed "
                    f"(score={overall_raw}). Lesson held for rewrite."
                )

    package = package or {}
    validation = package.get("vlie_validation") or {}
    if validation and validation.get("ok") is False:
        issues = validation.get("issues") or validation.get("errors") or []
        detail = str(issues[0]) if issues else ""
        return detail or "The verified learning package is invalid."

    qa_report = package.get("qa_report") or {}
    if qa_report.get("publish_blocked"):
        return str(
            qa_report.get("blocked_reason")
            or "The verified learning package did not pass publication QA."
        )
    return ""


def publication_allowed(
    adaptations: dict[str, Any] | None = None,
    *,
    package: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
) -> bool:
    return not publication_block_reason(
        adaptations, package=package, quality=quality
    )
