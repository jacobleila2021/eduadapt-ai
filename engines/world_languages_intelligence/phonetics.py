"""Phonetics / script / alphabet intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

PHONETICS_FOCI: tuple[dict[str, str], ...] = (
    {"id": "alphabet_systems", "label": "Alphabet systems"},
    {"id": "scripts", "label": "Scripts"},
    {"id": "ipa_mappings", "label": "IPA mappings"},
    {"id": "phonics", "label": "Phonics"},
    {"id": "phonemes", "label": "Phonemes"},
    {"id": "morphology_sounds", "label": "Sound–spelling links"},
)


def phonetics_metadata(
    text: str,
    domains: list[dict[str, Any]],
    languages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    scripts = sorted({s for lang in (languages or []) for s in (lang.get("scripts") or [])})
    return build_focus_metadata(
        foci_catalogue=PHONETICS_FOCI,
        text=text,
        domains=domains,
        domain_keys={"phonetics", "pronunciation"},
        provenance="world_languages_intelligence.phonetics",
        extra={
            "scripts_detected": scripts,
            "ipa_viewer": True,
            "owner_engine": "VMLE",
        },
    )
