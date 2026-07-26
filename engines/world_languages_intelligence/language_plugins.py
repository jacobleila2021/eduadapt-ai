"""World-language plugin catalogue — extend without engine changes."""

from __future__ import annotations

from typing import Any

# English is integration-only: ELIP owns the `english` SIF subject key.
# WLIP may annotate English when a multilingual lesson references it.
LANGUAGE_PLUGINS: dict[str, dict[str, Any]] = {
    "english": {
        "code": "en",
        "name": "English",
        "scripts": ["Latin"],
        "direction": "ltr",
        "integration_only": True,
        "authoritative_pack": "english_language_intelligence",
        "pronunciation_notes": ["stress-timed", "reduced_vowels"],
        "grammar_highlights": ["articles", "tense_aspect", "word_order_svo"],
    },
    "french": {
        "code": "fr",
        "name": "French",
        "scripts": ["Latin"],
        "direction": "ltr",
        "pronunciation_notes": ["nasal_vowels", "liaison"],
        "grammar_highlights": ["gender", "agreement", "passe_compose"],
    },
    "german": {
        "code": "de",
        "name": "German",
        "scripts": ["Latin"],
        "direction": "ltr",
        "pronunciation_notes": ["final_devoicing", "umlaut"],
        "grammar_highlights": ["cases", "verb_second", "compound_nouns"],
    },
    "spanish": {
        "code": "es",
        "name": "Spanish",
        "scripts": ["Latin"],
        "direction": "ltr",
        "pronunciation_notes": ["syllable_timed", "rolled_r"],
        "grammar_highlights": ["ser_estar", "subjunctive", "gender"],
    },
    "italian": {
        "code": "it",
        "name": "Italian",
        "scripts": ["Latin"],
        "direction": "ltr",
        "pronunciation_notes": ["double_consonants", "open_closed_e"],
        "grammar_highlights": ["gender", "passato_prossimo", "clitics"],
    },
    "portuguese": {
        "code": "pt",
        "name": "Portuguese",
        "scripts": ["Latin"],
        "direction": "ltr",
        "pronunciation_notes": ["nasal_vowels", "european_vs_brazilian"],
        "grammar_highlights": ["personal_infinitive", "gender", "ser_estar"],
    },
    "arabic": {
        "code": "ar",
        "name": "Arabic",
        "scripts": ["Arabic"],
        "direction": "rtl",
        "pronunciation_notes": ["emphatics", "pharyngeals"],
        "grammar_highlights": ["root_pattern", "dual", "idafa"],
    },
    "hindi": {
        "code": "hi",
        "name": "Hindi",
        "scripts": ["Devanagari"],
        "direction": "ltr",
        "pronunciation_notes": ["aspirated_stops", "retroflex"],
        "grammar_highlights": ["postpositions", "gender", "ergativity_perfective"],
    },
    "malayalam": {
        "code": "ml",
        "name": "Malayalam",
        "scripts": ["Malayalam"],
        "direction": "ltr",
        "pronunciation_notes": ["retroflex", "alveolar_stops"],
        "grammar_highlights": ["agglutinative", "SOV", "cases"],
    },
    "tamil": {
        "code": "ta",
        "name": "Tamil",
        "scripts": ["Tamil"],
        "direction": "ltr",
        "pronunciation_notes": ["short_long_vowels", "retroflex"],
        "grammar_highlights": ["agglutinative", "SOV", "honorifics"],
    },
    "kannada": {
        "code": "kn",
        "name": "Kannada",
        "scripts": ["Kannada"],
        "direction": "ltr",
        "pronunciation_notes": ["aspirates", "retroflex"],
        "grammar_highlights": ["agglutinative", "SOV", "cases"],
    },
    "telugu": {
        "code": "te",
        "name": "Telugu",
        "scripts": ["Telugu"],
        "direction": "ltr",
        "pronunciation_notes": ["aspirates", "retroflex"],
        "grammar_highlights": ["agglutinative", "SOV", "cases"],
    },
    "japanese": {
        "code": "ja",
        "name": "Japanese",
        "scripts": ["Hiragana", "Katakana", "Kanji"],
        "direction": "ltr",
        "pronunciation_notes": ["mora_timed", "pitch_accent"],
        "grammar_highlights": ["particles", "politeness", "SOV"],
    },
    "korean": {
        "code": "ko",
        "name": "Korean",
        "scripts": ["Hangul"],
        "direction": "ltr",
        "pronunciation_notes": ["batchim", "vowel_harmony_historical"],
        "grammar_highlights": ["honorifics", "particles", "SOV"],
    },
    "chinese": {
        "code": "zh",
        "name": "Chinese",
        "scripts": ["Hanzi", "Pinyin"],
        "direction": "ltr",
        "pronunciation_notes": ["tones", "pinyin"],
        "grammar_highlights": ["aspect", "classifiers", "topic_comment"],
    },
    "latin": {
        "code": "la",
        "name": "Latin",
        "scripts": ["Latin"],
        "direction": "ltr",
        "pronunciation_notes": ["classical_vs_ecclesiastical", "vowel_quantity"],
        "grammar_highlights": ["cases", "conjugation", "SOV_flexible"],
    },
    "greek": {
        "code": "el",
        "name": "Greek",
        "scripts": ["Greek"],
        "direction": "ltr",
        "pronunciation_notes": ["modern_vs_ancient", "stress_accent"],
        "grammar_highlights": ["cases", "aspect", "articles"],
    },
}

