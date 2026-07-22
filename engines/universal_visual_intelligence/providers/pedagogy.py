"""Pedagogy providers — flowchart / concept map / study SVG from verified lesson text."""

from __future__ import annotations

from typing import Any

from engines.universal_visual_intelligence.schemas import VisualIntent, VisualSpec


def _sanitize(svg: str) -> str:
    if not svg:
        return ""
    try:
        from svg_sanitizer import sanitize_svg

        return sanitize_svg(svg) or ""
    except Exception:  # noqa: BLE001
        return svg


def _lesson_dict_from_context(context: dict[str, Any], text: str) -> dict[str, Any]:
    lesson = context.get("lesson")
    if isinstance(lesson, dict):
        return lesson
    vocab = context.get("vocabulary")
    if isinstance(vocab, dict):
        return {"topic": context.get("topic") or "Lesson", "vocabulary": vocab, **vocab}
    title = str(context.get("topic") or context.get("title") or "Lesson")
    # Minimal lesson shape for study/flowchart builders
    sections = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("#"):
            sections.append({"title": line.lstrip("# ").strip(), "body": ""})
        elif sections and line:
            sections[-1]["body"] = (sections[-1].get("body") or "") + " " + line
    return {
        "topic": title,
        "title": title,
        "sections": sections or [{"title": title, "body": (text or "")[:1200]}],
        "word_wall": [
            {"term": t.strip()}
            for t in (context.get("terms") or [])[:8]
            if str(t).strip()
        ],
    }


def provide_pedagogy_visuals(
    intents: list[VisualIntent],
    *,
    text: str = "",
    context: dict[str, Any] | None = None,
) -> list[VisualSpec]:
    ctx = dict(context or {})
    lesson = _lesson_dict_from_context(ctx, text)
    specs: list[VisualSpec] = []
    wanted = {i.visual_type for i in intents if i.family == "pedagogy"}
    # Always allow organisers when pedagogy intents exist or text suggests process/structure.
    if not wanted and not any(i.family == "pedagogy" for i in intents):
        blob = (text or "").lower()
        if any(k in blob for k in ("cycle", "process", "flow", "structure", "concept map", "flowchart")):
            wanted = {"lesson_flowchart", "study_diagram", "concept_map"}
        else:
            return specs

    if "concept_map" in wanted or "vocabulary_concept_map" in wanted or not wanted:
        try:
            from concept_map_builder import build_vocabulary_concept_map_svg

            vocab = lesson.get("vocabulary") if isinstance(lesson.get("vocabulary"), dict) else lesson
            svg = _sanitize(build_vocabulary_concept_map_svg(vocab))
            if svg:
                specs.append(
                    VisualSpec(
                        visual_id="pedagogy:concept_map",
                        visual_type="concept_map",
                        source="pedagogy_organiser",
                        provenance="universal_visual_intelligence.providers.pedagogy",
                        caption="Lesson concept map",
                        alt_text="Concept map of lesson vocabulary and topic relationships from verified lesson text.",
                        svg=svg,
                        invents_curriculum=False,
                        deterministic=True,
                        engine_id="concept_map_builder",
                        task_kind="concept_map",
                    )
                )
        except Exception:  # noqa: BLE001
            pass

    if "lesson_flowchart" in wanted or "flowchart" in wanted or "process_flowchart" in wanted:
        try:
            from flowchart_builder import build_lesson_flowchart

            mermaid = build_lesson_flowchart(lesson)
            if mermaid:
                specs.append(
                    VisualSpec(
                        visual_id="pedagogy:lesson_flowchart",
                        visual_type="flowchart",
                        source="pedagogy_organiser",
                        provenance="universal_visual_intelligence.providers.pedagogy",
                        caption="Lesson flowchart",
                        alt_text="Flowchart of lesson concepts derived from verified lesson structure.",
                        mermaid=mermaid,
                        invents_curriculum=False,
                        deterministic=True,
                        engine_id="flowchart_builder",
                        task_kind="lesson_flowchart",
                    )
                )
        except Exception:  # noqa: BLE001
            pass

    if "study_diagram" in wanted or "study_organiser" in wanted or "infographic" in wanted:
        try:
            from study_diagram_builder import resolve_study_diagram_svg

            svg = _sanitize(resolve_study_diagram_svg(lesson))
            if svg:
                specs.append(
                    VisualSpec(
                        visual_id="pedagogy:study_diagram",
                        visual_type="study_diagram",
                        source="pedagogy_organiser",
                        provenance="universal_visual_intelligence.providers.pedagogy",
                        caption="Study diagram",
                        alt_text="Labelled study diagram built from verified lesson sections.",
                        svg=svg,
                        invents_curriculum=False,
                        deterministic=True,
                        engine_id="study_diagram_builder",
                        task_kind="study_diagram",
                    )
                )
        except Exception:  # noqa: BLE001
            pass

    return specs
