"""Contextual AI chat — preserves lesson/learner/mastery/a11y context."""

from __future__ import annotations

from typing import Any


def build_chat_context(
    *,
    lesson: dict[str, Any] | None = None,
    paragraph: str = "",
    competency: str = "",
    learner_id: str = "",
    engine_outputs: dict[str, Any] | None = None,
    conversation: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    engine_outputs = engine_outputs or {}
    aie = (engine_outputs.get("accessibility") or {}).get("payload") or {}
    ame = (engine_outputs.get("assessment") or {}).get("payload") or {}
    ale = (engine_outputs.get("adaptive_learning") or {}).get("payload") or {}
    return {
        "lesson_id": (lesson or {}).get("lesson_id") or (lesson or {}).get("title") or "",
        "lesson_title": (lesson or {}).get("title") or "",
        "paragraph": paragraph,
        "competency": competency,
        "learner_id": learner_id,
        "accessibility_profile": aie.get("learner_profile") or aie.get("profiles_generated") or [],
        "mastery_profile": ame.get("mastery") or ale.get("learner_model") or {},
        "adaptive_pathway": ale.get("pathway") or ale.get("next_activity") or {},
        "conversation": list(conversation or [])[-20:],
        "policy": "retain_context_never_hallucinate",
    }


def chat_turn(message: str, chat_ctx: dict[str, Any]) -> dict[str, Any]:
    history = list(chat_ctx.get("conversation") or [])
    history.append({"role": "learner", "text": message})
    try:
        from engines.ai_tutor_intelligence_engine.conversation_manager import run_tutor_turn

        out = run_tutor_turn(
            {
                "question": message,
                "lesson_excerpt": chat_ctx.get("paragraph") or "",
                "learner_id": chat_ctx.get("learner_id") or "",
                "topic": chat_ctx.get("lesson_title") or "",
                "history": history,
            }
        )
        reply = out.get("response") or out.get("message") or out.get("text") or str(out)
    except Exception as exc:  # noqa: BLE001
        try:
            from engines.ai_tutor_intelligence_engine.service import api_generate_hint

            out = api_generate_hint(question=message, lesson_excerpt=chat_ctx.get("paragraph") or "")
            reply = out.get("hint") or out.get("text") or "Let's look at the lesson facts together."
            out = {"fallback": True, "error": str(exc), **(out if isinstance(out, dict) else {})}
        except Exception as exc2:  # noqa: BLE001
            reply = "I can help once the AI Tutor is available — your lesson context is saved."
            out = {"ok": False, "error": str(exc2)}
    history.append({"role": "tutor", "text": str(reply)})
    return {
        "ok": True,
        "reply": str(reply),
        "conversation": history[-20:],
        "context_retained": True,
        "atie": out if isinstance(out, dict) else {"raw": out},
        "teaching_source": "atie",
    }
