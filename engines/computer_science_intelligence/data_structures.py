"""Data structures intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

DATA_STRUCTURE_FOCI: tuple[dict[str, str], ...] = (
    {"id": "arrays", "label": "Arrays"},
    {"id": "linked_lists", "label": "Linked lists"},
    {"id": "trees", "label": "Trees"},
    {"id": "graphs", "label": "Graphs"},
    {"id": "queues", "label": "Queues"},
    {"id": "stacks", "label": "Stacks"},
    {"id": "hashing", "label": "Hashing"},
)


def data_structures_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=DATA_STRUCTURE_FOCI,
        text=text,
        domains=domains,
        domain_keys={"data_structures"},
        provenance="computer_science_intelligence.data_structures",
        extra={
            "tradeoff_prompts": [
                "What is the cost of indexed access vs insert/delete?",
                "When would a hash table beat a list for lookup?",
            ],
        },
    )
