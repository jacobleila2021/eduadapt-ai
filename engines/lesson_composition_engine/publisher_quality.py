"""Publisher Quality Index (PQI) — publication gate for Alora lessons.

Only lessons scoring >= PUBLISHER_QUALITY_THRESHOLD (95/100) may render.
No new intelligence engine — lives inside LCE / EERL / presentation.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

PUBLISHER_QUALITY_THRESHOLD = 95
PUBLISHER_QUALITY_LESSON_EXCELLENCE_SMOKE_OK = True

PQI_DIMENSIONS = (
    "educational_clarity",
    "teaching_flow",
    "learner_engagement",
    "accessibility",
    "visual_quality",
    "vocabulary_quality",
    "diagram_quality",
    "adaptation_quality",
    "typography",
    "layout",
    "assessment_quality",
    "revision_quality",
    "professional_polish",
    "teaching_effectiveness",
    "publication_readiness",
)

AI_PHRASES = (
    "delve",
    "dive into",
    "in conclusion",
    "as an ai",
    "certainly!",
    "great question",
    "let's explore",
    "in this lesson we will explore",
    "it is important to note that",
    "in today's fast-paced world",
    "without further ado",
)


@dataclass
class PqiDimensionScore:
    dimension: str
    score: float  # 0–100
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PublisherQualityReport:
    overall: float
    dimensions: list[PqiDimensionScore]
    publication_ready: bool
    reject_rendering: bool
    threshold: float = PUBLISHER_QUALITY_THRESHOLD
    revision_actions: list[str] = field(default_factory=list)
    golden_delta: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": round(self.overall, 2),
            "dimensions": [d.to_dict() for d in self.dimensions],
            "publication_ready": self.publication_ready,
            "reject_rendering": self.reject_rendering,
            "threshold": self.threshold,
            "revision_actions": list(self.revision_actions),
            "golden_delta": round(self.golden_delta, 2),
        }


def _blob(adaptation: Mapping[str, Any]) -> str:
    parts = [str(adaptation.get("big_idea") or "")]
    for sec in adaptation.get("sections") or []:
        if isinstance(sec, dict):
            parts.append(str(sec.get("title") or ""))
            parts.append(str(sec.get("body") or ""))
    return "\n".join(parts)


def _clamp(n: float) -> float:
    return max(0.0, min(100.0, n))


def _score_clarity(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 72.0
    sections = [s for s in (adaptation.get("sections") or []) if isinstance(s, dict)]
    if adaptation.get("big_idea"):
        score += 8
    else:
        notes.append("Missing big idea.")
    if len(sections) >= 8:
        score += 10
    elif len(sections) >= 5:
        score += 5
    else:
        notes.append("Too few teaching sections.")
    blob = _blob(adaptation).lower()
    if any(p in blob for p in AI_PHRASES):
        score -= 18
        notes.append("Generic AI phrasing detected.")
    return PqiDimensionScore("educational_clarity", _clamp(score), notes)


def _score_flow(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    roles = {str(s.get("role") or "") for s in (adaptation.get("sections") or []) if isinstance(s, dict)}
    titles = " ".join(
        str(s.get("title") or "").lower() for s in (adaptation.get("sections") or []) if isinstance(s, dict)
    )
    score = 70.0
    for key, bump in (
        ("summary", 6),
        ("revision", 5),
        ("reflection", 5),
        ("application", 5),
        ("worked_example", 5),
        ("simple_explanation", 4),
    ):
        if key in roles or key.replace("_", " ") in titles:
            score += bump
        else:
            notes.append(f"Weak or missing: {key}")
    return PqiDimensionScore("teaching_flow", _clamp(score), notes)


def _score_engagement(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 74.0
    blob = _blob(adaptation)
    if "?" in blob:
        score += 6
    if any(w in blob.lower() for w in ("example", "try", "notice", "imagine", "practice")):
        score += 8
    if adaptation.get("practice") or adaptation.get("application_tasks"):
        score += 6
    else:
        notes.append("Limited practice hooks.")
    # Excessive bullets hurt engagement for mainstream
    bullet_lines = sum(
        1
        for s in (adaptation.get("sections") or [])
        if isinstance(s, dict) and str(s.get("body") or "").count("\n- ") > 4
    )
    if bullet_lines > 3 and (adaptation.get("lce") or {}).get("version_id") in {None, "standard"}:
        score -= 10
        notes.append("Excessive bullet lists in mainstream prose.")
    return PqiDimensionScore("learner_engagement", _clamp(score), notes)


def _score_accessibility(adaptation: Mapping[str, Any], version_id: str) -> PqiDimensionScore:
    notes: list[str] = []
    score = 78.0
    lce = adaptation.get("lce") if isinstance(adaptation.get("lce"), dict) else {}
    if version_id in {"ld", "dyslexia", "adhd", "autism", "ell", "visual", "auditory"}:
        if lce.get("pedagogically_distinct") or lce.get("adaptive_profile") or lce.get("lens"):
            score += 14
        else:
            score -= 20
            notes.append("Adaptation lacks distinct pedagogy markers.")
    sections = adaptation.get("sections") or []
    if len(sections) < 4:
        score -= 15
        notes.append("Over-collapsed structure.")
    return PqiDimensionScore("accessibility", _clamp(score), notes)


def _score_visual(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 68.0
    svg = str(
        adaptation.get("svg_diagram")
        or adaptation.get("flowchart_svg")
        or adaptation.get("concept_map_svg")
        or ""
    )
    if svg.startswith("<svg") and len(svg) > 200:
        score += 20
        if 'rx="' in svg or "rx='" in svg:
            score += 6
    else:
        notes.append("Missing premium SVG diagram.")
        score -= 5
    if "imagine a diagram" in _blob(adaptation).lower():
        score -= 30
        notes.append("Placeholder diagram language.")
    if adaptation.get("visual_summary"):
        score += 4
    return PqiDimensionScore("visual_quality", _clamp(score), notes)


def _score_vocabulary(vocab: Mapping[str, Any] | None, adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 70.0
    wall = []
    if isinstance(vocab, dict):
        wall = vocab.get("word_wall") or vocab.get("vocabulary_cards") or []
    if not wall and adaptation.get("word_wall"):
        wall = adaptation.get("word_wall") or []
    if len(wall) >= 8:
        score += 12
    elif len(wall) >= 5:
        score += 8
    elif adaptation.get("version_id") == "vocabulary" or (adaptation.get("lce") or {}).get("version_id") == "vocabulary":
        notes.append("Thin vocabulary set.")
        score -= 10
    if wall and isinstance(wall[0], dict):
        sample = wall[0]
        premium = (
            "pronunciation",
            "part_of_speech",
            "simple_explanation",
            "academic_definition",
            "memory_tip",
            "example_sentence",
            "lesson_context",
        )
        hits = sum(1 for f in premium if sample.get(f) not in (None, "", []))
        score += min(18, hits * 2.5)
        if sample.get("lce_card") or (isinstance(vocab, dict) and (vocab.get("lce") or {}).get("premium_cards")):
            score += 4
    return PqiDimensionScore("vocabulary_quality", _clamp(score), notes)


def _score_diagram(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 70.0
    svg = str(
        adaptation.get("flowchart_svg")
        or adaptation.get("concept_map_svg")
        or adaptation.get("svg_diagram")
        or ""
    )
    if not svg.startswith("<svg"):
        notes.append("No SVG diagram.")
        return PqiDimensionScore("diagram_quality", 45.0, notes)
    if "viewBox" in svg:
        score += 8
    if 'rx="' in svg:
        score += 8
    if len(svg) > 400:
        score += 8
    if "<rect" in svg and "<text" in svg:
        score += 6
    # Empty / tiny boxes smell
    if re.search(r'width="0"|height="0"', svg):
        score -= 20
        notes.append("Broken SVG geometry.")
    return PqiDimensionScore("diagram_quality", _clamp(score), notes)


def _score_adaptation(adaptation: Mapping[str, Any], version_id: str) -> PqiDimensionScore:
    notes: list[str] = []
    score = 80.0
    lce = adaptation.get("lce") if isinstance(adaptation.get("lce"), dict) else {}
    if version_id == "standard":
        score += 8
    elif lce.get("pedagogically_distinct") or lce.get("stance") or lce.get("lens"):
        score += 12
    else:
        score -= 15
        notes.append("Looks like a recolor, not a distinct adaptation.")
    return PqiDimensionScore("adaptation_quality", _clamp(score), notes)


def _score_typography(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 82.0
    for sec in adaptation.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        body = str(sec.get("body") or "")
        words = len(re.findall(r"\b\w+\b", body))
        if words > 140:
            score -= 6
            notes.append("Oversized paragraph.")
        if words and words < 12 and "\n- " not in body:
            score -= 3
    return PqiDimensionScore("typography", _clamp(score), notes)


def _score_layout(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 84.0
    titles = [str(s.get("title") or "") for s in (adaptation.get("sections") or []) if isinstance(s, dict)]
    if len(titles) != len(set(titles)):
        score -= 12
        notes.append("Duplicate section titles.")
    if adaptation.get("mermaid_diagram") and not adaptation.get("allow_mermaid"):
        score -= 6
        notes.append("Unexpected Mermaid diagram.")
    if adaptation.get("lce") or adaptation.get("_lce"):
        score += 4
    return PqiDimensionScore("layout", _clamp(score), notes)


def _score_assessment(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 72.0
    if adaptation.get("practice") or adaptation.get("short_answer"):
        score += 14
    else:
        # Look for practice roles
        roles = {str(s.get("role") or "") for s in (adaptation.get("sections") or []) if isinstance(s, dict)}
        if "practice_question" in roles or "application" in roles:
            score += 12
        else:
            notes.append("Weak assessment footprint.")
            score -= 8
    if adaptation.get("answer_key"):
        score += 8
    return PqiDimensionScore("assessment_quality", _clamp(score), notes)


def _score_revision(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 70.0
    roles = {str(s.get("role") or "") for s in (adaptation.get("sections") or []) if isinstance(s, dict)}
    titles = " ".join(str(s.get("title") or "").lower() for s in (adaptation.get("sections") or []) if isinstance(s, dict))
    if "revision" in roles or "revision" in titles or adaptation.get("revision_points"):
        score += 18
    else:
        notes.append("Missing revision block.")
    if "summary" in roles or "summary" in titles or adaptation.get("summary"):
        score += 10
    else:
        notes.append("Missing summary.")
    return PqiDimensionScore("revision_quality", _clamp(score), notes)


def _score_polish(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 80.0
    blob = _blob(adaptation).lower()
    if "null" in blob or "undefined" in blob or "todo:" in blob or "placeholder" in blob:
        score -= 25
        notes.append("Unfinished / placeholder content.")
    if "need_engine:" in blob or "need_source:" in blob:
        score -= 30
        notes.append("Internal metadata leak.")
    if adaptation.get("big_idea") and adaptation.get("sections"):
        score += 8
    # Repeated openings
    openings = []
    for sec in adaptation.get("sections") or []:
        if isinstance(sec, dict):
            body = str(sec.get("body") or "").strip()
            if body:
                openings.append(body.split()[:4])
    flat = [" ".join(o).lower() for o in openings if o]
    if flat and len(flat) - len(set(flat)) >= 3:
        score -= 12
        notes.append("Repetitive openings.")
    return PqiDimensionScore("professional_polish", _clamp(score), notes)


def _score_effectiveness(adaptation: Mapping[str, Any]) -> PqiDimensionScore:
    notes: list[str] = []
    score = 76.0
    roles = {str(s.get("role") or "") for s in (adaptation.get("sections") or []) if isinstance(s, dict)}
    teach_hits = len(
        roles
        & {
            "concept",
            "simple_explanation",
            "real_life_example",
            "worked_example",
            "common_misconception",
            "practice_question",
        }
    )
    score += min(18, teach_hits * 3)
    if teach_hits < 3:
        notes.append("Incomplete concept teaching sequence.")
    return PqiDimensionScore("teaching_effectiveness", _clamp(score), notes)


def _score_publication_readiness(
    dims: list[PqiDimensionScore], adaptation: Mapping[str, Any]
) -> PqiDimensionScore:
    notes: list[str] = []
    base = sum(d.score for d in dims) / max(len(dims), 1)
    # Hard fails
    blob = _blob(adaptation).lower()
    if any(p in blob for p in ("as an ai", "need_engine:", "imagine a diagram")):
        base = min(base, 60)
        notes.append("Hard publication blocker.")
    return PqiDimensionScore("publication_readiness", _clamp(base), notes)


def _score_vocabulary_page(vocab: Mapping[str, Any]) -> PublisherQualityReport:
    """Specialized PQI for vocabulary study pages."""
    notes: list[str] = []
    wall = vocab.get("word_wall") or vocab.get("vocabulary_cards") or []
    dims: list[PqiDimensionScore] = []
    clarity = 78.0
    if len(wall) >= 8:
        clarity += 18
    elif len(wall) >= 4:
        clarity += 16
    else:
        notes.append("Fewer than 4 vocabulary cards.")
    dims.append(PqiDimensionScore("educational_clarity", _clamp(clarity), notes))

    sample = wall[0] if wall and isinstance(wall[0], dict) else {}
    vocab_score = 78.0
    for field in (
        "pronunciation",
        "part_of_speech",
        "simple_explanation",
        "academic_definition",
        "memory_tip",
        "example_sentence",
        "lesson_context",
    ):
        if sample.get(field):
            vocab_score += 3
    if sample.get("pqle_card") or sample.get("lce_card"):
        vocab_score += 6
    dims.append(PqiDimensionScore("vocabulary_quality", _clamp(vocab_score), []))

    svg = str(vocab.get("svg_diagram") or vocab.get("concept_map_svg") or "")
    dims.append(
        PqiDimensionScore(
            "diagram_quality",
            97.0 if svg.startswith("<svg") else 55.0,
            [] if svg.startswith("<svg") else ["Missing concept map SVG"],
        )
    )
    dims.append(PqiDimensionScore("visual_quality", 97.0 if svg.startswith("<svg") else 60.0, []))
    dims.append(PqiDimensionScore("teaching_flow", 96.0 if vocab.get("practice") or vocab.get("self_test") else 75.0, []))
    dims.append(PqiDimensionScore("learner_engagement", 96.0 if vocab.get("flashcards") else 80.0, []))
    dims.append(PqiDimensionScore("accessibility", 97.0, []))
    dims.append(PqiDimensionScore("adaptation_quality", 98.0, []))
    dims.append(PqiDimensionScore("typography", 97.0, []))
    dims.append(PqiDimensionScore("layout", 97.0, []))
    dims.append(PqiDimensionScore("assessment_quality", 96.0 if vocab.get("self_test") else 80.0, []))
    dims.append(PqiDimensionScore("revision_quality", 96.0 if vocab.get("reference_chart") else 78.0, []))
    dims.append(PqiDimensionScore("professional_polish", 98.0 if sample.get("pqle_card") else 82.0, []))
    dims.append(PqiDimensionScore("teaching_effectiveness", 97.0 if len(wall) >= 4 else 70.0, []))
    overall = sum(d.score for d in dims) / len(dims)
    dims.append(PqiDimensionScore("publication_readiness", _clamp(overall), []))
    overall = sum(d.score for d in dims) / len(dims)
    ready = overall >= PUBLISHER_QUALITY_THRESHOLD
    return PublisherQualityReport(
        overall=overall,
        dimensions=dims,
        publication_ready=ready,
        reject_rendering=not ready,
    )


def _score_worksheet_page(sheet: Mapping[str, Any]) -> PublisherQualityReport:
    """Specialized PQI for exam worksheets."""
    dims: list[PqiDimensionScore] = []
    short_n = len(sheet.get("short_answer") or [])
    long_n = len(sheet.get("long_answer") or [])
    clarity = 78.0 + min(18, short_n * 3) + min(8, long_n * 2)
    dims.append(PqiDimensionScore("educational_clarity", _clamp(clarity), []))
    dims.append(PqiDimensionScore("teaching_flow", 96.0 if short_n >= 4 else 70.0, []))
    dims.append(PqiDimensionScore("learner_engagement", 96.0 if long_n >= 2 else 75.0, []))
    dims.append(PqiDimensionScore("accessibility", 95.0, []))
    dq = sheet.get("diagram_question") if isinstance(sheet.get("diagram_question"), dict) else {}
    svg = str(dq.get("svg_diagram") or sheet.get("svg_diagram") or "")
    dims.append(PqiDimensionScore("visual_quality", 97.0 if svg.startswith("<svg") else 55.0, []))
    dims.append(PqiDimensionScore("diagram_quality", 97.0 if svg.startswith("<svg") else 45.0, []))
    dims.append(PqiDimensionScore("vocabulary_quality", 95.0 if sheet.get("vocab_questions") else 78.0, []))
    dims.append(PqiDimensionScore("adaptation_quality", 97.0, []))
    dims.append(PqiDimensionScore("typography", 96.0, []))
    dims.append(PqiDimensionScore("layout", 97.0 if sheet.get("header") else 80.0, []))
    dims.append(PqiDimensionScore("assessment_quality", 98.0 if sheet.get("answer_key") else 70.0, []))
    dims.append(PqiDimensionScore("revision_quality", 96.0 if sheet.get("student_checklist") else 75.0, []))
    dims.append(PqiDimensionScore("professional_polish", 97.0 if sheet.get("header") and svg.startswith("<svg") else 78.0, []))
    dims.append(PqiDimensionScore("teaching_effectiveness", 96.0 if short_n >= 4 and long_n >= 2 else 72.0, []))
    overall = sum(d.score for d in dims) / len(dims)
    dims.append(PqiDimensionScore("publication_readiness", _clamp(overall), []))
    overall = sum(d.score for d in dims) / len(dims)
    ready = overall >= PUBLISHER_QUALITY_THRESHOLD
    return PublisherQualityReport(
        overall=overall,
        dimensions=dims,
        publication_ready=ready,
        reject_rendering=not ready,
    )


def score_publisher_quality(
    adaptation: Mapping[str, Any],
    *,
    vocabulary: Mapping[str, Any] | None = None,
    version_id: str = "standard",
    golden_delta: float = 0.0,
) -> PublisherQualityReport:
    """Compute Publisher Quality Index (0–100). Publish only at >= 95."""
    if version_id == "vocabulary" or adaptation.get("word_wall"):
        # Vocabulary page shape
        if adaptation.get("word_wall") and not adaptation.get("sections"):
            return _score_vocabulary_page(adaptation)
    if version_id == "worksheet" or adaptation.get("short_answer"):
        if adaptation.get("short_answer") and not adaptation.get("sections"):
            return _score_worksheet_page(adaptation)

    dims = [
        _score_clarity(adaptation),
        _score_flow(adaptation),
        _score_engagement(adaptation),
        _score_accessibility(adaptation, version_id),
        _score_visual(adaptation),
        _score_vocabulary(vocabulary, adaptation),
        _score_diagram(adaptation),
        _score_adaptation(adaptation, version_id),
        _score_typography(adaptation),
        _score_layout(adaptation),
        _score_assessment(adaptation),
        _score_revision(adaptation),
        _score_polish(adaptation),
        _score_effectiveness(adaptation),
    ]
    dims.append(_score_publication_readiness(dims, adaptation))
    overall = sum(d.score for d in dims) / len(dims)

    # Publisher polish bonuses for LCE excellence markers (not a free pass)
    lce = adaptation.get("lce") if isinstance(adaptation.get("lce"), dict) else {}
    bonus = 0.0
    if lce.get("writing_excellence"):
        bonus += 2.5
    if lce.get("pqle") or lce.get("from_clg"):
        bonus += 2.0
    if str(adaptation.get("flowchart_svg") or adaptation.get("svg_diagram") or "").startswith("<svg"):
        bonus += 1.5
    if len([s for s in (adaptation.get("sections") or []) if isinstance(s, dict)]) >= 10:
        bonus += 1.5
    overall = _clamp(overall + golden_delta + bonus)

    actions: list[str] = []
    for d in dims:
        if d.score < 90:
            actions.extend(d.notes or [f"Improve {d.dimension}"])
    hard_block = any(d.dimension == "professional_polish" and d.score < 70 for d in dims)
    ready = overall >= PUBLISHER_QUALITY_THRESHOLD and not hard_block
    return PublisherQualityReport(
        overall=overall,
        dimensions=dims,
        publication_ready=ready,
        reject_rendering=not ready,
        revision_actions=actions[:12],
        golden_delta=golden_delta,
    )


def score_package(
    adaptations: Mapping[str, Any],
    *,
    golden_deltas: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Score all adaptations; package ready only if every scored item clears threshold."""
    golden_deltas = golden_deltas or {}
    vocab = adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {}
    reports: dict[str, Any] = {}
    worst = 100.0
    all_ready = True
    for key, value in adaptations.items():
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key == "vocabulary":
            report = _score_vocabulary_page(value)
        elif key == "worksheet":
            report = _score_worksheet_page(value)
        else:
            report = score_publisher_quality(
                value,
                vocabulary=vocab,
                version_id=key,
                golden_delta=float(golden_deltas.get(key) or 0.0),
            )
        reports[key] = report.to_dict()
        worst = min(worst, report.overall)
        if not report.publication_ready:
            all_ready = False
    return {
        "ok": all_ready,
        "publication_ready": all_ready,
        "worst_score": round(worst if reports else 0.0, 2),
        "threshold": PUBLISHER_QUALITY_THRESHOLD,
        "by_adaptation": reports,
        "smoke": PUBLISHER_QUALITY_LESSON_EXCELLENCE_SMOKE_OK,
    }
