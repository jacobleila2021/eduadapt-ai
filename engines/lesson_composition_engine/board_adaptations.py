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
    """Author one pedagogically unique adaptation from the Intelligence Board."""
    from engines.lesson_composition_engine.publisher_author import compose_publisher_adaptation

    return compose_publisher_adaptation(
        board,
        version_id,
        flowchart_svg=flowchart_svg,
        concept_map_svg=concept_map_svg,
    )
