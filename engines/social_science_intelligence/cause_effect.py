"""Cause–effect reasoning metadata for social science."""

from __future__ import annotations

from typing import Any


def cause_effect_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    applicable = any(
        tok in blob for tok in ("cause", "effect", "because", "consequence", "led to", "resulted")
    ) or any(d["domain"] in {"history", "economics", "environmental_studies"} for d in domains)
    return {
        "applicable": applicable,
        "diagram_types": ["cause_effect_chain", "multi_causal_web", "short_vs_long_term"],
        "prompts": [
            "List immediate causes and underlying conditions.",
            "Separate intended outcomes from unintended consequences.",
        ],
        "renderer": "lxp",
        "provenance": "social_science_intelligence.cause_effect",
    }
