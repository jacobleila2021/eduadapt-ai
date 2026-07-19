"""Multilingual narration & glossary — curriculum accuracy preserved."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.schemas import SUPPORTED_LANGUAGES

# Small curated glossary seeds (presentation); full i18n remains roadmap
_GLOSSARY = {
    "en": {"cell": "Basic unit of life", "force": "A push or a pull"},
    "hi": {"cell": "कोशिका — जीवन की मूल इकाई", "force": "बल — धक्का या खिंचाव"},
    "en-IN": {"cell": "Basic unit of life", "force": "A push or a pull"},
}


def settings(*, language: str = "en", dual_language: bool = False, subtitles: bool = True) -> dict[str, Any]:
    lang = language if language in SUPPORTED_LANGUAGES else "en"
    return {
        "language": lang,
        "supported": list(SUPPORTED_LANGUAGES),
        "dual_language_mode": dual_language,
        "subtitles": subtitles,
        "pronunciation_by_language": True,
        "policy": "translations_must_not_alter_verified_facts",
    }


def translate_term(term: str, *, language: str = "hi") -> dict[str, Any]:
    lang = language if language in SUPPORTED_LANGUAGES else "en"
    gloss = _GLOSSARY.get(lang) or {}
    key = (term or "").strip().lower()
    return {
        "term": term,
        "language": lang,
        "translation": gloss.get(key),
        "found": key in gloss,
        "note": "Extend via CIE/KIE glossary packs — do not LLM-invent curriculum terms",
    }


def dual_language_overlay(text_en: str, *, secondary: str = "hi") -> dict[str, Any]:
    return {
        "primary": {"language": "en", "text": text_en},
        "secondary": {"language": secondary, "text": None, "status": "resolve_via_translation_memory"},
        "subtitles": True,
    }
