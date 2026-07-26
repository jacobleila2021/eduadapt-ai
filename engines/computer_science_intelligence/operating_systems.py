"""Operating systems intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

OS_FOCI: tuple[dict[str, str], ...] = (
    {"id": "processes", "label": "Processes"},
    {"id": "threads", "label": "Threads"},
    {"id": "memory_management", "label": "Memory management"},
    {"id": "file_systems", "label": "File systems"},
    {"id": "scheduling", "label": "Scheduling"},
    {"id": "kernel", "label": "Kernel concepts"},
)


def operating_systems_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=OS_FOCI,
        text=text,
        domains=domains,
        domain_keys={"operating_systems"},
        provenance="computer_science_intelligence.operating_systems",
    )
