"""Web development intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

WEB_FOCI: tuple[dict[str, str], ...] = (
    {"id": "html_structure", "label": "HTML structure"},
    {"id": "css_styling", "label": "CSS styling"},
    {"id": "http", "label": "HTTP"},
    {"id": "frontend", "label": "Frontend"},
    {"id": "backend", "label": "Backend"},
    {"id": "apis", "label": "APIs"},
)


def web_development_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=WEB_FOCI,
        text=text,
        domains=domains,
        domain_keys={"web_development"},
        provenance="computer_science_intelligence.web_development",
    )
