"""Schemdraw circuit diagrams."""

from __future__ import annotations

import tempfile
from pathlib import Path

from engines.types import EngineResult, TaskKind, ValidationStatus


def draw_circuit(description: str = "series") -> EngineResult:
    """
    Draw a labelled educational circuit.
    Supports: series (battery + resistor + lamp), parallel (battery + two resistors).
    """
    desc = (description or "series").lower()
    try:
        import schemdraw
        import schemdraw.elements as elm
    except ImportError:
        return EngineResult(
            engine_id="schemdraw",
            layer="computation",
            task_kind=TaskKind.DRAW_CIRCUIT,
            payload={"description": description},
            validation=ValidationStatus.FAIL,
            error="schemdraw not installed. Add schemdraw to requirements.",
            deterministic=True,
        )

    try:
        d = schemdraw.Drawing()
        if "parallel" in desc:
            d += elm.Battery().label("V")
            d += elm.Line().up()
            d += elm.Resistor().right().label("R1")
            d += elm.Line().down()
            d += elm.Line().left()
            d += elm.Resistor().up().label("R2")
            circuit_type = "parallel"
        else:
            d += elm.Battery().label("V")
            d += elm.Resistor().right().label("R")
            d += elm.Lamp().down().label("Lamp")
            d += elm.Line().left()
            circuit_type = "series"

        out_dir = Path(tempfile.gettempdir()) / "alora_engines"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"circuit_{abs(hash(desc)) % 10**10}.png"
        d.save(str(path))

        return EngineResult(
            engine_id="schemdraw",
            layer="computation",
            task_kind=TaskKind.DRAW_CIRCUIT,
            payload={"description": description, "circuit_type": circuit_type},
            asset_paths=[str(path)],
            validation=ValidationStatus.PASS,
            validation_detail=f"Drawn {circuit_type} circuit",
            provenance={"library": "schemdraw"},
            deterministic=True,
        )
    except Exception as exc:  # noqa: BLE001
        return EngineResult(
            engine_id="schemdraw",
            layer="computation",
            task_kind=TaskKind.DRAW_CIRCUIT,
            payload={"description": description},
            validation=ValidationStatus.FAIL,
            error=str(exc),
            deterministic=True,
        )
