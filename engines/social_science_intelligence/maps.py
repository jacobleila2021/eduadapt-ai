"""Map metadata — clickable maps / overlays; LXP renders."""

from __future__ import annotations

from typing import Any


def map_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    applicable = any(d["domain"] == "geography" for d in domains) or any(
        tok in blob for tok in ("map", "latitude", "longitude", "region", "continent", "ocean")
    )
    return {
        "applicable": applicable,
        "layers": [
            "base_map",
            "political_boundaries",
            "physical_features",
            "climate_zones",
            "population",
            "resources",
        ],
        "interaction_hooks": [
            "clickable_regions",
            "legend_toggle",
            "overlay_compare",
            "coordinate_readout",
        ],
        "accessibility": {
            "alt_description_prompt": "Describe mapped features and legend in plain language.",
            "owner": "AIE/VMLE",
        },
        "renderer": "lxp",
        "invents_geodata": False,
        "provenance": "social_science_intelligence.maps",
    }
