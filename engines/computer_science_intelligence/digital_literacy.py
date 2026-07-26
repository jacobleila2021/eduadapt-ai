"""Digital literacy intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

DIGITAL_LITERACY_FOCI: tuple[dict[str, str], ...] = (
    {"id": "digital_skills", "label": "Digital skills"},
    {"id": "online_safety", "label": "Online safety"},
    {"id": "media_literacy", "label": "Media literacy"},
    {"id": "information_literacy", "label": "Information literacy"},
    {"id": "digital_citizenship", "label": "Digital citizenship"},
)


def digital_literacy_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=DIGITAL_LITERACY_FOCI,
        text=text,
        domains=domains,
        domain_keys={"digital_literacy"},
        provenance="computer_science_intelligence.digital_literacy",
    )
