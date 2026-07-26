"""
World Languages Intelligence Pack (WLIP) — multilingual production SIF pack.

Plugin-based catalogues for world languages with pronunciation, grammar,
vocabulary, skills, culture, and translation metadata on SIF + SICS.
English subject ownership remains with ELIP (integration-only).
Does not invent curriculum or assessment answers.
"""

from __future__ import annotations

from engines.world_languages_intelligence.engine import WorldLanguagesIntelligenceEngine
from engines.world_languages_intelligence.language_plugins import (
    list_language_plugins,
    register_language_plugin,
)
from engines.world_languages_intelligence.pack import PACK_VERSION, WorldLanguagesIntelligencePack
from engines.world_languages_intelligence.service import (
    WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK,
    analyse_world_languages_lesson,
    get_world_languages_pack,
    pack_health,
    register_world_languages_pack,
    world_languages_quality_signals,
)

register_world_languages_pack(overwrite=True)

__all__ = [
    "WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "WorldLanguagesIntelligencePack",
    "WorldLanguagesIntelligenceEngine",
    "get_world_languages_pack",
    "register_world_languages_pack",
    "analyse_world_languages_lesson",
    "world_languages_quality_signals",
    "pack_health",
    "list_language_plugins",
    "register_language_plugin",
]
