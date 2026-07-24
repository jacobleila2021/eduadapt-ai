"""Small sample composer for PEEC CLI."""

from __future__ import annotations

from typing import Any


def compose_sample_for_peec() -> dict[str, Any]:
    from engines.lesson_composition_engine import compose_lesson_package
    from uevb.corpus import build_sample_sif, build_sample_uli, build_sample_uvie

    uli = build_sample_uli(
        subject="physics",
        topic="Force and Pressure",
        concept="Pressure",
        curriculum="cbse",
    )
    return compose_lesson_package(
        uli,
        sif=build_sample_sif(subject="physics", topic="Force and Pressure", concept="Pressure"),
        uvie=build_sample_uvie(topic="Force and Pressure", concept="Pressure"),
        topic_hint="Force and Pressure",
    )
