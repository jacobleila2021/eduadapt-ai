"""Conversational multimodal flow — ATIE remains teaching intelligence."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.schemas import VOICE_COMMANDS
from engines.voice_multimodal_learning.speech_to_text import transcribe
from engines.voice_multimodal_learning.text_to_speech import synthesize_speech


def parse_voice_command(utterance: str) -> dict[str, Any]:
    u = (utterance or "").lower().strip()
    mapping = [
        (("read this", "read the page", "read page"), "read_this_page"),
        (("explain", "what does this mean"), "explain_this_concept"),
        (("slow down", "slower"), "slow_down"),
        (("speed up", "faster"), "speed_up"),
        (("repeat", "say that again"), "repeat_that"),
        (("translate",), "translate_this"),
        (("diagram", "show figure", "show the diagram"), "show_the_diagram"),
        (("glossary",), "open_glossary"),
        (("quiz", "start quiz", "test me"), "start_quiz"),
        (("next question", "next"), "next_question"),
        (("previous", "back"), "previous_page"),
        (("highlight", "keywords"), "highlight_keywords"),
        (("example", "show examples"), "show_examples"),
        (("tutor", "ask my tutor", "help me"), "ask_my_tutor"),
    ]
    for phrases, cmd in mapping:
        if any(p in u for p in phrases):
            return {"ok": True, "command": cmd, "utterance": utterance, "supported": cmd in VOICE_COMMANDS}
    return {"ok": True, "command": "ask_my_tutor", "utterance": utterance, "fallback": True}


def conversational_turn(
    *,
    learner_utterance: str = "",
    audio_bytes: bytes | None = None,
    tutor_kwargs: dict[str, Any] | None = None,
    speak_response: bool = True,
    voice_style: str = "Female",
    api_key: str = "",
    mode: str = "socratic",  # socratic|guided_discovery|clarification|reflection|revision|exam_prep
) -> dict[str, Any]:
    """
    STT → ATIE teaching turn → optional TTS.
    Never bypasses ATIE for educational guidance.
    """
    stt = transcribe(audio_bytes=audio_bytes, transcript_hint=learner_utterance, purpose="question")
    text = stt.get("text") or learner_utterance or ""
    cmd = parse_voice_command(text)

    tutor_kwargs = dict(tutor_kwargs or {})
    tutor_kwargs.setdefault("question", text)
    tutor_kwargs["vmle_mode"] = mode

    tutor_out: dict[str, Any] = {}
    try:
        from engines.ai_tutor_intelligence_engine.conversation_manager import run_tutor_turn

        tutor_out = run_tutor_turn(tutor_kwargs) if text else {"ok": True, "message": "How can I help with this lesson?"}
    except Exception:  # noqa: BLE001
        try:
            from engines.ai_tutor_intelligence_engine.service import api_generate_hint

            tutor_out = api_generate_hint(**tutor_kwargs) if text else {"ok": True, "hint": "Let's look at the lesson together."}
        except Exception as exc:  # noqa: BLE001
            tutor_out = {"ok": False, "error": str(exc), "policy": "atie_required"}

    reply_text = (
        tutor_out.get("response")
        or tutor_out.get("message")
        or tutor_out.get("hint")
        or tutor_out.get("explanation")
        or tutor_out.get("text")
        or "I'm ready when you are — ask about this concept."
    )
    if isinstance(reply_text, dict):
        reply_text = reply_text.get("text") or str(reply_text)

    speech = None
    if speak_response and reply_text:
        speech = synthesize_speech(str(reply_text), voice_style=voice_style, api_key=api_key)

    return {
        "ok": True,
        "stt": stt,
        "voice_command": cmd,
        "mode": mode,
        "atie": tutor_out,
        "reply_text": str(reply_text),
        "speech": speech,
        "teaching_source": "atie",
        "encouragement": _encouragement(mode),
    }


def _encouragement(mode: str) -> str:
    return {
        "socratic": "Nice thinking — what do you notice next?",
        "guided_discovery": "You're discovering this step by step.",
        "clarification": "Good question — let's clarify carefully.",
        "reflection": "Reflecting helps ideas stick.",
        "revision": "Revision builds confidence for the exam.",
        "exam_prep": "Exam focus: clear steps, calm pace.",
    }.get(mode, "Keep going — I'm here with you.")
