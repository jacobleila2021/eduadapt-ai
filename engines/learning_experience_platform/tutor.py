"""ATIE tutor panel for LXP — hints, examples, misconceptions, reflection."""

from __future__ import annotations

from typing import Any


def tutor_panel(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    actions = {}
    try:
        from engines.ai_tutor_intelligence_engine.service import (
            api_generate_hint,
            api_generate_explanation,
            api_retrieve_worked_example,
            api_reflection_prompts,
        )

        q = context.get("question") or context.get("paragraph") or "Help me understand this lesson."
        actions["hint"] = api_generate_hint(question=q, **{k: context[k] for k in context if k not in ("engine_outputs",)})
        actions["explanation"] = api_generate_explanation(question=q)
        actions["worked_example"] = api_retrieve_worked_example(question=q)
        actions["reflection"] = api_reflection_prompts(**context)
    except Exception:  # noqa: BLE001
        actions = {
            "error": {
                "schema_version": "3.0.0",
                "stage": "ai_tutor",
                "code": "ai_tutor.scoped_failure",
                "status": "partial",
                "message": "Tutor assistance is temporarily unavailable.",
                "reason": "The tutor service could not complete this request.",
                "recovery": "Continue with the source lesson and retry the tutor shortly.",
                "fallback_used": "source_lesson",
                "retryable": True,
            },
            "modes": [
                "ask",
                "hint",
                "worked_example",
                "misconception",
                "reflection",
                "socratic",
            ],
        }
    return {
        "ok": True,
        "modes": ["ask", "hint", "worked_example", "misconception_correction", "reflection", "socratic"],
        "actions": actions,
        "policy": "never_provide_unverified_answers",
        "teaching_source": "atie",
    }
