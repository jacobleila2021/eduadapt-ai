"""Glossary repository accessors within UCF packages."""

from __future__ import annotations

from typing import Any


def upsert_term(package: dict[str, Any], term: dict[str, Any]) -> dict[str, Any]:
    gloss = list(package.get("glossary") or [])
    tid = term.get("term_id") or f"gl_{term.get('term', '').lower().replace(' ', '_')}"
    term = {
        "term_id": tid,
        "term": term.get("term") or "",
        "definition": term.get("definition") or "",
        "grade_level": term.get("grade_level") or "",
        "pronunciation": term.get("pronunciation") or "",
        "language": term.get("language") or "en",
        "simplified_definition": term.get("simplified_definition") or "",
        "visual_definition": term.get("visual_definition") or "",
        "related_concepts": list(term.get("related_concepts") or []),
    }
    gloss = [g for g in gloss if g.get("term_id") != tid] + [term]
    package = dict(package)
    package["glossary"] = gloss
    return package


def find_term(package: dict[str, Any], query: str) -> list[dict[str, Any]]:
    q = (query or "").lower()
    return [g for g in (package.get("glossary") or []) if q in str(g.get("term") or "").lower() or q in str(g.get("definition") or "").lower()]
