"""Answer Routing Engine — maps question type → engine (never bypass)."""

from __future__ import annotations

import re

from engines.router import route
from engines.types import EngineResult, TaskKind, ToolTask, ValidationStatus


QUESTION_ROUTING_TABLE = [
    ("balance_equation", TaskKind.BALANCE_EQUATION, r"balance\s+(?:the\s+)?(?:chemical\s+)?(?:equation|reaction)|stoichiometr"),
    ("physics_diagram", TaskKind.PHYSICS_DIAGRAM, r"free[\s-]?body|force\s+diagram|ray\s+diagram|projectile|vector\s+diagram|motion\s+graph|simple\s+machine|lever\b"),
    ("calculate_force", TaskKind.CALCULATE_FORCE, r"\bforce\b|\bpressure\b|\bF\s*=\s*ma\b|\bnewton"),
    ("draw_circuit", TaskKind.DRAW_CIRCUIT, r"circuit|schematic|resistor|battery\s+and\s+(?:bulb|lamp)"),
    ("molecule", TaskKind.MOLECULE_SMILES, r"smiles\s*[:=]|molecular\s+structure|draw\s+(?:the\s+)?molecule"),
    ("geometry", TaskKind.GEOMETRY, r"triangle|circle|construct|geogebra|angle\s+ABC|geometry"),
    ("statistics", TaskKind.STATISTICS, r"\b(mean|median|mode|standard\s+deviation|variance)\b"),
    ("chart", TaskKind.PLOT_GRAPH, r"\b(bar\s+graph|pie\s+chart|histogram|scatter\s+plot|line\s+graph)\b"),
    ("plot_graph", TaskKind.PLOT_GRAPH, r"\bplot\b|\bgraph\b"),
    ("solve_math", TaskKind.SOLVE_MATH, r"\bsolve\b|find\s+x\b|quadratic|factoris[ee]|simultaneous\s+equation|differentiate|integrate|derivative|integral|d/dx"),
    ("assertion_reason", TaskKind.ASSERTION_REASON, r"assertion\s*\(?A\)?|reason\s*\(?R\)?"),
    ("mcq", TaskKind.OFFICIAL_ANSWER, r"multiple\s+choice|\bmcq\b|choose\s+the\s+correct|options?\s*:"),
    ("compare", TaskKind.COMPARE_CONCEPTS, r"compare\s+(?:and\s+contrast\s+)?|difference\s+between|distinguish\s+between"),
    ("essay", TaskKind.ESSAY_RAG, r"essay|write\s+(?:a\s+)?(?:long\s+)?(?:note|paragraph)|explain\s+in\s+detail|discuss\b"),
    ("explain", TaskKind.EXPLAIN_RAG, r"explain\b|what\s+is\b|define\b|describe\b"),
]


def classify_question(text: str) -> tuple[str, TaskKind]:
    t = (text or "").strip()
    if not t:
        return "explain", TaskKind.EXPLAIN_RAG
    from engines.content_classifier import classify_content

    classified = classify_content(t)
    typed_routes = {
        "chemical_equation": ("balance_equation", TaskKind.BALANCE_EQUATION),
        "math_expression": ("solve_math", TaskKind.SOLVE_MATH),
        "math_equation": ("solve_math", TaskKind.SOLVE_MATH),
        "calculus_expression": ("solve_math", TaskKind.SOLVE_MATH),
        "plot_expression": ("plot_graph", TaskKind.PLOT_GRAPH),
        "physics_problem": ("calculate_force", TaskKind.CALCULATE_FORCE),
        "statistics_data": ("statistics", TaskKind.STATISTICS),
        "chart_request": ("chart", TaskKind.PLOT_GRAPH),
        "circuit_request": ("draw_circuit", TaskKind.DRAW_CIRCUIT),
        "molecule_request": ("molecule", TaskKind.MOLECULE_SMILES),
        "geometry_request": ("geometry", TaskKind.GEOMETRY),
    }
    if classified.content_type in typed_routes:
        return typed_routes[classified.content_type]
    unsafe_parser_kinds = {
        TaskKind.BALANCE_EQUATION,
        TaskKind.PHYSICS_DIAGRAM,
        TaskKind.CALCULATE_FORCE,
        TaskKind.DRAW_CIRCUIT,
        TaskKind.MOLECULE_SMILES,
        TaskKind.GEOMETRY,
        TaskKind.STATISTICS,
        TaskKind.PLOT_GRAPH,
        TaskKind.SOLVE_MATH,
    }
    for label, kind, pattern in QUESTION_ROUTING_TABLE:
        if kind in unsafe_parser_kinds:
            continue
        if re.search(pattern, t, re.I):
            return label, kind
    return "explain", TaskKind.EXPLAIN_RAG


