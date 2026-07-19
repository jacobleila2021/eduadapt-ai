"""AI revision assistant — ATIE grounded; never unsupported curriculum."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics


def ai_revision_assist(
    *,
    learner_id: str,
    message: str = "",
    action: str = "explain",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    actions = {
        "explain": "Explain difficult concepts using verified sources",
        "hint": "Generate hints without revealing unverified answers",
        "misconception": "Review misconceptions from AME bank",
        "question": "Ask revision questions from official items",
        "oral": "Conduct oral revision via VMLE",
        "memory_aid": "Generate memory aids from verified key ideas only",
        "summarize": "Summarize verified lesson content",
    }
    action = action if action in actions else "explain"

    tutor_out: dict[str, Any] = {}
    try:
        from engines.learning_experience_platform.tutor import tutor_panel
        from engines.learning_experience_platform.contextual_chat import build_chat_context, chat_turn

        tutor_out = tutor_panel({**context, "mode": "revision", "action": action})
        if message:
            ctx = build_chat_context(
                lesson=context.get("lesson"),
                paragraph=str(context.get("paragraph") or ""),
                competency=str(context.get("competency") or ""),
                learner_id=learner_id,
                engine_outputs=context.get("engine_outputs"),
            )
            tutor_out["chat"] = chat_turn(message, ctx)
    except Exception as exc:  # noqa: BLE001
        tutor_out = {"ok": False, "error": str(exc), "fallback": actions[action]}

    oral = {}
    if action == "oral":
        try:
            from engines.learning_experience_platform.voice import voice_controls

            oral = voice_controls()
        except Exception:  # noqa: BLE001
            oral = {"vmle": True}

    analytics.track("revision", learner_id=learner_id, payload={"ai_action": action})
    return {
        "ok": True,
        "action": action,
        "description": actions[action],
        "tutor": tutor_out,
        "oral": oral,
        "policy": {"never_generate_unsupported_curriculum": True, "source": "ATIE"},
    }
