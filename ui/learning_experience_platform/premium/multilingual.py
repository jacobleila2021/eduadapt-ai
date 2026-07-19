"""UI locale strings — do not auto-translate verified curriculum."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.phase4_schemas import CURRICULUM_TRANSLATION_POLICY, SUPPORTED_UI_LOCALES

# Minimal UI catalog (extend via approved locale packs)
_UI: dict[str, dict[str, str]] = {
    "en": {
        "reader": "Reader",
        "revision": "Revision",
        "exam": "Exam",
        "settings": "Settings",
        "sync": "Sync",
        "offline": "Offline",
        "notifications": "Notifications",
        "reduce_motion": "Reduce motion",
        "install_app": "Install app",
        "curriculum_locked": "Verified curriculum is not auto-translated",
    },
    "hi": {
        "reader": "पाठक",
        "revision": "पुनरावृत्ति",
        "exam": "परीक्षा",
        "settings": "सेटिंग्स",
        "sync": "समन्वय",
        "offline": "ऑफ़लाइन",
        "notifications": "सूचनाएँ",
        "reduce_motion": "गति कम करें",
        "install_app": "ऐप स्थापित करें",
        "curriculum_locked": "सत्यापित पाठ्यक्रम स्वतः अनुवादित नहीं होता",
    },
}


def t(key: str, locale: str = "en") -> str:
    loc = locale if locale in SUPPORTED_UI_LOCALES else "en"
    return (_UI.get(loc) or _UI["en"]).get(key) or (_UI["en"].get(key) or key)


def locale_meta(locale: str = "en") -> dict[str, Any]:
    rtl_locales = {"ur"}  # future-ready; layout hooks only
    return {
        "locale": locale if locale in SUPPORTED_UI_LOCALES else "en",
        "dir": "rtl" if locale in rtl_locales else "ltr",
        "supported": list(SUPPORTED_UI_LOCALES),
        "curriculum_policy": CURRICULUM_TRANSLATION_POLICY,
        "fonts": {
            "en": "Lexend",
            "hi": "Noto Sans Devanagari",
            "default_fallback": "Noto Sans, Segoe UI, sans-serif",
        },
        "unicode": True,
        "vmle_narration": True,
        "dual_language_glossary": True,
    }
