"""Question bank accessors — official items preferred; AI never replaces official."""

from __future__ import annotations

from typing import Any

QUESTION_KINDS = (
    "official_textbook",
    "exemplar",
    "previous_year",
    "competency",
    "hots",
    "project",
    "practical",
    "oral",
)


def normalize_question(raw: dict[str, Any]) -> dict[str, Any]:
    official = bool(raw.get("official") or raw.get("source") in ("official", "textbook", "exemplar", "pyq"))
    return {
        "question_id": raw.get("question_id") or raw.get("id") or "",
        "kind": raw.get("kind") or ("official_textbook" if official else "competency"),
        "text": raw.get("text") or raw.get("stem") or "",
        "marks": raw.get("marks"),
        "difficulty": raw.get("difficulty") or "medium",
        "bloom": raw.get("bloom") or "",
        "dok": raw.get("dok") or "",
        "competency_ids": list(raw.get("competency_ids") or []),
        "official": official,
        "official_answer": raw.get("official_answer") or raw.get("answer"),
        "rubric": raw.get("rubric"),
        "policy": "ai_generated_must_never_replace_official",
    }


def list_questions(package: dict[str, Any], *, official_only: bool = False) -> list[dict[str, Any]]:
    rows = [normalize_question(q) for q in (package.get("questions") or [])]
    if official_only:
        rows = [r for r in rows if r.get("official")]
    return rows
