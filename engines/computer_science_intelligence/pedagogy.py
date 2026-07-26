"""CSIP pedagogy, visuals, tutor, companion, LXP metadata via SICS."""

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
    {"id": "guided_discovery", "name": "Guided Discovery"},
    {"id": "socratic", "name": "Socratic Debugging"},
    {"id": "pair_programming", "name": "Pair Programming Patterns"},
    {"id": "trace_tables", "name": "Trace Tables"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
    {"id": "spaced_practice", "name": "Spaced Practice"},
    {"id": "project_based", "name": "Project-Based Learning"},
    {"id": "unplugged", "name": "Unplugged Activities"},
    {"id": "reflection", "name": "Reflection"},
)

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "computational_thinking": [
        {"visual_type": "flowchart", "label": "Problem decomposition flowchart"},
        {"visual_type": "decision_tree", "label": "Decision tree"},
    ],
    "programming": [
        {"visual_type": "execution_trace", "label": "Execution trace"},
        {"visual_type": "code_visualisation", "label": "Code visualisation"},
        {"visual_type": "flowchart", "label": "Program flowchart"},
        {"visual_type": "uml_diagram", "label": "UML / class sketch"},
    ],
    "algorithms": [
        {"visual_type": "algorithm_animation", "label": "Algorithm animation"},
        {"visual_type": "complexity_indicator", "label": "Complexity indicator"},
        {"visual_type": "state_machine", "label": "State machine"},
    ],
    "data_structures": [
        {"visual_type": "code_visualisation", "label": "Structure visualisation"},
        {"visual_type": "flowchart", "label": "Traversal flowchart"},
    ],
    "databases": [
        {"visual_type": "database_schema_diagram", "label": "Database schema diagram"},
        {"visual_type": "er_diagram", "label": "ER diagram"},
    ],
    "networking": [
        {"visual_type": "network_diagram", "label": "Network topology diagram"},
        {"visual_type": "protocol_stack", "label": "Protocol stack view"},
    ],
    "operating_systems": [
        {"visual_type": "state_machine", "label": "Process state machine"},
        {"visual_type": "flowchart", "label": "Scheduler flowchart"},
    ],
    "cybersecurity": [
        {"visual_type": "network_diagram", "label": "Trust boundary diagram"},
        {"visual_type": "decision_tree", "label": "Threat decision tree"},
    ],
    "web_development": [
        {"visual_type": "flowchart", "label": "Request/response flowchart"},
        {"visual_type": "uml_diagram", "label": "Component sketch"},
    ],
    "artificial_intelligence": [
        {"visual_type": "decision_tree", "label": "Conceptual ML pipeline"},
        {"visual_type": "flowchart", "label": "AI lifecycle flowchart"},
    ],
    "machine_learning": [
        {"visual_type": "flowchart", "label": "Train/evaluate flowchart"},
        {"visual_type": "decision_tree", "label": "Feature decision tree"},
    ],
    "robotics": [
        {"visual_type": "flowchart", "label": "Sense–plan–act flowchart"},
        {"visual_type": "state_machine", "label": "Robot state machine"},
    ],
    "cloud_computing": [
        {"visual_type": "network_diagram", "label": "Cloud service diagram"},
        {"visual_type": "flowchart", "label": "Deploy flowchart"},
    ],
    "digital_literacy": [
        {"visual_type": "decision_tree", "label": "Online safety decision tree"},
        {"visual_type": "infographic", "label": "Digital citizenship infographic"},
    ],
}


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="computer_science_intelligence.teaching",
        default_domain="programming",
        application_template="Apply {name} while teaching {primary} from the verified lesson.",
    )


def recommend_visuals(text: str, domains: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    from engines.computer_science_intelligence.domains import detect_domains

    domains = domains if domains is not None else detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="computer_science_intelligence.visuals",
        limit=10,
        default_visual={"visual_type": "flowchart", "label": "Computer science flowchart"},
    )


def assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    practices = (
        "coding_tasks",
        "debugging_exercises",
        "trace_tables",
        "flowchart_interpretation",
        "algorithm_analysis",
        "database_design",
        "networking_scenarios",
        "ai_ethics_questions",
    )

    def extra(i: int, _text: str | None) -> dict[str, Any]:
        return {
            "computer_science_practice": practices[i % len(practices)],
            "reveals_answers": False,
        }

    return build_assessment_hints(
        uli,
        domains,
        provenance="computer_science_intelligence.assessment",
        default_domain="programming",
        extra_fields=extra,
    )


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return build_revision_summary(
        domains,
        misconceptions,
        retrieval_prompts=[
            "Trace one algorithm or program fragment from the lesson step by step.",
            "Name the Big-O class (if discussed) and what grows with input size.",
            "State one security or ethics check relevant to this topic.",
        ],
        provenance="computer_science_intelligence.revision",
    )


def accessibility_guidance(uli: Any) -> list[dict[str, Any]]:
    return build_accessibility_guidance(
        [
            {
                "recommendation": "dyslexia_friendly_code_display",
                "detail": "Increase line spacing; avoid dense monospaced walls; offer dyslexia-friendly font option.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "adjustable_syntax_highlighting",
                "detail": "Allow contrast-safe highlight themes and toggle colour cues.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "line_by_line_execution_mode",
                "detail": "Step through execution traces one line at a time.",
                "owner": "LXP",
            },
            {
                "recommendation": "audio_explanations",
                "detail": "VMLE narration for algorithms and network walks.",
                "owner": "VMLE/AIE",
            },
            {
                "recommendation": "keyboard_navigation",
                "detail": "Full keyboard access for code viewer and diagram explorers.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "colour_blind_safe_visualisations",
                "detail": "Use patterns/labels in addition to colour for algorithm and network diagrams.",
                "owner": "AIE",
            },
            {
                "recommendation": "simplified_pseudocode",
                "detail": "Offer plain-language pseudocode beside formal syntax.",
                "owner": "AIE",
            },
            {
                "recommendation": "executive_function_scaffolds",
                "detail": "Checklists for debug → test → refactor; break projects into milestones.",
                "owner": "AIE",
            },
            {
                "recommendation": "cognitive_load_reduction",
                "detail": "Show one abstraction layer at a time (logic → structure → syntax).",
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
                "What is the program or algorithm supposed to do?",
                "Where does the observed behaviour first diverge?",
                "What evidence from a trace table supports your hypothesis?",
            ]
        ),
        custom_mode_block(
            "socratic_debugging",
            prompts=[
                "Predict the next variable values before revealing the next step.",
            ],
        ),
        custom_mode_block(
            "algorithm_walkthrough",
            prompts=[
                "Narrate each step of the algorithm on a small example from the lesson.",
            ],
        ),
        custom_mode_block(
            "incremental_scaffolding",
            prompts=[
                "Solve a smaller case, then generalise — without revealing protected answers.",
            ],
        ),
        graduated_hints_block(
            [
                "Hint 1: Restate inputs, outputs, and constraints.",
                "Hint 2: Draw the control flow or data structure shape.",
                "Hint 3: Compare expected vs actual at the first mismatch.",
            ]
        ),
        error_diagnosis_block(misconceptions),
        reflection_block(
            [
                "Which skill was hardest: reading code, designing steps, or analysing complexity?",
                "What healthy coding habit will you try next session?",
            ]
        ),
    ]


def companion_metadata(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "owner": "ALCIS",
        "behaviours": [
            {"id": "coding_milestones", "when": "feature_or_exercise_complete"},
            {"id": "debugging_encouragement", "when": "failed_run_or_test"},
            {"id": "project_planning", "when": "multi_step_project"},
            {"id": "healthy_coding_habits", "when": "long_session"},
            {"id": "revision_reminders", "when": "spaced_interval_due"},
        ],
        "active_domains": [d["domain"] for d in domains[:4]],
        "provenance": "computer_science_intelligence.companion",
    }


def lxp_hints(visuals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    types = {v.get("visual_type") for v in visuals}
    return [
        {"hook_id": "interactive_code_viewer", "available": "code_visualisation" in types or "execution_trace" in types},
        {"hook_id": "flowchart_explorer", "available": "flowchart" in types},
        {"hook_id": "algorithm_animation_controls", "available": "algorithm_animation" in types},
        {"hook_id": "database_schema_viewer", "available": "database_schema_diagram" in types or "er_diagram" in types},
        {"hook_id": "network_topology_viewer", "available": "network_diagram" in types},
        {"hook_id": "inline_code_annotations", "available": True},
        {"hook_id": "complexity_indicators", "available": "complexity_indicator" in types},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
