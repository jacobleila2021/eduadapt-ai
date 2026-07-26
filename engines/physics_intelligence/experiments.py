"""Experiment metadata scaffolds — structure only; never invent lab procedures beyond source."""

from __future__ import annotations

import re
from typing import Any, Mapping


def _source_text(uli: Any) -> str:
    parts: list[str] = []
    try:
        env = uli.source_envelope
        if isinstance(env, Mapping):
            parts.append(str(env.get("normalized_text") or env.get("text") or ""))
        else:
            parts.append(str(getattr(env, "normalized_text", "") or getattr(env, "text", "") or ""))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


def _looks_experimental(text: str) -> bool:
    blob = (text or "").lower()
    markers = (
        "experiment",
        "apparatus",
        "procedure",
        "observe",
        "measurement",
        "lab",
        "aim:",
        "equipment",
        "independent variable",
        "dependent variable",
    )
    return any(m in blob for m in markers)


def build_experiment_scaffolds(uli: Any, *, limit: int = 3) -> list[dict[str, Any]]:
    """
    Provide structured experiment *slots* for LXP/AME.

    Fills aim/equipment only when clearly present in source text; otherwise
    leaves prompts for teachers/learners to complete from the verified lesson.
    """
    text = _source_text(uli)
    if not _looks_experimental(text) and "experiment" not in text.lower():
        return []

    aim = None
    m = re.search(r"(?:aim|objective)\s*[:\-]\s*(.+)", text, re.I)
    if m:
        aim = m.group(1).strip()[:300]

    scaffolds = [
        {
            "experiment_id": "pip.exp.1",
            "aim": aim,
            "aim_prompt": "State the investigative question from the lesson.",
            "equipment": [],
            "equipment_prompt": "List apparatus named in the source lesson only.",
            "variables": {
                "independent": None,
                "dependent": None,
                "controlled": [],
                "prompt": "Identify IV, DV, and controlled variables from the lesson design.",
            },
            "method_steps": [
                {"step": 1, "prompt": "Set up apparatus as described in the source."},
                {"step": 2, "prompt": "Record the planned measurement sequence."},
                {"step": 3, "prompt": "Repeat for reliability if the lesson requires it."},
            ],
            "observations_prompt": "Record qualitative observations without inventing data.",
            "data_table_hint": {"columns": ["trial", "independent", "dependent", "notes"]},
            "graph_hint": "Plot dependent vs independent using verified axes from the lesson.",
            "conclusion_prompt": "Link observations to the lesson concept using CER.",
            "safety_notes": [
                "Follow all school laboratory safety rules stated in the source.",
                "Do not improvise hazardous procedures beyond the verified lesson.",
            ],
            "frameworks": ["inquiry", "poe", "cer", "experimental_investigation"],
            "provenance": "physics_intelligence.experiments",
            "source_bound": True,
        }
    ]
    return scaffolds[:limit]


def experiment_completeness_signals(scaffolds: list[dict[str, Any]]) -> dict[str, Any]:
    if not scaffolds:
        return {"applicable": False, "completeness": "n/a"}
    sc = scaffolds[0]
    filled = sum(
        1
        for key in ("aim",)
        if sc.get(key)
    )
    return {
        "applicable": True,
        "scaffolds": len(scaffolds),
        "aim_from_source": bool(sc.get("aim")),
        "slots_ready": True,
        "completeness": "partial" if filled else "template_only",
        "provenance": "physics_intelligence.experiments",
    }
