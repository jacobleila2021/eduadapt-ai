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


_COMPUTABLE_KINDS = frozenset(
    {
        "balance_equation",
        "solve_math",
        "calculate_force",
        "statistics",
        "plot_graph",
    }
)

_COMPUTABLE_STEM_RE = re.compile(
    r"(?i)\b("
    r"balance|equat(?:e|ion)|solve|calculate|determine|find|evaluate|simplify|"
    r"differentiate|integrate|ohm|ampere|volt|watt|force|pressure|"
    r"current|resistance|potential"
    r")\b"
    r"|[=→⟶]|->"
    r"|\d\s*[ΩVAW]"
)


def looks_like_computable_stem(text: str) -> bool:
    """True when a stem should be answered by the Subject Tool Router, not prose."""
    raw = str(text or "").strip()
    if len(raw) < 3:
        return False
    if _COMPUTABLE_STEM_RE.search(raw):
        return True
    if re.search(r"[A-Z][a-z]?\d*.*(?:->|→).*[A-Z][a-z]?\d*", raw):
        return True
    if re.search(r"[a-zA-Z0-9)\]]\s*=\s*[a-zA-Z0-9(\-]", raw) and re.search(
        r"[\d^*/+\-]|x\b|y\b", raw, re.I
    ):
        return True
    return False


def format_engine_answer(artifact: dict) -> str:
    """Learner-facing answer from a verified EngineResult dict — never invent."""
    if not isinstance(artifact, dict) or not artifact.get("ok"):
        return ""
    payload = artifact.get("payload") or {}
    parts: list[str] = []
    balanced = payload.get("balanced") or payload.get("balanced_equation")
    if balanced:
        parts.append(f"Balanced equation: {balanced}.")
    exact = payload.get("exact")
    if exact not in (None, "", [], {}):
        parts.append(f"Exact result: {exact}.")
    result = payload.get("result")
    if result not in (None, "", [], {}) and not parts:
        parts.append(f"Result: {result}.")
    answer = payload.get("answer")
    if answer not in (None, "", [], {}) and not parts:
        parts.append(f"Answer: {answer}.")
    solutions = payload.get("solutions")
    if solutions not in (None, "", [], {}):
        if isinstance(solutions, (list, tuple)):
            parts.append("Solutions: " + ", ".join(str(s) for s in solutions) + ".")
        else:
            parts.append(f"Solutions: {solutions}.")
    simplified = payload.get("simplified")
    if simplified not in (None, "") and str(simplified) not in " ".join(parts):
        parts.append(f"Simplified: {simplified}.")
    steps = payload.get("steps") or []
    if isinstance(steps, list) and steps:
        step_lines = [str(s).strip() for s in steps[:6] if str(s).strip()]
        if step_lines:
            parts.append("Steps: " + " ".join(step_lines))
    if artifact.get("latex") and not parts:
        parts.append(str(artifact["latex"]))
    official = payload.get("official_answer")
    if official and not parts:
        parts.append(str(official))
    text = " ".join(parts).strip()
    if text and not text.endswith((".", "!", "?")):
        text += "."
    return text


def match_artifact_to_prompt(prompt: str, artifacts: list[dict] | None) -> dict | None:
    """Best matching verified artifact for a question stem."""
    stem = str(prompt or "").strip().lower()
    if not stem or not artifacts:
        return None
    stem_compact = re.sub(r"\s+", "", stem)
    best: dict | None = None
    best_score = 0
    for art in artifacts:
        if not isinstance(art, dict) or not art.get("ok"):
            continue
        kind = str(art.get("task_kind") or "")
        payload = art.get("payload") or {}
        hay = " ".join(
            str(x)
            for x in (
                payload.get("input"),
                payload.get("expression"),
                payload.get("equation"),
                payload.get("problem"),
                payload.get("balanced"),
                payload.get("exact"),
                art.get("latex"),
                kind,
            )
            if x
        ).lower()
        hay_compact = re.sub(r"\s+", "", hay)
        score = 0
        if kind in _COMPUTABLE_KINDS:
            score += 1
        # Shared tokens of length ≥ 2
        stem_toks = set(re.findall(r"[a-z0-9]{2,}", stem))
        hay_toks = set(re.findall(r"[a-z0-9]{2,}", hay))
        overlap = stem_toks & hay_toks
        score += min(6, len(overlap))
        if any(tok in stem_compact for tok in (hay_compact[i : i + 8] for i in range(0, max(0, len(hay_compact) - 7), 4)) if len(tok) >= 6):
            score += 3
        # Chemistry: both mention arrow / formula fragments
        if kind == "balance_equation" and ("->" in stem or "→" in prompt or "balance" in stem):
            score += 4
        if kind == "solve_math" and any(k in stem for k in ("solve", "find", "evaluate", "=")):
            score += 2
        if score > best_score:
            best_score = score
            best = art
    if best_score < 3:
        return None
    return best


