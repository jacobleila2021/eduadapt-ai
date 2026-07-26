"""
Commerce & Economics Intelligence Pack (CEIP) — commerce production SIF pack.

Accounting, economics, business studies, finance, entrepreneurship, marketing,
management, taxation, and financial literacy on SIF + SICS.
Does not invent curriculum or assessment answers.
"""

from __future__ import annotations

from engines.commerce_economics_intelligence.engine import CommerceEconomicsIntelligenceEngine
from engines.commerce_economics_intelligence.pack import PACK_VERSION, CommerceEconomicsIntelligencePack
from engines.commerce_economics_intelligence.service import (
    COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK,
    analyse_commerce_economics_lesson,
    commerce_economics_quality_signals,
    get_commerce_economics_pack,
    pack_health,
    register_commerce_economics_pack,
)

register_commerce_economics_pack(overwrite=True)

__all__ = [
    "COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "CommerceEconomicsIntelligencePack",
    "CommerceEconomicsIntelligenceEngine",
    "get_commerce_economics_pack",
    "register_commerce_economics_pack",
    "analyse_commerce_economics_lesson",
    "commerce_economics_quality_signals",
    "pack_health",
]
