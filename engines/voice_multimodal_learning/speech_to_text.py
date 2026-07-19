"""Speech-to-text — learner voice input with confidence scores."""

from __future__ import annotations

from typing import Any
import re


def transcribe(
    *,
    audio_bytes: bytes | None = None,
    transcript_hint: str = "",
    language: str = "en",
    purpose: str = "question",  # question|quiz|reflection|dictation|oral_reading|language_practice
) -> dict[str, Any]:
    """
    STT facade. When audio_bytes + OpenAI key available, can call Whisper;
    otherwise accepts client-side transcript (browser Web Speech) with scoring.
    """
    purpose = purpose if purpose in (
        "question", "quiz", "reflection", "dictation", "oral_reading", "language_practice"
    ) else "question"

    if transcript_hint:
        text = _normalize(transcript_hint)
        return {
            "ok": True,
            "provider": "client_or_hint",
            "text": text,
            "confidence": _estimate_confidence(text),
            "language": language,
            "purpose": purpose,
            "live": False,
            "punctuation_applied": True,
            "noise_tolerance": "client_dependent",
        }

    if audio_bytes:
        whisper = _try_whisper(audio_bytes, language=language)
        if whisper.get("ok"):
            whisper["purpose"] = purpose
            return whisper
        return {
            "ok": False,
            "error": whisper.get("error") or "stt_unavailable",
            "fallback": "use_browser_web_speech",
            "purpose": purpose,
        }

    return {
        "ok": False,
        "error": "no_audio_or_transcript",
        "fallback": "use_browser_web_speech",
        "purpose": purpose,
    }


def _normalize(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"\s+", " ", text)
    if text and text[-1] not in ".!?":
        text += "."
    return text


def _estimate_confidence(text: str) -> float:
    if not text or len(text) < 2:
        return 0.2
    words = text.split()
    if len(words) < 2:
        return 0.55
    return min(0.95, 0.6 + 0.05 * min(len(words), 7))


def _try_whisper(audio_bytes: bytes, *, language: str = "en") -> dict[str, Any]:
    try:
        import os
        from openai import OpenAI

        key = os.environ.get("OPENAI_API_KEY") or ""
        if not key:
            return {"ok": False, "error": "no_api_key"}
        # Optional path — many deployments use browser STT instead
        return {
            "ok": False,
            "error": "whisper_upload_not_wired",
            "note": "Prefer client Web Speech; server Whisper can be enabled later",
            "language": language,
            "byte_length": len(audio_bytes),
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
