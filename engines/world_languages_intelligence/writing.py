"""Writing intelligence metadata — never invents assessment answers."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

WRITING_FOCI: tuple[dict[str, str], ...] = (
    {"id": "sentence_formation", "label": "Sentence formation"},
    {"id": "paragraph_writing", "label": "Paragraph writing"},
    {"id": "essay_structure", "label": "Essay structure"},
    {"id": "grammar_guidance", "label": "Grammar guidance"},
    {"id": "cohesion", "label": "Cohesion"},
    {"id": "academic_writing", "label": "Academic writing"},
)


def writing_metadata(
    text: str,
    domains: list[dict[str, Any]],
    *,
    exam_mode: bool = False,
) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=WRITING_FOCI,
        text=text,
        domains=domains,
        domain_keys={"writing"},
        provenance="world_languages_intelligence.writing",
        extra={
            "scaffolds": ["outline", "sentence_frames", "cohesion_checklist"],
            "reveals_assessment_answers": False,
            "exam_mode": exam_mode,
        },
    )
