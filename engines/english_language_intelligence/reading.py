"""Reading intelligence metadata — strategies only; ATIE/LXP present."""

from __future__ import annotations

from typing import Any

READING_CAPABILITIES: tuple[dict[str, str], ...] = (
    {"id": "fluency", "label": "Reading fluency"},
    {"id": "comprehension", "label": "Reading comprehension"},
    {"id": "guided_reading", "label": "Guided reading"},
    {"id": "close_reading", "label": "Close reading"},
    {"id": "inference", "label": "Inference"},
    {"id": "prediction", "label": "Prediction"},
    {"id": "sequencing", "label": "Sequencing"},
    {"id": "main_idea", "label": "Main idea"},
    {"id": "supporting_details", "label": "Supporting details"},
    {"id": "summarisation", "label": "Summarisation"},
    {"id": "authors_purpose", "label": "Author's purpose"},
    {"id": "tone", "label": "Tone"},
    {"id": "point_of_view", "label": "Point of view"},
    {"id": "critical_thinking", "label": "Critical thinking"},
    {"id": "reading_stamina", "label": "Reading stamina"},
)


def reading_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    active = []
    for cap in READING_CAPABILITIES:
        token = cap["id"].replace("_", " ")
        if token in blob or any(m in blob for m in (cap["label"].lower(),)):
            active.append(cap)
    if not active and any(d["domain"] == "reading" for d in domains):
        active = [dict(c) for c in READING_CAPABILITIES[:6]]
    return {
        "capabilities": active,
        "prompts": [
            "What is the main idea, and which details support it?",
            "What can you infer that is not stated directly?",
            "How would you summarise this section in two sentences?",
        ],
        "owner_presentation": "ATIE/LXP",
        "provenance": "english_language_intelligence.reading",
    }
