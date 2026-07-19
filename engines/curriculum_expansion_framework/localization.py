"""Localization metadata — terminology & spelling; no auto curriculum translation."""

from __future__ import annotations

from typing import Any

# Regional terminology aliases (UI / search only — not curriculum rewrites)
TERMINOLOGY: dict[str, dict[str, str]] = {
    "en-IN": {"maths": "mathematics", "class": "grade"},
    "en-GB": {"math": "mathematics", "grade": "year"},
    "en-US": {"maths": "mathematics", "year": "grade"},
}

SPELLING_VARIANTS = {
    "colour": "color",
    "organise": "organize",
    "centre": "center",
    "metre": "meter",
}


def localization_profile(locale: str = "en-IN") -> dict[str, Any]:
    return {
        "locale": locale,
        "terminology": TERMINOLOGY.get(locale) or TERMINOLOGY.get("en-IN") or {},
        "spelling_variants": SPELLING_VARIANTS,
        "rtl_ready": locale.lower().startswith("ur") or locale.lower().endswith("-arab"),
        "policy": {
            "never_auto_translate_verified_curriculum": True,
            "approved_locale_bundles_only": True,
        },
    }


def normalize_search_term(term: str, locale: str = "en-IN") -> str:
    t = (term or "").strip().lower()
    aliases = localization_profile(locale).get("terminology") or {}
    return aliases.get(t, t)
