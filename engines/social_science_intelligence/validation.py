"""SSIP quality signals for ULIQE — additive INFO only."""

from __future__ import annotations

from typing import Any, Mapping

from engines.social_science_intelligence.civics import civics_metadata
from engines.social_science_intelligence.domains import detect_domains
from engines.social_science_intelligence.economics import economics_metadata
from engines.social_science_intelligence.geography import geography_metadata
from engines.social_science_intelligence.history import history_metadata
from engines.social_science_intelligence.misconceptions import detect_social_science_misconceptions
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


def collect_social_science_quality_signals(uli: Any) -> dict[str, Any]:
    text = _source_text(uli)
    domains = detect_domains(text)
    misconceptions = detect_social_science_misconceptions(text)
    history = history_metadata(text, domains)
    geography = geography_metadata(text, domains)
    civics = civics_metadata(text, domains)
    economics = economics_metadata(text, domains)

    teaching = {
        "domains_detected": len(domains),
        "history_foci": len(history.get("foci") or []),
        "geography_foci": len(geography.get("foci") or []),
        "civics_foci": len(civics.get("foci") or []),
        "economics_foci": len(economics.get("foci") or []),
        "misconception_annotations": len(misconceptions),
    }

    findings_seed: list[dict[str, Any]] = []
    if domains:
        findings_seed.append(
            finding_seed(
                "ULIQE.SOC.SSIP.000",
                "info",
                f"SSIP signals: {len(domains)} domain(s).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "history" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.SOC.SSIP.HISTORY",
                "info",
                f"History metadata active ({teaching['history_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "geography" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.SOC.SSIP.GEOGRAPHY",
                "info",
                f"Geography metadata active ({teaching['geography_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] in {"civics", "political_science"} for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.SOC.SSIP.CIVICS",
                "info",
                f"Civics/political metadata active ({teaching['civics_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "economics" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.SOC.SSIP.ECONOMICS",
                "info",
                f"Economics metadata active ({teaching['economics_foci']} foci).",
                category="pedagogy",
            )
        )
    if misconceptions:
        findings_seed.append(
            finding_seed(
                "ULIQE.SOC.SSIP.MISC",
                "info",
                f"Annotated {len(misconceptions)} social science misconception pattern(s).",
                category="pedagogy",
            )
        )

    return {
        "domains": domains,
        "misconceptions": misconceptions,
        "history": history,
        "geography": geography,
        "civics": civics,
        "economics": economics,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "social_science_intelligence.validation",
    }
