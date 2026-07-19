"""Diagram repository — textbook figures + deterministic generators metadata."""

from __future__ import annotations

from typing import Any


def normalize_diagram(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "diagram_id": raw.get("diagram_id") or raw.get("id") or "",
        "title": raw.get("title") or "",
        "caption": raw.get("caption") or "",
        "alt_text": raw.get("alt_text") or raw.get("alt") or "",
        "formats": {
            "svg": raw.get("svg") or "",
            "png": raw.get("png") or raw.get("path") or "",
            "vector": raw.get("vector") or "",
        },
        "generators": {
            "geogebra": raw.get("geogebra"),
            "matplotlib": raw.get("matplotlib"),
            "schemdraw": raw.get("schemdraw"),
            "rdkit": raw.get("rdkit"),
        },
        "accessibility": raw.get("accessibility") or {},
        "source": raw.get("source") or "textbook_or_engine",
        "policy": "prefer_official_then_deterministic_engines_never_ai_invent",
    }


def list_diagrams(package: dict[str, Any]) -> list[dict[str, Any]]:
    return [normalize_diagram(d) for d in (package.get("diagrams") or [])]
