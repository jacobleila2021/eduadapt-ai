"""Curriculum normalization — map board-specific terms to common hierarchy."""

from __future__ import annotations

from typing import Any

# Internal hierarchy (curriculum-agnostic)
# Chapter → Topic → Concept → Learning Outcome → Skill → Assessment

BOARD_ALIASES = {
    "cbse": "CBSE",
    "ncert": "NCERT",
    "icse": "ICSE",
    "isc": "ISC",
    "cambridge": "Cambridge",
    "igcse": "Cambridge",
    "ib": "IB",
    "nios": "NIOS",
    "kerala": "Kerala SCERT",
    "scert": "State SCERT",
    "state": "State Board",
    "university": "University",
    "corporate": "Corporate",
}

TERMINOLOGY_MAP = {
    # original_term → internal_role
    "chapter": "chapter",
    "unit": "unit",
    "module": "unit",
    "topic": "topic",
    "lesson": "topic",
    "concept": "concept",
    "learning objective": "learning_outcome",
    "learning outcome": "learning_outcome",
    "lo": "learning_outcome",
    "competency": "skill",
    "skill": "skill",
    "assessment": "assessment",
    "exercise": "assessment",
}


def normalize_board(raw: str) -> str:
    key = (raw or "").strip().lower()
    return BOARD_ALIASES.get(key, raw.strip() if raw else "Unknown")


def normalize_hierarchy(
    *,
    chapter: int = 0,
    chapter_title: str = "",
    topic: str = "",
    concepts: list[str] | None = None,
    learning_objectives: list[str] | None = None,
    original_labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Produce common internal structure while preserving original terminology.
    """
    return {
        "internal": {
            "chapter": chapter,
            "topic": topic or chapter_title,
            "concepts": concepts or [],
            "learning_outcomes": learning_objectives or [],
            "skills": [],
            "assessment": [],
        },
        "original_labels": original_labels or {},
        "preserves_source_terminology": True,
    }
