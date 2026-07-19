"""Phase 4 experience metrics → LAIE (anonymized where possible)."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics


def track_experience(
    event: str,
    *,
    learner_id: str = "",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Track UX/performance metrics. Avoid unnecessary PII."""
    safe = dict(payload or {})
    # Strip potential PII keys
    for k in list(safe.keys()):
        if k.lower() in ("email", "phone", "name", "full_name", "address"):
            safe.pop(k, None)
    return analytics.track(f"ux_{event}", learner_id=learner_id, payload=safe)


def experience_summary(learner_id: str = "") -> dict[str, Any]:
    base = analytics.summary(learner_id=learner_id)
    counts = base.get("event_counts") or {}
    ux = {k: v for k, v in counts.items() if str(k).startswith("ux_")}
    return {
        "ok": True,
        "ux_events": ux,
        "metrics": {
            "page_load_samples": ux.get("ux_page_load", 0),
            "offline_usage": counts.get("offline", 0) + ux.get("ux_offline", 0),
            "sync_success": ux.get("ux_sync_success", 0),
            "sync_failure": ux.get("ux_sync_failure", 0),
            "animation_pref_changes": ux.get("ux_reduce_motion", 0),
            "a11y_feature_usage": counts.get("accessibility", 0) + ux.get("ux_a11y", 0),
            "cache_hits": ux.get("ux_cache_hit", 0),
            "cache_misses": ux.get("ux_cache_miss", 0),
        },
        "forward_to": "learning_analytics",
        "privacy": {"no_unnecessary_pii": True},
    }
