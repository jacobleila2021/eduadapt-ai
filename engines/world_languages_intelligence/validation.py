"""WLIP quality signals for ULIQE — additive INFO only."""

from __future__ import annotations

from typing import Any, Mapping

from engines.world_languages_intelligence.domains import detect_domains
from engines.world_languages_intelligence.grammar import grammar_metadata
from engines.world_languages_intelligence.language_plugins import detect_languages
from engines.world_languages_intelligence.misconceptions import detect_world_languages_misconceptions
from engines.world_languages_intelligence.pronunciation import pronunciation_metadata
from engines.world_languages_intelligence.reading import reading_metadata
from engines.world_languages_intelligence.vocabulary import vocabulary_metadata
from engines.world_languages_intelligence.writing import writing_metadata
from engines.subject_intelligence_core.utilities import envelope_text
from engines.subject_intelligence_core.validation import finding_seed


def _source_text(uli: Any) -> str:
    parts = [envelope_text(uli)]
    try:
        learn = dict(uli.learning_structure())
        for c in learn.get("key_concepts") or []:
            if isinstance(c, Mapping):
                parts.append(str(c.get("concept") or ""))
        for o in learn.get("learning_objectives") or []:
            if isinstance(o, Mapping):
                parts.append(str(o.get("objective") or ""))
            else:
                parts.append(str(o))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


def collect_world_languages_quality_signals(uli: Any) -> dict[str, Any]:
    text = _source_text(uli)
    domains = detect_domains(text)
    languages = detect_languages(text)
    misconceptions = detect_world_languages_misconceptions(text)
    pronunciation = pronunciation_metadata(text, domains, languages)
    grammar = grammar_metadata(text, domains, languages)
    reading = reading_metadata(text, domains)
    writing = writing_metadata(text, domains)
    vocabulary = vocabulary_metadata(text, domains, uli)

    teaching = {
        "domains_detected": len(domains),
        "languages_detected": len(languages),
        "pronunciation_foci": len(pronunciation.get("foci") or []),
        "grammar_foci": len(grammar.get("foci") or []),
        "reading_foci": len(reading.get("foci") or []),
        "writing_foci": len(writing.get("foci") or []),
        "vocabulary_foci": len(vocabulary.get("foci") or []),
        "misconception_annotations": len(misconceptions),
    }

    findings_seed: list[dict[str, Any]] = []
    if domains or languages:
        findings_seed.append(
            finding_seed(
                "ULIQE.WLIP.000",
                "info",
                f"WLIP signals: {len(domains)} domain(s), {len(languages)} language(s).",
                category="pedagogy",
            )
        )
    if any(d["domain"] in {"pronunciation", "phonetics"} for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.WLIP.PRONUNCIATION",
                "info",
                f"Pronunciation metadata active ({teaching['pronunciation_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "grammar" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.WLIP.GRAMMAR",
                "info",
                f"Grammar metadata active ({teaching['grammar_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "reading" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.WLIP.READING",
                "info",
                f"Reading metadata active ({teaching['reading_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "writing" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.WLIP.WRITING",
                "info",
                f"Writing metadata active ({teaching['writing_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "vocabulary" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.WLIP.VOCABULARY",
                "info",
                f"Vocabulary metadata active ({teaching['vocabulary_foci']} foci).",
                category="pedagogy",
            )
        )
    if misconceptions:
        findings_seed.append(
            finding_seed(
                "ULIQE.WLIP.MISC",
                "info",
                f"Annotated {len(misconceptions)} world-language misconception pattern(s).",
                category="pedagogy",
            )
        )

    return {
        "domains": domains,
        "languages": languages,
        "misconceptions": misconceptions,
        "pronunciation": pronunciation,
        "grammar": grammar,
        "reading": reading,
        "writing": writing,
        "vocabulary": vocabulary,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "world_languages_intelligence.validation",
    }
