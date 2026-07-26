"""Social science misconceptions — SICS catalogue detection."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

SOCIAL_SCIENCE_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "soc.history_inevitable",
        "label": "Historical events were inevitable",
        "domain": "history",
        "patterns": [
            r"history\s*(was\s*)?inevitable",
            r"events?\s*(had\s*)?to\s*happen\s*(this\s*)?way",
            r"no\s*other\s*outcome\s*was\s*possible",
        ],
        "correction": "Outcomes had contingent causes; examine alternatives, agency, and evidence—not destiny.",
        "related_concepts": ["causation", "contingency", "agency"],
    },
    {
        "misconception_id": "soc.map_equals_territory",
        "label": "A map is a complete picture of reality",
        "domain": "geography",
        "patterns": [
            r"maps?\s*(show|are)\s*(the\s*)?whole\s*truth",
            r"map\s*(is\s*)?(always\s*)?accurate",
            r"borders?\s*(are\s*)?natural",
        ],
        "correction": "Maps are selective representations with projections, scale, and purpose; read the legend and date.",
        "related_concepts": ["map_skills", "projection", "scale"],
    },
    {
        "misconception_id": "soc.democracy_only_voting",
        "label": "Democracy is only about voting",
        "domain": "civics",
        "patterns": [
            r"democracy\s*(is\s*)?(only|just)\s*(about\s*)?voting",
            r"voting\s*(is\s*)?(the\s*)?only\s*civic\s*duty",
        ],
        "correction": "Democracy also includes rights, rule of law, participation, accountability, and institutions.",
        "related_concepts": ["citizenship", "rule_of_law", "participation"],
    },
    {
        "misconception_id": "soc.price_only_seller",
        "label": "Prices are set only by sellers",
        "domain": "economics",
        "patterns": [
            r"sellers?\s*(alone\s*)?(set|decide)\s*prices?",
            r"demand\s*(does\s*not|doesn't)\s*affect\s*price",
        ],
        "correction": "In market models, price reflects interaction of supply and demand (with institutions/rules).",
        "related_concepts": ["supply", "demand", "markets"],
    },
    {
        "misconception_id": "soc.climate_equals_weather",
        "label": "Climate and weather are the same",
        "domain": "geography",
        "patterns": [
            r"climate\s*(is\s*)?(the\s*)?same\s*as\s*weather",
            r"today.?s\s*weather\s*(is\s*)?climate",
        ],
        "correction": "Weather is short-term conditions; climate is long-term average patterns for a region.",
        "related_concepts": ["climate", "weather"],
    },
    {
        "misconception_id": "soc.constitution_only_laws",
        "label": "Constitution is just a list of laws",
        "domain": "civics",
        "patterns": [
            r"constitution\s*(is\s*)?(just|only)\s*(a\s*)?list\s*of\s*laws",
            r"constitution\s*=\s*penal\s*code",
        ],
        "correction": "A constitution sets fundamental principles, structures of government, and rights—above ordinary laws.",
        "related_concepts": ["constitution", "rule_of_law", "rights"],
    },
    {
        "misconception_id": "soc.primary_source_always_true",
        "label": "Primary sources are always reliable",
        "domain": "history",
        "patterns": [
            r"primary\s*sources?\s*(are\s*)?(always\s*)?(true|reliable)",
            r"eyewitness\s*(is\s*)?(never\s*)?wrong",
        ],
        "correction": "Primary sources need contextualisation: bias, purpose, audience, and corroboration.",
        "related_concepts": ["source_analysis", "bias", "corroboration"],
    },
)


def detect_social_science_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    return detect_from_catalogue(
        SOCIAL_SCIENCE_MISCONCEPTIONS,
        text,
        provenance="social_science_intelligence.misconceptions",
        limit=limit,
    )
