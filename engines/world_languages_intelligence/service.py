"""Public service API for the World Languages Intelligence Pack."""

from __future__ import annotations

from typing import Any, Mapping

from engines.subject_intelligence_framework.registry import get_registry
from engines.subject_intelligence_framework.schemas import SubjectAnalysisResult
from engines.subject_intelligence_framework.validators import validate_pack_interface
from engines.world_languages_intelligence.language_plugins import (
    list_language_plugins,
    register_language_plugin,
)
from engines.world_languages_intelligence.pack import PACK_VERSION, WorldLanguagesIntelligencePack
from engines.world_languages_intelligence.validation import collect_world_languages_quality_signals

WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK = True

_PACK: WorldLanguagesIntelligencePack | None = None


def get_world_languages_pack() -> WorldLanguagesIntelligencePack:
    global _PACK
    if _PACK is None:
        _PACK = WorldLanguagesIntelligencePack()
    return _PACK


def register_world_languages_pack(*, overwrite: bool = True) -> WorldLanguagesIntelligencePack:
    pack = get_world_languages_pack()
    get_registry().register(pack, overwrite=overwrite)
    return pack


def analyse_world_languages_lesson(
    uli: Any,
    *,
    context: Mapping[str, Any] | None = None,
) -> SubjectAnalysisResult:
    return get_world_languages_pack().analyse_lesson(uli, context)


def world_languages_quality_signals(uli: Any) -> dict[str, Any]:
    return collect_world_languages_quality_signals(uli)


def pack_health() -> dict[str, Any]:
    pack = get_world_languages_pack()
    iface = validate_pack_interface(pack)
    registered = get_registry().get("languages")
    plugins = list_language_plugins()
    return {
        "ok": iface.get("ok") is True and registered.version == PACK_VERSION and len(plugins) >= 16,
        "smoke": WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "interface": iface,
        "registered_version": getattr(registered, "version", None),
        "placeholder": getattr(registered, "version", "").endswith("placeholder"),
        "language_plugins": len(plugins),
    }


__all__ = [
    "WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "WorldLanguagesIntelligencePack",
    "get_world_languages_pack",
    "register_world_languages_pack",
    "analyse_world_languages_lesson",
    "world_languages_quality_signals",
    "pack_health",
    "list_language_plugins",
    "register_language_plugin",
]
