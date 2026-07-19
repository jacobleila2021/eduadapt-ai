"""Lesson-level STEM + answer pipeline: claims → engines → viz priority → QA."""

from __future__ import annotations

import re

from engines.answer_router import route_question
from engines.claim_extractor import StemClaim, extract_stem_claims
from engines.qa.pipeline import QAReport, validate_engine_results
from engines.router import route
from engines.types import EngineResult, TaskKind, ToolTask, ValidationStatus
from engines.visualization.priority import select_preferred_visuals, visualization_prompt_rules


def engine_result_to_dict(result: EngineResult) -> dict:
    return {
        "engine_id": result.engine_id,
        "layer": result.layer,
        "task_kind": result.task_kind.value,
        "payload": result.payload,
        "latex": result.latex,
        "asset_paths": result.asset_paths,
        "validation": result.validation.value,
        "validation_detail": result.validation_detail,
        "error": result.error,
        "deterministic": result.deterministic,
        "ok": result.ok,
    }


def _is_explicit_question_line(line: str) -> bool:
    """Distinguish source questions from objectives/instructions containing question verbs."""
    return bool(
        line.rstrip().endswith("?")
        or re.match(
            r"^\s*(?:q(?:uestion)?\s*\d*[\s:.)-]|mcq\s*[:.)-]|"
            r"assertion\s*\(?a\)?\s*[:.)-]|exam\s+question\s*[:.)-])",
            line,
            re.I,
        )
    )


def _route_claim(claim: StemClaim) -> EngineResult:
    extra = claim.extra or {}
    if claim.kind == "chemistry_equation":
        return route(ToolTask(kind=TaskKind.BALANCE_EQUATION, payload={"equation": claim.raw}))
    if claim.kind == "math_equation":
        return route(ToolTask(kind=TaskKind.SOLVE_MATH, payload={"expression": claim.raw}))
    if claim.kind == "plot_expression":
        return route(
            ToolTask(
                kind=TaskKind.PLOT_GRAPH,
                payload={"expression": claim.raw, "x_min": -10, "x_max": 10},
            )
        )
    if claim.kind == "force_problem":
        return route(ToolTask(kind=TaskKind.CALCULATE_FORCE, payload={"problem": claim.raw}))
    if claim.kind == "physics_diagram":
        return route(
            ToolTask(
                kind=TaskKind.PHYSICS_DIAGRAM,
                payload={"diagram_type": extra.get("diagram_type") or claim.raw},
            )
        )
    if claim.kind == "chart":
        return route(
            ToolTask(
                kind=TaskKind.PLOT_GRAPH,
                payload={
                    "chart_type": extra.get("chart_type") or "bar",
                    "raw": extra.get("raw") or claim.raw,
                },
            )
        )
    if claim.kind == "statistics":
        return route(
            ToolTask(
                kind=TaskKind.STATISTICS,
                payload={"raw": extra.get("raw") or claim.raw},
            )
        )
    if claim.kind == "circuit":
        return route(
            ToolTask(
                kind=TaskKind.DRAW_CIRCUIT,
                payload={"description": extra.get("description") or claim.raw},
            )
        )
    if claim.kind == "geometry":
        return route(
            ToolTask(
                kind=TaskKind.GEOMETRY,
                payload={"kind": extra.get("kind") or claim.raw},
            )
        )
    if claim.kind == "molecule":
        return route(
            ToolTask(
                kind=TaskKind.MOLECULE_SMILES,
                payload={"smiles": extra.get("smiles") or claim.raw},
            )
        )
    return EngineResult(
        engine_id="router",
        layer="computation",
        task_kind=TaskKind.SOLVE_MATH,
        payload={},
        error=f"Unknown claim kind: {claim.kind}",
        deterministic=True,
    )


def artifacts_to_prompt_block(artifacts: list[dict]) -> str:
    if not artifacts:
        return ""

    lines = [
        "VERIFIED ENGINE ARTIFACTS (ground truth — do NOT change numbers, coefficients, or balanced equations):",
    ]
    for i, art in enumerate(artifacts, start=1):
        kind = art.get("task_kind", "")
        payload = art.get("payload") or {}
        lines.append(
            f"{i}. [{kind}/{art.get('engine_id')}] "
            f"input={payload.get('input') or payload.get('expression') or payload.get('equation') or payload.get('problem') or payload.get('smiles') or ''}"
        )
        if art.get("latex"):
            lines.append(f"   LaTeX: {art['latex']}")
        if payload.get("exact"):
            lines.append(f"   exact: {payload['exact']}")
        if payload.get("steps"):
            lines.append("   steps:")
            for s in payload["steps"][:8]:
                lines.append(f"     - {s}")
        if payload.get("common_mistakes"):
            lines.append(f"   common_mistakes: {payload['common_mistakes'][:3]}")
        for key in (
            "balanced",
            "simplified",
            "formula",
            "circuit_type",
            "geometry_kind",
            "diagram_type",
            "chart_type",
            "iframe_url",
            "official_answer",
        ):
            if payload.get(key):
                lines.append(f"   {key}: {payload[key]}")
        if payload.get("citations"):
            lines.append(f"   citations: {payload['citations']}")
        if art.get("validation"):
            lines.append(f"   validation: {art['validation']}")
        if art.get("error"):
            lines.append(f"   engine_error: {art['error']}")
    lines.append(
        "RULE: Use these values verbatim in lessons and worksheets. "
        "If a STEM fact is missing, write NEED_ENGINE instead of inventing. "
        "For explain/compare/essay, cite RETRIEVED_SOURCES / citations."
    )
    return "\n".join(lines)


