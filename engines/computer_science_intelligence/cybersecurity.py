"""Cybersecurity intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

CYBER_FOCI: tuple[dict[str, str], ...] = (
    {"id": "firewalls", "label": "Firewalls"},
    {"id": "encryption", "label": "Encryption"},
    {"id": "authentication", "label": "Authentication"},
    {"id": "cyber_hygiene", "label": "Cyber hygiene"},
    {"id": "secure_coding", "label": "Secure coding"},
    {"id": "digital_citizenship", "label": "Digital citizenship"},
)


def cybersecurity_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=CYBER_FOCI,
        text=text,
        domains=domains,
        domain_keys={"cybersecurity"},
        provenance="computer_science_intelligence.cybersecurity",
        extra={
            "ethics_prompts": [
                "Who is protected by this control, and what trade-offs remain?",
            ],
            "generates_exploits": False,
        },
    )
