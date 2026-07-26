"""Artificial intelligence education metadata — conceptual; does not replace AI engines."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

AI_FOCI: tuple[dict[str, str], ...] = (
    {"id": "ai_concepts", "label": "AI concepts"},
    {"id": "machine_learning_overview", "label": "Machine learning"},
    {"id": "neural_networks_conceptual", "label": "Neural networks (conceptual)"},
    {"id": "ethical_ai", "label": "Ethical AI"},
    {"id": "prompt_engineering", "label": "Prompt engineering"},
    {"id": "data_bias", "label": "Data bias"},
    {"id": "responsible_ai", "label": "Responsible AI"},
)


def artificial_intelligence_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=AI_FOCI,
        text=text,
        domains=domains,
        domain_keys={"artificial_intelligence", "machine_learning"},
        provenance="computer_science_intelligence.artificial_intelligence",
        default_count=7,
        extra={
            "conceptual_only": True,
            "replaces_ai_computation_engines": False,
            "ethics_first": True,
        },
    )
