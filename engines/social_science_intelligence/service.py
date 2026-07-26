"""Public service API for the Social Science Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.social_science_intelligence.pack import (
    PACK_VERSION,
    SocialScienceIntelligencePack,
    iter_family_packs,
)
from engines.social_science_intelligence.validation import collect_social_science_quality_signals
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface

SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK = True

_PACK: SocialScienceIntelligencePack | None = None


def get_social_science_pack() -> SocialScienceIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = SocialScienceIntelligencePack()
    return _PACK


def register_social_science_pack(*, overwrite: bool = True) -> SocialScienceIntelligencePack:
    """Register SSIP for social_science and related humanities subject keys."""
    primary = get_social_science_pack()
    for pack in iter_family_packs():
        get_registry().register(pack, overwrite=overwrite)
    return primary


def analyse_social_science_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_social_science_pack().analyse_lesson(uli, context)


def social_science_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_social_science_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_social_science_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("social_science")
    family_ok = all(
        not getattr(get_registry().get(key), "version", "").endswith("placeholder")
        for key in ("social_science", "history", "geography", "civics", "environmental_science")
    )
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION and family_ok,
        "smoke": SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
        "family_registered": family_ok,
    }


__all__ = [
    "SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "SocialScienceIntelligencePack",
    "get_social_science_pack",
    "register_social_science_pack",
    "analyse_social_science_lesson",
    "social_science_quality_signals",
    "pack_health",
]
