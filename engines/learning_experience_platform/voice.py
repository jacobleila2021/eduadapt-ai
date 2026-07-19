"""VMLE voice integration for LXP."""

from __future__ import annotations

from typing import Any


def voice_controls(utterance: str = "", **kwargs: Any) -> dict[str, Any]:
    try:
        from engines.voice_multimodal_learning.service import (
            api_voice_command,
            api_speech_to_text,
            api_pronunciation_feedback,
            api_text_to_speech,
        )

        cmd = api_voice_command(utterance) if utterance else {"ok": True, "command": None}
        return {
            "ok": True,
            "voice_command": cmd,
            "stt": api_speech_to_text(transcript_hint=utterance) if utterance else None,
            "tts": api_text_to_speech,
            "pronunciation": api_pronunciation_feedback,
            "features": [
                "voice_commands",
                "voice_navigation",
                "speech_to_text",
                "pronunciation_feedback",
                "narration",
                "multilingual_narration",
                "offline_narration",
            ],
            "source": "vmle",
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
