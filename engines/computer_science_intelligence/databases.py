"""Databases intelligence metadata — reuse Computation Layer DB tools where present."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

DATABASE_FOCI: tuple[dict[str, str], ...] = (
    {"id": "relational_databases", "label": "Relational databases"},
    {"id": "sql_concepts", "label": "SQL concepts"},
    {"id": "er_models", "label": "ER models"},
    {"id": "normalisation", "label": "Normalisation"},
    {"id": "transactions", "label": "Transactions"},
    {"id": "queries", "label": "Queries"},
)


def databases_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=DATABASE_FOCI,
        text=text,
        domains=domains,
        domain_keys={"databases"},
        provenance="computer_science_intelligence.databases",
        extra={
            "schema_viewer": True,
            "reuses_database_engines": True,
            "invents_query_results": False,
        },
    )
