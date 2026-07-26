"""Robotics intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

ROBOTICS_FOCI: tuple[dict[str, str], ...] = (
    {"id": "sensors", "label": "Sensors"},
    {"id": "actuators", "label": "Actuators"},
    {"id": "control_systems", "label": "Control systems"},
    {"id": "sense_plan_act", "label": "Sense–plan–act"},
    {"id": "safety", "label": "Robot safety"},
)


def robotics_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=ROBOTICS_FOCI,
        text=text,
        domains=domains,
        domain_keys={"robotics"},
        provenance="computer_science_intelligence.robotics",
    )
