"""
Subject Intelligence Core Services (SICS) — shared infrastructure for SIF packs.

Consolidates pedagogy, misconception detection, taxonomy, assessment metadata,
accessibility, tutor metadata, diagrams, analytics, and validation helpers.

Does not teach subjects, invent curriculum, or replace ATIE/AIE/AME/LAIE/ULIQE.
"""

from __future__ import annotations

from engines.subject_intelligence_core.engine import SubjectIntelligenceCoreEngine
from engines.subject_intelligence_core.service import (
    SUBJECT_INTELLIGENCE_CORE_SMOKE_OK,
    SHARED_STRATEGY_CATALOGUE,
    core_health,
    demo_capabilities,
)

__all__ = [
    "SUBJECT_INTELLIGENCE_CORE_SMOKE_OK",
    "SHARED_STRATEGY_CATALOGUE",
    "SubjectIntelligenceCoreEngine",
    "core_health",
    "demo_capabilities",
]
