"""CEIP pedagogy, visuals, tutor, companion, LXP metadata via SICS."""

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
    {"id": "worked_examples", "name": "Worked Examples"},
    {"id": "case_method", "name": "Case Method"},
    {"id": "guided_discovery", "name": "Guided Discovery"},
    {"id": "socratic", "name": "Socratic Learning"},
    {"id": "cause_effect", "name": "Cause–Effect Analysis"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
    {"id": "spaced_practice", "name": "Spaced Practice"},
    {"id": "project_based", "name": "Project-Based Learning"},
    {"id": "simulation", "name": "Market / Business Simulation"},
    {"id": "reflection", "name": "Reflection"},
)

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "accounting": [
        {"visual_type": "financial_statement_diagram", "label": "Financial statement diagram"},
        {"visual_type": "interactive_balance_sheet", "label": "Interactive balance sheet"},
        {"visual_type": "process_flowchart", "label": "Accounting cycle flowchart"},
    ],
    "economics": [
        {"visual_type": "supply_demand_curve", "label": "Supply–demand curve"},
        {"visual_type": "economic_graph", "label": "Economic graph"},
        {"visual_type": "market_simulation", "label": "Market simulation"},
    ],
    "business_studies": [
        {"visual_type": "business_process_flowchart", "label": "Business process flowchart"},
        {"visual_type": "decision_tree", "label": "Decision tree"},
    ],
    "finance": [
        {"visual_type": "investment_timeline", "label": "Investment timeline"},
        {"visual_type": "financial_dashboard", "label": "Financial dashboard"},
    ],
    "entrepreneurship": [
        {"visual_type": "business_model_canvas", "label": "Business model canvas"},
        {"visual_type": "decision_tree", "label": "Validation decision tree"},
    ],
    "management": [
        {"visual_type": "business_process_flowchart", "label": "Management process flowchart"},
        {"visual_type": "decision_tree", "label": "Decision tree"},
    ],
    "marketing": [
        {"visual_type": "product_lifecycle_chart", "label": "Product lifecycle chart"},
        {"visual_type": "infographic", "label": "Marketing mix infographic"},
    ],
    "taxation": [
        {"visual_type": "process_flowchart", "label": "Tax compliance flowchart"},
        {"visual_type": "infographic", "label": "Tax types infographic"},
    ],
    "commerce": [
        {"visual_type": "business_process_flowchart", "label": "Trade flow diagram"},
        {"visual_type": "infographic", "label": "Commerce channel infographic"},
    ],
    "financial_literacy": [
        {"visual_type": "investment_timeline", "label": "Saving timeline"},
        {"visual_type": "infographic", "label": "Budgeting infographic"},
    ],
}


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="commerce_economics_intelligence.teaching",
        default_domain="commerce",
        application_template="Apply {name} while teaching {primary} from the verified lesson.",
    )


def recommend_visuals(text: str, domains: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    from engines.commerce_economics_intelligence.domains import detect_domains

    domains = domains if domains is not None else detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="commerce_economics_intelligence.visuals",
        limit=10,
        default_visual={"visual_type": "infographic", "label": "Commerce concept infographic"},
    )


def assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    practices = (
        "case_studies",
        "numerical_accounting_problems",
        "financial_analysis",
        "business_scenarios",
        "economic_reasoning",
        "entrepreneurship_planning",
        "marketing_strategy_questions",
    )

    def extra(i: int, _text: str | None) -> dict[str, Any]:
        return {
            "commerce_practice": practices[i % len(practices)],
            "reveals_answers": False,
        }

    return build_assessment_hints(
        uli,
        domains,
        provenance="commerce_economics_intelligence.assessment",
        default_domain="commerce",
        extra_fields=extra,
    )


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return build_revision_summary(
        domains,
        misconceptions,
        retrieval_prompts=[
            "Explain one double-entry effect from the lesson using the accounting equation.",
            "Sketch supply and demand shift for one scenario in the lesson.",
            "List two risks and one mitigation for a finance or start-up decision discussed.",
        ],
        provenance="commerce_economics_intelligence.revision",
    )


