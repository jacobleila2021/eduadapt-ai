"""Encouragement messages — wraps motivation + personality."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.motivation import craft_encouragement, motivation_profile
from engines.learning_companion_engine.personality import apply_style
from engines.learning_companion_engine.schemas import CompanionMessage


def encourage(
    *,
    companion_id: str,
    style: str,
    context: dict[str, Any] | None = None,
    memory: dict[str, Any] | None = None,
    event: str = "progress",
) -> dict[str, Any]:
    profile = motivation_profile(context, memory)
    if memory and memory.get("challenges_attempted"):
        profile["challenges_completed"] = memory.get("challenges_attempted")
    raw = craft_encouragement(profile, event=event)
    styled = apply_style(raw["text"], style or (memory or {}).get("communication_style") or "gentle_coach")
    msg = CompanionMessage(
        text=styled["text"],
        kind="encouragement",
        companion_id=companion_id,
        evidence=raw["evidence"],
        speakable=True,
        refer_to_atie=False,
    )
    return {"ok": True, "message": msg.to_dict(), "profile": profile}
