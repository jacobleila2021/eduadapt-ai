"""Public service API for the Biology Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.biology_intelligence.pack import PACK_VERSION, BiologyIntelligencePack
from engines.biology_intelligence.validators import collect_biology_quality_signals
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface

BIOLOGY_INTELLIGENCE_SMOKE_OK = True

_PACK: BiologyIntelligencePack | None = None


def get_biology_pack() -> BiologyIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = BiologyIntelligencePack()
    return _PACK


def register_biology_pack(*, overwrite: bool = True) -> BiologyIntelligencePack:
    pack = get_biology_pack()
    get_registry().register(pack, overwrite=overwrite)
    return pack


def analyse_biology_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_biology_pack().analyse_lesson(uli, context)


def biology_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_biology_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_biology_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("biology")
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION,
        "smoke": BIOLOGY_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
    }


__all__ = [
    "BIOLOGY_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "BiologyIntelligencePack",
    "get_biology_pack",
    "register_biology_pack",
    "analyse_biology_lesson",
    "biology_quality_signals",
    "pack_health",
]
