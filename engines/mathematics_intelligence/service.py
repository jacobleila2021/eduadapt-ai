"""Public service API for the Mathematics Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.mathematics_intelligence.pack import MathematicsIntelligencePack, PACK_VERSION
from engines.mathematics_intelligence.validators import collect_math_quality_signals
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface

MATHEMATICS_INTELLIGENCE_SMOKE_OK = True

_PACK: MathematicsIntelligencePack | None = None


def get_mathematics_pack() -> MathematicsIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = MathematicsIntelligencePack()
    return _PACK


def register_mathematics_pack(*, overwrite: bool = True) -> MathematicsIntelligencePack:
    """Register MIP over the mathematics placeholder in the SIF registry."""
    pack = get_mathematics_pack()
    get_registry().register(pack, overwrite=overwrite)
    return pack


def analyse_mathematics_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_mathematics_pack().analyse_lesson(uli, context)


def math_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_math_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_mathematics_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("mathematics")
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION,
        "smoke": MATHEMATICS_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
    }


__all__ = [
    "MATHEMATICS_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "MathematicsIntelligencePack",
    "get_mathematics_pack",
    "register_mathematics_pack",
    "analyse_mathematics_lesson",
    "math_quality_signals",
    "pack_health",
]
