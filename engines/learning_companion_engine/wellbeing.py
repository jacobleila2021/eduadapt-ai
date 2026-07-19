"""Emotional support — encourage & normalize challenge; never clinical advice."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.personality import apply_style
from engines.learning_companion_engine.schemas import CompanionMessage

_POLICY = (
    "Never provide mental health advice or clinical guidance. "
    "Encourage, normalize challenge, suggest study strategies, recommend breaks, "
    "and refer academic help to ATIE."
)


def support(
    *,
    situation: str,
    companion_id: str,
    style: str = "gentle_coach",
) -> dict[str, Any]:
    """
    situation: struggle|low_confidence|frustrated|skipped|return_after_break
    """
    templates = {
        "struggle": "Hard problems mean your brain is stretching. Pause, breathe, then try one smaller step — or ask the AI Tutor to walk through it with you.",
        "low_confidence": "Confidence grows from small wins. You've done hard things before — pick one tiny goal for the next five minutes.",
        "frustrated": "Frustration is a signal, not a stop sign. Take a short break, then return with one clear question for the Tutor.",
        "skipped": "Missed a session? No guilt — restarting counts. Let's choose a short, doable chunk.",
        "return_after_break": "Welcome back. Starting again today is brave and smart. We'll ease in gently.",
    }
    key = situation if situation in templates else "struggle"
    styled = apply_style(templates[key], style)
    msg = CompanionMessage(
        text=styled["text"],
        kind="wellbeing",
        companion_id=companion_id,
        evidence=[{"situation": key}],
        speakable=True,
        refer_to_atie=key in ("struggle", "frustrated", "low_confidence"),
    )
    return {
        "ok": True,
        "message": msg.to_dict(),
        "policy": _POLICY,
        "clinical_advice": False,
        "suggest_break": key in ("frustrated", "struggle"),
        "handoff_atie": msg.refer_to_atie,
    }
