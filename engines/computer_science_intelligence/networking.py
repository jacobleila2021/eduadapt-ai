"""Networking intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

NETWORKING_FOCI: tuple[dict[str, str], ...] = (
    {"id": "network_models", "label": "Network models"},
    {"id": "internet_protocols", "label": "Internet protocols"},
    {"id": "routing", "label": "Routing"},
    {"id": "dns", "label": "DNS"},
    {"id": "packets", "label": "Packets"},
    {"id": "client_server", "label": "Client–server"},
)


def networking_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=NETWORKING_FOCI,
        text=text,
        domains=domains,
        domain_keys={"networking"},
        provenance="computer_science_intelligence.networking",
        extra={
            "topology_viewer": True,
            "invents_protocol_specs": False,
        },
    )
