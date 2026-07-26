"""Public service API for the Physics Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.physics_intelligence.pack import PACK_VERSION, PhysicsIntelligencePack
from engines.physics_intelligence.validators import collect_physics_quality_signals
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface

PHYSICS_INTELLIGENCE_SMOKE_OK = True

_PACK: PhysicsIntelligencePack | None = None


def get_physics_pack() -> PhysicsIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = PhysicsIntelligencePack()
    return _PACK


def register_physics_pack(*, overwrite: bool = True) -> PhysicsIntelligencePack:
    pack = get_physics_pack()
    get_registry().register(pack, overwrite=overwrite)
    return pack


def analyse_physics_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_physics_pack().analyse_lesson(uli, context)


def physics_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_physics_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_physics_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("physics")
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION,
        "smoke": PHYSICS_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
    }


__all__ = [
    "PHYSICS_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "PhysicsIntelligencePack",
    "get_physics_pack",
    "register_physics_pack",
    "analyse_physics_lesson",
    "physics_quality_signals",
    "pack_health",
]
