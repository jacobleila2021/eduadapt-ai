"""Lesson writing audit — remove mechanical/AI tone; require teachable prose."""

from __future__ import annotations

import re
from typing import Any, Mapping

from peec.constants import MECHANICAL_PHRASES


def _blob(adaptation: Mapping[str, Any]) -> str:
    parts = [str(adaptation.get("big_idea") or "")]
    for s in adaptation.get("sections") or []:
        if isinstance(s, dict):
            parts.append(str(s.get("body") or ""))
    return "\n".join(parts)


def audit_lesson_writing(adaptations: Mapping[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    page_notes: dict[str, list[str]] = {}

    for key, value in adaptations.items():
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key in {"worksheet"}:
            continue
        blob = _blob(value)
        low = blob.lower()
        notes: list[str] = []

        for phrase in MECHANICAL_PHRASES:
            if phrase in low:
                notes.append(f"Mechanical/AI phrasing: “{phrase}”.")
                issues.append({"page": key, "issue": f"mechanical:{phrase}"})

        # Repeated sentence openings
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", blob) if s.strip()]
        openings = [s.split()[:2] for s in sentences if len(s.split()) >= 2]
        opening_keys = [" ".join(o).lower() for o in openings]
        skip_openers = {"have you", "think of", "you can", "in real", "for example", "next keep"}
        for opener in set(opening_keys):
            if opener in skip_openers:
                continue
            if opening_keys.count(opener) >= 4:
                notes.append(f"Repeated phrasing starts with “{opener}”.")
                issues.append({"page": key, "issue": "repeated_opening"})

        # Thin sections / filler
        thin = sum(
            1
            for s in (value.get("sections") or [])
            if isinstance(s, dict) and len(str(s.get("body") or "").split()) < 10
        )
        if thin >= 3 and key not in {"vocabulary"}:
            notes.append("Several sections are too thin to teach with confidence.")
            issues.append({"page": key, "issue": "thin_sections"})

        # Curiosity / real-world signals for mainstream
        if key == "standard":
            if not any(w in low for w in ("example", "like", "imagine", "have you", "notice at", "in real")):
                notes.append("Needs stronger curiosity or real-world relevance.")
                issues.append({"page": key, "issue": "low_engagement"})
            if "next" not in low and "then" not in low:
                notes.append("Transitions feel abrupt — add natural bridges.")
                issues.append({"page": key, "issue": "abrupt_transitions"})

        if notes:
            page_notes[key] = notes

    ok = len(issues) == 0
    return {
        "schema": "alora.peec.lesson_writing_audit.v1",
        "ok": ok,
        "issues": issues,
        "by_page": page_notes,
        "summary": "Writing feels handcrafted." if ok else "Writing still feels mechanical in places.",
    }
