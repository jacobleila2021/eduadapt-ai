"""Resolve visual intents from ULI, SIF, UCF, STEM context."""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_visual_intelligence.schemas import VisualIntent


def _uli_text(uli: Any) -> str:
    try:
        from engines.subject_intelligence_core.utilities import extract_uli_text

        return extract_uli_text(uli, include_vocabulary=True)
    except Exception:  # noqa: BLE001
        pass
    parts: list[str] = []
    if isinstance(uli, Mapping):
        parts.append(str(uli.get("normalized_text") or uli.get("text") or ""))
    try:
        env = getattr(uli, "source_envelope", None)
        if isinstance(env, Mapping):
            parts.append(str(env.get("normalized_text") or env.get("text") or ""))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


def _visual_opportunities(uli: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        if hasattr(uli, "visual_opportunities"):
            raw = uli.visual_opportunities
            if callable(raw):
                raw = raw()
            if isinstance(raw, list):
                out.extend(x for x in raw if isinstance(x, dict))
        elif isinstance(uli, Mapping):
            out.extend(x for x in (uli.get("visual_opportunities") or []) if isinstance(x, dict))
    except Exception:  # noqa: BLE001
        pass
    try:
        profile = getattr(uli, "universal_profile", None) or getattr(uli, "profile", None)
        if isinstance(profile, Mapping):
            out.extend(x for x in (profile.get("visual_opportunities") or []) if isinstance(x, dict))
        elif profile is not None and hasattr(profile, "visual_opportunities"):
            raw = profile.visual_opportunities
            if isinstance(raw, list):
                out.extend(x for x in raw if isinstance(x, dict))
    except Exception:  # noqa: BLE001
        pass
    return out


def _sif_visuals(context: Mapping[str, Any]) -> list[dict[str, Any]]:
    visuals: list[dict[str, Any]] = []
    for key in ("sif_visuals", "visuals", "subject_intelligence"):
        raw = context.get(key)
        if isinstance(raw, Mapping):
            nested = raw.get("visuals") or raw.get("lxp", {}).get("visuals") if isinstance(raw.get("lxp"), Mapping) else raw.get("visuals")
            if isinstance(nested, list):
                visuals.extend(x for x in nested if isinstance(x, dict))
            si = raw.get("subject_intelligence") if isinstance(raw.get("subject_intelligence"), Mapping) else None
            if si and isinstance(si.get("visuals"), list):
                visuals.extend(x for x in si["visuals"] if isinstance(x, dict))
        elif isinstance(raw, list):
            visuals.extend(x for x in raw if isinstance(x, dict))
    return visuals


def _family_for_visual_type(visual_type: str) -> str:
    vt = (visual_type or "").lower()
    if any(k in vt for k in ("timeline",)):
        return "timeline"
    if any(k in vt for k in ("map", "geography", "overlay", "gis")):
        return "geography"
    if any(
        k in vt
        for k in (
            "plot",
            "graph",
            "circuit",
            "molecule",
            "physics",
            "geogebra",
            "force",
            "ray",
        )
    ):
        return "stem"
    if any(k in vt for k in ("ncert", "ucf", "figure", "textbook")):
        return "knowledge"
    return "pedagogy"


def resolve_visual_intents(
    uli: Any = None,
    *,
    context: Mapping[str, Any] | None = None,
    text: str | None = None,
) -> list[VisualIntent]:
    ctx = dict(context or {})
    blob = text if text is not None else (_uli_text(uli) if uli is not None else str(ctx.get("text") or ""))
    intents: list[VisualIntent] = []
    seen: set[str] = set()

    def _add(intent: VisualIntent) -> None:
        key = f"{intent.family}:{intent.visual_type}:{intent.label[:40]}"
        if key in seen:
            return
        seen.add(key)
        intents.append(intent)

    for i, opp in enumerate(_visual_opportunities(uli)):
        opportunity = str(opp.get("opportunity") or "")
        low = opportunity.lower()
        visual_type = "study_diagram"
        family = "pedagogy"
        if "timeline" in low or "sequence" in low:
            visual_type, family = "interactive_timeline", "timeline"
        elif "map" in low:
            visual_type, family = "clickable_map", "geography"
        elif "cycle" in low or "process" in low or "flow" in low:
            visual_type = "flowchart"
        elif "structure" in low or "compare" in low:
            visual_type = "concept_map"
        _add(
            VisualIntent(
                intent_id=f"uli:{i}",
                family=family,
                visual_type=visual_type,
                label=opportunity[:120] or visual_type,
                text_excerpt=opportunity,
                source_signal="uli",
                payload=dict(opp),
            )
        )

    for i, vis in enumerate(_sif_visuals(ctx)):
        vt = str(vis.get("visual_type") or "concept_map")
        family = _family_for_visual_type(vt)
        _add(
            VisualIntent(
                intent_id=f"sif:{i}:{vt}",
                family=family,
                visual_type=vt,
                label=str(vis.get("label") or vt),
                source_signal="sif",
                payload=dict(vis),
            )
        )

    for i, diagram_id in enumerate(ctx.get("diagram_ids") or []):
        _add(
            VisualIntent(
                intent_id=f"ucf:id:{i}",
                family="knowledge",
                visual_type="ucf_diagram",
                label=str(diagram_id),
                source_signal="ucf",
                payload={"diagram_id": diagram_id},
            )
        )

    for i, diagram in enumerate(ctx.get("ucf_diagrams") or []):
        if not isinstance(diagram, dict):
            continue
        _add(
            VisualIntent(
                intent_id=f"ucf:{diagram.get('diagram_id') or i}",
                family="knowledge",
                visual_type="ucf_diagram",
                label=str(diagram.get("title") or diagram.get("caption") or "UCF diagram"),
                source_signal="ucf",
                payload=dict(diagram),
            )
        )

    for i, art in enumerate(ctx.get("stem_artifacts") or []):
        if not isinstance(art, dict):
            continue
        kind = str(art.get("task_kind") or "")
        if not kind:
            continue
        _add(
            VisualIntent(
                intent_id=f"stem:{i}:{kind}",
                family="stem",
                visual_type=kind,
                label=str((art.get("payload") or {}).get("name") or kind),
                source_signal="stem",
                payload=dict(art.get("payload") or {}),
                priority_hint="",
            )
        )

    # Text heuristics when no structured intents
    if not intents and blob:
        low = blob.lower()
        if any(k in low for k in ("timeline", "1857", "1947", "chronology")):
            _add(
                VisualIntent(
                    intent_id="heuristic:timeline",
                    family="timeline",
                    visual_type="interactive_timeline",
                    label="Lesson timeline",
                    text_excerpt=blob[:200],
                    source_signal="context",
                )
            )
        if any(k in low for k in ("map", "geography", "latitude")):
            _add(
                VisualIntent(
                    intent_id="heuristic:map",
                    family="geography",
                    visual_type="clickable_map",
                    label="Geography map scaffold",
                    text_excerpt=blob[:200],
                    source_signal="context",
                )
            )
        if any(k in low for k in ("cycle", "process", "flow", "structure", "concept")):
            _add(
                VisualIntent(
                    intent_id="heuristic:flowchart",
                    family="pedagogy",
                    visual_type="flowchart",
                    label="Lesson process flowchart",
                    text_excerpt=blob[:200],
                    source_signal="context",
                )
            )
            _add(
                VisualIntent(
                    intent_id="heuristic:concept_map",
                    family="pedagogy",
                    visual_type="concept_map",
                    label="Lesson concept map",
                    text_excerpt=blob[:200],
                    source_signal="context",
                )
            )

    return intents
