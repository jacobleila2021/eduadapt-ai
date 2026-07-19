"""REST-shaped API facade for Voice & Multimodal Learning Experience."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning import analytics
from engines.voice_multimodal_learning.accessibility import apply_aie
from engines.voice_multimodal_learning.conversation import conversational_turn, parse_voice_command
from engines.voice_multimodal_learning.multilingual import settings as lang_settings
from engines.voice_multimodal_learning.narration import plan_narration
from engines.voice_multimodal_learning.offline import cache_lesson_bundle, list_cached, synchronize
from engines.voice_multimodal_learning.pronunciation import coach, practice_card
from engines.voice_multimodal_learning.read_along import (
    bookmark,
    create_read_along_state,
    jump_to,
    pause,
    resume,
    set_speed,
)
from engines.voice_multimodal_learning.session_memory import end_session, start_session, load_session, save_session
from engines.voice_multimodal_learning.speech_to_text import transcribe
from engines.voice_multimodal_learning.synchronization import publish_to_vlie
from engines.voice_multimodal_learning.text_to_speech import available_voices, synthesize_speech
from engines.voice_multimodal_learning.multimodal import interactive_bundle


def api_start_voice_session(learner_id: str, **meta: Any) -> dict[str, Any]:
    doc = start_session(learner_id, **{k: v for k, v in meta.items() if k in (
        "lesson_id", "vlie_session_id", "language", "voice_style", "teacher_controls", "parent_controls", "accessibility"
    )})
    analytics.record("voice_session_start", session_id=doc["session_id"])
    if doc.get("vlie_session_id"):
        publish_to_vlie("audio_played", session_id=doc["vlie_session_id"], learner_id=learner_id, payload={"phase": "session_start"})
    return {"ok": True, "session": doc}


def api_end_voice_session(session_id: str) -> dict[str, Any]:
    result = end_session(session_id)
    analytics.record("voice_session_end", session_id=session_id)
    return result


def api_speech_to_text(**kwargs: Any) -> dict[str, Any]:
    out = transcribe(**kwargs)
    analytics.record("stt", session_id=str(kwargs.get("session_id") or ""), payload={"ok": out.get("ok")})
    return out


def api_text_to_speech(text: str, **kwargs: Any) -> dict[str, Any]:
    # Strip audio_bytes from default API response size unless requested
    include_bytes = bool(kwargs.pop("include_audio_bytes", False))
    out = synthesize_speech(text, **{k: v for k, v in kwargs.items() if k in ("voice_style", "api_key", "speed")})
    if not include_bytes and out.get("audio_bytes") is not None:
        out = {**out, "audio_bytes": None, "audio_omitted": True, "byte_length": out.get("byte_length")}
    analytics.record("audio_played", session_id=str(kwargs.get("session_id") or ""))
    return out


def api_read_along_state(content: Any = None, **kwargs: Any) -> dict[str, Any]:
    plan = plan_narration(content or kwargs.get("lesson_text") or "", **{
        k: kwargs[k] for k in ("spec_id", "speed", "language", "voice_style", "title") if k in kwargs
    })
    state = create_read_along_state(plan, highlight_mode=kwargs.get("highlight_mode") or "sentence", speed=kwargs.get("speed") or 1.0)
    return {"ok": True, "narration": plan.to_dict(), "state": state}


def api_read_along_control(session_id: str, action: str, **kwargs: Any) -> dict[str, Any]:
    doc = load_session(session_id)
    if not doc:
        return {"ok": False, "error": "session_not_found"}
    state = dict(doc.get("read_along") or {})
    if action == "pause":
        state = pause(state)
    elif action == "resume":
        state = resume(state)
    elif action == "speed":
        state = set_speed(state, float(kwargs.get("speed") or 1.0))
    elif action == "jump":
        state = jump_to(state, int(kwargs.get("index") or 0))
    elif action == "bookmark":
        state = bookmark(state, str(kwargs.get("label") or ""))
    else:
        return {"ok": False, "error": "unknown_action"}
    doc["read_along"] = state
    save_session(doc)
    if action in ("resume", "pause"):
        analytics.record("read_along_" + action, session_id=session_id)
    return {"ok": True, "state": state}


def api_pronunciation_feedback(word: str, heard: str = "", **kwargs: Any) -> dict[str, Any]:
    attempt = coach(word, heard=heard, slow_mode=bool(kwargs.get("slow_mode")))
    analytics.record("pronunciation", session_id=str(kwargs.get("session_id") or ""), payload=attempt.to_dict())
    return {"ok": True, "attempt": attempt.to_dict(), "card": practice_card(word, category=str(kwargs.get("category") or "vocabulary"))}


def api_voice_command(utterance: str, **kwargs: Any) -> dict[str, Any]:
    parsed = parse_voice_command(utterance)
    analytics.record("voice_command", session_id=str(kwargs.get("session_id") or ""), payload=parsed)
    vlie_sid = kwargs.get("vlie_session_id") or ""
    if vlie_sid and parsed.get("command") == "ask_my_tutor":
        publish_to_vlie("tutor_question", session_id=vlie_sid, payload=parsed)
    return {"ok": True, **parsed}


def api_interactive_content(**kwargs: Any) -> dict[str, Any]:
    return {"ok": True, "content": interactive_bundle(kwargs)}


def api_offline_sync(**kwargs: Any) -> dict[str, Any]:
    if kwargs.get("cache_id"):
        out = synchronize(str(kwargs["cache_id"]))
        analytics.record("offline_sync", payload=out)
        return out
    if kwargs.get("action") == "list":
        return {"ok": True, "cached": list_cached(str(kwargs.get("learner_id") or ""))}
    out = cache_lesson_bundle(
        learner_id=str(kwargs.get("learner_id") or "anonymous"),
        lesson_id=str(kwargs.get("lesson_id") or "lesson"),
        lesson_text=str(kwargs.get("lesson_text") or ""),
        audio_meta=kwargs.get("audio_meta"),
        images=kwargs.get("images"),
        diagrams=kwargs.get("diagrams"),
        assessments=kwargs.get("assessments"),
        session_state=kwargs.get("session_state"),
        progress=kwargs.get("progress"),
    )
    return out


def api_multilingual_settings(**kwargs: Any) -> dict[str, Any]:
    return {"ok": True, **lang_settings(**{k: kwargs[k] for k in ("language", "dual_language", "subtitles") if k in kwargs})}


def api_usage_analytics(session_id: str = "") -> dict[str, Any]:
    return {"ok": True, "analytics": analytics.summary(session_id)}


def api_conversational_turn(**kwargs: Any) -> dict[str, Any]:
    return conversational_turn(**{k: kwargs[k] for k in kwargs if k in (
        "learner_utterance", "audio_bytes", "tutor_kwargs", "speak_response", "voice_style", "api_key", "mode"
    )})


def api_voices() -> dict[str, Any]:
    return {"ok": True, **available_voices()}


def api_accessibility_profile(**kwargs: Any) -> dict[str, Any]:
    return {"ok": True, "accessibility": apply_aie(kwargs)}
