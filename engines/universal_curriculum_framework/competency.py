"""Competency extraction & progression levels from UCF topics."""

from __future__ import annotations

from typing import Any


def list_competencies(package: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for t in package.get("topics") or []:
        for c in t.get("competencies") or []:
            row = dict(c) if isinstance(c, dict) else {"competency_id": str(c), "description": str(c)}
            row["topic_id"] = t.get("topic_id")
            out.append(row)
    return out


def competency_progression(competencies: list[dict[str, Any]]) -> dict[str, Any]:
    levels = {"emerging": [], "developing": [], "proficient": [], "advanced": []}
    for c in competencies:
        lvl = (c.get("progression_level") or "developing").lower()
        if lvl not in levels:
            lvl = "developing"
        levels[lvl].append(c.get("competency_id"))
    return {"by_level": levels, "total": len(competencies)}
