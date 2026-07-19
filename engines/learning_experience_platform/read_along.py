"""Read-along bridge — VMLE + audio_learning."""

from __future__ import annotations

from typing import Any


def read_along_bundle(lesson_text: str, *, prefs: dict[str, Any] | None = None) -> dict[str, Any]:
    prefs = prefs or {}
    try:
        from engines.voice_multimodal_learning.narration import plan_narration
        from engines.voice_multimodal_learning.read_along import create_read_along_state

        plan = plan_narration(
            lesson_text,
            speed=float(prefs.get("speed") or 1.0),
            voice_style=str(prefs.get("voice_style") or "Female"),
        )
        state = create_read_along_state(plan, highlight_mode=str(prefs.get("highlight_mode") or "sentence"))
        return {
            "ok": True,
            "narration": plan.to_dict(),
            "state": state,
            "controls": ["play", "pause", "speed", "repeat_sentence", "repeat_paragraph"],
            "integrates": ["vmle", "audio_learning"],
            "offline_narration": True,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "fallback": "audio_learning.render_audio_learning_panel"}
