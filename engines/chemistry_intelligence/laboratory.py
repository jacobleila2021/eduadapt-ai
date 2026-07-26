"""Laboratory metadata scaffolds — source-bound; never invent unsafe procedures."""

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


def _looks_lab(text: str) -> bool:
    blob = (text or "").lower()
    return any(
        m in blob
        for m in (
            "laboratory",
            "apparatus",
            "titration",
            "experiment",
            "bunsen",
            "pipette",
            "burette",
            "hazard",
            "safety",
            "procedure",
        )
    )


def build_laboratory_scaffolds(uli: Any, *, limit: int = 3) -> list[dict[str, Any]]:
    text = _source_text(uli)
    if not _looks_lab(text):
        return []

    aim = None
    m = re.search(r"(?:aim|objective)\s*[:\-]\s*(.+)", text, re.I)
    if m:
        aim = m.group(1).strip()[:300]

    return [
        {
            "lab_id": "cip.lab.1",
            "aim": aim,
            "aim_prompt": "State the investigative aim from the verified lesson.",
            "equipment": [],
            "equipment_prompt": "List apparatus named in the source only.",
            "experimental_setup_prompt": "Describe the setup exactly as specified in the lesson.",
            "variables": {
                "independent": None,
                "dependent": None,
                "controlled": [],
                "prompt": "Identify IV, DV, and controlled variables from the lesson.",
            },
            "observation_table_hint": {
                "columns": ["trial", "observation", "measurement", "notes"],
            },
            "safety_precautions": [
                "Follow all laboratory safety rules stated in the source.",
                "Wear appropriate PPE as required by the lesson / school policy.",
            ],
            "hazard_warnings": [
                "Treat unnamed reagents as potentially hazardous until identified in the source.",
            ],
            "chemical_handling": "Handle chemicals only as directed in the verified procedure.",
            "waste_disposal": "Dispose of waste only via methods named in the lesson or school protocol.",
            "conclusion_prompt": "Link observations to the lesson concept using CER.",
            "frameworks": ["inquiry", "poe", "cer", "experimental_investigation"],
            "provenance": "chemistry_intelligence.laboratory",
            "source_bound": True,
        }
    ][:limit]


def laboratory_completeness_signals(scaffolds: list[dict[str, Any]]) -> dict[str, Any]:
    if not scaffolds:
        return {"applicable": False, "completeness": "n/a", "safety_metadata": "n/a"}
    sc = scaffolds[0]
    return {
        "applicable": True,
        "scaffolds": len(scaffolds),
        "aim_from_source": bool(sc.get("aim")),
        "safety_metadata": "present" if sc.get("safety_precautions") else "missing",
        "hazard_metadata": "present" if sc.get("hazard_warnings") else "missing",
        "completeness": "partial" if sc.get("aim") else "template_only",
        "provenance": "chemistry_intelligence.laboratory",
    }