# Aliases for detection in lesson text / subject lines
LANGUAGE_ALIASES: dict[str, str] = {
    "en": "english",
    "fr": "french",
    "de": "german",
    "es": "spanish",
    "it": "italian",
    "pt": "portuguese",
    "ar": "arabic",
    "hi": "hindi",
    "ml": "malayalam",
    "ta": "tamil",
    "kn": "kannada",
    "te": "telugu",
    "ja": "japanese",
    "jp": "japanese",
    "ko": "korean",
    "zh": "chinese",
    "mandarin": "chinese",
    "la": "latin",
    "el": "greek",
    "ancient greek": "greek",
}


def list_language_plugins() -> list[dict[str, Any]]:
    return [
        {"id": key, **{k: v for k, v in meta.items() if k != "id"}}
        for key, meta in LANGUAGE_PLUGINS.items()
    ]


def get_language_plugin(language_id: str) -> dict[str, Any] | None:
    key = (language_id or "").strip().lower().replace("-", "_").replace(" ", "_")
    key = LANGUAGE_ALIASES.get(key, key)
    meta = LANGUAGE_PLUGINS.get(key)
    if not meta:
        return None
    return {"id": key, **meta}


def detect_languages(text: str) -> list[dict[str, Any]]:
    """Detect referenced world languages from lesson text (catalogue-bound)."""
    blob = (text or "").lower()
    found: list[dict[str, Any]] = []
    for lang_id, meta in LANGUAGE_PLUGINS.items():
        markers = {lang_id, meta.get("name", "").lower(), meta.get("code", "").lower()}
        markers |= {s.lower() for s in (meta.get("scripts") or [])}
        if any(m and m in blob for m in markers):
            found.append({"id": lang_id, **meta})
    return found


def register_language_plugin(language_id: str, meta: dict[str, Any], *, overwrite: bool = False) -> dict[str, Any]:
    """Plug in an additional language without changing pack engines."""
    key = (language_id or "").strip().lower().replace(" ", "_")
    if not key:
        raise ValueError("language_id required")
    if key in LANGUAGE_PLUGINS and not overwrite:
        raise ValueError(f"Language plugin already exists: {key}")
    required = {"code", "name", "scripts", "direction"}
    missing = required - set(meta)
    if missing:
        raise ValueError(f"Missing language plugin fields: {sorted(missing)}")
    LANGUAGE_PLUGINS[key] = dict(meta)
    return get_language_plugin(key) or {"id": key, **meta}