def accessibility_guidance(uli: Any) -> list[dict[str, Any]]:
    return build_accessibility_guidance(
        [
            {
                "recommendation": "simplified_financial_explanations",
                "detail": "Gloss ratios, journal terms, and policy jargon beside first use.",
                "owner": "AIE",
            },
            {
                "recommendation": "executive_function_scaffolds",
                "detail": "Checklists for journal → ledger → trial balance → statements.",
                "owner": "AIE",
            },
            {
                "recommendation": "dyslexia_friendly_tables",
                "detail": "Increase row spacing; zebra optional; avoid dense multi-column walls.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "audio_summaries",
                "detail": "VMLE narration for statement walkthroughs and policy cause–effect.",
                "owner": "VMLE/AIE",
            },
            {
                "recommendation": "vocabulary_simplification",
                "detail": "Side-panel definitions for commerce/economics/finance terms.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "step_by_step_accounting_workflows",
                "detail": "Reveal one accounting cycle step at a time.",
                "owner": "LXP",
            },
            {
                "recommendation": "high_contrast_charts",
                "detail": "Colour-blind safe supply–demand and dashboard charts with labels.",
                "owner": "AIE",
            },
            {
                "recommendation": "cognitive_load_reduction",
                "detail": "Separate narrative case text from numerical workings.",
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
                "What decision or transaction is the lesson examining?",
                "Which accounts, markets, or stakeholders are affected?",
                "What evidence from the lesson supports your conclusion?",
            ]
        ),
        custom_mode_block(
            "guided_business_reasoning",
            prompts=[
                "Map options → criteria → recommendation using only lesson facts.",
            ],
        ),
        custom_mode_block(
            "accounting_walkthrough",
            prompts=[
                "Narrate debit/credit effects before computing totals — do not reveal protected answers.",
            ],
        ),
        custom_mode_block(
            "economic_thinking",
            prompts=[
                "Identify the shift (demand/supply/policy) and predict direction of change.",
            ],
        ),
        graduated_hints_block(
            [
                "Hint 1: Classify the problem (accounting / market / business decision).",
                "Hint 2: List knowns and unknowns from the lesson only.",
                "Hint 3: Apply the relevant principle, then check reasonableness.",
            ]
        ),
        error_diagnosis_block(misconceptions),
        reflection_block(
            [
                "Which skill was hardest: numerical accuracy, economic reasoning, or business judgment?",
                "What financial literacy habit will you practise next?",
            ]
        ),
    ]


def companion_metadata(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "owner": "ALCIS",
        "behaviours": [
            {"id": "project_milestones", "when": "case_or_plan_checkpoint"},
            {"id": "financial_literacy_encouragement", "when": "budget_or_ratio_attempt"},
            {"id": "business_planning_reminders", "when": "multi_step_project"},
            {"id": "entrepreneurship_motivation", "when": "validation_or_pitch_task"},
            {"id": "revision_planning", "when": "spaced_interval_due"},
        ],
        "active_domains": [d["domain"] for d in domains[:4]],
        "provenance": "commerce_economics_intelligence.companion",
    }


def lxp_hints(visuals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    types = {v.get("visual_type") for v in visuals}
    return [
        {"hook_id": "interactive_balance_sheets", "available": "interactive_balance_sheet" in types or "financial_statement_diagram" in types},
        {"hook_id": "financial_dashboards", "available": "financial_dashboard" in types},
        {"hook_id": "business_flowcharts", "available": "business_process_flowchart" in types or "process_flowchart" in types},
        {"hook_id": "economic_graph_explorer", "available": "economic_graph" in types or "supply_demand_curve" in types},
        {"hook_id": "timeline_visualisations", "available": "investment_timeline" in types},
        {"hook_id": "decision_tree_viewer", "available": "decision_tree" in types},
        {"hook_id": "vocabulary_side_panels", "available": True},
        {"hook_id": "business_model_canvas", "available": "business_model_canvas" in types},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
