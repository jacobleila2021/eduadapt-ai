"""Map external curriculum packages → UCF (engines consume UCF only)."""

from __future__ import annotations

from typing import Any

from engines.curriculum_expansion_framework.schemas import CURRICULUM_FAMILIES


REQUIRED_MAP_FIELDS = (
    "board",
    "subject",
    "grade",
    "units",
    "chapters",
    "topics",
    "learning_objectives",
    "competencies",
    "blooms",
    "dok",
    "prerequisites",
    "assessment_mappings",
    "official_questions",
    "formulae",
    "figures",
    "glossary",
    "accessibility",
)


def resolve_ucf_board(curriculum_id: str) -> str:
    meta = CURRICULUM_FAMILIES.get(curriculum_id) or {}
    return str(meta.get("ucf_board") or curriculum_id)


def map_to_ucf_payload(raw: dict[str, Any], *, curriculum_id: str) -> dict[str, Any]:
    """
    Normalize an external curriculum package into a UCF importer payload.
    Does not invent academic content — only reshapes provided fields.
    """
    board = resolve_ucf_board(curriculum_id)
    topics_in = list(raw.get("topics") or raw.get("chapters") or [])
    concepts = []
    for i, t in enumerate(topics_in):
        if isinstance(t, str):
            concepts.append({"id": f"{curriculum_id}.t{i}", "title": t, "definition": f"Understand {t}"})
            continue
        title = str(t.get("title") or t.get("name") or f"Topic {i}")
        definition = str(
            t.get("definition")
            or t.get("summary")
            or ((t.get("objectives") or [None])[0] if isinstance(t.get("objectives"), list) else None)
            or f"Understand {title}"
        )
        concepts.append(
            {
                "id": str(t.get("id") or t.get("topic_id") or f"{curriculum_id}.t{i}"),
                "title": title,
                "definition": definition,
                "prerequisites": list(t.get("prerequisites") or []),
                "misconceptions": list(t.get("misconceptions") or []),
                "bloom": str(t.get("bloom") or t.get("blooms") or "understand"),
                "dok": str(t.get("dok") or "2"),
                "chapter": t.get("chapter") or t.get("chapter_number") or 0,
                "chapter_title": str(t.get("chapter_title") or t.get("unit") or ""),
                "competency_ids": list(t.get("competencies") or t.get("competency_ids") or []),
            }
        )

    objectives = list(raw.get("learning_objectives") or raw.get("objectives") or [])
    if not concepts and objectives:
        for i, o in enumerate(objectives):
            text = o if isinstance(o, str) else str(o.get("text") or o)
            concepts.append({"id": f"{curriculum_id}.lo{i}", "title": text[:80], "definition": text})

    return {
        "board": board,
        "grade": str(raw.get("grade") or raw.get("year") or ""),
        "subject": str(raw.get("subject") or ""),
        "curriculum_id": str(raw.get("package_id") or raw.get("curriculum_id") or f"cef_{curriculum_id}"),
        "package_id": str(raw.get("package_id") or ""),
        "concepts": concepts,
        "learning_objectives": objectives,
        "equations": list(raw.get("formulae") or raw.get("formulas") or []),
        "figures": list(raw.get("figures") or raw.get("diagrams") or []),
        "vocabulary": list(raw.get("glossary") or []),
        "questions": list(raw.get("official_questions") or raw.get("questions") or []),
        "version": str(raw.get("version") or "1.0.0"),
        "units": list(raw.get("units") or []),
        "chapters": list(raw.get("chapters") or []),
        "assessment_mappings": list(raw.get("assessment_mappings") or []),
        "accessibility": raw.get("accessibility") or {},
        "provenance": {
            "cef_curriculum_id": curriculum_id,
            "ucf_board": board,
            "mapped_by": "curriculum_expansion_framework",
        },
    }


def mapping_completeness(raw: dict[str, Any]) -> dict[str, Any]:
    present = []
    missing = []
    for f in REQUIRED_MAP_FIELDS:
        val = raw.get(f)
        # aliases
        if f == "blooms" and not val:
            val = raw.get("bloom")
        if f == "formulae" and not val:
            val = raw.get("formulas")
        if f == "figures" and not val:
            val = raw.get("diagrams")
        if f == "official_questions" and not val:
            val = raw.get("questions")
        if f == "learning_objectives" and not val:
            val = raw.get("objectives")
        if val not in (None, "", [], {}):
            present.append(f)
        else:
            missing.append(f)
    score = len(present) / max(len(REQUIRED_MAP_FIELDS), 1)
    return {"ok": True, "present": present, "missing": missing, "completeness": round(score, 3)}
