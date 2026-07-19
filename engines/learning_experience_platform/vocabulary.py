"""Vocabulary intelligence — glossary + UCF + optional pronunciation."""

from __future__ import annotations

from typing import Any


def vocabulary_card(term: str, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    definition = ""
    related = []
    picture = ""
    # UCF glossary
    try:
        from engines.universal_curriculum_framework.curriculum_registry import list_packages, load_package
        from engines.universal_curriculum_framework.glossary import find_term

        pkgs = list_packages()
        if pkgs:
            pkg = load_package(pkgs[0]["package_id"]) or {}
            hits = find_term(pkg, term)
            if hits:
                definition = hits[0].get("definition") or ""
                related = hits[0].get("related_concepts") or []
                picture = hits[0].get("visual_definition") or ""
    except Exception:  # noqa: BLE001
        pass

    # Lesson vocab wall
    lesson = context.get("lesson") or {}
    for w in lesson.get("word_wall") or lesson.get("vocabulary") or []:
        if isinstance(w, dict) and term.lower() in str(w.get("term") or "").lower():
            definition = definition or w.get("definition") or w.get("child_friendly") or ""
            break

    pronunciation = ""
    try:
        from engines.voice_multimodal_learning.pronunciation import practice_card

        pronunciation = practice_card(term).get("syllables") or []
    except Exception:  # noqa: BLE001
        pronunciation = []

    return {
        "ok": True,
        "term": term,
        "definition": definition or "Not found in verified glossary — ask AI Tutor with lesson context.",
        "pronunciation": pronunciation,
        "simplified": definition,
        "translation": None,  # multilingual packs via UCF/roadmap
        "example_sentence": "",
        "picture": picture,
        "related_concepts": related,
        "reading_level": context.get("reading_level") or "grade_appropriate",
        "verified": bool(definition),
    }
