"""Worked-example scaffolds for chemistry — exam-safe; no invented solutions."""

from __future__ import annotations

from typing import Any, Mapping


def build_worked_example_scaffolds(
    uli: Any,
    *,
    exam_mode: bool = False,
    limit: int = 5,
) -> list[dict[str, Any]]:
    scaffolds: list[dict[str, Any]] = []
    claims: list[Mapping[str, Any]] = []
    try:
        stem = dict(uli.stem_structure())
        for eq in stem.get("chemical_equations") or []:
            if isinstance(eq, Mapping):
                claims.append(eq)
            else:
                claims.append({"raw": str(eq), "kind": "chemical_equation"})
        claims.extend(c for c in (stem.get("claims_found") or []) if isinstance(c, Mapping))
    except Exception:  # noqa: BLE001
        claims = []

    if not claims:
        try:
            for c in list(uli.claim_ledger)[:limit]:
                if isinstance(c, Mapping):
                    text = str(c.get("text") or "")
                    if any(tok in text.lower() for tok in ("mole", "reaction", "balance", "acid", "→", "->")):
                        claims.append(c)
        except Exception:  # noqa: BLE001
            pass

    for i, claim in enumerate(claims[:limit]):
        raw = str(claim.get("raw") or claim.get("text") or "")[:300]
        scaffolds.append(
            {
                "example_id": f"cip.we.{i+1}",
                "goal": "Justify each chemical transformation using lesson principles.",
                "given": raw,
                "claim_kind": str(claim.get("kind") or "source_claim"),
                "steps": [
                    {"step": 1, "prompt": "List known formulae, states, and what is asked.", "reveal": False},
                    {"step": 2, "prompt": "Identify reaction type or mole relationship from the lesson.", "reveal": False},
                    {"step": 3, "prompt": "Check atom counts / conservation before accepting a balance.", "reveal": False},
                    {"step": 4, "prompt": "Complete stoichiometric links (n = m/M, c = n/V) if required.", "reveal": False},
                    {"step": 5, "prompt": "State assumptions and interpret the chemical meaning of the result.", "reveal": False},
                ],
                "scientific_justification_prompt": "Cite conservation of mass, mole ratios, or bonding rules from the lesson.",
                "common_mistakes": [
                    "Confusing mass with moles",
                    "Balancing by changing subscripts instead of coefficients",
                    "Equating strong with concentrated for acids",
                ],
                "extension_challenge": "Predict how changing one reactant amount affects limiting reagent (POE).",
                "exam_mode": exam_mode,
                "final_verification": None
                if exam_mode
                else "Confirm atom balance and units; cross-check with any Computation Layer balancer artifact.",
                "provenance": "chemistry_intelligence.worked_examples",
                "source_refs": claim.get("source_block_ids") or claim.get("source_refs") or [],
            }
        )
    return scaffolds
