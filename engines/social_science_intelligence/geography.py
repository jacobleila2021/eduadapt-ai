"""Geography intelligence metadata — maps/overlays as LXP metadata only."""

from __future__ import annotations

from typing import Any

GEOGRAPHY_FOCI: tuple[dict[str, str], ...] = (
    {"id": "physical_geography", "label": "Physical geography"},
    {"id": "human_geography", "label": "Human geography"},
    {"id": "climate", "label": "Climate"},
    {"id": "weather", "label": "Weather"},
    {"id": "landforms", "label": "Landforms"},
    {"id": "natural_resources", "label": "Natural resources"},
    {"id": "population", "label": "Population"},
    {"id": "maps", "label": "Maps"},
    {"id": "coordinates", "label": "Coordinates"},
    {"id": "gis_ready", "label": "GIS-ready metadata"},
    {"id": "environmental_systems", "label": "Environmental systems"},
    {"id": "sustainable_development", "label": "Sustainable development"},
)


def geography_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    active = [
        f
        for f in GEOGRAPHY_FOCI
        if f["id"].replace("_", " ") in blob or f["label"].lower() in blob
    ]
    if not active and any(d["domain"] == "geography" for d in domains):
        active = [dict(f) for f in GEOGRAPHY_FOCI[:6]]
    return {
        "foci": active,
        "map_skills_prompts": [
            "Read the legend, scale, and direction indicator.",
            "What pattern does the map emphasise, and what might it omit?",
        ],
        "interactive_maps": True,
        "gis_ready_fields": ["place_name", "region", "lat_hint", "lon_hint", "theme_layer"],
        "renderer": "lxp",
        "provenance": "social_science_intelligence.geography",
    }
