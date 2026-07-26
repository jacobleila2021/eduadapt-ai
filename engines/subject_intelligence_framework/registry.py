"""Subject Intelligence Framework — plug-in registry."""

from __future__ import annotations

from typing import Iterable

from engines.subject_intelligence_framework.interfaces import (
    PlaceholderSubjectPack,
    SubjectIntelligencePack,
)
from engines.subject_intelligence_framework.schemas import SubjectId

# Initial plug-in registry (placeholders only — no subject logic yet)
_REGISTERED_SUBJECTS: tuple[SubjectId, ...] = (
    SubjectId("mathematics", "Mathematics", "stem"),
    SubjectId("physics", "Physics", "stem"),
    SubjectId("chemistry", "Chemistry", "stem"),
    SubjectId("biology", "Biology", "stem"),
    SubjectId("english", "English", "languages"),
    SubjectId("social_science", "Social Science", "humanities"),
    SubjectId("computer_science", "Computer Science", "stem"),
    SubjectId("commerce", "Commerce", "commerce"),
    SubjectId("economics", "Economics", "commerce"),
    SubjectId("business_studies", "Business Studies", "commerce"),
    SubjectId("geography", "Geography", "humanities"),
    SubjectId("history", "History", "humanities"),
    SubjectId("civics", "Civics", "humanities"),
    SubjectId("environmental_science", "Environmental Science", "stem"),
    SubjectId("languages", "Languages", "languages"),
    SubjectId("general", "General / Mixed", "general"),
)


class SubjectPackRegistry:
    """In-memory registry of subject intelligence packs."""

    def __init__(self) -> None:
        self._packs: dict[str, SubjectIntelligencePack] = {}
        self._register_placeholders()

    def _register_placeholders(self) -> None:
        for subject in _REGISTERED_SUBJECTS:
            if subject.key not in self._packs:
                self._packs[subject.key] = PlaceholderSubjectPack(subject)

    def register(self, pack: SubjectIntelligencePack, *, overwrite: bool = False) -> None:
        key = pack.subject.key
        if key in self._packs and not overwrite and not isinstance(self._packs[key], PlaceholderSubjectPack):
            raise ValueError(f"Subject pack already registered: {key}")
        self._packs[key] = pack

    def get(self, subject_key: str) -> SubjectIntelligencePack:
        key = (subject_key or "general").strip().lower().replace(" ", "_")
        if key not in self._packs:
            return self._packs["general"]
        return self._packs[key]

    def list_subjects(self) -> list[dict]:
        return [
            {
                **pack.subject.to_dict(),
                "version": pack.version,
                "placeholder": isinstance(pack, PlaceholderSubjectPack),
                "capabilities": [c.to_dict() for c in pack.capabilities()],
            }
            for pack in self._packs.values()
        ]

    def keys(self) -> list[str]:
        return sorted(self._packs.keys())

    def __contains__(self, subject_key: str) -> bool:
        return subject_key in self._packs

    def __iter__(self) -> Iterable[SubjectIntelligencePack]:
        return iter(self._packs.values())


_REGISTRY: SubjectPackRegistry | None = None


def _ensure_production_packs(registry: SubjectPackRegistry) -> None:
    """Register real Subject Intelligence Packs over placeholders (lazy import)."""
    try:
        from engines.mathematics_intelligence.service import register_mathematics_pack

        register_mathematics_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    try:
        from engines.physics_intelligence.service import register_physics_pack

        register_physics_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    try:
        from engines.chemistry_intelligence.service import register_chemistry_pack

        register_chemistry_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    try:
        from engines.biology_intelligence.service import register_biology_pack

        register_biology_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    try:
        from engines.english_language_intelligence.service import register_english_pack

        register_english_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    try:
        from engines.social_science_intelligence.service import register_social_science_pack

        register_social_science_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    try:
        from engines.computer_science_intelligence.service import register_computer_science_pack

        register_computer_science_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    try:
        from engines.commerce_economics_intelligence.service import register_commerce_economics_pack

        register_commerce_economics_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    try:
        from engines.world_languages_intelligence.service import register_world_languages_pack

        register_world_languages_pack(overwrite=True)
    except Exception:  # noqa: BLE001
        pass
    _ = registry


def get_registry() -> SubjectPackRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = SubjectPackRegistry()
        _ensure_production_packs(_REGISTRY)
    return _REGISTRY


def reset_registry_for_tests() -> SubjectPackRegistry:
    global _REGISTRY
    _REGISTRY = SubjectPackRegistry()
    _ensure_production_packs(_REGISTRY)
    return _REGISTRY
