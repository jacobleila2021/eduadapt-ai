"""Normalize raw packages into canonical CMIF → UCF-ready shape."""

from __future__ import annotations

from typing import Any

from engines.curriculum_expansion_framework.taxonomy import normalize_taxonomy
from engines.curriculum_migration_framework.schemas import SUPPORTED_BOARDS


def normalize_package(raw: dict[str, Any], *, board: str = "") -> dict[str, Any]:
    out = dict(raw)
    b = (board or str(out.get("board") or "cbse")).strip().lower().replace(" ", "_")
    aliases = {"scert": "kerala_scert", "kerala": "kerala_scert", "igcse": "cambridge", "state": "state_board"}
    b = aliases.get(b, b)
    out["board"] = b
    out["subject"] = str(out.get("subject") or "").strip() or "General"
    out["grade"] = str(out.get("grade") or out.get("year") or "").strip() or "0"
    langs = out.get("languages")
    if isinstance(langs, list) and langs:
        out["language"] = str(out.get("language") or langs[0])
    else:
        out["language"] = str(out.get("language") or "en")
    tax = normalize_taxonomy({"blooms": out.get("blooms") or out.get("bloom"), "dok": out.get("dok")})
    out["blooms"] = tax["blooms"]
    out["dok"] = tax["dok"]

    if out.get("concepts") and not out.get("topics"):
        out["topics"] = out["concepts"]
    topics = []
    for i, t in enumerate(out.get("topics") or []):
        if isinstance(t, str):
            topics.append({"id": f"{b}.t{i}", "title": t, "definition": f"Understand {t}"})
        elif isinstance(t, dict):
            topics.append(t)
    out["topics"] = topics
    out.setdefault("accessibility", {"alt_text_required": True})
    out.setdefault("units", [])
    out.setdefault("chapters", [])
    out.setdefault("glossary", out.get("vocabulary") or [])
    out.setdefault("formulae", out.get("formulas") or out.get("equations") or [])
    out.setdefault("figures", out.get("diagrams") or [])
    out.setdefault("official_questions", out.get("questions") or [])
    out["_board_supported"] = b in SUPPORTED_BOARDS or b in (
        "cambridge_primary", "cambridge_igcse", "ib_pyp", "ib_myp", "ib_dp", "ncert", "cbse"
    )
    return out
