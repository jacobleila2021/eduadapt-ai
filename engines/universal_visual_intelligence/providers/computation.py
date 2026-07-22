"""Computation-layer visual providers — route STEM draw tasks via Subject Tool Router."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engines.universal_visual_intelligence.schemas import VisualIntent, VisualSpec


def _engine_result_to_spec(intent: VisualIntent, result: Any) -> VisualSpec | None:
    if result is None:
        return None
    ok = bool(getattr(result, "ok", True))
    validation = str(getattr(result, "validation", "") or "")
    if validation.lower() == "fail" or (hasattr(result, "ok") and not ok and validation.lower() == "fail"):
        return None

    payload = getattr(result, "payload", None) or {}
    if not isinstance(payload, dict):
        payload = {}
    paths = [p for p in (getattr(result, "asset_paths", None) or []) if Path(str(p)).is_file()]
    iframe = payload.get("iframe_url")
    latex = getattr(result, "latex", None)
    engine_id = str(getattr(result, "engine_id", "") or "")
    kind = getattr(result, "task_kind", None)
    kind_s = kind.value if hasattr(kind, "value") else str(kind or intent.visual_type)

    source = intent.priority_hint or "matplotlib"
    if engine_id == "geogebra" or kind_s == "geometry":
        source = "geogebra"
    elif engine_id == "schemdraw" or kind_s == "draw_circuit":
        source = "schemdraw"
    elif engine_id in ("rdkit", "molecule_fallback") or kind_s == "molecule_smiles":
        source = "rdkit" if engine_id == "rdkit" else "molecule_fallback"
    elif kind_s == "physics_diagram" or engine_id.startswith("physics"):
        source = "physics_diagram"
    elif kind_s == "plot_graph" or engine_id == "matplotlib":
        source = "matplotlib"

    if not paths and not iframe and not latex:
        return None

    caption = str(
        intent.label
        or payload.get("name")
        or payload.get("circuit_type")
        or payload.get("geometry_kind")
        or payload.get("diagram_type")
        or kind_s
        or "STEM visual"
    )
    return VisualSpec(
        visual_id=f"stem:{intent.intent_id}",
        visual_type=intent.visual_type or kind_s,
        source=source,
        provenance="universal_visual_intelligence.providers.computation",
        caption=caption,
        alt_text=str(intent.payload.get("alt_text") or caption),
        asset_paths=[str(p) for p in paths],
        iframe_url=iframe,
        latex=latex,
        invents_curriculum=False,
        deterministic=True,
        engine_id=engine_id,
        task_kind=kind_s,
        metadata={"intent_family": intent.family},
    )


def provide_computation_visuals(
    intents: list[VisualIntent],
    *,
    stem_artifacts: list[dict[str, Any]] | None = None,
) -> list[VisualSpec]:
    """Convert existing STEM artifacts and optional router tasks into VisualSpecs."""
    from engines.universal_visual_intelligence.priority import select_preferred_visuals

    specs: list[VisualSpec] = []

    # Prefer already-computed pipeline artifacts (do not re-route unless needed).
    preferred = select_preferred_visuals(stem_artifacts or [], biology_figures=None, max_visuals=12)
    for i, v in enumerate(preferred):
        if str(v.get("source") or "") == "ncert_figure":
            continue  # knowledge provider owns NCERT
        specs.append(
            VisualSpec(
                visual_id=str(v.get("visual_id") or f"artifact:{i}"),
                visual_type=str(v.get("visual_type") or v.get("task_kind") or "stem_visual"),
                source=str(v.get("source") or "matplotlib"),
                provenance="universal_visual_intelligence.providers.computation",
                caption=str(v.get("caption") or "STEM visual"),
                alt_text=str(v.get("alt_text") or v.get("caption") or "Verified STEM visual"),
                asset_paths=list(v.get("asset_paths") or []),
                iframe_url=v.get("iframe_url"),
                latex=v.get("latex"),
                invents_curriculum=False,
                deterministic=True,
                engine_id=str(v.get("engine_id") or ""),
                task_kind=str(v.get("task_kind") or ""),
            )
        )

    # Explicit STEM intents may request a fresh router draw when payload includes task_kind.
    for intent in intents:
        if intent.family != "stem":
            continue
        task_kind = intent.payload.get("task_kind")
        if not task_kind:
            continue
        try:
            from engines.router import route
            from engines.types import TaskKind, ToolTask

            kind = TaskKind(str(task_kind))
            result = route(ToolTask(kind=kind, payload=dict(intent.payload)))
            spec = _engine_result_to_spec(intent, result)
            if spec:
                specs.append(spec)
        except Exception:  # noqa: BLE001
            continue

    return specs
