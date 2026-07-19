"""Evidence-based XP — anti-farming, difficulty/subject weighting."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from engines.learning_motivation_engine.schemas import XP_BASE, XP_EVENTS

DIFFICULTY_WEIGHT = {"easy": 0.8, "medium": 1.0, "hard": 1.25, "challenge": 1.4}
SUBJECT_WEIGHT = {
    "mathematics": 1.05,
    "science": 1.05,
    "reading": 1.0,
    "language": 1.0,
    "default": 1.0,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def event_fingerprint(learner_id: str, event: str, evidence_key: str) -> str:
    raw = f"{learner_id}|{event}|{evidence_key}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def compute_xp(
    event: str,
    *,
    difficulty: str = "medium",
    subject: str = "default",
    improvement_delta: float = 0.0,
    teacher_approved: bool = False,
    bonus_multiplier: float = 1.0,
) -> dict[str, Any]:
    if event not in XP_EVENTS:
        return {"ok": False, "xp": 0, "error": "unknown_event"}
    if event == "helping_classmate" and not teacher_approved:
        return {"ok": False, "xp": 0, "error": "teacher_approval_required"}

    base = XP_BASE[event]
    # Do not reward guessing — improvement/mastery events need positive signal
    if event in ("improvement", "concept_mastered") and improvement_delta < 0:
        return {"ok": False, "xp": 0, "error": "no_xp_for_negative_or_guessing", "anti_farming": True}

    d_w = DIFFICULTY_WEIGHT.get(difficulty, 1.0)
    s_w = SUBJECT_WEIGHT.get(subject, SUBJECT_WEIGHT["default"])
    improve_bonus = 1.0 + min(max(improvement_delta, 0.0), 0.5)  # cap
    mult = max(0.5, min(float(bonus_multiplier), 2.0))
    xp = int(round(base * d_w * s_w * improve_bonus * mult))
    return {
        "ok": True,
        "xp": xp,
        "event": event,
        "formula": {
            "base": base,
            "difficulty_weight": d_w,
            "subject_weight": s_w,
            "improvement_bonus": improve_bonus,
            "bonus_multiplier": mult,
        },
        "ts": _now(),
    }


def apply_anti_farming(state: dict[str, Any], fingerprint: str) -> dict[str, Any]:
    """Reject duplicate evidence keys (excessive repetition)."""
    seen = list(state.get("last_event_hashes") or [])
    if fingerprint in seen:
        return {"ok": False, "error": "duplicate_or_farming", "xp": 0}
    seen.append(fingerprint)
    state["last_event_hashes"] = seen[-200:]
    return {"ok": True, "state": state}


def award_xp(
    state: dict[str, Any],
    event: str,
    *,
    evidence_key: str,
    difficulty: str = "medium",
    subject: str = "default",
    improvement_delta: float = 0.0,
    teacher_approved: bool = False,
    bonus_multiplier: float = 1.0,
) -> dict[str, Any]:
    learner_id = str(state.get("learner_id") or "")
    fp = event_fingerprint(learner_id, event, evidence_key)
    farm = apply_anti_farming(state, fp)
    if not farm.get("ok"):
        return {**farm, "event": event}
    state = farm["state"]
    calc = compute_xp(
        event,
        difficulty=difficulty,
        subject=subject,
        improvement_delta=improvement_delta,
        teacher_approved=teacher_approved,
        bonus_multiplier=bonus_multiplier,
    )
    if not calc.get("ok"):
        return calc
    xp = int(calc["xp"])
    state["xp_total"] = int(state.get("xp_total") or 0) + xp
    log = list(state.get("xp_log") or [])
    log.append({"event": event, "xp": xp, "evidence_key": evidence_key, "fingerprint": fp, **calc.get("formula", {}), "ts": calc["ts"]})
    state["xp_log"] = log[-500:]
    return {"ok": True, "xp_awarded": xp, "xp_total": state["xp_total"], "state": state, "calc": calc}
