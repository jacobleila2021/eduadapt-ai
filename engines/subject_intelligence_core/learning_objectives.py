"""Learning objective helpers."""

from __future__ import annotations

from typing import Any, Mapping

from engines.subject_intelligence_core.utilities import learning_structure_dict


def list_learning_objectives(uli: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for obj in learning_structure_dict(uli).get("learning_objectives") or []:
        if isinstance(obj, Mapping):
            out.append(
                {
                    "objective": obj.get("objective"),
                    "source_refs": obj.get("source_refs") or [],
                    "bloom_hint": None,
                    "dok_hint": None,
                }
            )
        else:
            out.append({"objective": str(obj), "source_refs": [], "bloom_hint": None, "dok_hint": None})
    return out


def objective_metadata(
    objectives: list[dict[str, Any]],
    *,
    provenance: str,
) -> dict[str, Any]:
    return {
        "objectives": objectives,
        "count": len(objectives),
        "owner": "ULI/CIE",
        "provenance": provenance,
    }
