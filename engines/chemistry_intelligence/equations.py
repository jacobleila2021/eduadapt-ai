"""Chemical equation metadata inspection — never balances beyond Computation Layer."""

from __future__ import annotations

import re
from typing import Any, Mapping

_ARROW = re.compile(r"(?:→|->|⇒|=)")
_STATE = re.compile(r"\((?:s|l|g|aq)\)", re.I)
_REACTION_TYPES: tuple[tuple[str, str], ...] = (
    ("combustion", r"combust|burn|\+\s*o2"),
    ("neutralisation", r"neutrali|acid.*base|h\+|oh-"),
    ("precipitation", r"precipitat|insoluble"),
    ("decomposition", r"decompos"),
    ("displacement", r"displac|single.?replacement"),
    ("redox", r"redox|oxid|reduct|electron"),
    ("electrolysis", r"electrolys"),
)


def _stem(uli: Any) -> dict[str, Any]:
    try:
        return dict(uli.stem_structure())
    except Exception:  # noqa: BLE001
        return {}


def inspect_equations_and_notation(uli: Any) -> dict[str, Any]:
    stem = _stem(uli)
    equations = list(stem.get("chemical_equations") or [])
    artifacts = [a for a in (stem.get("artifacts") or []) if isinstance(a, Mapping)]
    chem_artifacts = [
        a
        for a in artifacts
        if str(a.get("engine_id") or "") in {"chemistry_balancer", "chempy", "mhchem", "rdkit"}
        or "chem" in str(a.get("task_kind") or "").lower()
    ]
    failed = [
        a
        for a in chem_artifacts
        if a.get("ok") is False or str(a.get("validation") or "").lower() in {"fail", "failed"}
    ]

    equation_meta: list[dict[str, Any]] = []
    for i, eq in enumerate(equations[:12]):
        raw = str(eq.get("raw") if isinstance(eq, Mapping) else eq)
        sides = _ARROW.split(raw, maxsplit=1)
        reactants = [p.strip() for p in sides[0].split("+")] if sides else []
        products = [p.strip() for p in sides[1].split("+")] if len(sides) > 1 else []
        rtypes = [name for name, pat in _REACTION_TYPES if re.search(pat, raw, re.I)]
        equation_meta.append(
            {
                "index": i,
                "raw": raw[:300],
                "reactants": reactants,
                "products": products,
                "state_symbols": _STATE.findall(raw),
                "has_arrow": bool(_ARROW.search(raw)),
                "reaction_type_hints": rtypes,
                "catalyst_prompt": "Note any catalyst named in the lesson (do not invent).",
                "conditions_prompt": "Record temperature/pressure/solvent only if stated in source.",
                "energy_change_prompt": "Mark exo/endothermic only if the lesson states it.",
                "ionic_half_equation_prompt": "Use ionic/half equations only when present in verified content.",
            }
        )

    balancing = "pass"
    if failed:
        balancing = "warn"
    elif chem_artifacts and all(a.get("ok") is not False for a in chem_artifacts):
        balancing = "pass"
    elif equations and not chem_artifacts:
        balancing = "n/a"  # present in text; Computation Layer not yet attached

    notation = "pass"
    if any(isinstance(eq, Mapping) and not eq.get("raw") for eq in equations):
        notation = "warn"

    return {
        "equation_count": len(equations),
        "equations": equation_meta,
        "chem_artifact_count": len(chem_artifacts),
        "artifact_failed_count": len(failed),
        "balancing_signal": balancing,
        "notation_consistency": notation,
        "formula_validation": "pass" if not failed else "warn",
        "provenance": "chemistry_intelligence.equations",
        "note": "CIP never invents balanced equations; balancer artifacts remain Computation Layer truth.",
    }
