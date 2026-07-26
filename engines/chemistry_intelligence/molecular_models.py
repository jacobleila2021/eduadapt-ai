"""Molecular / structural representation metadata (LXP/VMLE render)."""

from __future__ import annotations

import re
from typing import Any, Mapping

from engines.chemistry_intelligence.domains import detect_domains

_FORMULA = re.compile(r"\b(?:[A-Z][a-z]?\d*){1,8}(?:\([A-Z][a-z]?\d*\)\d*)?\b")

MOLECULAR_HOOKS: tuple[dict[str, str], ...] = (
    {"hook": "molecule", "label": "Molecule identity"},
    {"hook": "compound", "label": "Compound"},
    {"hook": "chemical_formula", "label": "Chemical formula"},
    {"hook": "structural_formula", "label": "Structural formula"},
    {"hook": "lewis_structure", "label": "Lewis / electron-dot structure"},
    {"hook": "electron_dot_diagram", "label": "Electron-dot diagram"},
    {"hook": "bond_angles", "label": "Bond angles"},
    {"hook": "hybridization", "label": "Hybridization"},
    {"hook": "functional_groups", "label": "Functional groups"},
    {"hook": "crystal_structure", "label": "Crystal structure"},
    {"hook": "molecular_viewer_3d", "label": "3D molecular viewer"},
)


def extract_formula_candidates(text: str, *, limit: int = 12) -> list[str]:
    # Filter common English false positives lightly
    skip = {"I", "A", "In", "As", "At", "He", "Be", "No", "If"}
    out: list[str] = []
    for m in _FORMULA.finditer(text or ""):
        tok = m.group(0)
        if tok in skip or len(tok) < 2:
            continue
        if tok not in out:
            out.append(tok)
        if len(out) >= limit:
            break
    return out


def build_molecular_metadata(text: str, domains: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    domains = domains if domains is not None else detect_domains(text)
    active = {d["domain"] for d in domains}
    hooks = []
    for h in MOLECULAR_HOOKS:
        relevant = True
        if h["hook"] in {"functional_groups"} and "organic" not in active and "organic" not in (text or "").lower():
            relevant = "functional" in (text or "").lower()
        if h["hook"] == "crystal_structure" and "crystal" not in (text or "").lower():
            relevant = False
        if relevant:
            hooks.append({**h, "renderer": "lxp_or_vmle"})
    formulas = extract_formula_candidates(text)
    return {
        "formula_candidates": formulas,
        "representation_hooks": hooks,
        "active_domains": sorted(active),
        "provenance": "chemistry_intelligence.molecular_models",
    }


def molecular_from_uli(uli: Any) -> dict[str, Any]:
    parts: list[str] = []
    try:
        env = uli.source_envelope
        if isinstance(env, Mapping):
            parts.append(str(env.get("normalized_text") or env.get("text") or ""))
    except Exception:  # noqa: BLE001
        pass
    try:
        stem = dict(uli.stem_structure())
        for eq in stem.get("chemical_equations") or []:
            if isinstance(eq, Mapping):
                parts.append(str(eq.get("raw") or ""))
            else:
                parts.append(str(eq))
    except Exception:  # noqa: BLE001
        pass
    text = "\n".join(p for p in parts if p)
    return build_molecular_metadata(text)
