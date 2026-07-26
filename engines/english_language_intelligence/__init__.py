"""
English Language Intelligence Pack (ELIP) — first non-STEM production SIF pack.

Literacy / language teaching layer built on SIF + SICS. Does not invent curriculum
or act as a grammar-checker / LLM wrapper.
"""

from __future__ import annotations

from engines.english_language_intelligence.engine import EnglishLanguageIntelligenceEngine
from engines.english_language_intelligence.pack import PACK_VERSION, EnglishLanguageIntelligencePack
from engines.english_language_intelligence.service import (
    ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK,
    analyse_english_lesson,
    english_quality_signals,
    get_english_pack,
    pack_health,
    register_english_pack,
)

register_english_pack(overwrite=True)

__all__ = [
    "ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "EnglishLanguageIntelligencePack",
    "EnglishLanguageIntelligenceEngine",
    "get_english_pack",
    "register_english_pack",
    "analyse_english_lesson",
    "english_quality_signals",
    "pack_health",
]
