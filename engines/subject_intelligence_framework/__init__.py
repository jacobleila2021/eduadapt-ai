"""
Subject Intelligence Framework (SIF) — core architecture.

Plug-in framework for subject-specific intelligence packs.
Does not implement Mathematics/Physics/… logic yet — placeholders only.
"""

from __future__ import annotations

from engines.subject_intelligence_framework.engine import SubjectIntelligenceFrameworkEngine
from engines.subject_intelligence_framework.interfaces import (
    PlaceholderSubjectPack,
    SubjectIntelligencePack,
)
from engines.subject_intelligence_framework.registry import get_registry, reset_registry_for_tests
from engines.subject_intelligence_framework.service import (
    SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK,
    capability_matrix,
    enrich_uli_with_subject_intelligence,
    list_subject_packs,
    lxp_hook_catalogue,
    validate_pack_interface,
    validate_registry,
)
from engines.subject_intelligence_framework.subject_profile import detect_subject_from_uli

# Ensure production packs (e.g. Mathematics / Physics Intelligence Packs) replace placeholders.
try:
    import engines.mathematics_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass
try:
    import engines.physics_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass
try:
    import engines.chemistry_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass
try:
    import engines.biology_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass
try:
    import engines.english_language_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass
try:
    import engines.social_science_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass
try:
    import engines.computer_science_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass
try:
    import engines.commerce_economics_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass
try:
    import engines.world_languages_intelligence  # noqa: F401
except Exception:  # noqa: BLE001
    pass

__all__ = [
    "SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK",
    "SubjectIntelligencePack",
    "PlaceholderSubjectPack",
    "SubjectIntelligenceFrameworkEngine",
    "get_registry",
    "reset_registry_for_tests",
    "list_subject_packs",
    "enrich_uli_with_subject_intelligence",
    "detect_subject_from_uli",
    "capability_matrix",
    "lxp_hook_catalogue",
    "validate_registry",
    "validate_pack_interface",
]
