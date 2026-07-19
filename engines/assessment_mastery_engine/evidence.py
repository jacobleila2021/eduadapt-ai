"""Learning evidence collection + attempt evaluation against official answers."""

from __future__ import annotations

import re
import uuid
from typing import Any

from engines.assessment_mastery_engine.mastery import compute_concept_mastery
from engines.assessment_mastery_engine.misconceptions import detect_from_attempt
from engines.assessment_mastery_engine.schemas import AttemptResult, EvidenceRecord
from engines.assessment_mastery_engine.store import add_evidence, append_attempt


def _normalize_answer(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r"^[\s]*([a-d])[\).\s:-]+", r"\1", t)
    return re.sub(r"\s+", " ", t)


def evaluate_response(
    *,
    response: str,
    official_answer: str,
    question_type: str = "mcq",
) -> dict[str, Any]:
    """
    Compare against official bank answer only — never LLM-invented keys.
    """
    if not official_answer:
        return {"correct": None, "score": 0.0, "reason": "no_official_answer"}
    r = _normalize_answer(response)
    o = _normalize_answer(official_answer)
    if not r:
        return {"correct": False, "score": 0.0, "reason": "empty"}
    # MCQ letter match
    if question_type in ("mcq", "assertion_reason") or len(o) <= 3:
        # extract leading letter
        rm = re.match(r"^([a-d])\b", r)
        om = re.match(r"^([a-d])\b", o)
        if rm and om:
            ok = rm.group(1) == om.group(1)
            return {"correct": ok, "score": 1.0 if ok else 0.0, "reason": "letter_match"}
        ok = r == o or o in r or r in o
        return {"correct": ok, "score": 1.0 if ok else 0.0, "reason": "exactish"}
    # short answer: containment / token overlap
    if o in r or r in o:
        return {"correct": True, "score": 1.0, "reason": "containment"}
    ot = set(o.split())
    rt = set(r.split())
    if not ot:
        return {"correct": False, "score": 0.0, "reason": "empty_official"}
    overlap = len(ot & rt) / len(ot)
    ok = overlap >= 0.6
    return {"correct": ok, "score": round(overlap, 3), "reason": "token_overlap"}


def submit_answer(
    *,
    learner_id: str,
    assessment_id: str,
    item_id: str,
    response: str,
    official_answer: str,
    question_type: str = "mcq",
    concept_id: str = "",
    bloom: str = "",
    question: str = "",
    confidence: float | None = None,
    time_sec: float | None = None,
    source: str = "assessment",
) -> dict[str, Any]:
    ev = evaluate_response(
        response=response,
        official_answer=official_answer,
        question_type=question_type,
    )
    attempt = AttemptResult(
        attempt_id=f"at_{uuid.uuid4().hex[:10]}",
        learner_id=learner_id,
        assessment_id=assessment_id,
        item_id=item_id,
        response=response,
        correct=ev["correct"],
        official_answer=official_answer,
        score=float(ev["score"]),
        concept_id=concept_id,
        bloom=bloom,
        time_sec=time_sec,
    )
    append_attempt(learner_id, attempt.to_dict())

    evidence = EvidenceRecord(
        evidence_id=f"ev_{uuid.uuid4().hex[:10]}",
        learner_id=learner_id,
        concept_id=concept_id,
        source=source,
        correct=ev["correct"],
        score=float(ev["score"]),
        confidence=confidence,
        item_id=item_id,
        notes=ev.get("reason") or "",
    )
    add_evidence(learner_id, evidence)

    mastery = None
    if concept_id:
        mastery = compute_concept_mastery(learner_id, concept_id).to_dict()

    misc = [
        h.to_dict()
        for h in detect_from_attempt(
            response=response,
            correct=ev["correct"],
            concept_id=concept_id,
            question=question,
        )
    ]
    return {
        "attempt": attempt.to_dict(),
        "evaluation": ev,
        "mastery": mastery,
        "misconceptions": misc,
        "policy": "official_answer_only",
    }
