"""Public service API for the English Language Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.english_language_intelligence.pack import PACK_VERSION, EnglishLanguageIntelligencePack
from engines.english_language_intelligence.validation import collect_english_quality_signals
from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface

ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK = True

_PACK: EnglishLanguageIntelligencePack | None = None


def get_english_pack() -> EnglishLanguageIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = EnglishLanguageIntelligencePack()
    return _PACK


def register_english_pack(*, overwrite: bool = True) -> EnglishLanguageIntelligencePack:
    pack = get_english_pack()
    get_registry().register(pack, overwrite=overwrite)
    return pack


def analyse_english_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_english_pack().analyse_lesson(uli, context)


def english_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_english_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_english_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("english")
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION,
        "smoke": ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
    }


__all__ = [
    "ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "EnglishLanguageIntelligencePack",
    "get_english_pack",
    "register_english_pack",
    "analyse_english_lesson",
    "english_quality_signals",
    "pack_health",
]
