"""
Mathematics Intelligence Pack (MIP) — first production Subject Intelligence Pack.

Teaching-layer pedagogy for mathematics. Plugs into SIF; does not replace
Computation Layer (``engines.mathematics`` / SymPy) or invent curriculum.
"""

from __future__ import annotations

from engines.mathematics_intelligence.engine import MathematicsIntelligenceEngine
from engines.mathematics_intelligence.pack import MathematicsIntelligencePack, PACK_VERSION
from engines.mathematics_intelligence.service import (
    MATHEMATICS_INTELLIGENCE_SMOKE_OK,
    analyse_mathematics_lesson,
    get_mathematics_pack,
    math_quality_signals,
    pack_health,
    register_mathematics_pack,
)

# Auto-register over mathematics placeholder when the package is imported.
register_mathematics_pack(overwrite=True)

__all__ = [
    "MATHEMATICS_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "MathematicsIntelligencePack",
    "MathematicsIntelligenceEngine",
    "get_mathematics_pack",
    "register_mathematics_pack",
    "analyse_mathematics_lesson",
    "math_quality_signals",
    "pack_health",
]
