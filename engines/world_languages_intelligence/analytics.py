"""LAIE analytics metadata for WLIP."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.analytics import analytics_event_template


def analytics_metadata(
    domains: list[dict[str, Any]],
    misconceptions: list[dict[str, Any]],
    languages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return analytics_event_template(
        interaction_events=[
            "click_pronunciation",
            "read_aloud",
            "vocab_popup_open",
            "grammar_panel_open",
            "translation_drawer",
            "speaking_record",
            "ipa_view",
        ],
        engagement_signals=[
            "vocabulary_growth",
            "pronunciation_progress",
            "reading_fluency",
        ],
        competency_ids=[d["domain"] for d in domains[:8]],
        misconception_ids=[m.get("misconception_id") for m in misconceptions[:8]],
        progression_markers=[
            "vocabulary_growth",
            "pronunciation_progress",
            "reading_fluency",
            "writing_competency",
            "grammar_mastery",
            "speaking_confidence",
        ],
        intervention_recommendations=[
            {
                "misconception_id": m.get("misconception_id"),
                "strategy": m.get("correction_strategy"),
            }
            for m in misconceptions[:5]
        ],
        provenance="world_languages_intelligence.analytics",
    ) | {
        "languages": [lang.get("id") for lang in (languages or [])[:8]],
        "track": [
            "vocabulary_growth",
            "pronunciation_progress",
            "reading_fluency",
            "writing_competency",
            "grammar_mastery",
            "speaking_confidence",
        ],
    }
