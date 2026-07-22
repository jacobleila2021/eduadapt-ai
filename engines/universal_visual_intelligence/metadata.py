"""UVIE metadata envelope."""

from __future__ import annotations

from typing import Any, Mapping


def build_uvie_metadata(
    *,
    version: str,
    intent_count: int,
    visual_count: int,
    exam_mode: bool = False,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "pack": "universal_visual_intelligence",
        "version": version,
        "intent_count": intent_count,
        "visual_count": visual_count,
        "exam_mode": exam_mode,
        "mutates_curriculum": False,
        "generative_images_enabled": False,
        "policy": "prefer_official_then_deterministic_engines_never_ai_invent",
    }
    if extra:
        out.update(dict(extra))
    return out
