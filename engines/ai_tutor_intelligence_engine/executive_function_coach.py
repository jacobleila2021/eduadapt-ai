"""Executive function coaching — complements ALE/AIE (presentation/planning only)."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import TutorContext


def executive_function_coach(ctx: TutorContext) -> dict[str, Any]:
    profiles = set(ctx.accessibility_profiles or [])
    need = bool(profiles.intersection({"adhd", "executive_function", "working_memory", "processing_speed", "autism"}))
    tips = []
    if need or ctx.confidence < 0.5:
        tips = [
            {"area": "planning", "tip": "Write a 3-step checklist before starting."},
            {"area": "task_initiation", "tip": "Start with a 2-minute timer on the first step only."},
            {"area": "organisation", "tip": "Keep one notebook section: Goal → Evidence → Check."},
            {"area": "time_management", "tip": f"Budget {(ctx.pathway.get('next_activity') or {}).get('estimated_minutes') or 10} minutes, then pause."},
            {"area": "goal_setting", "tip": (ctx.goals[0] if ctx.goals else "Finish one concept check today.")},
            {"area": "reflection", "tip": "After, note: What worked? What is still unclear?"},
            {"area": "study_scheduling", "tip": "Schedule a short review tomorrow (spaced repetition)."},
            {"area": "revision_planning", "tip": "Use official practice items only — no invented keys."},
        ]
    return {
        "enabled": need or bool(tips),
        "tips": tips,
        "complements": ["ALE pacing", "AIE EF supports"],
        "policy": "coaching_only_no_curriculum_change",
    }
