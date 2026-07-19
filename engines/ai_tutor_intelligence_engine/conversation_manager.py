"""Conversation manager — session lifecycle + grounded turns."""

from __future__ import annotations

import uuid
from typing import Any

from engines.ai_tutor_intelligence_engine.personalization import select_mode
from engines.ai_tutor_intelligence_engine.reasoning import reason_response
from engines.ai_tutor_intelligence_engine.retrieval import retrieve_grounding
from engines.ai_tutor_intelligence_engine.schemas import TutorTurn
from engines.ai_tutor_intelligence_engine.session_memory import append_turn, start_session
from engines.ai_tutor_intelligence_engine.tutor_profile import build_tutor_context


def run_tutor_turn(context: dict[str, Any]) -> dict[str, Any]:
    ctx = build_tutor_context(context)
    grounding = retrieve_grounding(ctx, context)
    mode_info = select_mode(ctx)
    mode = mode_info["mode"]
    action = context.get("tutor_action") or "tutor"
    hint_level = int(context.get("hint_level") or 1)

    reasoned = reason_response(ctx, grounding, mode=mode, action=action, hint_level=hint_level)
    turn = TutorTurn(
        turn_id=f"turn_{uuid.uuid4().hex[:8]}",
        role="tutor",
        mode=mode,
        content=reasoned.get("content") or "",
        grounding_ok=bool(reasoned.get("ok")),
        hint_level=hint_level if action == "hint" else None,
        citations=(reasoned.get("grounding") or {}).get("citations") or grounding.citations,
        explainability=reasoned.get("explainability") or "",
    )

    session_id = context.get("session_id")
    session = None
    if not session_id and context.get("start_session", True):
        session = start_session(ctx.learner_id, {"topic": ctx.topic, "mode": mode})
        session_id = session["session_id"]
    if session_id:
        try:
            session = append_turn(
                session_id,
                {
                    **turn.to_dict(),
                    "concept_id": (ctx.concept_ids[0] if ctx.concept_ids else None),
                    "action": action,
                },
            )
        except FileNotFoundError:
            session = start_session(ctx.learner_id, {"topic": ctx.topic})
            session_id = session["session_id"]
            session = append_turn(session_id, turn.to_dict())

    return {
        "session_id": session_id,
        "context": ctx.to_dict(),
        "mode": mode_info,
        "turn": turn.to_dict(),
        "response": reasoned,
        "session": {"concepts_discussed": (session or {}).get("concepts_discussed"), "hints_used": (session or {}).get("hints_used")}
        if session
        else {},
    }
