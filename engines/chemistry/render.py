"""Chemical notation rendering hints (LaTeX / mhchem)."""

from __future__ import annotations

from engines.types import EngineResult, TaskKind, ValidationStatus


def render_mhchem(equation: str) -> EngineResult:
    eq = (equation or "").strip()
    if not eq:
        return EngineResult(
            engine_id="mhchem",
            layer="computation",
            task_kind=TaskKind.RENDER_CHEMISTRY,
            payload={},
            validation=ValidationStatus.FAIL,
            error="Empty equation",
            deterministic=True,
        )
    # Streamlit: st.latex(rf"\ce{{{eq}}}")
    latex = rf"\ce{{{eq}}}"
    return EngineResult(
        engine_id="mhchem",
        layer="computation",
        task_kind=TaskKind.RENDER_CHEMISTRY,
        payload={"equation": eq},
        latex=latex,
        validation=ValidationStatus.PASS,
        provenance={"render": "mhchem"},
        deterministic=True,
    )
