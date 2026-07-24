"""Persona-intentional authorship — each adaptation must feel written for that learner."""

from __future__ import annotations

from typing import Any, Mapping

from epp.constants import PERSONA_INTENTS


def _ensure_section(
    sections: list[dict[str, Any]],
    *,
    role: str,
    title: str,
    body: str,
    box: str = "",
) -> list[dict[str, Any]]:
    roles = {str(s.get("role") or "") for s in sections}
    if role in roles:
        return sections
    sections.append(
        {
            "title": title,
            "role": role,
            "box": box or role,
            "body": body,
        }
    )
    return sections


def apply_persona_intent(
    adaptation: dict[str, Any],
    *,
    version_id: str,
    topic: str,
) -> dict[str, Any]:
    """Light structural cues so each version feels intentionally authored."""
    if version_id in {"vocabulary", "worksheet"}:
        return adaptation

    page = dict(adaptation)
    sections = [dict(s) for s in (page.get("sections") or []) if isinstance(s, dict)]
    intent = PERSONA_INTENTS.get(version_id, PERSONA_INTENTS["standard"])
    page["persona_intent"] = intent  # renderer may hide; used for QA transparency

    if version_id == "adhd":
        sections = _ensure_section(
            sections,
            role="hook",
            title="Mission Goal",
            body=f"Today’s mission: explain one clear idea from {topic} in two short bursts.",
            box="hook",
        )
        sections = _ensure_section(
            sections,
            role="reflection",
            title="Movement Break",
            body="Stand, stretch for thirty seconds, then tick what you finished.",
            box="break",
        )
    elif version_id == "autism":
        sections = _ensure_section(
            sections,
            role="hook",
            title="What Happens Today",
            body=f"First we define the idea. Next we see one example. Then we check our understanding of {topic}.",
            box="routine",
        )
    elif version_id == "ell":
        sections = _ensure_section(
            sections,
            role="vocabulary_support",
            title="Say It Aloud",
            body=f"Say the key word from {topic} three times. Then use it in one short sentence.",
            box="speak",
        )
    elif version_id == "visual":
        sections = _ensure_section(
            sections,
            role="visual",
            title="See · Label · Trace",
            body=f"Look at the {topic} diagram. Label one part. Trace the path with your finger, then explain it.",
            box="visual",
        )
    elif version_id == "auditory":
        sections = _ensure_section(
            sections,
            role="listen",
            title="Listen and Retell",
            body=f"Read the main idea of {topic} aloud. Cover the page. Retell it to a partner in your own words.",
            box="listen",
        )
    elif version_id in {"ld", "dyslexia"}:
        sections = _ensure_section(
            sections,
            role="hook",
            title="Step by Step",
            body=f"Read one short line about {topic}. Pause. Then write one word that captures the meaning.",
            box="steps",
        )
    elif version_id == "parent":
        sections = _ensure_section(
            sections,
            role="home",
            title="At Home Tonight",
            body=f"Ask: “What is one idea you learned about {topic}?” Praise a clear answer in their own words.",
            box="home",
        )
    elif version_id == "teacher":
        sections = _ensure_section(
            sections,
            role="exit_ticket",
            title="Exit Ticket",
            body=f"Before leaving: explain one idea from {topic} in two sentences and give one real-life example.",
            box="assess",
        )
    elif version_id == "standard":
        # Engagement without scaffold language
        blob = " ".join(str(s.get("body") or "") for s in sections).lower()
        if "have you ever" not in blob and "you can" not in blob:
            sections = _ensure_section(
                sections,
                role="hook",
                title="Start Here",
                body=(
                    f"Have you ever noticed {topic.lower()} showing up in everyday life? "
                    "Hold that moment in mind — you will use it to unlock the lesson."
                ),
                box="hook",
            )

    page["sections"] = sections
    return page


def persona_notes(adaptations: Mapping[str, Any]) -> list[dict[str, str]]:
    notes: list[dict[str, str]] = []
    for key, value in adaptations.items():
        if str(key).startswith("_") or not isinstance(value, dict):
            continue
        if key in PERSONA_INTENTS and value.get("persona_intent"):
            notes.append({"adaptation": key, "intent": str(value.get("persona_intent"))})
    return notes
