"""Shared focus-metadata helper for CSIP domain modules."""

from __future__ import annotations

from typing import Any


def build_focus_metadata(
    *,
    foci_catalogue: tuple[dict[str, str], ...],
    text: str,
    domains: list[dict[str, Any]],
    domain_keys: set[str],
    provenance: str,
    default_count: int = 6,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blob = (text or "").lower()
    active = [
        dict(f)
        for f in foci_catalogue
        if f["id"].replace("_", " ") in blob or f["label"].lower() in blob
    ]
    if not active and any(d.get("domain") in domain_keys for d in domains):
        active = [dict(f) for f in foci_catalogue[:default_count]]
    out: dict[str, Any] = {
        "foci": active,
        "renderer": "lxp",
        "invents_curriculum": False,
        "provenance": provenance,
    }
    if extra:
        out.update(extra)
    return out
