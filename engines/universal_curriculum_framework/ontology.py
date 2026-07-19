"""Ontology helpers — taxonomy tags & concept typing over UCF topics."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.schemas import TAXONOMIES


def annotate_taxonomies(topic: dict[str, Any]) -> dict[str, Any]:
    tax = dict(topic.get("taxonomy") or {})
    tax.setdefault("blooms", "understand")
    tax.setdefault("dok", "2")
    topic = dict(topic)
    topic["taxonomy"] = tax
    topic["taxonomies_supported"] = list(TAXONOMIES)
    return topic


def ontology_summary(package: dict[str, Any]) -> dict[str, Any]:
    topics = package.get("topics") or []
    blooms = {}
    for t in topics:
        b = (t.get("taxonomy") or {}).get("blooms") or "unknown"
        blooms[b] = blooms.get(b, 0) + 1
    return {
        "topic_count": len(topics),
        "blooms_distribution": blooms,
        "taxonomies": list(TAXONOMIES),
        "source": "ucf",
    }
