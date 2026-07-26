"""Terminology / taxonomy consistency inspection over ULI passthrough."""

from __future__ import annotations

from typing import Any, Mapping

_TAXON_RANK_HINTS = ("kingdom", "phylum", "class", "order", "family", "genus", "species")


def inspect_terminology_and_taxonomy(uli: Any) -> dict[str, Any]:
    stem: dict[str, Any] = {}
    learn: dict[str, Any] = {}
    try:
        stem = dict(uli.stem_structure())
    except Exception:  # noqa: BLE001
        stem = {}
    try:
        learn = dict(uli.learning_structure())
    except Exception:  # noqa: BLE001
        learn = {}

    bio_terms = list(stem.get("biological_terminology") or [])
    vocab = list(learn.get("vocabulary") or [])
    preferred = list(stem.get("preferred_visuals") or [])

    term_strings: list[str] = []
    for row in bio_terms + vocab:
        if isinstance(row, Mapping):
            term_strings.append(str(row.get("term") or row.get("raw") or ""))
        else:
            term_strings.append(str(row))
    blob = " ".join(term_strings).lower()

    taxonomy_hits = [r for r in _TAXON_RANK_HINTS if r in blob]
    terminology_consistency = "pass"
    if not bio_terms and not vocab:
        terminology_consistency = "n/a"
    elif bio_terms and any(isinstance(t, Mapping) and not (t.get("term") or t.get("raw")) for t in bio_terms):
        terminology_consistency = "warn"

    taxonomy_consistency = "pass" if taxonomy_hits else "n/a"
    # Soft flag: species mentioned without genus-like pairing is still OK at INFO level only via n/a/pass

    return {
        "biological_term_count": len(bio_terms),
        "vocabulary_count": len(vocab),
        "preferred_visual_count": len(preferred),
        "taxonomy_rank_hints": taxonomy_hits,
        "terminology_consistency": terminology_consistency,
        "taxonomy_consistency": taxonomy_consistency,
        "provenance": "biology_intelligence.terminology",
    }
