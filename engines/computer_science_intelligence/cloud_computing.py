"""Cloud computing intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

CLOUD_FOCI: tuple[dict[str, str], ...] = (
    {"id": "saas", "label": "SaaS"},
    {"id": "iaas", "label": "IaaS"},
    {"id": "paas", "label": "PaaS"},
    {"id": "virtualisation", "label": "Virtualisation"},
    {"id": "containers", "label": "Containers"},
    {"id": "scalability", "label": "Scalability"},
)


def cloud_computing_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=CLOUD_FOCI,
        text=text,
        domains=domains,
        domain_keys={"cloud_computing"},
        provenance="computer_science_intelligence.cloud_computing",
    )
