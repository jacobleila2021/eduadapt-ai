"""Intelligent glossary panel."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.vocabulary import vocabulary_card


def build_glossary(terms: list[str] | None = None, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    terms = terms or []
    # Pull from lesson word wall
    lesson = context.get("lesson") or {}
    for w in lesson.get("word_wall") or []:
        if isinstance(w, dict) and w.get("term"):
            terms.append(str(w["term"]))
    # UCF
    try:
        from engines.universal_curriculum_framework.curriculum_registry import list_packages, load_package

        pkgs = list_packages()
        if pkgs:
            pkg = load_package(pkgs[0]["package_id"]) or {}
            for g in pkg.get("glossary") or []:
                if g.get("term"):
                    terms.append(str(g["term"]))
    except Exception:  # noqa: BLE001
        pass

    uniq = []
    seen = set()
    for t in terms:
        key = t.lower().strip()
        if key and key not in seen:
            seen.add(key)
            uniq.append(t)

    cards = [vocabulary_card(t, context=context) for t in uniq[:40]]
    return {
        "ok": True,
        "expandable": True,
        "entries": cards,
        "features": ["definitions", "cross_links", "audio_pronunciation", "visuals", "examples", "related_lessons", "competencies"],
    }
