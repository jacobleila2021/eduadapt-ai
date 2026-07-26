"""CSIP quality signals for ULIQE — additive INFO only."""

from __future__ import annotations

from typing import Any, Mapping

from engines.computer_science_intelligence.algorithms import algorithms_metadata
from engines.computer_science_intelligence.artificial_intelligence import artificial_intelligence_metadata
from engines.computer_science_intelligence.databases import databases_metadata
from engines.computer_science_intelligence.domains import detect_domains
from engines.computer_science_intelligence.misconceptions import detect_computer_science_misconceptions
from engines.computer_science_intelligence.networking import networking_metadata
from engines.computer_science_intelligence.programming import programming_metadata
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


def collect_computer_science_quality_signals(uli: Any) -> dict[str, Any]:
    text = _source_text(uli)
    domains = detect_domains(text)
    misconceptions = detect_computer_science_misconceptions(text)
    programming = programming_metadata(text, domains)
    algorithms = algorithms_metadata(text, domains)
    databases = databases_metadata(text, domains)
    networking = networking_metadata(text, domains)
    ai = artificial_intelligence_metadata(text, domains)

    teaching = {
        "domains_detected": len(domains),
        "programming_foci": len(programming.get("foci") or []),
        "algorithms_foci": len(algorithms.get("foci") or []),
        "databases_foci": len(databases.get("foci") or []),
        "networking_foci": len(networking.get("foci") or []),
        "ai_foci": len(ai.get("foci") or []),
        "misconception_annotations": len(misconceptions),
    }

    findings_seed: list[dict[str, Any]] = []
    if domains:
        findings_seed.append(
            finding_seed(
                "ULIQE.CS.CSIP.000",
                "info",
                f"CSIP signals: {len(domains)} domain(s).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "programming" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CS.CSIP.PROGRAMMING",
                "info",
                f"Programming metadata active ({teaching['programming_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] in {"algorithms", "data_structures"} for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CS.CSIP.ALGORITHMS",
                "info",
                f"Algorithms/data-structure metadata active ({teaching['algorithms_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "databases" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CS.CSIP.DATABASES",
                "info",
                f"Database metadata active ({teaching['databases_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] in {"networking", "cybersecurity"} for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CS.CSIP.NETWORKING",
                "info",
                f"Networking/cyber metadata active ({teaching['networking_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] in {"artificial_intelligence", "machine_learning"} for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CS.CSIP.AI",
                "info",
                f"AI education metadata active ({teaching['ai_foci']} foci).",
                category="pedagogy",
            )
        )
    if misconceptions:
        findings_seed.append(
            finding_seed(
                "ULIQE.CS.CSIP.MISC",
                "info",
                f"Annotated {len(misconceptions)} computer science misconception pattern(s).",
                category="pedagogy",
            )
        )

    return {
        "domains": domains,
        "misconceptions": misconceptions,
        "programming": programming,
        "algorithms": algorithms,
        "databases": databases,
        "networking": networking,
        "artificial_intelligence": ai,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "computer_science_intelligence.validation",
    }
