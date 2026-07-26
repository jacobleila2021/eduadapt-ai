"""Writing intelligence metadata — guidance only; never auto-generate assessment answers."""

from __future__ import annotations

from typing import Any

WRITING_MODES: tuple[dict[str, str], ...] = (
    {"id": "narrative", "label": "Narrative writing"},
    {"id": "descriptive", "label": "Descriptive writing"},
    {"id": "persuasive", "label": "Persuasive writing"},
    {"id": "informative", "label": "Informative writing"},
    {"id": "expository", "label": "Expository writing"},
    {"id": "creative", "label": "Creative writing"},
)


def writing_metadata(text: str, domains: list[dict[str, Any]], *, exam_mode: bool = False) -> dict[str, Any]:
    blob = (text or "").lower()
    modes = [m for m in WRITING_MODES if m["id"] in blob or m["label"].split()[0].lower() in blob]
    if not modes and any(d["domain"] == "writing" for d in domains):
        modes = [dict(m) for m in WRITING_MODES[:4]]
    return {
        "modes": modes,
        "organisation": [
            "Clarify purpose and audience",
            "Plan thesis / controlling idea",
            "Structure paragraphs with topic sentence + evidence + link",
            "Conclude by synthesising, not merely repeating",
        ],
        "craft_prompts": [
            "Where is your thesis or controlling idea?",
            "Which evidence from the lesson supports each claim?",
            "What will you revise for clarity and cohesion?",
        ],
        "editing_revision": True,
        "exam_mode": exam_mode,
        "generates_assessment_answers": False,
        "provenance": "english_language_intelligence.writing",
    }
