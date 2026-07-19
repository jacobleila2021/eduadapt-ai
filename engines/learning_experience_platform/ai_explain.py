"""AI Explain actions — ATIE-backed; never invent curriculum."""

from __future__ import annotations

from typing import Any


ACTIONS = ("explain", "simplify", "summarize", "example", "real_life", "vocabulary")


def paragraph_actions(paragraph: str, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    results = {}
    for action in ACTIONS:
        results[action] = _run_action(action, paragraph, context)
    return {
        "ok": True,
        "paragraph_excerpt": (paragraph or "")[:240],
        "actions": results,
        "teaching_source": "atie",
        "policy": "never_generate_unsupported_curriculum",
    }


def _run_action(action: str, paragraph: str, context: dict[str, Any]) -> dict[str, Any]:
    try:
        from engines.ai_tutor_intelligence_engine.service import api_generate_explanation, api_generate_hint

        kwargs = {
            **context,
            "question": f"{action}: {paragraph[:500]}",
            "lesson_excerpt": paragraph,
        }
        if action in ("explain", "simplify", "summarize", "example", "real_life"):
            out = api_generate_explanation(**kwargs)
        else:
            out = api_generate_hint(**kwargs)
        return {"ok": True, "action": action, "result": out, "grounded": True}
    except Exception as exc:  # noqa: BLE001
        # Safe fallback — surface paragraph only, no invented facts
        templates = {
            "summarize": "Re-read the key sentence and list 2–3 facts stated above.",
            "vocabulary": "Look up highlighted terms in the verified glossary.",
            "simplify": "Break the paragraph into shorter sentences using the same facts.",
            "example": "Ask the AI Tutor for a worked example grounded in this lesson.",
            "real_life": "Ask the AI Tutor how this idea appears in everyday life — using lesson facts only.",
            "explain": "Open AI Tutor with this paragraph selected for a grounded explanation.",
        }
        return {
            "ok": True,
            "action": action,
            "result": {"text": templates.get(action, ""), "fallback": True, "error": str(exc)},
            "grounded": False,
            "requires_atie": True,
        }
