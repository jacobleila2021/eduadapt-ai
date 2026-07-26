"""Source analysis scaffolds — primary/secondary evaluation."""

from __future__ import annotations

from typing import Any


def source_analysis_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    applicable = any(d["domain"] == "history" for d in domains) or any(
        tok in blob for tok in ("primary source", "secondary source", "evidence", "document", "inscription")
    )
    return {
        "applicable": applicable,
        "framework": ["origin", "purpose", "content", "value", "limitations"],
        "prompts": [
            "Who created this source, when, and for what audience?",
            "What does it claim, and what evidence supports or challenges it?",
            "How would you corroborate it with another lesson source?",
        ],
        "annotation_owner": "LXP/ATIE",
        "provenance": "social_science_intelligence.source_analysis",
    }
