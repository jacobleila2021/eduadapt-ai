"""Algorithms intelligence metadata — complexity annotations for LXP."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

ALGORITHM_FOCI: tuple[dict[str, str], ...] = (
    {"id": "sorting", "label": "Sorting"},
    {"id": "searching", "label": "Searching"},
    {"id": "complexity", "label": "Complexity"},
    {"id": "big_o", "label": "Big-O notation"},
    {"id": "algorithm_design", "label": "Algorithm design"},
    {"id": "correctness", "label": "Correctness reasoning"},
)


def algorithms_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=ALGORITHM_FOCI,
        text=text,
        domains=domains,
        domain_keys={"algorithms"},
        provenance="computer_science_intelligence.algorithms",
        extra={
            "complexity_annotations": True,
            "visual_walkthrough": True,
            "animation_controls": ["play", "pause", "step", "reset"],
            "invents_complexity_proofs": False,
        },
    )
