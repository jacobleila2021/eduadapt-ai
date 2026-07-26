"""Capability matrix — aggregate declared pack capabilities for LXP/ATIE."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_framework.registry import get_registry


def capability_matrix(subject_key: str | None = None) -> dict[str, Any]:
    registry = get_registry()
    if subject_key:
        pack = registry.get(subject_key)
        return {
            "subject_key": pack.subject.key,
            "capabilities": [c.to_dict() for c in pack.capabilities()],
        }
    return {
        "subjects": {
            key: [c.to_dict() for c in registry.get(key).capabilities()]
            for key in registry.keys()
        }
    }


# LXP-facing capability catalogue (framework describes; does not implement widgets)
LXP_HOOK_CATALOGUE: tuple[dict[str, str], ...] = (
    {"hook_id": "interactive_diagrams", "description": "Subject may request interactive diagrams"},
    {"hook_id": "formula_viewers", "description": "Symbolic / formula viewer panels"},
    {"hook_id": "concept_maps", "description": "Concept map visualisations"},
    {"hook_id": "simulations", "description": "Simulation launch hints"},
    {"hook_id": "subject_toolbars", "description": "Subject-specific toolbar actions"},
    {"hook_id": "revision_widgets", "description": "Revision / spaced practice widgets"},
)


def lxp_hook_catalogue() -> list[dict[str, str]]:
    return [dict(row) for row in LXP_HOOK_CATALOGUE]
