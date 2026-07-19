"""Unified curriculum model — extends KIE normalization."""

from __future__ import annotations

from typing import Any

from engines.knowledge_ingestion_engine.normalization import (
    BOARD_ALIASES,
    normalize_board,
    normalize_hierarchy,
)

# Extended programme / board aliases (curriculum-agnostic core)
PROGRAMME_ALIASES = {
    "pyp": "IB PYP",
    "myp": "IB MYP",
    "dp": "IB DP",
    "igcse": "Cambridge IGCSE",
    "as level": "Cambridge AS & A Level",
    "a level": "Cambridge AS & A Level",
    "lower secondary": "Cambridge Lower Secondary",
    "primary": "Cambridge Primary",
    "secondary": "Secondary",
}


def normalize_programme(raw: str) -> str:
    key = (raw or "").strip().lower()
    return PROGRAMME_ALIASES.get(key, raw.strip() if raw else "")


def supported_curricula() -> list[dict[str, str]]:
    """Catalogue of supported education systems (future-ready)."""
    return [
        {"id": "ncert", "name": "NCERT", "region": "India"},
        {"id": "cbse", "name": "CBSE", "region": "India"},
        {"id": "icse", "name": "ICSE", "region": "India"},
        {"id": "isc", "name": "ISC", "region": "India"},
        {"id": "cambridge_primary", "name": "Cambridge Primary", "region": "International"},
        {"id": "cambridge_lower_secondary", "name": "Cambridge Lower Secondary", "region": "International"},
        {"id": "cambridge_igcse", "name": "Cambridge IGCSE", "region": "International"},
        {"id": "cambridge_a_level", "name": "Cambridge AS & A Level", "region": "International"},
        {"id": "ib_pyp", "name": "IB PYP", "region": "International"},
        {"id": "ib_myp", "name": "IB MYP", "region": "International"},
        {"id": "ib_dp", "name": "IB DP", "region": "International"},
        {"id": "kerala_scert", "name": "Kerala SCERT", "region": "India"},
        {"id": "state_board", "name": "State Board", "region": "India"},
        {"id": "nios", "name": "NIOS", "region": "India"},
        {"id": "university", "name": "University", "region": "Higher Education"},
        {"id": "professional", "name": "Professional Certification", "region": "Future"},
    ]


def build_unified_path(
    *,
    board: str = "Unknown",
    programme: str = "",
    grade: str = "",
    subject: str = "",
    unit: str = "",
    chapter: int = 0,
    chapter_title: str = "",
    topic: str = "",
    concept: str = "",
    learning_objective: str = "",
    competency: str = "",
    original_labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Full internal path:
    Curriculum → Programme → Grade → Subject → Unit → Chapter → Topic →
    Concept → LO → Competency → Assessment → Resources → Accessibility → Adaptations
    """
    hierarchy = normalize_hierarchy(
        chapter=chapter,
        chapter_title=chapter_title,
        topic=topic or concept,
        concepts=[concept] if concept else [],
        learning_objectives=[learning_objective] if learning_objective else [],
        original_labels=original_labels,
    )
    return {
        "curriculum": normalize_board(board),
        "programme": normalize_programme(programme),
        "grade": str(grade),
        "subject": subject,
        "unit": unit,
        "chapter": chapter,
        "chapter_title": chapter_title,
        "topic": topic or chapter_title,
        "concept": concept,
        "learning_objective": learning_objective,
        "competency": competency,
        "assessment_outcome": "",
        "resources": [],
        "accessibility_supports": [],
        "adaptations": [],
        "hierarchy": hierarchy,
        "board_aliases_available": sorted(set(BOARD_ALIASES.values())),
    }
