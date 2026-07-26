"""
Computer Science Intelligence Pack (CSIP) — technology production SIF pack.

Computational thinking, programming, algorithms, databases, networking,
cybersecurity, AI literacy, and related domains on SIF + SICS.
Does not invent curriculum or assessment answers.
"""

from __future__ import annotations

from engines.computer_science_intelligence.engine import ComputerScienceIntelligenceEngine
from engines.computer_science_intelligence.pack import PACK_VERSION, ComputerScienceIntelligencePack
from engines.computer_science_intelligence.service import (
    COMPUTER_SCIENCE_INTELLIGENCE_SMOKE_OK,
    analyse_computer_science_lesson,
    computer_science_quality_signals,
    get_computer_science_pack,
    pack_health,
    register_computer_science_pack,
)

register_computer_science_pack(overwrite=True)

__all__ = [
    "COMPUTER_SCIENCE_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "ComputerScienceIntelligencePack",
    "ComputerScienceIntelligenceEngine",
    "get_computer_science_pack",
    "register_computer_science_pack",
    "analyse_computer_science_lesson",
    "computer_science_quality_signals",
    "pack_health",
]
