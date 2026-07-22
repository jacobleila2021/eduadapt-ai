"""
Universal Visual Intelligence Engine (UVIE) — Platform Excellence Phase 1.

Orchestrates deterministic educational visuals from verified ULI / SIF / UCF / STEM
signals. Never invents curriculum; generative image providers remain disabled.
"""

from __future__ import annotations

from engines.universal_visual_intelligence.engine import UniversalVisualIntelligenceEngine
from engines.universal_visual_intelligence.pack import PACK_VERSION, inject_uvie_into_lesson, render_visual_specs
from engines.universal_visual_intelligence.service import (
    UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK,
    inject_into_lesson,
    pack_health,
    render_visuals_for_uli,
    uvie_quality_signals,
)

__all__ = [
    "UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "UniversalVisualIntelligenceEngine",
    "render_visuals_for_uli",
    "render_visual_specs",
    "inject_into_lesson",
    "inject_uvie_into_lesson",
    "uvie_quality_signals",
    "pack_health",
]