def _rag_style_result(kind: TaskKind, question: str, mode: str) -> EngineResult:
    """Knowledge/Teaching bridge — retrieves NCERT context; LLM explains later."""
    try:
        from knowledge.service import prepare_knowledge_for_lesson

        knowledge = prepare_knowledge_for_lesson(question, {"topic": question[:120]})
        hits = knowledge.get("rag_hits") or []
        citations = knowledge.get("citations") or []
        return EngineResult(
            engine_id="llm_rag",
            layer="teaching",
            task_kind=kind,
            payload={
                "question": question,
                "mode": mode,
                "rag_hits": hits,
                "citations": citations,
                "instruction": (
                    "Teaching Layer must answer using RETRIEVED_SOURCES only; cite chapters."
                    if mode != "essay"
                    else "Write a structured essay using RETRIEVED_SOURCES; cite every major claim."
                ),
            },
            validation=ValidationStatus.PASS if hits else ValidationStatus.WARN,
            validation_detail=f"{len(hits)} NCERT chunk(s) retrieved for {mode}",
            deterministic=False,
            provenance={"layer": "knowledge+teaching"},
        )
    except Exception as exc:  # noqa: BLE001
        return EngineResult(
            engine_id="llm_rag",
            layer="teaching",
            task_kind=kind,
            payload={"question": question, "mode": mode},
            validation=ValidationStatus.WARN,
            error=str(exc),
            deterministic=False,
        )


def _official_result(kind: TaskKind, question: str) -> EngineResult:
    try:
        from knowledge.question_bank import load_official_items, match_official_mcqs

        want_ar = kind == TaskKind.ASSERTION_REASON
        items = match_official_mcqs(question, [], limit=8)
        if want_ar:
            ar = [it for it in load_official_items() if it.question_type == "assertion_reason"]
            items = ar[:3] or items
        else:
            items = [it for it in items if it.question_type != "assertion_reason"] or items

        if not items:
            return EngineResult(
                engine_id="official_answer_bank",
                layer="knowledge",
                task_kind=kind,
                payload={"question": question},
                validation=ValidationStatus.FAIL,
                error="No official answer found — do not invent MCQ keys",
                deterministic=True,
            )

        packed = [
            {
                "item_id": it.item_id,
                "question": it.question,
                "options": it.options,
                "official_answer": it.official_answer,
                "explanation": it.explanation,
                "source": it.source,
                "question_type": it.question_type,
            }
            for it in items[:5]
        ]
        return EngineResult(
            engine_id="official_answer_bank",
            layer="knowledge",
            task_kind=kind,
            payload={"question": question, "matches": packed, "official_answer": packed[0]["official_answer"]},
            validation=ValidationStatus.PASS,
            validation_detail=f"{len(packed)} official item(s)",
            deterministic=True,
            provenance={"layer": "knowledge"},
        )
    except Exception as exc:  # noqa: BLE001
        return EngineResult(
            engine_id="official_answer_bank",
            layer="knowledge",
            task_kind=kind,
            payload={"question": question},
            validation=ValidationStatus.FAIL,
            error=str(exc),
            deterministic=True,
        )


