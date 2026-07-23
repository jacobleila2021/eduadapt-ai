"""Non-breaking EATS hooks for publication gate and post-generation attach."""

from __future__ import annotations

from typing import Any, Mapping

from eats.constants import PUBLISHER_READY
from eats.pipeline import accept_lesson


def attach_eats_to_adaptations(
    adaptations: dict[str, Any],
    *,
    subject: str = "",
    topic: str = "",
    auto_revise: bool = True,
    capture_screenshots: bool = False,
) -> dict[str, Any]:
    """Run acceptance and return adaptations with ``_meta.eats`` attached."""
    result = accept_lesson(
        adaptations,
        subject=subject,
        topic=topic,
        auto_revise=auto_revise,
        capture_screenshots=capture_screenshots,
        try_png=False,
    )
    return result["adaptations"]


def eats_block_reason(adaptations: Mapping[str, Any] | None) -> str:
    """Return block reason from ``_meta.eats`` if acceptance failed."""
    if not isinstance(adaptations, dict):
        return ""
    meta = adaptations.get("_meta") or {}
    eats = meta.get("eats") if isinstance(meta, dict) else None
    if not isinstance(eats, dict) or not eats:
        return ""
    if eats.get("reject_rendering") or eats.get("publication_ready") is False:
        overall = eats.get("overall")
        verdict = eats.get("verdict") or "reject"
        return (
            f"Educational Acceptance Testing failed ({verdict}; "
            f"score={overall}, need ≥{PUBLISHER_READY}). Lesson held for rewrite."
        )
    return ""
