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
