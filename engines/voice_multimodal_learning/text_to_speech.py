"""Text-to-speech — wraps audio_learning; never invents curriculum content."""

from __future__ import annotations

from typing import Any


def synthesize_speech(
    text: str,
    *,
    voice_style: str = "Female",
    api_key: str = "",
    speed: float = 1.0,
) -> dict[str, Any]:
    """
    Headless TTS. Prefers OpenAI speech via audio_learning; falls back to
    browser-playback instructions when no key / API unavailable.
    """
    from audio_learning import OPENAI_VOICE_MAP, VOICE_OPTIONS, _clean_for_speech, generate_openai_speech

    cleaned = _clean_for_speech(text or "")
    if not cleaned:
        return {"ok": False, "error": "empty_text", "provider": None}

    voice = (
        OPENAI_VOICE_MAP.get(voice_style)
        or OPENAI_VOICE_MAP.get("Warm Female (Indian)")
        or OPENAI_VOICE_MAP.get("Female")
    )
    legacy_voice_aliases = {
        "Female": "Warm Female (Indian)",
        "Male": "Warm Male (Indian)",
    }
    resolved_style = (
        voice_style
        if voice_style in VOICE_OPTIONS
        else legacy_voice_aliases.get(voice_style, "Warm Female (Indian)")
    )
    if resolved_style not in VOICE_OPTIONS:
        resolved_style = next(iter(VOICE_OPTIONS))
    instructions = (VOICE_OPTIONS.get(resolved_style) or {}).get("instructions") or ""
    if not voice:
        voice = OPENAI_VOICE_MAP.get(resolved_style)

    audio_bytes = None
    if api_key:
        try:
            audio_bytes = generate_openai_speech(cleaned, voice=voice, api_key=api_key, instructions=instructions)
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "error": str(exc),
                "provider": "openai",
                "fallback": "browser_tts",
                "text": cleaned,
                "speed": speed,
            }

    if audio_bytes:
        return {
            "ok": True,
            "provider": "openai",
            "voice": voice,
            "voice_style": voice_style,
            "text": cleaned,
            "speed": speed,
            "audio_bytes": audio_bytes,
            "mime": "audio/mpeg",
            "byte_length": len(audio_bytes),
        }

    return {
        "ok": True,
        "provider": "browser_tts",
        "voice_style": voice_style,
        "text": cleaned,
        "speed": speed,
        "audio_bytes": None,
        "note": "Client should use Web Speech API / device TTS",
    }


def available_voices() -> dict[str, Any]:
    from audio_learning import PLAYBACK_SPEEDS, VOICE_OPTIONS

    return {"voices": list(VOICE_OPTIONS.keys()), "speeds": list(PLAYBACK_SPEEDS)}
