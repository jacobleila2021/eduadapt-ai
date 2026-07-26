"""Public service API for the Computer Science Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.computer_science_intelligence.pack import PACK_VERSION, ComputerScienceIntelligencePack
from engines.computer_science_intelligence.validation import collect_computer_science_quality_signals
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface

COMPUTER_SCIENCE_INTELLIGENCE_SMOKE_OK = True

_PACK: ComputerScienceIntelligencePack | None = None


def get_computer_science_pack() -> ComputerScienceIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = ComputerScienceIntelligencePack()
    return _PACK


def register_computer_science_pack(*, overwrite: bool = True) -> ComputerScienceIntelligencePack:
    pack = get_computer_science_pack()
    get_registry().register(pack, overwrite=overwrite)
    return pack


def analyse_computer_science_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_computer_science_pack().analyse_lesson(uli, context)


def computer_science_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_computer_science_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_computer_science_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("computer_science")
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION,
        "smoke": COMPUTER_SCIENCE_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
    }


__all__ = [
    "COMPUTER_SCIENCE_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "ComputerScienceIntelligencePack",
    "get_computer_science_pack",
    "register_computer_science_pack",
    "analyse_computer_science_lesson",
    "computer_science_quality_signals",
    "pack_health",
]
