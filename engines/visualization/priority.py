"""Visualization priority pipeline — deterministic assets before AI diagrams."""

from __future__ import annotations

from pathlib import Path


PRIORITY_ORDER = (
    "ncert_figure",
    "geogebra",
    "matplotlib",
    "schemdraw",
    "rdkit",
    "molecule_fallback",
    "physics_diagram",
    "ai_illustration",
)


def _artifact_visuals(artifacts: list[dict]) -> list[dict]:
    visuals: list[dict] = []
    for art in artifacts or []:
        if not art.get("ok") and art.get("validation") == "fail":
            continue
        engine = art.get("engine_id") or ""
        kind = art.get("task_kind") or ""
        payload = art.get("payload") or {}
        paths = [p for p in (art.get("asset_paths") or []) if Path(p).is_file()]
        iframe = payload.get("iframe_url")

        source = None
        if engine in ("geogebra",) or kind == "geometry":
            source = "geogebra"
        elif engine in ("matplotlib",) or kind == "plot_graph":
            source = "matplotlib"
        elif engine in ("schemdraw",) or kind == "draw_circuit":
            source = "schemdraw"
        elif engine in ("rdkit", "molecule_fallback") or kind == "molecule_smiles":
            source = "rdkit" if engine == "rdkit" else "molecule_fallback"
        elif kind == "physics_diagram" or engine.startswith("physics"):
            source = "physics_diagram"
        elif paths or iframe:
            source = "matplotlib"

        if source and (paths or iframe or art.get("latex")):
            visuals.append(
                {
                    "source": source,
                    "engine_id": engine,
                    "task_kind": kind,
                    "asset_paths": paths,
                    "iframe_url": iframe,
                    "latex": art.get("latex"),
                    "caption": payload.get("name")
                    or payload.get("circuit_type")
                    or payload.get("geometry_kind")
                    or payload.get("diagram_type")
                    or kind,
                }
            )
    return visuals


def select_preferred_visuals(
    artifacts: list[dict],
    biology_figures: list[dict] | None = None,
    max_visuals: int = 6,
) -> list[dict]:
    """
    Priority: NCERT figure → GeoGebra → Matplotlib → Schemdraw → RDKit → physics → AI last.
    """
    selected: list[dict] = []

    for fig in biology_figures or []:
        path = fig.get("path") or fig.get("asset_path")
        if path and Path(path).is_file():
            selected.append(
                {
                    "source": "ncert_figure",
                    "engine_id": "biology_ncert",
                    "task_kind": "biology_figure",
                    "asset_paths": [path],
                    "iframe_url": None,
                    "latex": None,
                    "caption": fig.get("caption") or fig.get("title") or "NCERT figure",
                    "alt_text": fig.get("alt_text") or "",
                    "chapter": fig.get("chapter"),
                }
            )

    selected.extend(_artifact_visuals(artifacts))

    # Sort by priority order
    rank = {name: i for i, name in enumerate(PRIORITY_ORDER)}
    selected.sort(key=lambda v: rank.get(v.get("source", "ai_illustration"), 99))

    # Dedupe by source+caption
    seen: set[str] = set()
    unique: list[dict] = []
    for v in selected:
        key = f"{v.get('source')}:{v.get('caption')}:{','.join(v.get('asset_paths') or [])}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(v)
        if len(unique) >= max_visuals:
            break
    return unique


def has_deterministic_visuals(preferred: list[dict]) -> bool:
    return any(v.get("source") != "ai_illustration" for v in preferred)


def visualization_prompt_rules(preferred: list[dict]) -> str:
    if not has_deterministic_visuals(preferred):
        return (
            "VISUALIZATION: No verified engine/NCERT figure found. "
            "You may include mermaid_diagram and svg_diagram as educational illustrations only, "
            "and mark them as unverified_visual."
        )

    lines = [
        "VISUALIZATION PRIORITY (mandatory):",
        "Verified deterministic visuals already exist (NCERT / GeoGebra / Matplotlib / Schemdraw / RDKit / physics).",
        "DO NOT invent competing scientific diagrams. Set mermaid_diagram and svg_diagram to empty strings \"\".",
        "In sections, refer teachers/students to VERIFIED_VISUALS listed below — do not redraw equations, circuits, molecules, or graphs.",
        "VERIFIED_VISUALS:",
    ]
    for i, v in enumerate(preferred, 1):
        lines.append(
            f"{i}. [{v.get('source')}] {v.get('caption')} "
            f"(engine={v.get('engine_id')}, files={len(v.get('asset_paths') or [])})"
        )
    return "\n".join(lines)


def inject_verified_visuals_into_lesson(lesson: dict, preferred: list[dict]) -> dict:
    """Attach verified visuals and clear AI diagrams when deterministic assets exist."""
    if not isinstance(lesson, dict):
        return lesson
    out = dict(lesson)
    out["verified_visuals"] = preferred
    if has_deterministic_visuals(preferred):
        out["mermaid_diagram"] = ""
        out["svg_diagram"] = ""
        out["diagram_source"] = "deterministic_engines"
    else:
        out["diagram_source"] = "ai_illustration"
    return out
