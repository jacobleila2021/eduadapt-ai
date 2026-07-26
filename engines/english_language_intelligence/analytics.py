"""LAIE-oriented analytics metadata for ELIP."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.analytics import analytics_event_template


def analytics_metadata(
    domains: list[dict[str, Any]],
    vocabulary: dict[str, Any],
    misconceptions: list[dict[str, Any]],
) -> dict[str, Any]:
    return analytics_event_template(
        interaction_events=[
            "passage_open",
            "vocab_define",
            "pronounce_click",
            "annotation_add",
            "draft_revise",
            "listening_play",
        ],
        engagement_signals=["reading_time", "words_looked_up", "draft_iterations", "oral_attempts"],
        learning_objective_ids=[],
        competency_ids=[d["domain"] for d in domains[:8]],
        misconception_ids=[m.get("misconception_id") for m in misconceptions[:8]],
        progression_markers=[
            "reading_progress",
            "vocabulary_growth",
            "writing_development",
            "grammar_mastery",
            "reading_fluency",
            "pronunciation_practice",
            "literature_engagement",
        ],
        intervention_recommendations=[
            {
                "misconception_id": m.get("misconception_id"),
                "strategy": m.get("correction_strategy"),
            }
            for m in misconceptions[:5]
        ],
        provenance="english_language_intelligence.analytics",
    ) | {
        "vocabulary_entry_count": len(vocabulary.get("entries") or []),
        "track": [
            "reading_progress",
            "vocabulary_growth",
            "writing_development",
            "grammar_mastery",
            "reading_fluency",
            "pronunciation_practice",
            "literature_engagement",
        ],
    }
