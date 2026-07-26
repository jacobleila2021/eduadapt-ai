"""Worked-example scaffolds for physics problem-solving — exam-safe."""

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
        claims = [c for c in (stem.get("claims_found") or []) if isinstance(c, Mapping)]
        for expr in stem.get("scientific_calculations") or []:
            if isinstance(expr, Mapping):
                claims.append(expr)
            else:
                claims.append({"raw": str(expr), "kind": "scientific_calculation"})
    except Exception:  # noqa: BLE001
        claims = []

    if not claims:
        try:
            for c in list(uli.claim_ledger)[:limit]:
                if isinstance(c, Mapping):
                    text = str(c.get("text") or "")
                    if any(tok in text.lower() for tok in ("force", "energy", "velocity", "ohm", "newton", "=")):
                        claims.append(c)
        except Exception:  # noqa: BLE001
            pass

    for i, claim in enumerate(claims[:limit]):
        raw = str(claim.get("raw") or claim.get("text") or "")[:300]
        scaffolds.append(
            {
                "example_id": f"pip.we.{i+1}",
                "goal": "Model the physical situation and justify each quantitative step.",
                "given": raw,
                "claim_kind": str(claim.get("kind") or "source_claim"),
                "steps": [
                    {"step": 1, "prompt": "Sketch the situation and label known quantities with units.", "reveal": False},
                    {"step": 2, "prompt": "Identify the governing principle or formula from the lesson.", "reveal": False},
                    {"step": 3, "prompt": "Check units / dimensions before substituting values.", "reveal": False},
                    {"step": 4, "prompt": "Solve symbolically, then substitute; state assumptions.", "reveal": False},
                    {"step": 5, "prompt": "Interpret the result physically (direction, magnitude, limits).", "reveal": False},
                ],
                "scientific_justification_prompt": "Cite the lesson law/principle (e.g. Newton II, Ohm, energy conservation).",
                "common_mistakes": [
                    "Mixing mass and weight units",
                    "Omitting vector direction on force diagrams",
                    "Using the wrong form of a kinematics equation",
                ],
                "extension_challenge": "Change one variable and predict how the result shifts (POE).",
                "exam_mode": exam_mode,
                "final_verification": None
                if exam_mode
                else "Check units, limiting cases, and consistency with the free-body / circuit diagram.",
                "provenance": "physics_intelligence.worked_examples",
                "source_refs": claim.get("source_block_ids") or claim.get("source_refs") or [],
            }
        )
    return scaffolds
