"""Formula repository — verified formulae with LaTeX & engine hints."""

from __future__ import annotations

from typing import Any


def normalize_formula(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "formula_id": raw.get("formula_id") or raw.get("id") or "",
        "domain": raw.get("domain") or "general",  # math|physics|chemistry|biology|statistics|engineering
        "latex": raw.get("latex") or raw.get("expression") or "",
        "variables": list(raw.get("variables") or []),
        "units": list(raw.get("units") or []),
        "verification_engine": raw.get("verification_engine") or "sympy",
        "examples": list(raw.get("examples") or []),
        "topic_ids": list(raw.get("topic_ids") or []),
        "policy": "deterministic_verification_preferred",
    }


def list_formulae(package: dict[str, Any], *, domain: str = "") -> list[dict[str, Any]]:
    rows = [normalize_formula(f) for f in (package.get("formulae") or [])]
    if domain:
        rows = [r for r in rows if r.get("domain") == domain]
    return rows
