"""Lesson summary — verified lesson content only."""

from __future__ import annotations

from typing import Any


def build_summary(lesson: dict[str, Any] | None = None, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    lesson = lesson or {}
    context = context or {}
    sections = lesson.get("sections") or []
    key_ideas = []
    if lesson.get("big_idea"):
        key_ideas.append(lesson["big_idea"])
    for sec in sections[:8]:
        if isinstance(sec, dict):
            body = (sec.get("body") or "")[:200]
            if body:
                key_ideas.append(body)
        elif isinstance(sec, str):
            key_ideas.append(sec[:200])

    outputs = context.get("engine_outputs") or {}
    cie = (outputs.get("curriculum") or {}).get("payload") or {}
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}

    formulae = []
    for a in sa.get("artifacts") or []:
        if isinstance(a, dict) and (a.get("payload") or {}).get("latex"):
            formulae.append((a.get("payload") or {}).get("latex"))

    vocab = []
    for w in lesson.get("word_wall") or []:
        if isinstance(w, dict):
            vocab.append(w.get("term"))

    objectives = cie.get("learning_objectives") or lesson.get("learning_objectives") or []
    competencies = cie.get("competencies") or []

    # Prefer UVIE / preferred_visuals when SAE attached them.
    diagrams = []
    uvie = sa.get("uvie") if isinstance(sa.get("uvie"), dict) else {}
    for v in (sa.get("preferred_visuals") or uvie.get("lxp", {}).get("important_diagrams") or [])[:8]:
        if isinstance(v, dict):
            diagrams.append(v)
    if not diagrams:
        diagrams = [a for a in (sa.get("artifacts") or []) if isinstance(a, dict)][:8]

    return {
        "ok": True,
        "key_ideas": key_ideas[:10],
        "concept_map": {"concepts": [c.get("title") if isinstance(c, dict) else str(c) for c in (cie.get("concepts") or [])[:12]]},
        "important_formulae": formulae[:10],
        "important_diagrams": diagrams,
        "uvie": {
            "visuals": (uvie.get("visuals") or [])[:8],
            "placeholders": ((uvie.get("lxp") or {}).get("placeholders") or [])[:8],
            "policy": "deterministic_engines_only_never_ai_invent_diagrams",
        },
        "vocabulary_review": [v for v in vocab if v][:20],
        "revision_checklist": [f"Review: {k[:80]}" for k in key_ideas[:5]],
        "learning_objectives": objectives[:10],
        "competencies_covered": competencies[:10],
        "source": "verified_lesson_content",
        "policy": "no_unsupported_summary_facts",
    }
