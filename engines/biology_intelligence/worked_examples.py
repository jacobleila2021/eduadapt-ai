"""Worked-example scaffolds for biology — exam-safe; no invented answers."""

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
        for term in stem.get("biological_terminology") or []:
            if isinstance(term, Mapping):
                claims.append({"raw": str(term.get("term") or term.get("raw") or ""), "kind": "bio_term"})
    except Exception:  # noqa: BLE001
        claims = []

    if not claims:
        try:
            for c in list(uli.claim_ledger)[:limit]:
                if isinstance(c, Mapping):
                    text = str(c.get("text") or "")
                    if any(
                        tok in text.lower()
                        for tok in ("cell", "gene", "photosynthesis", "ecosystem", "organ", "dna")
                    ):
                        claims.append(c)
        except Exception:  # noqa: BLE001
            pass

    for i, claim in enumerate(claims[:limit]):
        raw = str(claim.get("raw") or claim.get("text") or "")[:300]
        if not raw.strip():
            continue
        scaffolds.append(
            {
                "example_id": f"bip.we.{i+1}",
                "goal": "Explain the biological system or process using lesson evidence.",
                "given": raw,
                "claim_kind": str(claim.get("kind") or "source_claim"),
                "steps": [
                    {"step": 1, "prompt": "Identify the level of organisation (cell → tissue → organ → system → ecosystem).", "reveal": False},
                    {"step": 2, "prompt": "State the structure–function relationship from the lesson.", "reveal": False},
                    {"step": 3, "prompt": "Trace cause → effect in the process pathway.", "reveal": False},
                    {"step": 4, "prompt": "Use a diagram or concept map to organise the relationships.", "reveal": False},
                    {"step": 5, "prompt": "Check the explanation against lesson vocabulary and evidence (CER).", "reveal": False},
                ],
                "scientific_justification_prompt": "Cite lesson definitions, labelled structures, and observed evidence.",
                "common_mistakes": [
                    "Confusing related processes (e.g. respiration vs breathing)",
                    "Skipping organisational levels (cell vs tissue)",
                    "Treating food chains as complete ecosystems",
                ],
                "extension_challenge": "Predict what changes if one factor in the system shifts (POE).",
                "exam_mode": exam_mode,
                "final_verification": None
                if exam_mode
                else "Re-check terminology and diagram labels against the verified source.",
                "provenance": "biology_intelligence.worked_examples",
                "source_refs": claim.get("source_block_ids") or claim.get("source_refs") or [],
            }
        )
    return scaffolds
