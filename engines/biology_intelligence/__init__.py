"""
Biology Intelligence Pack (BIP) — fourth production Subject Intelligence Pack.

Teaching-layer pedagogy for biology / life sciences. Plugs into SIF; does not
invent biology facts or replace Knowledge Layer curriculum sources.
"""

from __future__ import annotations

from engines.biology_intelligence.engine import BiologyIntelligenceEngine
from engines.biology_intelligence.pack import PACK_VERSION, BiologyIntelligencePack
from engines.biology_intelligence.service import (
    BIOLOGY_INTELLIGENCE_SMOKE_OK,
    analyse_biology_lesson,
    biology_quality_signals,
    get_biology_pack,
    pack_health,
    register_biology_pack,
)

register_biology_pack(overwrite=True)

__all__ = [
    "BIOLOGY_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "BiologyIntelligencePack",
    "BiologyIntelligenceEngine",
    "get_biology_pack",
    "register_biology_pack",
    "analyse_biology_lesson",
    "biology_quality_signals",
    "pack_health",
]
