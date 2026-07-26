"""
Physics Intelligence Pack (PIP) — second production Subject Intelligence Pack.

Teaching-layer pedagogy for physics. Plugs into SIF; does not invent physics
or replace Computation Layer solvers / diagram engines.
"""

from __future__ import annotations

from engines.physics_intelligence.engine import PhysicsIntelligenceEngine
from engines.physics_intelligence.pack import PACK_VERSION, PhysicsIntelligencePack
from engines.physics_intelligence.service import (
    PHYSICS_INTELLIGENCE_SMOKE_OK,
    analyse_physics_lesson,
    get_physics_pack,
    pack_health,
    physics_quality_signals,
    register_physics_pack,
)

register_physics_pack(overwrite=True)

__all__ = [
    "PHYSICS_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "PhysicsIntelligencePack",
    "PhysicsIntelligenceEngine",
    "get_physics_pack",
    "register_physics_pack",
    "analyse_physics_lesson",
    "physics_quality_signals",
    "pack_health",
]
