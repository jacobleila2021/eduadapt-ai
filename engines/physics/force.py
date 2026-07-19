"""Physics force calculations — SymPy / deterministic formulas."""

from __future__ import annotations

import re

from engines.types import EngineResult, TaskKind, ValidationStatus


def _parse_number(text: str, patterns: list[str]) -> float | None:
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                continue
    return None


def calculate_force(raw: str) -> EngineResult:
    """
    Solve F = ma, P = F/A, and related Class 8–11 style problems.
    Never invents numbers — requires values in the prompt text.
    """
    text = (raw or "").strip()
    if not text:
        return EngineResult(
            engine_id="sympy_force",
            layer="computation",
            task_kind=TaskKind.CALCULATE_FORCE,
            payload={},
            validation=ValidationStatus.FAIL,
            error="Empty force problem",
            deterministic=True,
        )

    try:
        import sympy as sp
    except ImportError:
        return EngineResult(
            engine_id="sympy_force",
            layer="computation",
            task_kind=TaskKind.CALCULATE_FORCE,
            payload={"input": text},
            validation=ValidationStatus.FAIL,
            error="SymPy not installed",
            deterministic=True,
        )

    mass = _parse_number(text, [r"mass\s*(?:of|=|:)?\s*([\d.]+)\s*kg", r"m\s*=\s*([\d.]+)"])
    accel = _parse_number(
        text,
        [r"accelerat(?:ion|es)?\s*(?:of|=|:)?\s*([\d.]+)\s*m/?s", r"a\s*=\s*([\d.]+)"],
    )
    force = _parse_number(text, [r"force\s*(?:of|=|:)?\s*([\d.]+)\s*N", r"F\s*=\s*([\d.]+)"])
    area = _parse_number(text, [r"area\s*(?:of|=|:)?\s*([\d.]+)\s*m", r"A\s*=\s*([\d.]+)"])
    pressure = _parse_number(text, [r"pressure\s*(?:of|=|:)?\s*([\d.]+)", r"P\s*=\s*([\d.]+)"])

    F, m, a, P, A = sp.symbols("F m a P A", positive=True)
    result_val = None
    formula = None
    unit = ""
    exact = ""

    lower = text.lower()
    try:
        if ("force" in lower or "f =" in lower or "find f" in lower) and mass is not None and accel is not None:
            formula = "F = m a"
            result_val = mass * accel
            unit = "N"
            exact = f"{result_val} N"
            latex = rf"F = ma = ({mass})({accel}) = {result_val}\,\mathrm{{N}}"
        elif "pressure" in lower and force is not None and area is not None and area != 0:
            formula = "P = F / A"
            result_val = force / area
            unit = "Pa"
            exact = f"{result_val} Pa"
            latex = rf"P = \frac{{F}}{{A}} = \frac{{{force}}}{{{area}}} = {result_val}\,\mathrm{{Pa}}"
        elif "pressure" in lower and pressure is not None and area is not None:
            formula = "F = P A"
            result_val = pressure * area
            unit = "N"
            exact = f"{result_val} N"
            latex = rf"F = PA = ({pressure})({area}) = {result_val}\,\mathrm{{N}}"
        elif mass is not None and force is not None and ("acceleration" in lower or "find a" in lower):
            formula = "a = F / m"
            if mass == 0:
                raise ValueError("Mass cannot be zero")
            result_val = force / mass
            unit = "m/s²"
            exact = f"{result_val} m/s²"
            latex = rf"a = \frac{{F}}{{m}} = \frac{{{force}}}{{{mass}}} = {result_val}\,\mathrm{{m/s^2}}"
        else:
            return EngineResult(
                engine_id="sympy_force",
                layer="computation",
                task_kind=TaskKind.CALCULATE_FORCE,
                payload={"input": text},
                validation=ValidationStatus.FAIL,
                error=(
                    "Could not extract enough values for F=ma or P=F/A. "
                    "Include numeric mass/acceleration/force/area in the problem text."
                ),
                deterministic=True,
            )

        return EngineResult(
            engine_id="sympy_force",
            layer="computation",
            task_kind=TaskKind.CALCULATE_FORCE,
            payload={
                "input": text,
                "formula": formula,
                "exact": exact,
                "value": float(result_val),
                "unit": unit,
                "mass_kg": mass,
                "acceleration_m_s2": accel,
                "force_N": force,
                "area_m2": area,
            },
            latex=latex,
            validation=ValidationStatus.PASS,
            validation_detail=f"Computed via {formula}",
            provenance={"library": f"sympy-{getattr(sp, '__version__', 'unknown')}"},
            deterministic=True,
        )
    except Exception as exc:  # noqa: BLE001
        return EngineResult(
            engine_id="sympy_force",
            layer="computation",
            task_kind=TaskKind.CALCULATE_FORCE,
            payload={"input": text},
            validation=ValidationStatus.FAIL,
            error=str(exc),
            deterministic=True,
        )
