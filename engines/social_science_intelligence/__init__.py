"""
Social Science Intelligence Pack (SSIP) — humanities production SIF pack.

History, geography, civics/political science, school economics, sociology, and
environmental studies metadata on SIF + SICS. Does not invent curriculum.
"""

from __future__ import annotations

from engines.social_science_intelligence.engine import SocialScienceIntelligenceEngine
from engines.social_science_intelligence.pack import PACK_VERSION, SocialScienceIntelligencePack
from engines.social_science_intelligence.service import (
    SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK,
    analyse_social_science_lesson,
    get_social_science_pack,
    pack_health,
    register_social_science_pack,
    social_science_quality_signals,
)

register_social_science_pack(overwrite=True)

__all__ = [
    "SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "SocialScienceIntelligencePack",
    "SocialScienceIntelligenceEngine",
    "get_social_science_pack",
    "register_social_science_pack",
    "analyse_social_science_lesson",
    "social_science_quality_signals",
    "pack_health",
]
