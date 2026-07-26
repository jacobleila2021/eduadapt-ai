"""Worked-example *guidance scaffolds* from ULI — never invent protected answers."""

from __future__ import annotations

from typing import Any, Mapping


def build_worked_example_scaffolds(
    uli: Any,
    *,
    exam_mode: bool = False,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Structure pedagogical scaffolds around source claims / STEM expressions.

    When exam_mode=True, omit final verification payloads that could leak answers.
    """
    scaffolds: list[dict[str, Any]] = []
    claims: list[Mapping[str, Any]] = []
    try:
        stem = dict(uli.stem_structure())
        claims = [c for c in (stem.get("claims_found") or []) if isinstance(c, Mapping)]
    except Exception:  # noqa: BLE001
        claims = []

    if not claims:
        try:
            for c in list(uli.claim_ledger)[:limit]:
                if isinstance(c, Mapping) and ("=" in str(c.get("text") or "") or "solve" in str(c.get("text") or "").lower()):
                    claims.append(c)
        except Exception:  # noqa: BLE001
            pass

    for i, claim in enumerate(claims[:limit]):
        raw = str(claim.get("raw") or claim.get("text") or "")[:300]
        kind = str(claim.get("kind") or "source_claim")
        scaffold = {
            "example_id": f"mip.we.{i+1}",
            "goal": "Understand and justify each transformation using lesson concepts.",
            "given": raw,
            "claim_kind": kind,
            "steps": [
                {"step": 1, "prompt": "Identify known quantities and the unknown.", "reveal": False},
                {"step": 2, "prompt": "State the property or rule that applies (from the lesson).", "reveal": False},
                {"step": 3, "prompt": "Perform one valid transformation; justify why it preserves equality/value.", "reveal": False},
                {"step": 4, "prompt": "Check the result against the original statement.", "reveal": False},
            ],
            "mathematical_justification_prompt": "Cite the lesson rule (e.g. inverse operations, congruence) for each step.",
            "common_mistakes": [
                "Applying an operation to only one side of an equation",
                "Sign errors when expanding brackets",
                "Skipping order of operations",
            ],
            "extension_challenge": "Create a related problem that uses the same property with different numbers.",
            "exam_mode": exam_mode,
            "final_verification": None if exam_mode else "Re-substitute or reverse the steps to confirm consistency with the source.",
            "provenance": "mathematics_intelligence.worked_examples",
            "source_refs": claim.get("source_block_ids") or claim.get("source_refs") or [],
        }
        scaffolds.append(scaffold)
    return scaffolds
