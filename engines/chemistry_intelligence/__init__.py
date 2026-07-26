"""
Chemistry Intelligence Pack (CIP) — third production Subject Intelligence Pack.

Teaching-layer pedagogy for chemistry. Plugs into SIF; does not invent chemistry
or replace Computation Layer balancers (ChemPy / atom-count validation).
"""

from __future__ import annotations

from engines.chemistry_intelligence.engine import ChemistryIntelligenceEngine
from engines.chemistry_intelligence.pack import PACK_VERSION, ChemistryIntelligencePack
from engines.chemistry_intelligence.service import (
    CHEMISTRY_INTELLIGENCE_SMOKE_OK,
    analyse_chemistry_lesson,
    chemistry_quality_signals,
    get_chemistry_pack,
    pack_health,
    register_chemistry_pack,
)

register_chemistry_pack(overwrite=True)

__all__ = [
    "CHEMISTRY_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "ChemistryIntelligencePack",
    "ChemistryIntelligenceEngine",
    "get_chemistry_pack",
    "register_chemistry_pack",
    "analyse_chemistry_lesson",
    "chemistry_quality_signals",
    "pack_health",
]
