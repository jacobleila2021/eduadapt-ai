"""ELIP quality signals for ULIQE — additive INFO/WARNING only."""

from __future__ import annotations

from typing import Any, Mapping

from engines.english_language_intelligence.domains import detect_domains
from engines.english_language_intelligence.grammar import grammar_metadata
from engines.english_language_intelligence.literature import literature_metadata
from engines.english_language_intelligence.misconceptions import detect_english_misconceptions
from engines.english_language_intelligence.reading import reading_metadata
from engines.english_language_intelligence.vocabulary import vocabulary_metadata
from engines.english_language_intelligence.writing import writing_metadata
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


def collect_english_quality_signals(uli: Any) -> dict[str, Any]:
    text = _source_text(uli)
    domains = detect_domains(text)
    misconceptions = detect_english_misconceptions(text)
    reading = reading_metadata(text, domains)
    vocab = vocabulary_metadata(text, uli)
    grammar = grammar_metadata(text, domains)
    writing = writing_metadata(text, domains)
    literature = literature_metadata(text, domains)

    teaching = {
        "domains_detected": len(domains),
        "reading_capabilities": len(reading.get("capabilities") or []),
        "vocabulary_entries": len(vocab.get("entries") or []),
        "grammar_foci": len(grammar.get("foci") or []),
        "writing_modes": len(writing.get("modes") or []),
        "literature_lenses": len(literature.get("lenses") or []),
        "misconception_annotations": len(misconceptions),
    }

    findings_seed: list[dict[str, Any]] = []
    if domains:
        findings_seed.append(
            finding_seed(
                "ULIQE.ENG.ELIP.000",
                "info",
                (
                    f"ELIP signals: {len(domains)} domain(s), "
                    f"reading={teaching['reading_capabilities']}, "
                    f"vocab={teaching['vocabulary_entries']}."
                ),
                category="pedagogy",
            )
        )
    if any(d["domain"] == "reading" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.ENG.ELIP.READING",
                "info",
                f"Reading metadata active ({teaching['reading_capabilities']} capabilities).",
                category="pedagogy",
            )
        )
    if teaching["vocabulary_entries"]:
        findings_seed.append(
            finding_seed(
                "ULIQE.ENG.ELIP.VOCAB",
                "info",
                f"Vocabulary scaffolds proposed for {teaching['vocabulary_entries']} term(s).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "grammar" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.ENG.ELIP.GRAMMAR",
                "info",
                f"Grammar foci annotated ({teaching['grammar_foci']}).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "writing" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.ENG.ELIP.WRITING",
                "info",
                "Writing guidance metadata present (no auto-generated assessment answers).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "literature" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.ENG.ELIP.LITERATURE",
                "info",
                f"Literature lenses annotated ({teaching['literature_lenses']}).",
                category="pedagogy",
            )
        )
    if misconceptions:
        findings_seed.append(
            finding_seed(
                "ULIQE.ENG.ELIP.MISC",
                "info",
                f"Annotated {len(misconceptions)} English misconception pattern(s).",
                category="pedagogy",
            )
        )

    return {
        "domains": domains,
        "misconceptions": misconceptions,
        "reading": reading,
        "vocabulary": vocab,
        "grammar": grammar,
        "writing": writing,
        "literature": literature,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "english_language_intelligence.validation",
    }
