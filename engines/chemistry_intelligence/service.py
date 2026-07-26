"""Public service API for the Chemistry Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.chemistry_intelligence.pack import PACK_VERSION, ChemistryIntelligencePack
from engines.chemistry_intelligence.validators import collect_chemistry_quality_signals
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface

CHEMISTRY_INTELLIGENCE_SMOKE_OK = True

_PACK: ChemistryIntelligencePack | None = None


def get_chemistry_pack() -> ChemistryIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = ChemistryIntelligencePack()
    return _PACK


def register_chemistry_pack(*, overwrite: bool = True) -> ChemistryIntelligencePack:
    pack = get_chemistry_pack()
    get_registry().register(pack, overwrite=overwrite)
    return pack


def analyse_chemistry_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_chemistry_pack().analyse_lesson(uli, context)


def chemistry_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_chemistry_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_chemistry_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("chemistry")
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION,
        "smoke": CHEMISTRY_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
    }


__all__ = [
    "CHEMISTRY_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "ChemistryIntelligencePack",
    "get_chemistry_pack",
    "register_chemistry_pack",
    "analyse_chemistry_lesson",
    "chemistry_quality_signals",
    "pack_health",
]
