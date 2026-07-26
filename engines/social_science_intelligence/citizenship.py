"""Citizenship education metadata."""

from __future__ import annotations

from typing import Any


def citizenship_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(d["domain"] in {"civics", "sociology", "political_science"} for d in domains) or any(
        tok in (text or "").lower()
        for tok in ("citizenship", "civic", "rights", "responsibilities", "participation")
    )
    return {
        "applicable": active,
        "foci": [
            "rights_and_responsibilities",
            "participation",
            "respect_for_diversity",
            "rule_of_law",
            "global_citizenship",
        ],
        "discussion_prompts": [
            "How can a citizen participate beyond voting?",
            "Which responsibility balances this right?",
        ],
        "provenance": "social_science_intelligence.citizenship",
    }
