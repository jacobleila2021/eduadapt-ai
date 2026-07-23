"""LCE quality gate — reject rendering below production threshold."""

from __future__ import annotations

import re
from typing import Any

from engines.lesson_composition_engine.schemas import (
    PRODUCTION_THRESHOLD,
    QUALITY_CATEGORIES,
    CompositionQualityReport,
    QualityScore,
)
from engines.lesson_composition_engine.teaching_rules import sentence_count, word_count

AI_TELLS = (
    "delve",
    "dive into",
    "in conclusion",
    "in this lesson we will explore",
    "let's explore",
    "as an ai",
    "certainly!",
    "great question",
)


def _sections(lesson: dict[str, Any]) -> list[dict[str, Any]]:
    return [s for s in (lesson.get("sections") or []) if isinstance(s, dict)]


def score_flow_quality(lesson: dict[str, Any]) -> QualityScore:
    sections = _sections(lesson)
    roles = [str(s.get("role") or "") for s in sections]
    notes: list[str] = []
    score = 0.5
    if len(sections) >= 6:
        score += 0.2
    else:
        notes.append("Too few sections for progressive teaching flow.")
    needed = {"summary", "reflection", "application"}
    # roles may use revision/summary etc.
    present = set(roles)
    titles = " ".join(str(s.get("title") or "").lower() for s in sections)
    for key in needed:
        if key in present or key in titles:
            score += 0.08
        else:
            notes.append(f"Missing flow element: {key}")
    # transitions / multi-paragraph teaching
    bodies = [str(s.get("body") or "") for s in sections]
    if any(sentence_count(b) >= 2 for b in bodies):
        score += 0.1
    score = min(1.0, score)
    return QualityScore("flow_quality", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def score_teaching_quality(lesson: dict[str, Any]) -> QualityScore:
    sections = _sections(lesson)
    notes: list[str] = []
    score = 0.4
    concept_steps = {
        "concept",
        "simple_explanation",
        "real_life_example",
        "worked_example",
        "common_misconception",
        "practice_question",
        "reflection",
    }
    roles = {str(s.get("role") or "") for s in sections}
    hit = len(roles & concept_steps)
    score += min(0.45, hit * 0.06)
    if lesson.get("big_idea"):
        score += 0.1
    else:
        notes.append("Missing big idea.")
    lce = lesson.get("lce") if isinstance(lesson.get("lce"), dict) else {}
    if lce.get("concept_blocks"):
        score += 0.05
    # AI tell detection
    blob = " ".join(str(s.get("body") or "") for s in sections).lower()
    if any(t in blob for t in AI_TELLS):
        score -= 0.15
        notes.append("AI-sounding phrasing detected.")
    score = max(0.0, min(1.0, score))
    return QualityScore("teaching_quality", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def score_vocabulary_quality(vocab: dict[str, Any] | None) -> QualityScore:
    vocab = vocab or {}
    notes: list[str] = []
    wall = vocab.get("word_wall") or vocab.get("vocabulary_cards") or []
    score = 0.3
    if len(wall) >= 8:
        score += 0.25
    elif len(wall) >= 5:
        score += 0.15
    else:
        notes.append("Fewer than 5 vocabulary cards.")
    premium_fields = (
        "pronunciation",
        "part_of_speech",
        "simple_explanation",
        "example_sentence",
        "synonyms",
        "difficulty",
        "reading_level",
        "color",
    )
    if wall:
        sample = wall[0] if isinstance(wall[0], dict) else {}
        present = sum(1 for f in premium_fields if sample.get(f) not in (None, "", []))
        score += min(0.4, present * 0.05)
        if sample.get("lce_card") or (vocab.get("lce") or {}).get("premium_cards"):
            score += 0.05
    score = min(1.0, score)
    return QualityScore("vocabulary_quality", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def score_visual_placement(lesson: dict[str, Any]) -> QualityScore:
    notes: list[str] = []
    score = 0.55
    lce = lesson.get("lce") if isinstance(lesson.get("lce"), dict) else {}
    placements = lce.get("visual_placements") or []
    if placements:
        score += 0.25
    if lesson.get("svg_diagram") or lesson.get("flowchart_svg") or lesson.get("concept_map_svg"):
        score += 0.15
    else:
        notes.append("No SVG diagram attached.")
    # Random mermaid without allow flag is discouraged
    if lesson.get("mermaid_diagram") and not lesson.get("allow_mermaid"):
        score -= 0.1
        notes.append("Mermaid present without explicit request.")
    score = max(0.0, min(1.0, score))
    return QualityScore("visual_placement", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def score_diagram_quality(lesson: dict[str, Any]) -> QualityScore:
    notes: list[str] = []
    score = 0.5
    svg = str(
        lesson.get("flowchart_svg")
        or lesson.get("concept_map_svg")
        or lesson.get("svg_diagram")
        or ""
    )
    if svg.startswith("<svg") and "rounded" not in svg:
        # our builder uses rx=
        if 'rx="' in svg or "rx='" in svg:
            score += 0.25
        if "viewBox" in svg:
            score += 0.1
        if len(svg) > 200:
            score += 0.1
    else:
        if not svg:
            notes.append("Missing professional SVG diagram.")
        else:
            score += 0.15
    score = min(1.0, score)
    return QualityScore("diagram_quality", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def score_reading_quality(lesson: dict[str, Any]) -> QualityScore:
    notes: list[str] = []
    bodies = [str(s.get("body") or "") for s in _sections(lesson)]
    if not bodies:
        return QualityScore("reading_quality", 0.2, ["No body text."], False)
    scores = []
    for b in bodies:
        wc = word_count(b)
        sc = sentence_count(b)
        local = 0.6
        if sc >= 2:
            local += 0.2
        elif wc > 0:
            notes.append("One-sentence fragment found.")
            local -= 0.1
        if wc > 140:
            notes.append("Paragraph exceeds ~120 words.")
            local -= 0.15
        if wc and wc < 8 and sc < 2:
            local -= 0.1
        scores.append(max(0.0, min(1.0, local)))
    score = sum(scores) / len(scores)
    return QualityScore("reading_quality", score, notes[:5], passed=score >= PRODUCTION_THRESHOLD)


def score_accessibility(lesson: dict[str, Any], version_id: str = "standard") -> QualityScore:
    notes: list[str] = []
    score = 0.7
    lce = lesson.get("lce") if isinstance(lesson.get("lce"), dict) else {}
    if version_id in {"ld", "dyslexia", "adhd", "autism", "ell", "visual", "auditory"}:
        if lce.get("pedagogically_distinct") or lce.get("adaptive_profile"):
            score += 0.2
        else:
            notes.append("Adaptive version lacks distinct pedagogy markers.")
            score -= 0.2
    # Never reward content collapse — check section count still healthy
    if len(_sections(lesson)) < 4:
        notes.append("Over-simplified structure.")
        score -= 0.2
    score = max(0.0, min(1.0, score))
    return QualityScore("accessibility", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def score_consistency(lesson: dict[str, Any], blueprint: dict[str, Any] | None = None) -> QualityScore:
    notes: list[str] = []
    score = 0.65
    topic = str((blueprint or {}).get("topic") or lesson.get("topic") or "")
    blob = (lesson.get("big_idea") or "") + " ".join(
        str(s.get("title") or "") for s in _sections(lesson)
    )
    if topic and topic.lower().split()[0] in blob.lower():
        score += 0.15
    titles = [str(s.get("title") or "").lower() for s in _sections(lesson)]
    if len(titles) != len(set(titles)):
        notes.append("Duplicate section titles.")
        score -= 0.15
    # repeated sentences
    bodies = " ".join(str(s.get("body") or "") for s in _sections(lesson))
    sentences = [s.strip().lower() for s in re.split(r"(?<=[.!?])\s+", bodies) if s.strip()]
    if sentences and len(sentences) != len(set(sentences)):
        notes.append("Repeated sentences detected.")
        score -= 0.1
    score = max(0.0, min(1.0, score))
    return QualityScore("consistency", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def score_subject_quality(lesson: dict[str, Any], subject: str = "general") -> QualityScore:
    notes: list[str] = []
    score = 0.7
    lce = lesson.get("lce") if isinstance(lesson.get("lce"), dict) else {}
    if lce.get("subject") or subject:
        score += 0.1
    roles = {str(s.get("role") or "") for s in _sections(lesson)}
    expected = {
        "mathematics": {"worked_example", "symbols", "concrete"},
        "physics": {"phenomenon", "formula", "experiment"},
        "chemistry": {"equation", "safety", "particle_view"},
        "biology": {"process", "analogy", "diagram"},
    }.get(subject, set())
    if expected:
        overlap = roles & expected
        if overlap:
            score += 0.15
        else:
            # concept teaching steps still count as subject-quality teaching
            if {"worked_example", "simple_explanation"} & roles:
                score += 0.1
            else:
                notes.append(f"Weak {subject} teaching markers.")
                score -= 0.1
    score = max(0.0, min(1.0, score))
    return QualityScore("subject_quality", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def score_publication_quality(lesson: dict[str, Any], vocab: dict[str, Any] | None = None) -> QualityScore:
    notes: list[str] = []
    score = 0.55
    if lesson.get("big_idea") and _sections(lesson):
        score += 0.15
    if lesson.get("svg_diagram") or lesson.get("flowchart_svg"):
        score += 0.1
    if lesson.get("visual_summary"):
        score += 0.05
    if (vocab or {}).get("word_wall"):
        score += 0.1
    if (lesson.get("lce") or {}) if isinstance(lesson.get("lce"), dict) else {}:
        score += 0.05
    # Metadata-like smell
    blob = " ".join(str(s.get("body") or "") for s in _sections(lesson)).lower()
    if "null" in blob or "undefined" in blob or "todo:" in blob:
        notes.append("Metadata-like content present.")
        score -= 0.2
    score = max(0.0, min(1.0, score))
    return QualityScore("publication_quality", score, notes, passed=score >= PRODUCTION_THRESHOLD)


def evaluate_composition(
    lesson: dict[str, Any],
    *,
    vocabulary: dict[str, Any] | None = None,
    blueprint: dict[str, Any] | None = None,
    version_id: str = "standard",
    subject: str = "general",
    threshold: float = PRODUCTION_THRESHOLD,
) -> CompositionQualityReport:
    scores = [
        score_flow_quality(lesson),
        score_teaching_quality(lesson),
        score_vocabulary_quality(vocabulary),
        score_visual_placement(lesson),
        score_diagram_quality(lesson),
        score_reading_quality(lesson),
        score_accessibility(lesson, version_id=version_id),
        score_consistency(lesson, blueprint),
        score_subject_quality(lesson, subject=subject),
        score_publication_quality(lesson, vocabulary),
    ]
    # Ensure category coverage matches contract
    assert {s.category for s in scores} == set(QUALITY_CATEGORIES)
    overall = sum(s.score for s in scores) / len(scores)
    production_ready = overall >= threshold and all(s.passed for s in scores)
    # Soft fail individual categories slightly under threshold if overall strong
    if overall >= threshold + 0.05 and sum(1 for s in scores if not s.passed) <= 2:
        production_ready = all(s.score >= threshold - 0.08 for s in scores)
    return CompositionQualityReport(
        overall=round(overall, 4),
        scores=scores,
        production_ready=production_ready,
        reject_rendering=not production_ready,
        threshold=threshold,
    )


def gate_for_rendering(report: CompositionQualityReport) -> dict[str, Any]:
    return {
        "allowed": not report.reject_rendering,
        "production_ready": report.production_ready,
        "overall": report.overall,
        "reject_rendering": report.reject_rendering,
        "failed_categories": [s.category for s in report.scores if not s.passed],
        "report": report.to_dict(),
    }
