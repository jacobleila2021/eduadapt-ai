"""Official answer bank — MCQs never keyed by LLM when a match exists."""

from __future__ import annotations

import json
import re
from pathlib import Path

from knowledge.paths import SEED_DIR
from knowledge.pilot_config import ACTIVE_PILOT, PilotScope
from knowledge.types import OfficialMcq


def load_official_items(scope: PilotScope | None = None) -> list[OfficialMcq]:
    scope = scope or ACTIVE_PILOT
    path = SEED_DIR / scope.mcq_file
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items: list[OfficialMcq] = []
    for row in data.get("items") or []:
        items.append(
            OfficialMcq(
                item_id=str(row["id"]),
                source=str(row.get("source") or "Official"),
                subject=str(row.get("subject") or scope.subject),
                grade=str(row.get("grade") or scope.grade),
                chapter=int(row.get("chapter") or 0),
                topic=str(row.get("topic") or ""),
                question_type=str(row.get("question_type") or "mcq"),
                question=str(row.get("question") or ""),
                options=list(row.get("options") or []),
                official_answer=str(row.get("official_answer") or ""),
                explanation=str(row.get("explanation") or ""),
                marks=int(row.get("marks") or 1),
                board=str(row.get("board") or scope.board),
                bloom=str(row.get("bloom") or "remember"),
                year=str(row.get("year") or ""),
                difficulty=str(row.get("difficulty") or "medium"),
                learning_objective=str(row.get("learning_objective") or ""),
                tags=list(row.get("tags") or []),
            )
        )
    return items


def _score_item(item: OfficialMcq, topic: str, terms: list[str]) -> float:
    blob = f"{item.topic} {item.question} {' '.join(item.options)}".lower()
    score = 0.0
    topic_l = (topic or "").lower()
    if topic_l and topic_l in blob:
        score += 3.0
    for term in terms:
        t = (term or "").lower().strip()
        if len(t) >= 4 and t in blob:
            score += 1.0
    return score


MIN_RELEVANCE_SCORE = 2.0


def match_official_mcqs(
    topic: str,
    vocabulary_terms: list[str] | None = None,
    limit: int = 6,
    scope: PilotScope | None = None,
    question_types: list[str] | None = None,
) -> list[OfficialMcq]:
    items = load_official_items(scope)
    if question_types:
        allowed = {t.lower() for t in question_types}
        items = [
            it
            for it in items
            if it.question_type.lower() in allowed
            or any(t in (it.tags or []) for t in allowed)
            or any(t in it.source.lower() for t in allowed)
        ]
    terms = vocabulary_terms or []
    scored = [_score_item(it, topic, terms) for it in items]
    # Fail closed: one generic shared word is not enough to insert a question.
    # This prevents a fixed pilot bank from leaking questions from another chapter
    # or subject into the uploaded lesson.
    scored_pairs = [
        (s, it) for s, it in zip(scored, items) if s >= MIN_RELEVANCE_SCORE
    ]
    scored_pairs.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in scored_pairs[:limit]]


def match_exam_bundle(
    topic: str,
    vocabulary_terms: list[str] | None = None,
    limit_per_type: int = 2,
    scope: PilotScope | None = None,
) -> dict[str, list[OfficialMcq]]:
    """Retrieve Exemplar / PYQ / Sample / Competency / HOTS for a topic."""
    type_keys = {
        "exemplar": ["exemplar", "mcq"],
        "previous_year": ["previous year", "pyq"],
        "sample": ["sample"],
        "competency": ["competency"],
        "hots": ["hots"],
    }
    all_items = load_official_items(scope)
    terms = vocabulary_terms or []
    out: dict[str, list[OfficialMcq]] = {}
    for key, needles in type_keys.items():
        pool = [
            it
            for it in all_items
            if any(n in it.source.lower() or n in it.question_type.lower() or n in (it.tags or []) for n in needles)
        ]
        scored = [(_score_item(it, topic, terms), it) for it in pool]
        scored = [(s, it) for s, it in scored if s >= MIN_RELEVANCE_SCORE]
        scored.sort(key=lambda x: x[0], reverse=True)
        out[key] = [it for _, it in scored[:limit_per_type]]
    return out


def official_items_to_worksheet_entries(items: list[OfficialMcq]) -> list[dict]:
    """Convert bank items to worksheet short-answer rows with official keys."""
    rows: list[dict] = []
    for item in items:
        options_text = "\n".join(item.options) if item.options else ""
        q = item.question
        if options_text:
            q = f"{q}\n{options_text}"
        rows.append(
            {
                "question": q,
                "marks": item.marks,
                "lines": 2,
                "model_answer": item.official_answer,
                "source": item.source,
                "official_item_id": item.item_id,
                "question_type": item.question_type,
                "citation": f"[{item.source} · {item.item_id} · Ch.{item.chapter}]",
                "explanation_official": item.explanation,
            }
        )
    return rows


def build_official_answer_key(items: list[OfficialMcq]) -> list[dict]:
    return [
        {
            "question_ref": f"Official {item.item_id}",
            "model_answer": item.official_answer,
            "marks_notes": f"{item.marks} mark(s) — {item.source}",
            "citation": f"[{item.source} · Ch.{item.chapter}]",
        }
        for item in items
    ]
