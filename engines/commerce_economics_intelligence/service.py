"""Public service API for the Commerce & Economics Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.commerce_economics_intelligence.pack import (
    PACK_VERSION,
    CommerceEconomicsIntelligencePack,
    iter_family_packs,
)
from engines.commerce_economics_intelligence.validation import collect_commerce_economics_quality_signals
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface

COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK = True

_PACK: CommerceEconomicsIntelligencePack | None = None


def get_commerce_economics_pack() -> CommerceEconomicsIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = CommerceEconomicsIntelligencePack()
    return _PACK


def register_commerce_economics_pack(*, overwrite: bool = True) -> CommerceEconomicsIntelligencePack:
    """Register CEIP for commerce, economics, and business_studies."""
    primary = get_commerce_economics_pack()
    for pack in iter_family_packs():
        get_registry().register(pack, overwrite=overwrite)
    return primary


def analyse_commerce_economics_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_commerce_economics_pack().analyse_lesson(uli, context)


def commerce_economics_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_commerce_economics_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_commerce_economics_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("commerce")
    family_ok = all(
        not getattr(get_registry().get(key), "version", "").endswith("placeholder")
        for key in ("commerce", "economics", "business_studies")
    )
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION and family_ok,
        "smoke": COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
        "family_registered": family_ok,
    }


__all__ = [
    "COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "CommerceEconomicsIntelligencePack",
    "get_commerce_economics_pack",
    "register_commerce_economics_pack",
    "analyse_commerce_economics_lesson",
    "commerce_economics_quality_signals",
    "pack_health",
]
