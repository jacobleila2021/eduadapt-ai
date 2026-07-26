"""SSIP pedagogy, visuals, tutor, companion, LXP metadata via SICS."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.accessibility import build_accessibility_guidance
from engines.subject_intelligence_core.assessment import (
    build_assessment_hints,
    build_revision_summary,
)
from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue
from engines.subject_intelligence_core.pedagogy import build_teaching_strategies
from engines.subject_intelligence_core.tutor_metadata import (
    custom_mode_block,
    error_diagnosis_block,
    graduated_hints_block,
    reflection_block,
    socratic_block,
)

TEACHING_FRAMEWORKS: tuple[dict[str, str], ...] = (
    {"id": "inquiry", "name": "Inquiry-Based Learning"},
    {"id": "guided_discovery", "name": "Guided Discovery"},
    {"id": "socratic", "name": "Socratic Learning"},
    {"id": "concept_mapping", "name": "Concept Mapping"},
    {"id": "cause_effect", "name": "Cause–Effect Analysis"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
    {"id": "spaced_practice", "name": "Spaced Practice"},
    {"id": "reflection", "name": "Reflection"},
    {"id": "collaborative", "name": "Collaborative Learning"},
    {"id": "project_based", "name": "Project-Based Learning"},
)

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "history": [
        {"visual_type": "interactive_timeline", "label": "Interactive timeline"},
        {"visual_type": "historical_comparison", "label": "Historical comparison"},
        {"visual_type": "historical_figure_card", "label": "Historical figure card"},
        {"visual_type": "source_annotation", "label": "Source annotation"},
    ],
    "geography": [
        {"visual_type": "clickable_map", "label": "Clickable map"},
        {"visual_type": "geography_overlay", "label": "Geography overlay"},
        {"visual_type": "population_chart", "label": "Population chart"},
        {"visual_type": "infographic", "label": "Geographic infographic"},
    ],
    "civics": [
        {"visual_type": "civic_decision_tree", "label": "Civic decision tree"},
        {"visual_type": "civic_concept_explorer", "label": "Civic concept explorer"},
        {"visual_type": "government_structure_diagram", "label": "Government structure diagram"},
    ],
    "political_science": [
        {"visual_type": "government_structure_diagram", "label": "Comparative government diagram"},
        {"visual_type": "civic_decision_tree", "label": "Policy decision tree"},
    ],
    "economics": [
        {"visual_type": "economic_flow_diagram", "label": "Economic flow diagram"},
        {"visual_type": "supply_demand_graph", "label": "Supply and demand graph"},
        {"visual_type": "infographic", "label": "Economics infographic"},
    ],
    "sociology": [
        {"visual_type": "concept_map", "label": "Community / culture concept map"},
        {"visual_type": "infographic", "label": "Social institutions infographic"},
    ],
    "environmental_studies": [
        {"visual_type": "cause_effect_diagram", "label": "Human impact cause–effect"},
        {"visual_type": "geography_overlay", "label": "Environment overlay"},
        {"visual_type": "infographic", "label": "Sustainability infographic"},
    ],
}


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="social_science_intelligence.teaching",
        default_domain="history",
        application_template="Apply {name} while teaching {primary} from the verified lesson.",
    )


def recommend_visuals(text: str, domains: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    from engines.social_science_intelligence.domains import detect_domains

    domains = domains if domains is not None else detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="social_science_intelligence.visuals",
        limit=10,
        default_visual={"visual_type": "concept_map", "label": "Social science concept map"},
    )


def assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    practices = (
        "source_based_questions",
        "map_based_questions",
        "timeline_sequencing",
        "case_studies",
        "civic_reasoning",
        "data_interpretation",
        "essay_planning",
        "hots_questions",
    )

    def extra(i: int, _text: str | None) -> dict[str, Any]:
        return {"social_science_practice": practices[i % len(practices)]}

    return build_assessment_hints(
        uli,
        domains,
        provenance="social_science_intelligence.assessment",
        default_domain="history",
        extra_fields=extra,
    )


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return build_revision_summary(
        domains,
        misconceptions,
        retrieval_prompts=[
            "Place three lesson events in chronological order and justify.",
            "Explain one cause–effect link using lesson evidence.",
            "Evaluate one source for purpose and limitation.",
        ],
        provenance="social_science_intelligence.revision",
    )


def accessibility_guidance(uli: Any) -> list[dict[str, Any]]:
    return build_accessibility_guidance(
        [
            {
                "recommendation": "simplified_explanations",
                "detail": "Gloss historical/geographic/civic terms beside first use.",
                "owner": "AIE",
            },
            {
                "recommendation": "reading_level_adaptation",
                "detail": "Chunk long source extracts; highlight key claims.",
                "owner": "AIE",
            },
            {
                "recommendation": "vocabulary_support",
                "detail": "Provide pop-up definitions for period, place, and institution names.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "audio_narration",
                "detail": "Offer VMLE narration for timelines and source passages.",
                "owner": "VMLE/AIE",
            },
            {
                "recommendation": "visual_summaries",
                "detail": "Pair dense text with timeline/map/infographic summaries.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "map_descriptions",
                "detail": "Structured alt text for maps: region, legend, key patterns.",
                "owner": "AIE",
            },
            {
                "recommendation": "timeline_narration",
                "detail": "Read timeline events in order with date cues for TTS.",
                "owner": "VMLE/AIE",
            },
            {
                "recommendation": "executive_function_supports",
                "detail": "Checklists for source OPCVL / cause–effect planning.",
                "owner": "AIE",
            },
            {
                "recommendation": "cognitive_load_reduction",
                "detail": "Introduce map or timeline before combining both with text.",
                "owner": "AIE",
            },
        ],
        uli,
        attach_reading_band_to="cognitive_load_reduction",
    )


def tutor_guidance(misconceptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        socratic_block(
            [
                "What claim is the lesson making?",
                "What evidence supports that claim?",
                "What other explanation might fit the same evidence?",
            ]
        ),
        custom_mode_block(
            "debate_prompts",
            prompts=[
                "Argue for and against one interpretation using only lesson sources.",
            ],
        ),
        custom_mode_block(
            "source_evaluation",
            prompts=[
                "Who created this source and why?",
                "What is valuable, and what is limited about it?",
            ],
        ),
        custom_mode_block(
            "evidence_based_reasoning",
            prompts=[
                "Link each cause to a specific piece of lesson evidence.",
            ],
        ),
        custom_mode_block(
            "citizenship_discussions",
            prompts=[
                "How does this lesson connect to rights, duties, or participation today?",
            ],
        ),
        custom_mode_block(
            "ethical_reasoning",
            prompts=[
                "Whose perspectives are included or missing in this account?",
            ],
        ),
        graduated_hints_block(
            [
                "Hint 1: Identify the time, place, and actors.",
                "Hint 2: Separate causes from consequences.",
                "Hint 3: Corroborate with a second source from the lesson.",
            ]
        ),
        error_diagnosis_block(misconceptions),
        reflection_block(
            [
                "Which skill was hardest: chronology, map reading, or source evaluation?",
                "What would you investigate next with more evidence?",
            ]
        ),
    ]


def companion_metadata(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "owner": "ALCIS",
        "behaviours": [
            {"id": "milestone_celebrations", "when": "timeline_or_map_goal_complete"},
            {"id": "encouragement", "when": "source_analysis_attempt"},
            {"id": "revision_reminders", "when": "spaced_interval_due"},
            {"id": "reflection_prompts", "when": "session_end"},
            {"id": "project_planning_support", "when": "project_based_task"},
        ],
        "active_domains": [d["domain"] for d in domains[:4]],
        "provenance": "social_science_intelligence.companion",
    }


def lxp_hints(visuals: list[dict[str, Any]], timelines: dict[str, Any], maps: dict[str, Any]) -> list[dict[str, Any]]:
    types = {v.get("visual_type") for v in visuals}
    return [
        {"hook_id": "interactive_timelines", "available": timelines.get("applicable") or "interactive_timeline" in types},
        {"hook_id": "clickable_maps", "available": maps.get("applicable") or "clickable_map" in types},
        {"hook_id": "source_annotations", "available": "source_annotation" in types},
        {"hook_id": "vocabulary_popups", "available": True},
        {"hook_id": "timeline_navigation", "available": bool(timelines.get("applicable"))},
        {"hook_id": "civic_concept_explorer", "available": "civic_concept_explorer" in types},
        {"hook_id": "historical_figure_cards", "available": "historical_figure_card" in types},
        {"hook_id": "geography_overlays", "available": "geography_overlay" in types},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
