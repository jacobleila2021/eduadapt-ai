"""Rewards bridge — intrinsic framing; extrinsic is optional recognition only."""

from __future__ import annotations

from typing import Any


def summarize_rewards(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "xp_total": state.get("xp_total") or 0,
        "level_id": state.get("level_id"),
        "badges_count": len(state.get("badges") or []),
        "achievements_count": len(state.get("achievements") or []),
        "certificates_count": len(state.get("certificates") or []),
        "quests_completed": len([q for q in (state.get("quests") or []) if q.get("status") == "completed"]),
        "framing": "Recognition of growth — not a pay-to-win economy",
        "competitive_leaderboards": False,
    }


def alcis_celebration_payload(state: dict[str, Any], newly: dict[str, Any] | None = None) -> dict[str, Any]:
    """Payload ALCIS can celebrate; LMAS remains source of truth for XP economy."""
    newly = newly or {}
    return {
        "xp": state.get("xp_total"),
        "badges": state.get("badges") or [],
        "streaks": state.get("streaks") or {},
        "new_badges": newly.get("badges") or [],
        "new_achievements": newly.get("achievements") or [],
        "owner": "learning_motivation_engine",
    }


def atie_context_snippet(state: dict[str, Any]) -> dict[str, Any]:
    """ATIE may reference achievements — never alter curriculum."""
    return {
        "level": state.get("level_id"),
        "recent_achievements": (state.get("achievements") or [])[-3:],
        "active_quests": [q for q in (state.get("quests") or []) if q.get("status") == "active"][:3],
        "policy": "reference_only_do_not_change_curriculum",
    }


def vmle_announcements(newly: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    newly = newly or {}
    lines = []
    for b in newly.get("badges") or []:
        lines.append({"type": "achievement", "text": f"You earned the badge {b.get('name')}!", "speakable": True})
    for c in newly.get("certificates") or []:
        lines.append({"type": "certificate", "text": f"Certificate issued: {c.get('title')}", "speakable": True})
    return lines