def process_lesson_stem(lesson_text: str, topic: str = "") -> dict:
    """Run Computation + Answer Routing + visualization priority."""
    from engines.content_classifier import classify_text

    routing_warnings: list[dict] = []
    for classified in classify_text(lesson_text):
        low = classified.raw.lower()
        looks_like_rejected_domain_input = (
            ("->" in classified.raw or "→" in classified.raw)
            or (
                re.match(
                    r"^\s*(?:solve|calculate|differentiate|integrate|plot|graph|balance)\b",
                    low,
                )
                is not None
            )
        )
        if (
            looks_like_rejected_domain_input
            and classified.content_type in {"prose", "unknown", "question"}
        ):
            routing_warnings.append(
                {
                    "stage": "content_classification",
                    "code": "ambiguous_stem_not_routed",
                    "line": classified.line_no,
                    "message": "Ambiguous STEM notation was omitted from computation.",
                    "recovery": "Use a complete equation or expression to request verified computation.",
                    "fallback_used": "source_prose",
                }
            )
    claims = extract_stem_claims(lesson_text)
    results: list[EngineResult] = []
    artifacts: list[dict] = []

    for claim in claims:
        result = _route_claim(claim)
        if (
            result.task_kind in (TaskKind.MOLECULE_SMILES, TaskKind.DRAW_CIRCUIT)
            and result.error
            and ("not installed" in (result.error or "").lower())
        ):
            result = EngineResult(
                engine_id=result.engine_id,
                layer=result.layer,
                task_kind=result.task_kind,
                payload={**result.payload, "optional_dep_missing": True},
                latex=result.latex,
                asset_paths=result.asset_paths,
                validation=ValidationStatus.WARN,
                validation_detail=result.validation_detail or result.error or "",
                provenance=result.provenance,
                deterministic=True,
                error=None,
            )
        result.payload = {
            **result.payload,
            "claim_kind": claim.kind,
            "claim_line": claim.line_no,
        }
        if result.validation == ValidationStatus.FAIL or not result.ok:
            routing_warnings.append(
                {
                    "stage": "deterministic_computation",
                    "code": "scoped_computation_omitted",
                    "line": claim.line_no,
                    "task_kind": result.task_kind.value,
                    "message": (
                        "A source item could not be verified and was omitted from "
                        "computed answers."
                    ),
                    "recovery": (
                        "Review the source notation or provide a complete equation "
                        "before requesting a verified result."
                    ),
                    "fallback_used": "source_explanation_without_computed_answer",
                }
            )
            continue
        results.append(result)
        artifacts.append(engine_result_to_dict(result))

    for i, line in enumerate(lesson_text.splitlines(), start=1):
        low = line.lower().strip()
        if len(low) < 20:
            continue
        # Route only explicit source questions. Learning objectives such as
        # "Students will explain..." are lesson content, not answer-bank queries.
        explicit_question = _is_explicit_question_line(line)
        if explicit_question and any(
            k in low
            for k in (
                "explain",
                "compare",
                "essay",
                "mcq",
                "assertion",
                "multiple choice",
                "discuss",
                "distinguish",
            )
        ):
            if len(artifacts) >= 16:
                break
            q_result = route_question(line.strip())
            q_result.payload = {**q_result.payload, "claim_kind": "question", "claim_line": i}
            if q_result.validation == ValidationStatus.FAIL or not q_result.ok:
                routing_warnings.append(
                    {
                        "stage": "answer_routing",
                        "code": "scoped_answer_omitted",
                        "line": i,
                        "task_kind": q_result.task_kind.value,
                        "message": (
                            "An answer could not be verified and was omitted from "
                            "generated answer keys."
                        ),
                        "recovery": "Review the source question or add verified references.",
                        "fallback_used": "source_question_without_answer",
                    }
                )
                continue
            results.append(q_result)
            artifacts.append(engine_result_to_dict(q_result))

    # Biology NCERT curated figures
    try:
        from knowledge.biology_figures import match_biology_figures

        biology_figures = match_biology_figures(lesson_text, topic=topic, limit=3)
    except Exception:
        biology_figures = []

    preferred_visuals = select_preferred_visuals(artifacts, biology_figures, max_visuals=6)
    viz_rules = visualization_prompt_rules(preferred_visuals)

    hard = [r for r in results if r.deterministic and r.layer == "computation"]
    qa: QAReport = validate_engine_results(hard) if hard else QAReport(passed=True, checks=[])

    prompt_block = artifacts_to_prompt_block(artifacts)
    if viz_rules:
        prompt_block = (prompt_block + "\n\n" + viz_rules).strip()

    return {
        "claims_found": len(claims),
        "artifacts": artifacts,
        "biology_figures": biology_figures,
        "preferred_visuals": preferred_visuals,
        "qa": {
            "passed": qa.passed,
            "checks": qa.checks,
            "blocked_reason": qa.blocked_reason,
            "publish_blocked": qa.publish_blocked,
        },
        "prompt_block": prompt_block,
        "routing_table_complete": True,
        "routing_warnings": routing_warnings,
    }
