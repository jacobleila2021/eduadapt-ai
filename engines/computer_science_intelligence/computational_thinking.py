"""Computational thinking intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

CT_FOCI: tuple[dict[str, str], ...] = (
    {"id": "decomposition", "label": "Decomposition"},
    {"id": "pattern_recognition", "label": "Pattern recognition"},
    {"id": "abstraction", "label": "Abstraction"},
    {"id": "algorithm_design", "label": "Algorithm design"},
    {"id": "logical_reasoning", "label": "Logical reasoning"},
    {"id": "problem_solving", "label": "Problem solving"},
    {"id": "computational_models", "label": "Computational models"},
)


def computational_thinking_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=CT_FOCI,
        text=text,
        domains=domains,
        domain_keys={"computational_thinking"},
        provenance="computer_science_intelligence.computational_thinking",
        extra={
            "reasoning_prompts": [
                "Break the problem into smaller parts.",
                "What pattern repeats across examples?",
                "What details can you hide behind an abstraction?",
            ],
        },
    )
