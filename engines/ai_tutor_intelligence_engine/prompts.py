"""Prompt orchestration notes — for LLM presentation layer (facts stay locked)."""

from __future__ import annotations

from typing import Any

SYSTEM_GUARDRAILS = """
You are Alora AI Tutor. You MUST:
1) Use only verified evidence provided in GROUNDING (CIE/KIE/STEM/RAG/AME).
2) Never invent curriculum facts, equations, official answers, or diagrams.
3) Prefer Socratic questions and graduated hints over direct answers.
4) Adapt language/pacing for accessibility — do not change academic standards.
5) If GROUNDING is insufficient, refuse and suggest lesson review or teacher help.
"""


def build_presentation_prompt(
    *,
    learner_message: str,
    grounding: dict[str, Any],
    mode: str,
    personalization: dict[str, Any],
) -> dict[str, Any]:
    """
    Optional prompt pack for an LLM *presentation* layer.
    Deterministic ATIE already produced content; LLM may only rephrase tone.
    """
    return {
        "system": SYSTEM_GUARDRAILS,
        "mode": mode,
        "personalization": personalization,
        "grounding": grounding,
        "learner_message": learner_message,
        "instruction": "Rephrase the tutor CONTENT for tone only. Do not add new facts.",
        "policy": "llm_presentation_optional_facts_locked",
    }
