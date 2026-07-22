"""UVIE schemas — VisualSpec and VisualIntent contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class VisualIntent:
    """Resolved request to produce or locate an educational visual."""

    intent_id: str
    family: str  # stem | knowledge | pedagogy | timeline | geography | placeholder
    visual_type: str
    label: str = ""
    text_excerpt: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    source_signal: str = ""  # uli | sif | ucf | stem | context
    priority_hint: str = ""  # optional PRIORITY_ORDER source name

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VisualSpec:
    """Single consumer shape for LXP / SAE / exporters."""

    visual_id: str
    visual_type: str
    source: str
    provenance: str
    caption: str = ""
    alt_text: str = ""
    lang: str = "en"
    asset_paths: list[str] = field(default_factory=list)
    svg: str = ""
    mermaid: str = ""
    iframe_url: str | None = None
    latex: str | None = None
    invents_curriculum: bool = False
    deterministic: bool = True
    placeholder: bool = False
    a11y_variants: dict[str, Any] = field(default_factory=dict)
    renderer: str = "lxp"
    engine_id: str = ""
    task_kind: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_preferred_visual(self) -> dict[str, Any]:
        """Backward-compatible preferred_visuals entry."""
        return {
            "source": self.source,
            "engine_id": self.engine_id or "universal_visual_intelligence",
            "task_kind": self.task_kind or self.visual_type,
            "asset_paths": list(self.asset_paths),
            "iframe_url": self.iframe_url,
            "latex": self.latex,
            "caption": self.caption or self.visual_type,
            "alt_text": self.alt_text,
            "svg": self.svg,
            "mermaid": self.mermaid,
            "visual_id": self.visual_id,
            "visual_type": self.visual_type,
            "provenance": self.provenance,
            "invents_curriculum": self.invents_curriculum,
            "deterministic": self.deterministic,
            "placeholder": self.placeholder,
            "renderer": self.renderer,
            "a11y_variants": dict(self.a11y_variants),
        }


def make_placeholder(
    *,
    intent: VisualIntent,
    reason: str = "No deterministic provider matched this intent.",
) -> VisualSpec:
    return VisualSpec(
        visual_id=f"placeholder:{intent.intent_id}",
        visual_type=intent.visual_type or "placeholder",
        source="placeholder",
        provenance="universal_visual_intelligence.placeholder",
        caption=intent.label or intent.visual_type or "Visual placeholder",
        alt_text=f"Placeholder for {intent.visual_type or 'visual'}: {reason}",
        invents_curriculum=False,
        deterministic=False,
        placeholder=True,
        metadata={"reason": reason, "intent": intent.to_dict()},
    )
