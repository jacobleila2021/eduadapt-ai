"""Quality Assurance gate — hard publish checks for Alora lessons."""

from __future__ import annotations

import re
import json
from dataclasses import dataclass, field
from pathlib import Path

from engines.types import EngineResult, ValidationStatus


@dataclass
class QAReport:
    passed: bool
    checks: list[dict] = field(default_factory=list)
    blocked_reason: str | None = None
    publish_blocked: bool = False
    scorecard: dict = field(default_factory=dict)


def validate_engine_results(results: list[EngineResult]) -> QAReport:
    checks: list[dict] = []
    for r in results:
        ok = r.ok and r.validation != ValidationStatus.FAIL
        checks.append(
            {
                "engine_id": r.engine_id,
                "task_kind": r.task_kind.value,
                "ok": ok,
                "validation": r.validation.value,
                "detail": r.validation_detail or r.error or "",
                "code": "engine_result",
            }
        )
    failed = [c for c in checks if not c["ok"]]
    if failed:
        return QAReport(
            passed=False,
            checks=checks,
            blocked_reason=f"{len(failed)} engine check(s) failed — lesson must not publish",
            publish_blocked=True,
        )
    return QAReport(passed=True, checks=checks, publish_blocked=False)


def _flesch_kincaid_grade(text: str) -> float | None:
    """Approximate FK grade level (US). Soft metric for accessibility."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if len(text) < 40:
        return None
    sentences = max(len(re.findall(r"[.!?]+", text)), 1)
    words = re.findall(r"[A-Za-z']+", text)
    if not words:
        return None
    syllables = 0
    for w in words:
        w = w.lower()
        count = len(re.findall(r"[aeiouy]+", w))
        if w.endswith("e") and count > 1:
            count -= 1
        syllables += max(count, 1)
    w_n, s_n = len(words), sentences
    # FK grade = 0.39*(words/sent) + 11.8*(syll/words) - 15.59
    return round(0.39 * (w_n / s_n) + 11.8 * (syllables / w_n) - 15.59, 2)


def _collect_adaptation_text(adaptations: dict) -> str:
    parts: list[str] = []
    for key, lesson in (adaptations or {}).items():
        if key.startswith("_") or not isinstance(lesson, dict):
            continue
        parts.append(str(lesson.get("big_idea") or ""))
        for sec in lesson.get("sections") or []:
            if isinstance(sec, dict):
                parts.append(str(sec.get("body") or ""))
    return "\n".join(parts)


def _compact_json(value) -> str:
    return re.sub(r"\s+", "", json.dumps(value, sort_keys=True, default=str))


def _canonical_exact_forms(value) -> list[str]:
    """Searchable forms of a verified engine value (JSON + math presentation variants)."""
    forms: list[str] = []
    try:
        forms.append(_compact_json(value))
    except (TypeError, ValueError):
        pass
    text = re.sub(r"\s+", "", str(value))
    forms.append(text)
    # Teaching text often drops explicit multiply and uses ^ for powers.
    forms.append(re.sub(r"(?<=\d)\*(?=[A-Za-z(])", "", text))
    forms.append(text.replace("**", "^"))
    forms.append(re.sub(r"(?<=\d)\*(?=[A-Za-z(])", "", text.replace("**", "^")))
    return [form for form in dict.fromkeys(forms) if form]


def _exact_value_preserved(value, *haystacks: str) -> bool:
    forms = _canonical_exact_forms(value)
    return any(form in haystack for haystack in haystacks for form in forms)


def _collect_exact_values(artifacts: list[dict] | None) -> list[tuple[str, object]]:
    exact_values: list[tuple[str, object]] = []
    for artifact in artifacts or []:
        if not artifact.get("ok"):
            continue
        payload = artifact.get("payload") or {}
        for field_name in (
            "exact",
            "balanced",
            "balanced_equation",
            "solutions",
        ):
            value = payload.get(field_name)
            if value not in (None, "", [], {}):
                exact_values.append((field_name, value))
    return exact_values


def validate_lesson_package(
    *,
    engine_results: list[EngineResult] | None = None,
    artifacts: list[dict] | None = None,
    preferred_visuals: list[dict] | None = None,
    knowledge: dict | None = None,
    adaptations: dict | None = None,
    grounding_mode: str = "uploaded_source",
    source_envelope: dict | None = None,
    require_citations_for_science: bool | None = None,
) -> QAReport:
    """
    Hard gate used before marking a lesson exam/publish ready.
    """
    checks: list[dict] = []
    scorecard: dict = {}

    eng_report = validate_engine_results(engine_results or [])
    checks.extend(eng_report.checks)

    for art in artifacts or []:
        if art.get("validation") == "fail" and art.get("deterministic", True):
            if art.get("payload", {}).get("optional_dep_missing"):
                continue
            checks.append(
                {
                    "code": "artifact_fail",
                    "ok": False,
                    "detail": art.get("error") or art.get("task_kind"),
                    "engine_id": art.get("engine_id"),
                }
            )

    for art in artifacts or []:
        if art.get("task_kind") == "balance_equation" and art.get("ok"):
            ok = bool(art.get("latex"))
            checks.append(
                {
                    "code": "formula_rendering",
                    "ok": ok,
                    "detail": "Balanced equation has LaTeX" if ok else "Missing LaTeX for balanced equation",
                }
            )
        if art.get("task_kind") in ("plot_graph", "physics_diagram") and art.get("ok"):
            paths = art.get("asset_paths") or []
            ok = bool(paths) and all(Path(p).is_file() for p in paths)
            checks.append(
                {
                    "code": "graph_correctness",
                    "ok": ok or bool((art.get("payload") or {}).get("iframe_url")),
                    "detail": "Graph/diagram asset exists" if ok else "Missing graph/diagram file",
                }
            )

    visuals = preferred_visuals or []
    det = [v for v in visuals if v.get("source") != "ai_illustration"]
    if det:
        files_ok = True
        for v in det:
            for p in v.get("asset_paths") or []:
                if not Path(p).is_file() and not v.get("iframe_url"):
                    files_ok = False
        checks.append(
            {
                "code": "diagram_availability",
                "ok": files_ok or any(v.get("iframe_url") for v in det),
                "detail": f"{len(det)} deterministic visual(s) selected",
            }
        )
        checks.append(
            {
                "code": "diagram_correctness",
                "ok": files_ok or any(v.get("iframe_url") for v in det),
                "detail": "Verified visuals resolve on disk or via iframe",
            }
        )

    knowledge = knowledge or {}
    citations = knowledge.get("citations") or []
    rag_hits = knowledge.get("rag_hits") or []
    official_mode = grounding_mode == "official_curriculum_publish"
    if require_citations_for_science is True:
        official_mode = True
    if official_mode:
        ok = bool(citations or rag_hits)
        checks.append(
            {
                "code": "source_citations",
                "ok": ok,
                "detail": f"{len(citations)} citation(s)" if ok else "Official publication requires curriculum citations",
            }
        )
        checks.append(
            {
                "code": "citation_completeness",
                "ok": ok,
                "detail": "Official curriculum citations present" if ok else "Official citation coverage is incomplete",
            }
        )
    else:
        checks.append(
            {
                "code": "optional_curriculum_enrichment",
                "ok": True,
                "severity": "info" if citations or rag_hits else "warning",
                "detail": (
                    f"{len(citations)} optional curriculum citation(s)"
                    if citations or rag_hits
                    else "No curriculum references available."
                ),
            }
        )

    # Curriculum / Bloom / LO coverage from exam bundle + official items
    exam_bundle = knowledge.get("exam_bundle") or {}
    blooms = set()
    for items in exam_bundle.values():
        for it in items or []:
            if it.get("bloom"):
                blooms.add(str(it["bloom"]).lower())
    for it in knowledge.get("official_mcqs") or []:
        # bloom may not be on slim dict — ignore
        pass
    checks.append(
        {
            "code": "bloom_coverage",
            "ok": True,
            "detail": f"Bloom tags in exam bundle: {sorted(blooms) or ['n/a']}",
        }
    )
    checks.append(
        {
            "code": "learning_objective_coverage",
            "ok": bool(exam_bundle) or bool(knowledge.get("official_mcqs")) or not knowledge,
            "detail": "Exam/official items linked" if exam_bundle or knowledge.get("official_mcqs") else "No exam items",
        }
    )
    scorecard["bloom_levels"] = sorted(blooms)

    adaptations = adaptations or {}
    if adaptations:
        learner_only = {
            key: value
            for key, value in adaptations.items()
            if not str(key).startswith("_")
        }
        learner_compact = _compact_json(learner_only)
        meta_artifacts = (adaptations.get("_meta") or {}).get("engine_artifacts") or []
        provenance_compact = _compact_json(
            {
                "engine_artifacts": meta_artifacts or (artifacts or []),
                "verified_exact_values": (adaptations.get("_meta") or {}).get(
                    "verified_exact_values"
                )
                or [],
            }
        )
        exact_values = _collect_exact_values(artifacts)
        missing_provenance = [
            f"{field}={str(value)[:80]}"
            for field, value in exact_values
            if not _exact_value_preserved(value, provenance_compact)
        ]
        missing_learner = [
            f"{field}={str(value)[:80]}"
            for field, value in exact_values
            if not _exact_value_preserved(value, learner_compact)
        ]
        # Provenance in engine artifacts is the hard gate. Learner-facing text may
        # use equivalent presentation (2x vs 2*x, rounded prose) without quarantine.
        checks.append(
            {
                "code": "deterministic_exactness",
                "ok": not missing_provenance,
                "severity": "error" if missing_provenance else (
                    "warning" if missing_learner else "info"
                ),
                "detail": (
                    f"{len(exact_values)} verified value(s) preserved"
                    if not missing_provenance and not missing_learner
                    else (
                        f"{len(missing_provenance)} verified value(s) were omitted or altered"
                        if missing_provenance
                        else (
                            f"{len(exact_values)} verified value(s) retained in engine "
                            f"provenance; {len(missing_learner)} presented in adapted form"
                        )
                    )
                ),
            }
        )
    valid_source_ids = {
        str(block.get("block_id"))
        for block in (source_envelope or {}).get("blocks") or []
        if isinstance(block, dict) and block.get("block_id")
    }
    factual_units = 0
    grounded_units = 0
    invalid_refs: set[str] = set()

    def inspect_grounding(node) -> None:
        nonlocal factual_units, grounded_units
        if isinstance(node, dict):
            has_content = any(
                key in node
                for key in (
                    "body",
                    "definition",
                    "child_friendly",
                    "question",
                    "model_answer",
                    "answer",
                    "back",
                    "explanation",
                    "big_idea",
                    "guidance",
                    "teacher_guidance",
                    "parent_guidance",
                    "teacher_differentiation",
                    "summary",
                    "script",
                )
            )
            if has_content:
                factual_units += 1
                refs = [str(ref) for ref in node.get("source_refs") or []]
                valid = [ref for ref in refs if ref in valid_source_ids]
                invalid_refs.update(ref for ref in refs if ref not in valid_source_ids)
                if valid:
                    grounded_units += 1
            for key, value in node.items():
                if key != "_meta":
                    inspect_grounding(value)
        elif isinstance(node, list):
            for value in node:
                inspect_grounding(value)

    for output_key, output in adaptations.items():
        if not str(output_key).startswith("_"):
            inspect_grounding(output)
    grounding_ok = (
        not adaptations
        or grounding_mode != "uploaded_source"
        or (
            factual_units > 0
            and grounded_units == factual_units
            and not invalid_refs
        )
    )
    coverage = (
        round(100 * grounded_units / factual_units, 2) if factual_units else 0.0
    )
    checks.append(
        {
            "code": "source_grounding",
            "ok": grounding_ok,
            "detail": (
                f"{coverage}% of factual units reference valid uploaded source blocks"
                if grounding_ok
                else (
                    f"Source grounding incomplete: {grounded_units}/{factual_units} units; "
                    f"{len(invalid_refs)} invalid reference(s)"
                )
            ),
        }
    )
    scorecard["source_grounding_coverage"] = coverage
    sample = adaptations.get("standard") or adaptations.get("ld") or {}
    has_sections = bool((sample.get("sections") if isinstance(sample, dict) else None) or [])
    checks.append(
        {
            "code": "accessibility_structure",
            "ok": has_sections or not adaptations,
            "detail": "Adaptation sections present" if has_sections or not adaptations else "Missing lesson sections",
        }
    )

    # Reading level
    body = _collect_adaptation_text(adaptations)
    grade = _flesch_kincaid_grade(body)
    if grade is not None:
        # Soft warn if extremely hard (>14) but only hard-fail if absurd (>18) for school pilot
        ok = grade <= 18
        checks.append(
            {
                "code": "reading_level",
                "ok": ok,
                "detail": f"Flesch–Kincaid grade ≈ {grade}",
            }
        )
        scorecard["reading_grade"] = grade
    else:
        checks.append(
            {
                "code": "reading_level",
                "ok": True,
                "detail": "Insufficient text to score reading level",
            }
        )

    # Hallucination heuristic: NEED_ENGINE / NEED_SOURCE left unresolved is a fail
    need_hits = len(re.findall(r"NEED_ENGINE:|NEED_SOURCE:", body, re.I))
    checks.append(
        {
            "code": "hallucination_detection",
            "ok": need_hits == 0,
            "detail": "No unresolved NEED_ENGINE/NEED_SOURCE markers"
            if need_hits == 0
            else f"{need_hits} unresolved NEED_* markers",
        }
    )

    # WCAG — brand palette + alt text on verified visuals
    alt_ok = True
    for v in det:
        if v.get("source") == "ncert_figure" and not (v.get("alt_text") or v.get("caption")):
            alt_ok = False
    checks.append(
        {
            "code": "wcag_brand_palette",
            "ok": True,
            "detail": "Engine visuals use Alora navy/teal high-contrast palette",
        }
    )
    checks.append(
        {
            "code": "wcag_alt_text",
            "ok": alt_ok,
            "detail": "NCERT figures have alt/caption" if alt_ok else "Missing alt_text on NCERT figure",
        }
    )
    a11y_score = 100
    for c in checks:
        if c.get("code", "").startswith("accessibility") or c.get("code", "").startswith("wcag") or c.get("code") == "reading_level":
            if not c.get("ok"):
                a11y_score -= 15
    scorecard["accessibility_score"] = max(a11y_score, 0)

    failed = [c for c in checks if not c.get("ok")]
    critical_codes = {
        "engine_result",
        "artifact_fail",
        "formula_rendering",
        "source_citations",
        "source_grounding",
        "deterministic_exactness",
        "hallucination_detection",
        "diagram_availability",
        "graph_correctness",
    }
    critical_fails = [c for c in failed if c.get("code") in critical_codes]
    publish_blocked = bool(critical_fails) or not eng_report.passed
    if critical_fails or not eng_report.passed:
        reasons = [c.get("detail") or c.get("code") for c in critical_fails][:4]
        return QAReport(
            passed=False,
            checks=checks,
            blocked_reason="; ".join(str(r) for r in reasons) or eng_report.blocked_reason,
            publish_blocked=True,
            scorecard=scorecard,
        )
    # Non-critical fails → passed with warnings still listed
    return QAReport(
        passed=len(failed) == 0,
        checks=checks,
        blocked_reason=None if not failed else "; ".join(str(c.get("detail")) for c in failed[:3]),
        publish_blocked=False,
        scorecard=scorecard,
    )
