"""Subject Tool Router — never bypass for STEM / official answers."""

from __future__ import annotations

from engines.types import EngineResult, TaskKind, ToolTask, ValidationStatus


def route(task: ToolTask) -> EngineResult:
    """
    Route a task to the correct Computation or Knowledge engine.

    Teaching-layer explanation is NOT performed here.
    """
    kind = task.kind

    if kind == TaskKind.SOLVE_MATH:
        from engines.mathematics.solver import solve

        return solve(str(task.payload.get("expression", "")))

    if kind == TaskKind.BALANCE_EQUATION:
        from engines.content_classifier import classify_content
        from engines.chemistry.balancer import balance_equation

        equation = str(task.payload.get("equation", ""))
        classified = classify_content(equation)
        if classified.content_type != "chemical_equation":
            return EngineResult(
                engine_id="chemistry_classifier",
                layer="computation",
                task_kind=kind,
                payload={"input_type": classified.content_type},
                validation=ValidationStatus.WARN,
                error="No unambiguous chemical equation was detected",
                deterministic=True,
            )
        return balance_equation(classified.normalized)

    if kind == TaskKind.RENDER_CHEMISTRY:
        from engines.content_classifier import classify_content
        from engines.chemistry.render import render_mhchem

        equation = str(task.payload.get("equation", ""))
        classified = classify_content(equation)
        if classified.content_type != "chemical_equation":
            return EngineResult(
                engine_id="chemistry_classifier",
                layer="computation",
                task_kind=kind,
                payload={"input_type": classified.content_type},
                validation=ValidationStatus.WARN,
                error="No unambiguous chemical equation was detected",
                deterministic=True,
            )
        return render_mhchem(classified.normalized)

    if kind == TaskKind.PLOT_GRAPH:
        from engines.graphs.plotter import plot_chart, plot_function

        chart_type = str(task.payload.get("chart_type") or "").lower()
        if chart_type in ("bar", "pie", "histogram", "scatter", "line"):
            return plot_chart(chart_type, str(task.payload.get("expression") or task.payload.get("raw") or ""))
        expr = str(task.payload.get("expression", "x"))
        x0 = float(task.payload.get("x_min", -10))
        x1 = float(task.payload.get("x_max", 10))
        return plot_function(expr, (x0, x1))

    if kind == TaskKind.MOLECULE_SMILES:
        from engines.molecules.rdkit_render import smiles_to_png

        return smiles_to_png(str(task.payload.get("smiles", "")))

    if kind == TaskKind.CALCULATE_FORCE:
        from engines.physics.force import calculate_force

        return calculate_force(str(task.payload.get("problem") or task.payload.get("text") or ""))

    if kind == TaskKind.PHYSICS_DIAGRAM:
        from engines.physics.diagrams import draw_physics_diagram

        return draw_physics_diagram(str(task.payload.get("diagram_type") or "free_body"))

    if kind == TaskKind.DRAW_CIRCUIT:
        from engines.circuits.schemdraw_circuit import draw_circuit

        return draw_circuit(str(task.payload.get("description", "series")))

    if kind == TaskKind.GEOMETRY:
        from engines.geometry.geogebra import build_geogebra

        return build_geogebra(str(task.payload.get("kind", "triangle")))

    if kind == TaskKind.STATISTICS:
        from engines.statistics.engine import compute_statistics

        return compute_statistics(str(task.payload.get("raw") or task.payload.get("expression") or ""))

    if kind in (
        TaskKind.OFFICIAL_ANSWER,
        TaskKind.ASSERTION_REASON,
        TaskKind.EXPLAIN_RAG,
        TaskKind.COMPARE_CONCEPTS,
        TaskKind.ESSAY_RAG,
    ):
        # Prefer Answer Routing Engine for full knowledge/teaching handling
        from engines.answer_router import route_question

        return route_question(str(task.payload.get("question") or task.payload.get("text") or ""))

    return EngineResult(
        engine_id="router",
        layer="computation",
        task_kind=kind,
        payload={},
        validation=ValidationStatus.FAIL,
        error=f"No engine registered for task kind: {kind}",
        deterministic=True,
    )
