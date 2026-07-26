"""Physics misconception library — pattern detection only; no invented curriculum."""

from __future__ import annotations

from typing import Any

PHYSICS_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "phys.force_needed_for_motion",
        "label": "Continuous force required to keep an object moving",
        "domain": "forces",
        "patterns": [
            r"force\s+(is\s+)?(needed|required)\s+to\s+(keep|continue).{0,40}(moving|motion)",
            r"no force.*stops?.*immediately",
            r"motion\s*requires\s*constant\s*force",
        ],
        "correction": "Net force changes velocity; constant velocity can occur with zero net force (Newton I).",
        "related_concepts": ["newton_first_law", "inertia", "net_force"],
    },
    {
        "misconception_id": "phys.weight_vs_mass",
        "label": "Weight and mass treated as identical",
        "domain": "forces",
        "patterns": [
            r"weight\s*(is\s*)?(the\s*)?same\s*as\s*mass",
            r"mass\s*=\s*weight",
            r"kg\s*(of\s*)?weight",
        ],
        "correction": "Mass is amount of matter (kg); weight is gravitational force (N) = mg.",
        "related_concepts": ["mass", "weight", "gravity"],
    },
    {
        "misconception_id": "phys.velocity_vs_acceleration",
        "label": "Velocity and acceleration conflated",
        "domain": "motion",
        "patterns": [
            r"velocity\s*(is\s*)?(the\s*)?same\s*as\s*acceleration",
            r"faster\s*means\s*accelerating",
            r"constant\s*speed\s*means\s*accelerating",
        ],
        "correction": "Velocity is rate of change of position; acceleration is rate of change of velocity.",
        "related_concepts": ["velocity", "acceleration", "kinematics"],
    },
    {
        "misconception_id": "phys.current_vs_voltage",
        "label": "Current and voltage confused",
        "domain": "electricity",
        "patterns": [
            r"current\s*(is\s*)?(the\s*)?same\s*as\s*voltage",
            r"voltage\s*flows",
            r"current\s*is\s*used\s*up",
        ],
        "correction": "Voltage is potential difference (push); current is charge flow. Current is not 'used up'.",
        "related_concepts": ["current", "voltage", "ohm_law"],
    },
    {
        "misconception_id": "phys.heat_vs_temperature",
        "label": "Heat and temperature treated as the same",
        "domain": "thermodynamics",
        "patterns": [
            r"heat\s*(is\s*)?(the\s*)?same\s*as\s*temperature",
            r"hotter\s*objects?\s*have\s*more\s*heat\s*always",
            r"temperature\s*flows",
        ],
        "correction": "Temperature measures average kinetic energy; heat is energy transfer due to temperature difference.",
        "related_concepts": ["heat", "temperature", "thermal_energy"],
    },
    {
        "misconception_id": "phys.power_vs_energy",
        "label": "Power and energy conflated",
        "domain": "energy",
        "patterns": [
            r"power\s*(is\s*)?(the\s*)?same\s*as\s*energy",
            r"energy\s*per\s*second\s*is\s*energy",
            r"watt\s*=\s*joule(?!\s*/\s*s)",
        ],
        "correction": "Energy is capacity to do work (J); power is energy transfer rate (W = J/s).",
        "related_concepts": ["power", "energy", "work"],
    },
    {
        "misconception_id": "phys.reflection_vs_refraction",
        "label": "Reflection and refraction swapped",
        "domain": "optics",
        "patterns": [
            r"reflection\s*(is\s*)?bending\s*(in|through)\s*(glass|water)",
            r"refraction\s*(is\s*)?bouncing\s*off",
            r"confus(e|ion).*reflection.*refraction",
        ],
        "correction": "Reflection: bounce at a boundary; refraction: change of direction when entering a new medium.",
        "related_concepts": ["reflection", "refraction", "snell"],
    },
    {
        "misconception_id": "phys.frequency_vs_amplitude",
        "label": "Frequency and amplitude roles confused",
        "domain": "waves",
        "patterns": [
            r"louder\s*(sound\s*)?means\s*higher\s*frequency",
            r"amplitude\s*(is\s*)?pitch",
            r"frequency\s*(is\s*)?loudness",
        ],
        "correction": "Amplitude relates to energy/loudness; frequency relates to pitch for sound.",
        "related_concepts": ["amplitude", "frequency", "waves"],
    },
)


def detect_physics_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

    return detect_from_catalogue(
        PHYSICS_MISCONCEPTIONS,
        text,
        provenance="physics_intelligence.misconceptions",
        limit=limit,
    )
