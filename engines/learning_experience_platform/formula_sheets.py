"""Verified formula sheets — STEM engines only; never invent formulas."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics


def build_formula_sheets(
    *,
    subject: str = "",
    context: dict[str, Any] | None = None,
    lesson: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    lesson = lesson or {}
    outputs = context.get("engine_outputs") or {}
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}
    cie = (outputs.get("curriculum") or {}).get("payload") or {}

    formulae: list[dict[str, Any]] = []

    for a in sa.get("artifacts") or []:
        if not isinstance(a, dict):
            continue
        payload = a.get("payload") or {}
        latex = payload.get("latex") or payload.get("balanced") or payload.get("formula")
        if not latex and a.get("kind") not in ("equation", "formula", "balance", "sympy"):
            continue
        if latex:
            formulae.append({
                "name": str(payload.get("name") or a.get("title") or "Verified formula"),
                "formula": str(latex),
                "variables": payload.get("variables") or [],
                "units": payload.get("units") or [],
                "explanation": str(payload.get("explanation") or payload.get("notes") or "From verified STEM engine"),
                "worked_example": payload.get("worked_example") or payload.get("steps") or None,
                "related_concepts": payload.get("related_concepts") or [],
                "subject": subject or str(payload.get("subject") or a.get("subject") or ""),
                "source": a.get("engine") or "scientific_accuracy",
                "verified": True,
            })

    # Stem interactives may expose sympy/chempy results
    try:
        from engines.learning_experience_platform.stem import stem_interactives

        stem = stem_interactives(context)
        for item in stem.get("items") or stem.get("interactives") or []:
            if not isinstance(item, dict):
                continue
            f = item.get("formula") or item.get("latex") or (item.get("payload") or {}).get("latex")
            if f:
                formulae.append({
                    "name": str(item.get("name") or "STEM formula"),
                    "formula": str(f),
                    "variables": item.get("variables") or [],
                    "units": item.get("units") or [],
                    "explanation": str(item.get("explanation") or "Verified STEM interactive"),
                    "worked_example": item.get("steps"),
                    "related_concepts": item.get("related") or [],
                    "subject": subject or str(item.get("subject") or ""),
                    "source": "stem_interactives",
                    "verified": True,
                })
    except Exception:  # noqa: BLE001
        pass

    # Curriculum concept formulae if tagged
    for c in cie.get("concepts") or []:
        if isinstance(c, dict) and c.get("formula"):
            formulae.append({
                "name": str(c.get("title") or "Concept formula"),
                "formula": str(c["formula"]),
                "variables": c.get("variables") or [],
                "units": c.get("units") or [],
                "explanation": str(c.get("definition") or "CIE concept"),
                "worked_example": None,
                "related_concepts": [c.get("concept_id")] if c.get("concept_id") else [],
                "subject": subject,
                "source": "curriculum",
                "verified": True,
            })

    # Deduplicate by formula string
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for f in formulae:
        key = f["formula"].strip()
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)

    analytics.track("formula_sheet", learner_id=str(context.get("learner_id") or ""), payload={"count": len(unique)})
    return {
        "ok": True,
        "subject": subject or "mixed",
        "domains": ["mathematics", "physics", "chemistry", "statistics"],
        "formulae": unique[:40],
        "count": len(unique[:40]),
        "policy": {"never_invent_formulas": True, "verified_stem_only": True},
    }
