"""Formula / unit consistency inspection over STEM passthrough — never invents physics."""

from __future__ import annotations

import re
from typing import Any, Mapping

# Common SI / derived unit tokens for lightweight consistency signals
_UNIT_TOKEN = re.compile(
    r"\b(?:m/s\^?2|m/s²|m/s|km/h|N|J|W|V|A|Ω|ohm|Hz|kg|g|°C|K|Pa|C)\b",
    re.I,
)

_FORMULA_HINTS = (
    ("f=ma", ("force", "mass", "acceleration")),
    ("v=u+at", ("velocity", "acceleration", "time")),
    ("v=ir", ("voltage", "current", "resistance")),
    ("e=mc", ("energy",)),
    ("p=mv", ("momentum", "mass", "velocity")),
    ("p=w/t", ("power", "work", "time")),
    ("p=iv", ("power", "current", "voltage")),
)


def _stem_payload(uli: Any) -> dict[str, Any]:
    try:
        return dict(uli.stem_structure())
    except Exception:  # noqa: BLE001
        return {}


def inspect_formula_and_units(uli: Any) -> dict[str, Any]:
    stem = _stem_payload(uli)
    claims = [c for c in (stem.get("claims_found") or []) if isinstance(c, Mapping)]
    calcs = list(stem.get("scientific_calculations") or [])
    artifacts = [a for a in (stem.get("artifacts") or []) if isinstance(a, Mapping)]

    phys_artifacts = [
        a
        for a in artifacts
        if str(a.get("engine_id") or "") in {"sympy_force", "physics_diagram", "sympy"}
        or "physics" in str(a.get("task_kind") or "").lower()
        or "force" in str(a.get("task_kind") or "").lower()
    ]
    failed = [
        a
        for a in phys_artifacts
        if a.get("ok") is False or str(a.get("validation") or "").lower() in {"fail", "failed"}
    ]

    unit_mentions: list[str] = []
    formula_hits: list[str] = []
    blob_parts: list[str] = []
    for c in claims[:20]:
        blob_parts.append(str(c.get("raw") or c.get("text") or ""))
    for calc in calcs[:20]:
        if isinstance(calc, Mapping):
            blob_parts.append(str(calc.get("raw") or calc.get("expression") or ""))
        else:
            blob_parts.append(str(calc))
    blob = " ".join(blob_parts)
    unit_mentions = sorted({m.group(0) for m in _UNIT_TOKEN.finditer(blob)})
    lower = blob.lower().replace(" ", "")
    for key, _concepts in _FORMULA_HINTS:
        if key.replace("=", "") in lower.replace("=", "") or key in lower:
            formula_hits.append(key)

    unit_consistency = "pass"
    if unit_mentions and ("kg" in [u.lower() for u in unit_mentions]) and any(
        "weight" in str(c.get("raw") or c.get("text") or "").lower() for c in claims
    ):
        # Soft pedagogical flag — mass unit near weight wording
        unit_consistency = "warn"

    formula_consistency = "pass" if not failed else "warn"
    if failed:
        formula_consistency = "warn"

    return {
        "physics_artifact_count": len(phys_artifacts),
        "artifact_failed_count": len(failed),
        "unit_mentions": unit_mentions[:20],
        "formula_hints_detected": formula_hits,
        "unit_consistency": unit_consistency if unit_mentions else "n/a",
        "formula_consistency": formula_consistency if (phys_artifacts or calcs or formula_hits) else "n/a",
        "provenance": "physics_intelligence.units_formulas",
    }
