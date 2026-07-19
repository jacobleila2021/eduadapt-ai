"""VMLE intelligence aggregator — presentation plan from engine context."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.accessibility import apply_aie
from engines.voice_multimodal_learning.analytics import record, summary
from engines.voice_multimodal_learning.multimodal import interactive_bundle
from engines.voice_multimodal_learning.multilingual import settings as lang_settings
from engines.voice_multimodal_learning.narration import plan_narration
from engines.voice_multimodal_learning.personalization import personalize
from engines.voice_multimodal_learning.recommendations import recommend
from engines.voice_multimodal_learning.synchronization import devices


def analyze_voice_multimodal_context(context: dict[str, Any]) -> dict[str, Any]:
    lesson = context.get("lesson_text") or context.get("topic") or ""
    prefs = personalize(context)
    a11y = apply_aie(context)
    narration = plan_narration(
        lesson,
        spec_id="original",
        speed=float(prefs.get("speed") or 1.0),
        language=context.get("language") or "en",
        voice_style=prefs.get("voice_style") or "Female",
        title=context.get("title") or "",
    )
    stem = interactive_bundle(context)
    recs = recommend({**context, "personalization": prefs, "has_stem": bool(stem.get("verified_artifacts"))})
    record("session_plan", session_id=str(context.get("vmle_session_id") or ""), payload={"lesson_chars": len(lesson)})

    return {
        "engine": "voice_multimodal",
        "version": "1.0.0",
        "layer": "presentation_interaction",
        "personalization": prefs,
        "accessibility": a11y,
        "narration": narration.to_dict(),
        "multimodal": stem,
        "multilingual": lang_settings(
            language=context.get("language") or "en",
            dual_language=bool(context.get("dual_language")),
        ),
        "recommendations": recs,
        "devices": devices(),
        "teacher_controls": context.get("teacher_controls")
        or {"narration": True, "voice_style": prefs.get("voice_style"), "pronunciation": True, "interactive": True, "offline": True},
        "parent_controls": context.get("parent_controls")
        or {"enable_narration": True, "view_audio_usage": True, "monitor_pronunciation": True},
        "analytics_hook": summary(str(context.get("vmle_session_id") or "")),
        "policy": {
            "atie_is_teaching_intelligence": True,
            "stem_via_deterministic_engines": True,
            "never_invent_official_answers": True,
            "vlie_orchestrates_events": True,
        },
    }
