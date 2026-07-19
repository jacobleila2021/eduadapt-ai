"""REST-shaped API facade for AI Tutor Intelligence Engine."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.analytics import tutor_analytics_summary
from engines.ai_tutor_intelligence_engine.conversation_manager import run_tutor_turn
from engines.ai_tutor_intelligence_engine.explanations import generate_explanation
from engines.ai_tutor_intelligence_engine.hints import generate_hint
from engines.ai_tutor_intelligence_engine.indexing import rebuild_atie_index
from engines.ai_tutor_intelligence_engine.intelligence import analyze_tutor_context
from engines.ai_tutor_intelligence_engine.personalization import select_explanation_depth
from engines.ai_tutor_intelligence_engine.reflection import format_reflection_record, reflection_prompts
from engines.ai_tutor_intelligence_engine.retrieval import retrieve_grounding
from engines.ai_tutor_intelligence_engine.session_memory import end_session, record_reflection, start_session
from engines.ai_tutor_intelligence_engine.tutor_profile import build_tutor_context
from engines.ai_tutor_intelligence_engine.worked_examples import worked_example


def api_start_tutoring_session(learner_id: str, **meta: Any) -> dict[str, Any]:
    return start_session(learner_id, meta)


def api_end_session(session_id: str, progress: dict[str, Any] | None = None) -> dict[str, Any]:
    return end_session(session_id, progress)


def api_retrieve_learner_context(**kwargs: Any) -> dict[str, Any]:
    ctx = build_tutor_context(kwargs)
    return {"ok": True, "context": ctx.to_dict()}


def api_generate_explanation(**kwargs: Any) -> dict[str, Any]:
    ctx = build_tutor_context(kwargs)
    grounding = retrieve_grounding(ctx, kwargs)
    depth = kwargs.get("depth") or select_explanation_depth(ctx)
    return generate_explanation(ctx, grounding, depth=depth)


def api_generate_hint(**kwargs: Any) -> dict[str, Any]:
    ctx = build_tutor_context(kwargs)
    grounding = retrieve_grounding(ctx, kwargs)
    return generate_hint(ctx, grounding, level=int(kwargs.get("hint_level") or 1), allow_full_solution=ctx.allow_direct_answers)


def api_retrieve_worked_example(**kwargs: Any) -> dict[str, Any]:
    ctx = build_tutor_context(kwargs)
    grounding = retrieve_grounding(ctx, kwargs)
    return worked_example(ctx, grounding)


def api_record_reflection(session_id: str, answers: dict[str, Any]) -> dict[str, Any]:
    return record_reflection(session_id, format_reflection_record(answers))


def api_update_session_memory(**kwargs: Any) -> dict[str, Any]:
    """Run a tutor turn which appends to session memory."""
    return run_tutor_turn(kwargs)


def api_retrieve_tutor_analytics(learner_id: str) -> dict[str, Any]:
    return tutor_analytics_summary(learner_id)


def api_analyze_context(context: dict[str, Any]) -> dict[str, Any]:
    return analyze_tutor_context(context)


def api_reflection_prompts(**kwargs: Any) -> dict[str, Any]:
    return reflection_prompts(build_tutor_context(kwargs))


def api_rebuild_index() -> dict[str, Any]:
    return rebuild_atie_index()