def verified_or_wall_answer(
    prompt: str,
    *,
    artifacts: list[dict] | None = None,
    wall_prose: str = "",
) -> dict:
    """Answer policy: EngineResult for computable stems, else wall/prose only.

    Returns {source, text, omitted}.
    """
    prompt = str(prompt or "").strip()
    art = match_artifact_to_prompt(prompt, artifacts)
    if art:
        text = format_engine_answer(art)
        if text:
            return {
                "source": "engine_result",
                "text": text,
                "omitted": False,
                "task_kind": art.get("task_kind"),
            }
    if looks_like_computable_stem(prompt):
        # Never invent a numerical/balance answer when routing failed.
        prose = str(wall_prose or "").strip()
        if prose and not re.search(r"(?i)\b(equals?|is\s+\d|balanced\s+equation)\b", prose):
            # Conceptual scaffold only — no fake computation.
            return {
                "source": "wall_prose_no_computation",
                "text": prose,
                "omitted": True,
                "task_kind": None,
            }
        return {
            "source": "omitted_unverified",
            "text": "",
            "omitted": True,
            "task_kind": None,
        }
    prose = str(wall_prose or "").strip()
    return {
        "source": "wall_prose" if prose else "empty",
        "text": prose,
        "omitted": False,
        "task_kind": None,
    }


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
                    "message": (
                        "Some STEM-looking text was too incomplete to verify safely "
                        "(for example a fragment with → or 'solve' without a full equation)."
                    ),
                    "recovery": (
                        "For verified calculation: paste a complete expression "
                        "(e.g. 2H2 + O2 → , or solve x^2 - 5x + 6 = 0). "
                        "The reading lesson still uses the source text."
                    ),
                    "fallback_used": "source_prose",
                    "learner_visible": True,
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
                        "A calculation or balance step could not be verified by the "
                        "Subject Tool Router, so no computed answer was added."
                    ),
                    "recovery": (
                        "Check the equation/expression is complete and standard "
                        "(e.g. 2H2 + O2 → , V = IR with numbers, or solve x^2-5x+6=0). "
                        "Explanations from the source text are still shown."
                    ),
                    "fallback_used": "source_explanation_without_computed_answer",
                    "learner_visible": True,
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

    # UVIE: merge pedagogy/timeline/map organisers from verified lesson text (additive).
    try:
        from engines.universal_visual_intelligence import render_visuals_for_uli

        uvie = render_visuals_for_uli(
            None,
            context={
                "text": lesson_text,
                "topic": topic,
                "stem_artifacts": artifacts,
                "biology_figures": biology_figures,
                "preferred_visuals": preferred_visuals,
                "stem_preferred": preferred_visuals,
            },
            max_visuals=8,
        )
        preferred_visuals = uvie.get("preferred_visuals") or preferred_visuals
        uvie_payload = {
            "visuals": uvie.get("visuals") or [],
            "lxp": uvie.get("lxp") or {},
            "metadata": uvie.get("metadata") or {},
        }
    except Exception:  # noqa: BLE001
        uvie_payload = {}

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
        "uvie": uvie_payload,
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