def route_question(question: str, smiles: str | None = None) -> EngineResult:
    """
    Full Answer Routing Engine entry point.
    Maps each question type to ChemPy / SymPy / Matplotlib / Schemdraw / RDKit /
    GeoGebra / Official Answer Bank / LLM+RAG.
    """
    label, kind = classify_question(question)
    from engines.content_classifier import classify_content

    classified = classify_content(question)

    if kind == TaskKind.BALANCE_EQUATION:
        eq = (
            classified.normalized
            if classified.content_type == "chemical_equation"
            else ""
        )
        if not eq:
            return EngineResult(
                engine_id="chemistry_balancer",
                layer="computation",
                task_kind=kind,
                payload={"input": question},
                validation=ValidationStatus.FAIL,
                error="Could not extract a chemical equation to balance",
                deterministic=True,
            )
        return route(ToolTask(kind=kind, payload={"equation": eq}))
    if kind == TaskKind.SOLVE_MATH:
        if classified.content_type in {
            "math_expression",
            "math_equation",
        }:
            expr = classified.normalized
        elif classified.content_type == "calculus_expression":
            expr = question
        else:
            return EngineResult(
                engine_id="math_classifier",
                layer="computation",
                task_kind=kind,
                payload={"input": question},
                validation=ValidationStatus.WARN,
                error="No validated mathematical expression was found",
                deterministic=True,
            )
        return route(ToolTask(kind=kind, payload={"expression": expr}))
    if kind == TaskKind.CALCULATE_FORCE:
        return route(ToolTask(kind=kind, payload={"problem": question}))
    if kind == TaskKind.STATISTICS:
        return route(ToolTask(kind=kind, payload={"raw": question}))
    if kind == TaskKind.PHYSICS_DIAGRAM:
        qlow = question.lower()
        dtype = "free_body"
        if "ray" in qlow:
            dtype = "ray"
        elif "projectile" in qlow:
            dtype = "projectile"
        elif "vector" in qlow:
            dtype = "vector"
        elif "motion" in qlow:
            dtype = "motion_graph"
        elif "lever" in qlow or "simple machine" in qlow:
            dtype = "simple_machine"
        return route(ToolTask(kind=kind, payload={"diagram_type": dtype}))
    if kind == TaskKind.PLOT_GRAPH:
        qlow = question.lower()
        chart = None
        if "bar" in qlow:
            chart = "bar"
        elif "pie" in qlow:
            chart = "pie"
        elif "histogram" in qlow:
            chart = "histogram"
        elif "scatter" in qlow:
            chart = "scatter"
        elif "line graph" in qlow or "line chart" in qlow:
            chart = "line"
        if chart:
            return route(ToolTask(kind=kind, payload={"chart_type": chart, "raw": question}))
        if classified.content_type != "plot_expression":
            return EngineResult(
                engine_id="graph_classifier",
                layer="computation",
                task_kind=kind,
                payload={"input": question},
                validation=ValidationStatus.WARN,
                error="No validated plot expression was found",
                deterministic=True,
            )
        return route(
            ToolTask(kind=kind, payload={"expression": classified.normalized})
        )
    if kind == TaskKind.DRAW_CIRCUIT:
        ctype = "parallel" if "parallel" in question.lower() else "series"
        return route(ToolTask(kind=kind, payload={"description": ctype}))
    if kind == TaskKind.MOLECULE_SMILES:
        smi = smiles or ""
        m = re.search(r"smiles\s*[:=]\s*([A-Za-z0-9\(\)\[\]=#\\\+\-]+)", question, re.I)
        if m:
            smi = m.group(1)
        if not smi:
            curated = {
                "ethanol": "CCO",
                "methane": "C",
                "ethene": "C=C",
                "ethyne": "C#C",
                "benzene": "c1ccccc1",
                "acetic acid": "CC(=O)O",
            }
            for name, code in curated.items():
                if name in question.lower():
                    smi = code
                    break
        return route(ToolTask(kind=kind, payload={"smiles": smi or "CCO"}))
    if kind == TaskKind.GEOMETRY:
        qlow = question.lower()
        gkind = "triangle"
        if "circle" in qlow:
            gkind = "circle"
        elif re.search(r"\bangle\b", qlow):
            gkind = "angle"
        elif "transform" in qlow or "reflect" in qlow:
            gkind = "transform"
        return route(ToolTask(kind=kind, payload={"kind": gkind}))
    if kind in (TaskKind.OFFICIAL_ANSWER, TaskKind.ASSERTION_REASON):
        return _official_result(kind, question)
    if kind == TaskKind.COMPARE_CONCEPTS:
        return _rag_style_result(kind, question, "compare")
    if kind == TaskKind.ESSAY_RAG:
        return _rag_style_result(kind, question, "essay")
    if kind == TaskKind.EXPLAIN_RAG:
        return _rag_style_result(kind, question, "explain")

    return EngineResult(
        engine_id="answer_router",
        layer="computation",
        task_kind=kind,
        payload={"question": question, "label": label},
        validation=ValidationStatus.FAIL,
        error=f"Unhandled route: {label}",
        deterministic=True,
    )
