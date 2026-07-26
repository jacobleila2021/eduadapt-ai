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
            "microscope",
            "specimen",
            "dissection",
            "slide",
            "investigation",
            "apparatus",
            "observe",
            "experiment",
            "staining",
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
            "lab_id": "bip.lab.1",
            "aim": aim,
            "aim_prompt": "State the investigative aim from the verified lesson.",
            "equipment": [],
            "equipment_prompt": "List apparatus / microscopy tools named in the source only.",
            "specimens_prompt": "Identify specimens only if named in the lesson.",
            "microscopy_prompt": "Record magnification / staining steps only as stated in the source.",
            "variables": {
                "independent": None,
                "dependent": None,
                "controlled": [],
                "prompt": "Identify IV, DV, and controlled variables from the lesson.",
            },
            "observation_sheet_hint": {
                "columns": ["trial", "observation", "drawing_or_photo_ref", "notes"],
            },
            "data_recording_prompt": "Record qualitative and quantitative data without inventing measurements.",
            "conclusion_prompt": "Link observations to the lesson concept using CER.",
            "safety_guidance": [
                "Follow all laboratory safety rules stated in the source.",
                "Handle specimens, stains, and sharp tools only as directed.",
                "Do not invent dissection or chemical procedures beyond the verified lesson.",
            ],
            "frameworks": ["inquiry", "poe", "cer", "scientific_investigation"],
            "provenance": "biology_intelligence.laboratory",
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
        "safety_metadata": "present" if sc.get("safety_guidance") else "missing",
        "completeness": "partial" if sc.get("aim") else "template_only",
        "provenance": "biology_intelligence.laboratory",
    }
