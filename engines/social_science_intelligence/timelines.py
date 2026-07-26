"""Timeline metadata scaffolds — LXP renders interactive timelines."""

from __future__ import annotations

import re
from typing import Any


_YEAR = re.compile(r"\b(?:c\.?\s*)?(?:1[0-9]{3}|20[0-2][0-9]|[1-9][0-9]{0,2}\s*(?:BCE|BC|CE|AD))\b", re.I)


def timeline_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    years = [m.group(0) for m in _YEAR.finditer(text or "")][:12]
    applicable = bool(years) or any(d["domain"] == "history" for d in domains) or "timeline" in (text or "").lower()
    return {
        "applicable": applicable,
        "extracted_year_hints": years,
        "slots": [
            {"role": "start", "prompt": "Earliest event named in the lesson"},
            {"role": "turning_point", "prompt": "Key turning point from the source"},
            {"role": "end_or_outcome", "prompt": "Outcome or later consequence in the lesson"},
        ],
        "navigation": ["zoom", "compare_periods", "link_to_sources"],
        "renderer": "lxp",
        "invents_events": False,
        "provenance": "social_science_intelligence.timelines",
    }
