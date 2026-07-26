"""Board-driven adaptation authorship — pedagogically unique experiences.

Phase Omega: never deep-copy mainstream and wrap. Each profile builds from the
Lesson Intelligence Board with its own sequence, load, examples, and checks.

Human-first recovery: publisher_author writes classroom-ready prose.
"""

from __future__ import annotations

from typing import Any, Mapping

# Profile metadata retained for lenses / diagnostics
PROFILE_AUTHORING: dict[str, dict[str, Any]] = {
    "standard": {"structure_key": "standard", "visual_first": False},
    "ld": {"structure_key": "ld", "use_bullets": True, "visual_first": True},
    "dyslexia": {"structure_key": "ld", "use_bullets": True, "visual_first": True},
    "adhd": {"structure_key": "adhd", "use_bullets": True, "visual_first": True, "movement": True},
    "autism": {"structure_key": "autism", "visual_first": True, "literal": True},
    "ell": {"structure_key": "ell", "glossary": True},
    "visual": {"structure_key": "visual", "visual_first": True},
    "auditory": {"structure_key": "auditory", "listen": True},
    "teacher": {"structure_key": "teacher", "teacher": True},
    "parent": {"structure_key": "parent", "home": True},
}


def compose_adaptation_from_board(
    board: Mapping[str, Any],
    version_id: str,
    *,
    flowchart_svg: str = "",
    concept_map_svg: str = "",
) -> dict[str, Any]:
    """Master Lesson Architecture (v3.3): every adaptation inherits the ONE
    canonical Mainstream lesson — presentation changes only. No adaptation
    may bypass the Canonical Lesson or compose its own curriculum."""
    from engines.lesson_composition_engine.canonical import (
        PRESENTATION_LENSES,
        augment_support_version,
        build_canonical_lesson,
        derive_presentation_adaptation,
        extract_essential_learning_core,
        freeze_canonical,
    )

    canonical = build_canonical_lesson(
        board, flowchart_svg=flowchart_svg, concept_map_svg=concept_map_svg
    )
    core = extract_essential_learning_core(canonical, board)
    frozen = freeze_canonical(canonical, core)
    if version_id == "standard":
        return frozen
    if version_id in {"teacher", "parent"}:
        return augment_support_version(frozen, core, board, version_id)
    if version_id in PRESENTATION_LENSES:
        return derive_presentation_adaptation(frozen, core, version_id)
    return frozen
