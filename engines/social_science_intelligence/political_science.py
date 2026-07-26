"""Political science intelligence metadata (school level)."""

from __future__ import annotations

from typing import Any


def political_science_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(d["domain"] == "political_science" for d in domains) or any(
        tok in (text or "").lower()
        for tok in ("governance", "public policy", "legislature", "judiciary", "federal")
    )
    return {
        "applicable": active,
        "foci": [
            "government_structures",
            "governance",
            "public_policy",
            "comparative_structures",
            "power_and_authority",
        ],
        "prompts": [
            "Compare how two institutions make decisions.",
            "Who is accountable, and through what mechanism?",
        ],
        "provenance": "social_science_intelligence.political_science",
    }
