"""UVIE accessibility variants — AIE-aligned presentation hooks."""

from __future__ import annotations

from typing import Any

from engines.universal_visual_intelligence.schemas import VisualSpec


def apply_accessibility_variants(
    specs: list[VisualSpec],
    *,
    uli: Any = None,
) -> list[VisualSpec]:
    """Attach a11y variant descriptors; do not invent alternate scientific content."""
    reading_band = None
    try:
        if uli is not None and hasattr(uli, "educational_structure"):
            edu = uli.educational_structure()
            if isinstance(edu, dict):
                reading_band = edu.get("reading_band") or edu.get("difficulty")
    except Exception:  # noqa: BLE001
        pass

    out: list[VisualSpec] = []
    for spec in specs:
        variants = dict(spec.a11y_variants or {})
        variants.setdefault(
            "dyslexia_friendly",
            {
                "recommendation": "Increase spacing; prefer Lexend/Arial; avoid dense label stacks.",
                "owner": "AIE/LXP",
            },
        )
        variants.setdefault(
            "high_contrast",
            {
                "recommendation": "Use navy/teal on light fills; pair colour with labels/patterns.",
                "owner": "AIE",
            },
        )
        variants.setdefault(
            "executive_function_organiser",
            {
                "recommendation": "Show one panel/step at a time for multi-step diagrams.",
                "owner": "AIE/LXP",
            },
        )
        if reading_band is not None:
            variants["reading_band"] = reading_band
        if not (spec.alt_text or "").strip():
            spec.alt_text = spec.caption or f"{spec.visual_type} educational visual"
        spec.a11y_variants = variants
        out.append(spec)
    return out


def accessibility_guidance_for_visuals(specs: list[VisualSpec]) -> list[dict[str, Any]]:
    return [
        {
            "recommendation": "alt_text_required",
            "detail": "Every UVIE visual must expose meaningful alt text.",
            "owner": "AIE",
            "visual_ids": [s.visual_id for s in specs[:12]],
        },
        {
            "recommendation": "dyslexia_friendly_diagrams",
            "detail": "Prefer spacious labelled organisers over dense decorative art.",
            "owner": "AIE/LXP",
        },
        {
            "recommendation": "colour_blind_safe",
            "detail": "Do not rely on colour alone for meaning in diagrams.",
            "owner": "AIE",
        },
    ]
