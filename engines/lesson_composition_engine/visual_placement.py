"""Visual placement — LCE decides where UVIE visuals appear in the lesson."""

from __future__ import annotations

from typing import Any

from engines.lesson_composition_engine.schemas import LessonSection, VisualPlacement


def collect_uvie_visuals(meta: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Gather verified visuals from UVIE / STEM preferred_visuals — never invent."""
    meta = meta or {}
    visuals: list[dict[str, Any]] = []
    seen: set[str] = set()

    for key in ("preferred_visuals", "uvie_visuals", "biology_figures"):
        for row in meta.get(key) or []:
            if not isinstance(row, dict):
                continue
            vid = str(row.get("visual_id") or row.get("id") or row.get("figure_id") or "")
            if not vid:
                # synthesize stable id from type+index
                vid = f"visual_{len(visuals)}"
            if vid in seen:
                continue
            seen.add(vid)
            visuals.append({**row, "visual_id": vid})

    # UVIE pack nested under uli / engine outputs
    uli = meta.get("uli") or {}
    for row in (uli.get("visuals") or []):
        if isinstance(row, dict):
            vid = str(row.get("visual_id") or f"uli_visual_{len(visuals)}")
            if vid not in seen:
                seen.add(vid)
                visuals.append({**row, "visual_id": vid})

    return visuals


def place_visuals(
    sections: list[LessonSection],
    visuals: list[dict[str, Any]],
    *,
    concept_titles: list[str] | None = None,
) -> tuple[list[LessonSection], list[VisualPlacement]]:
    """
    Attach each visual immediately after the explanation it supports.
    Matching: concept name / title overlap, else sequential teach sections.
    """
    placements: list[VisualPlacement] = []
    if not visuals:
        return sections, placements

    teach_indices = [
        i
        for i, s in enumerate(sections)
        if s.role in {
            "simple_explanation",
            "visual",
            "concept",
            "diagram",
            "explain",
            "teach",
            "process",
            "phenomenon",
        }
        or "Understanding" in s.title
        or s.role == "real_life_example"
    ]
    if not teach_indices:
        teach_indices = list(range(min(len(sections), max(1, len(visuals)))))

    concepts = [c.lower() for c in (concept_titles or [])]

    for vi, visual in enumerate(visuals):
        vid = str(visual.get("visual_id"))
        hay = " ".join(
            str(visual.get(k) or "")
            for k in ("title", "caption", "alt_text", "concept", "label", "topic")
        ).lower()
        target_i = teach_indices[min(vi, len(teach_indices) - 1)]
        for ci, concept in enumerate(concepts):
            if concept and concept in hay:
                # prefer section for that concept
                for i, s in enumerate(sections):
                    if s.concept_id.lower() == concept or concept in s.title.lower():
                        if s.role in {"simple_explanation", "visual", "concept", "diagram"}:
                            target_i = i
                            break
                break
        section = sections[target_i]
        if vid not in section.visual_ids:
            section.visual_ids.append(vid)
        placements.append(
            VisualPlacement(
                visual_id=vid,
                after_section_id=section.section_id,
                rationale=f"Supports explanation in '{section.title}'",
                preferred_format="svg",
            )
        )
    return sections, placements


def inject_visual_markers(section_dict: dict[str, Any], visuals_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Append visual captions/SVG immediately after section body when available."""
    out = dict(section_dict)
    body = str(out.get("body") or "")
    chunks = [body] if body else []
    for vid in out.get("visual_ids") or []:
        visual = visuals_by_id.get(vid) or {}
        svg = visual.get("svg") or visual.get("svg_diagram") or ""
        caption = visual.get("caption") or visual.get("alt_text") or visual.get("title") or "Lesson diagram"
        if svg:
            chunks.append(f"\n\n<!-- LCE_VISUAL:{vid} -->\n{svg}\n")
        else:
            chunks.append(f"\n\n**Visual:** {caption}\n")
        # Prefer storing svg on lesson later; marker keeps placement intentional
    out["body"] = "".join(chunks).strip()
    return out


def build_visual_summary_table(placements: list[VisualPlacement], visuals: list[dict[str, Any]]) -> str:
    if not placements:
        return (
            "| Color | Idea |\n| --- | --- |\n"
            "| Teal | Core concept |\n| Navy | Practice |\n| Soft gold | Check understanding |"
        )
    by_id = {str(v.get("visual_id")): v for v in visuals}
    lines = ["| Visual | Supports |", "| --- | --- |"]
    for p in placements[:8]:
        v = by_id.get(p.visual_id) or {}
        label = v.get("title") or v.get("caption") or p.visual_id
        lines.append(f"| {label} | {p.rationale} |")
    return "\n".join(lines)
