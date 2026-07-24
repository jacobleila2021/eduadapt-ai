"""Publisher benchmark + curriculum consistency + golden compare helpers."""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.golden import compare_to_golden
from engines.lesson_composition_engine.publisher_remediation import (
    has_teacher_objective_leak,
    template_hits,
)
from engines.lesson_composition_engine.publisher_style_guide import BANNED_AUTHORING
from uevb.constants import GOLDEN_MIN_DELTA, PUBLISHER_MIN


def _blob_lesson(adaptation: Mapping[str, Any]) -> str:
    parts = [str(adaptation.get("big_idea") or "")]
    for s in adaptation.get("sections") or []:
        if isinstance(s, dict):
            parts.append(str(s.get("title") or ""))
            parts.append(str(s.get("body") or ""))
    return "\n".join(parts)


def publisher_benchmark_lesson(
    adaptations: Mapping[str, Any],
    *,
    publisher_review_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate against publisher standards (writes comments, not vanity scores alone)."""
    dimensions = {
        "educational_writing": 100.0,
        "narrative_flow": 100.0,
        "concept_development": 100.0,
        "diagram_quality": 100.0,
        "vocabulary_presentation": 100.0,
        "assessment_quality": 100.0,
        "accessibility": 100.0,
        "visual_design": 100.0,
        "learner_engagement": 100.0,
    }
    comments: list[str] = []

    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    blob = _blob_lesson(std).lower()
    if any(p in blob for p in BANNED_AUTHORING) or template_hits(blob) or has_teacher_objective_leak(blob):
        dimensions["educational_writing"] -= 25
        comments.append("Educational writing still shows template or scaffold language.")
    sections = [s for s in (std.get("sections") or []) if isinstance(s, dict)]
    if len(sections) < 6:
        dimensions["concept_development"] -= 20
        comments.append("Concept development feels thin for a publisher lesson.")
    if not any(str(s.get("role") or "") in {"real_life_example", "worked_example"} for s in sections):
        dimensions["learner_engagement"] -= 15
        comments.append("Narrative needs stronger examples for engagement.")
    if not str(std.get("flowchart_svg") or std.get("svg_diagram") or "").startswith("<svg"):
        dimensions["diagram_quality"] -= 30
        comments.append("Diagram quality fails publisher SVG standard.")
    pkg = std.get("diagram_package") if isinstance(std.get("diagram_package"), dict) else {}
    if not pkg.get("practice_question"):
        dimensions["diagram_quality"] -= 10
    vocab = adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {}
    wall = vocab.get("word_wall") or []
    if len(wall) < 4:
        dimensions["vocabulary_presentation"] -= 25
        comments.append("Vocabulary presentation below flashcard standard.")
    if not std.get("practice") and not any(str(s.get("role") or "") == "practice_question" for s in sections):
        dimensions["assessment_quality"] -= 20
        comments.append("Assessment quality insufficient.")

    # Accessibility: distinct adaptations present
    for key in ("adhd", "autism", "ell", "visual"):
        if key not in adaptations:
            dimensions["accessibility"] -= 8
            comments.append(f"Missing {key} adaptation for accessibility coverage.")

    if publisher_review_report and not publisher_review_report.get("approved"):
        dimensions["educational_writing"] -= 10
        comments.append("PMES Publisher Review Report has open rejections.")

    overall = round(sum(dimensions.values()) / len(dimensions), 2)
    return {
        "schema": "alora.uevb.publisher_benchmark.v1",
        "publisher_quality_score": overall,
        "threshold": PUBLISHER_MIN,
        "ok": overall >= PUBLISHER_MIN,
        "dimensions": {k: round(v, 2) for k, v in dimensions.items()},
        "comments": comments,
        "pmes_report_attached": bool(publisher_review_report),
    }


def curriculum_consistency_report(
    packages: list[Mapping[str, Any]],
    *,
    concept: str = "",
) -> dict[str, Any]:
    """Identical concepts across curricula should stay educationally equivalent."""
    if len(packages) < 2:
        return {
            "schema": "alora.uevb.curriculum_consistency.v1",
            "ok": True,
            "notes": ["Insufficient curricula compared — single package."],
            "equivalence_score": 100.0,
        }

    claim_sets: list[set[str]] = []
    concept_sets: list[set[str]] = []
    for pkg in packages:
        board = pkg.get("intelligence_board") or {}
        claims = {str(c).lower()[:80] for c in (board.get("verified_claims") or [])}
        concepts = {
            str(c.get("name") or "").lower()
            for c in (board.get("concepts") or [])
            if isinstance(c, dict)
        }
        claim_sets.append(claims)
        concept_sets.append(concepts)

    # Jaccard across first vs others
    base_c, base_n = claim_sets[0], concept_sets[0]
    overlaps = []
    for other_c, other_n in zip(claim_sets[1:], concept_sets[1:]):
        if not base_n and not other_n:
            overlaps.append(1.0)
            continue
        union_n = base_n | other_n
        inter_n = base_n & other_n
        overlaps.append(len(inter_n) / len(union_n) if union_n else 0.0)

    score = round(100.0 * (sum(overlaps) / len(overlaps)), 2) if overlaps else 100.0
    notes = []
    if concept:
        present = sum(1 for n in concept_sets if concept.lower() in n)
        if present < max(1, len(concept_sets) // 2):
            notes.append(f"Seed concept '{concept}' not uniformly present across curricula.")
    if score < 40:
        notes.append("Curriculum variants diverge too far on core concepts.")
    return {
        "schema": "alora.uevb.curriculum_consistency.v1",
        "ok": score >= 40.0,
        "equivalence_score": score,
        "notes": notes,
        "packages_compared": len(packages),
    }


def golden_benchmark_package(
    adaptations: Mapping[str, Any],
    *,
    subject: str = "",
) -> dict[str, Any]:
    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    if not std:
        return {
            "schema": "alora.uevb.golden_benchmark.v1",
            "ok": False,
            "delta": -8.0,
            "notes": ["No standard adaptation to compare."],
        }
    result = compare_to_golden(std, subject=subject)
    delta = float(result.get("delta") or 0.0)
    return {
        "schema": "alora.uevb.golden_benchmark.v1",
        "ok": delta >= GOLDEN_MIN_DELTA,
        "delta": delta,
        "threshold": GOLDEN_MIN_DELTA,
        "matched": bool(result.get("matched")),
        "notes": list(result.get("notes") or []),
        "dimensions": {
            "teaching_quality": delta,
            "learner_engagement": delta,
            "explanation_clarity": delta,
            "pedagogical_richness": delta,
            "accessibility": delta,
            "editorial_quality": delta,
        },
    }
