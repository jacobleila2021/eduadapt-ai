"""ATIE intelligence — full tutoring package for VLIE AITutorEngine."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.analytics import record_tutor_event, tutor_analytics_summary
from engines.ai_tutor_intelligence_engine.confidence import estimate_tutor_confidence
from engines.ai_tutor_intelligence_engine.conversation_manager import run_tutor_turn
from engines.ai_tutor_intelligence_engine.executive_function_coach import executive_function_coach
from engines.ai_tutor_intelligence_engine.indexing import rebuild_atie_index
from engines.ai_tutor_intelligence_engine.motivation import motivation_nudge
from engines.ai_tutor_intelligence_engine.multimodal import multimodal_bundle
from engines.ai_tutor_intelligence_engine.personalization import select_mode
from engines.ai_tutor_intelligence_engine.prompts import build_presentation_prompt
from engines.ai_tutor_intelligence_engine.recommendations import tutor_recommendations
from engines.ai_tutor_intelligence_engine.reflection import reflection_prompts
from engines.ai_tutor_intelligence_engine.retrieval import retrieve_grounding
from engines.ai_tutor_intelligence_engine.schemas import TUTOR_MODES
from engines.ai_tutor_intelligence_engine.tutor_profile import build_tutor_context


def analyze_tutor_context(context: dict[str, Any]) -> dict[str, Any]:
    """
    Prepare grounded tutor resources + optional first turn.
    Never invents curriculum/STEM/official answers.
    """
    ctx = build_tutor_context(context)
    grounding = retrieve_grounding(ctx, context)
    mode_info = select_mode(ctx)
    conf = estimate_tutor_confidence(
        ctx,
        hint_usage=int(context.get("hint_usage") or 0),
        self_reported=context.get("self_reported_confidence"),
    )
    ef = executive_function_coach(ctx)
    reflection = reflection_prompts(ctx)
    motivation = motivation_nudge(ctx)
    multimodal = multimodal_bundle(ctx, grounding, context)
    recs = tutor_recommendations(ctx, mode=mode_info["mode"], grounding_ok=grounding.ok)

    # Optional immediate turn when asked
    turn_pack = None
    if context.get("generate_turn", True):
        turn_pack = run_tutor_turn({**context, "start_session": context.get("start_session", True)})
        if ctx.learner_id and ctx.learner_id != "anonymous":
            try:
                record_tutor_event(ctx.learner_id, "session_start", {"mode": mode_info["mode"]})
                if context.get("tutor_action") == "hint":
                    record_tutor_event(ctx.learner_id, "hint", {"level": context.get("hint_level")})
                else:
                    record_tutor_event(ctx.learner_id, "question", {"mode": mode_info["mode"]})
            except Exception:  # noqa: BLE001
                pass

    # STEM misconception hooks (v1 compatibility)
    outputs = context.get("engine_outputs") or {}
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}
    artifacts = sa.get("artifacts") or []
    misconception_hooks = [
        a.get("payload", {}).get("common_mistakes")
        for a in artifacts
        if (a.get("payload") or {}).get("common_mistakes")
    ][:5]

    prompt_pack = build_presentation_prompt(
        learner_message=context.get("learner_message") or "",
        grounding=grounding.to_dict(),
        mode=mode_info["mode"],
        personalization=(turn_pack or {}).get("response", {}).get("personalization") or {},
    )

    return {
        # v1 compatibility keys
        "modes": list(TUTOR_MODES),
        "grounding": "ENGINE_ARTIFACTS + RAG + CIE + AME — never general knowledge first",
        "verified_artifact_count": len(artifacts) + len(grounding.stem_artifacts),
        "misconception_hooks": misconception_hooks or ctx.misconceptions[:3],
        "audio_available": True,
        "accessibility_profile": {
            "profiles": ctx.accessibility_profiles,
            "presentation_mode": ctx.presentation_mode,
            "never_alter_curriculum_accuracy": True,
        },
        "adaptive_brief": ((outputs.get("adaptive_learning") or {}).get("payload") or {}).get("explainability")
        or {},
        "next_activity": ((outputs.get("adaptive_learning") or {}).get("payload") or {}).get("next_activity"),
        "presentation_policy": "adjust language/pacing/style only — facts locked",
        # ATIE enrichment
        "tutor_context": ctx.to_dict(),
        "selected_mode": mode_info,
        "grounding_packet": grounding.to_dict(),
        "confidence": conf,
        "executive_function_coach": ef,
        "reflection": reflection,
        "motivation": motivation,
        "multimodal": multimodal,
        "recommendations": recs,
        "session": turn_pack,
        "prompt_pack": prompt_pack,
        "analytics": tutor_analytics_summary(ctx.learner_id) if ctx.learner_id != "anonymous" else {},
        "teacher_controls": {
            "set_mode": True,
            "limit_assistance": True,
            "disable_direct_answers": True,
            "require_socratic": True,
            "assign_goals": True,
            "override_recommendations": True,
            "review_conversations": True,
        },
        "parent_controls": {
            "view_summaries": True,
            "home_suggestions": True,
            "monitor_activity": True,
            "hide_assessment_keys": True,
        },
        "policy": {
            "never_invent_curriculum": True,
            "never_invent_official_answers": True,
            "never_invent_stem_facts": True,
            "retrieve_before_generate": True,
            "prefer_hints_over_answers": True,
            "refuse_if_ungrounded": True,
        },
        "atie_version": "1.0.0",
    }


def ensure_indexed() -> dict[str, Any]:
    return rebuild_atie_index()
