"""Taxonomy helpers — Bloom / DOK / SOLO / Marzano / future skills."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.schemas import TAXONOMIES

BLOOM_LEVELS = ("remember", "understand", "apply", "analyze", "evaluate", "create")
DOK_LEVELS = ("1", "2", "3", "4")


def normalize_taxonomy(tags: dict[str, Any] | None = None) -> dict[str, Any]:
    tags = dict(tags or {})
    bloom = str(tags.get("blooms") or tags.get("bloom") or "understand").lower()
    if bloom not in BLOOM_LEVELS:
        bloom = "understand"
    dok = str(tags.get("dok") or "2")
    if dok not in DOK_LEVELS:
        dok = "2"
    return {
        "blooms": bloom,
        "dok": dok,
        "solo": tags.get("solo") or "",
        "marzano": tags.get("marzano") or "",
        "skills_21st": list(tags.get("skills_21st") or []),
        "future_skills": list(tags.get("future_skills") or []),
        "critical_thinking": bool(tags.get("critical_thinking")),
        "computational_thinking": bool(tags.get("computational_thinking")),
        "scientific_inquiry": bool(tags.get("scientific_inquiry")),
        "supported": list(TAXONOMIES),
    }
