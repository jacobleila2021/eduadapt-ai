"""Taxonomy helpers — Bloom / DoK tags for expansion packages."""

from __future__ import annotations

from typing import Any

BLOOM_LEVELS = ("remember", "understand", "apply", "analyze", "evaluate", "create")
DOK_LEVELS = ("1", "2", "3", "4")


def normalize_taxonomy(tags: dict[str, Any] | None = None) -> dict[str, Any]:
    tags = tags or {}
    bloom = str(tags.get("blooms") or tags.get("bloom") or "understand").lower()
    if bloom not in BLOOM_LEVELS:
        bloom = "understand"
    dok = str(tags.get("dok") or "2")
    if dok not in DOK_LEVELS:
        dok = "2"
    return {"blooms": bloom, "dok": dok, "source": "cef_taxonomy"}
