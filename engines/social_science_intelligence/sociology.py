"""Sociology intelligence metadata."""

from __future__ import annotations

from typing import Any


def sociology_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(d["domain"] == "sociology" for d in domains) or any(
        tok in (text or "").lower()
        for tok in ("community", "culture", "diversity", "social institution", "family", "global citizenship")
    )
    return {
        "applicable": active,
        "foci": [
            "communities",
            "culture",
            "diversity",
            "social_institutions",
            "family",
            "global_citizenship",
        ],
        "prompts": [
            "Which social institutions shape this community practice?",
            "How does diversity appear in roles, norms, or values in the lesson?",
        ],
        "provenance": "social_science_intelligence.sociology",
    }
