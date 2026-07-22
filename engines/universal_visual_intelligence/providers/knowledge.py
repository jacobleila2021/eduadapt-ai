"""Knowledge-layer visual providers — NCERT / curated / UCF diagram paths."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engines.universal_visual_intelligence.schemas import VisualIntent, VisualSpec, make_placeholder


def _resolve_path(raw: str | None) -> str | None:
    if not raw:
        return None
    p = Path(raw)
    return str(p) if p.is_file() else None


def provide_knowledge_visuals(
    intents: list[VisualIntent],
    *,
    biology_figures: list[dict[str, Any]] | None = None,
    ucf_diagrams: list[dict[str, Any]] | None = None,
) -> list[VisualSpec]:
    specs: list[VisualSpec] = []

    for i, fig in enumerate(biology_figures or []):
        path = _resolve_path(fig.get("path") or fig.get("asset_path"))
        if not path:
            continue
        caption = str(fig.get("caption") or fig.get("title") or "NCERT figure")
        specs.append(
            VisualSpec(
                visual_id=f"ncert:{i}:{Path(path).name}",
                visual_type="ncert_figure",
                source="ncert_figure",
                provenance="universal_visual_intelligence.providers.knowledge",
                caption=caption,
                alt_text=str(fig.get("alt_text") or caption),
                asset_paths=[path],
                invents_curriculum=False,
                deterministic=True,
                engine_id="biology_ncert",
                task_kind="biology_figure",
                metadata={"chapter": fig.get("chapter")},
            )
        )

    for i, diagram in enumerate(ucf_diagrams or []):
        formats = diagram.get("formats") if isinstance(diagram.get("formats"), dict) else {}
        path = _resolve_path(
            (formats or {}).get("png")
            or (formats or {}).get("svg")
            or diagram.get("path")
            or diagram.get("png")
        )
        svg = str((formats or {}).get("svg") or diagram.get("svg") or "")
        if not path and not svg:
            # Keep metadata-only UCF entry as placeholder (no invented figure).
            intent = VisualIntent(
                intent_id=f"ucf:{diagram.get('diagram_id') or i}",
                family="knowledge",
                visual_type="ucf_diagram",
                label=str(diagram.get("title") or diagram.get("caption") or "UCF diagram"),
                source_signal="ucf",
                payload=dict(diagram),
            )
            specs.append(make_placeholder(intent=intent, reason="UCF diagram has no resolvable asset path."))
            continue
        caption = str(diagram.get("title") or diagram.get("caption") or "Curriculum figure")
        specs.append(
            VisualSpec(
                visual_id=f"ucf:{diagram.get('diagram_id') or i}",
                visual_type="ucf_diagram",
                source="ncert_figure",
                provenance="universal_visual_intelligence.providers.knowledge",
                caption=caption,
                alt_text=str(diagram.get("alt_text") or caption),
                asset_paths=[path] if path else [],
                svg=svg if not path else "",
                invents_curriculum=False,
                deterministic=True,
                engine_id="ucf_diagram",
                task_kind="ucf_diagram",
            )
        )

    # Explicit knowledge intents without assets still get placeholders later if unmatched.
    _ = intents
    return specs
