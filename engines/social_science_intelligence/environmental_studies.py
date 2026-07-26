"""Environmental studies intelligence metadata."""

from __future__ import annotations

from typing import Any


def environmental_studies_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(d["domain"] == "environmental_studies" for d in domains) or any(
        tok in (text or "").lower()
        for tok in ("environment", "conservation", "sustainability", "pollution", "human impact")
    )
    return {
        "applicable": active,
        "foci": [
            "environment",
            "conservation",
            "sustainability",
            "human_impact",
            "resource_use",
        ],
        "prompts": [
            "What human activity is affecting this system?",
            "Which conservation action is suggested by the lesson evidence?",
        ],
        "provenance": "social_science_intelligence.environmental_studies",
    }
