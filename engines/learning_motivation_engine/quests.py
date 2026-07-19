"""Quest system — daily/weekly/revision/project/EF/subject/exam; non-competitive."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from engines.learning_motivation_engine.schemas import QUEST_TYPES


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_quests(context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    context = context or {}
    subject = context.get("subject") or "general"
    topic = context.get("topic") or "today's lesson"
    outputs = context.get("engine_outputs") or {}
    ame = (outputs.get("assessment") or {}).get("payload") or {}
    gaps = (ame.get("mastery") or {}).get("concepts_at_risk") or context.get("gaps") or []

    quests = [
        {
            "quest_id": f"q_{uuid.uuid4().hex[:8]}",
            "type": "daily",
            "title": "Complete one focused lesson block",
            "description": f"Finish a meaningful chunk of {topic}.",
            "reward_xp_hint": 25,
            "competitive": False,
        },
        {
            "quest_id": f"q_{uuid.uuid4().hex[:8]}",
            "type": "weekly",
            "title": "Three healthy study sessions",
            "description": "Show up three days this week — grace days allowed.",
            "reward_xp_hint": 45,
            "competitive": False,
        },
        {
            "quest_id": f"q_{uuid.uuid4().hex[:8]}",
            "type": "revision",
            "title": "Revise a weak concept",
            "description": f"Review: {(gaps[0] if gaps else 'a prior concept')}.",
            "reward_xp_hint": 18,
            "competitive": False,
        },
        {
            "quest_id": f"q_{uuid.uuid4().hex[:8]}",
            "type": "executive_function",
            "title": "Plan before you start",
            "description": "Write a 3-step plan, then begin step 1.",
            "reward_xp_hint": 12,
            "competitive": False,
        },
        {
            "quest_id": f"q_{uuid.uuid4().hex[:8]}",
            "type": "subject",
            "title": f"{subject.title()} practice",
            "description": "Complete subject practice with understanding over speed.",
            "reward_xp_hint": 20,
            "competitive": False,
        },
        {
            "quest_id": f"q_{uuid.uuid4().hex[:8]}",
            "type": "exam_preparation",
            "title": "Official practice set",
            "description": "Attempt official/exam-style items via AME — no guessing farm.",
            "reward_xp_hint": 30,
            "competitive": False,
        },
        {
            "quest_id": f"q_{uuid.uuid4().hex[:8]}",
            "type": "project",
            "title": "Mini project",
            "description": "Create or explain one applied example from the lesson.",
            "reward_xp_hint": 50,
            "competitive": False,
        },
    ]
    for q in quests:
        q["status"] = "active"
        q["created_at"] = _now()
        q["types_available"] = list(QUEST_TYPES)
    return quests


def complete_quest(state: dict[str, Any], quest_id: str) -> dict[str, Any]:
    quests = list(state.get("quests") or [])
    found = None
    for q in quests:
        if q.get("quest_id") == quest_id:
            q["status"] = "completed"
            q["completed_at"] = _now()
            found = q
    state["quests"] = quests
    return {"ok": bool(found), "quest": found, "state": state}
