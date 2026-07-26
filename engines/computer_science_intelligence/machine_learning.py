"""Machine learning education metadata — conceptual overlays only."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

ML_FOCI: tuple[dict[str, str], ...] = (
    {"id": "supervised_learning", "label": "Supervised learning"},
    {"id": "unsupervised_learning", "label": "Unsupervised learning"},
    {"id": "training_data", "label": "Training data"},
    {"id": "features", "label": "Features"},
    {"id": "overfitting", "label": "Overfitting"},
    {"id": "evaluation", "label": "Model evaluation"},
)


def machine_learning_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=ML_FOCI,
        text=text,
        domains=domains,
        domain_keys={"machine_learning"},
        provenance="computer_science_intelligence.machine_learning",
        extra={
            "conceptual_only": True,
            "invents_trained_models": False,
        },
    )
