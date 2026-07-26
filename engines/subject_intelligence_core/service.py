"""Public service API for Subject Intelligence Core Services."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.analytics import analytics_event_template, from_analysis
from engines.subject_intelligence_core.competencies import competency_graph, from_domain_prereqs
from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue
from engines.subject_intelligence_core.misconceptions import detect_from_catalogue
from engines.subject_intelligence_core.pedagogy import (
    SHARED_STRATEGY_CATALOGUE,
    build_teaching_strategies,
    resolve_strategies,
)
from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.subject_intelligence_core.validation import (
    validate_accessibility_rows,
    validate_diagram_rows,
    validate_misconception_rows,
)

SUBJECT_INTELLIGENCE_CORE_SMOKE_OK = True


def core_health() -> dict[str, Any]:
    strategies = resolve_strategies(["inquiry", "cra", "retrieval_practice", "socratic"])
    return {
        "ok": SUBJECT_INTELLIGENCE_CORE_SMOKE_OK and len(strategies) == 4,
        "smoke": SUBJECT_INTELLIGENCE_CORE_SMOKE_OK,
        "version": "1.0.0",
        "strategy_catalogue_size": len(SHARED_STRATEGY_CATALOGUE),
        "modules": [
            "pedagogy",
            "misconceptions",
            "competencies",
            "taxonomy",
            "diagrams",
            "accessibility",
            "assessment",
            "tutor_metadata",
            "analytics",
            "validation",
            "visualization",
            "learning_objectives",
            "metadata",
        ],
    }


def demo_capabilities() -> dict[str, Any]:
    """Lightweight self-check used by unit tests — not a subject pack."""
    domains = detect_domains(
        "force and acceleration with photosynthesis and equations",
        {
            "forces": ("force", "acceleration"),
            "plant_biology": ("photosynthesis",),
            "algebra": ("equation",),
        },
    )
    return {
        "domains": domains,
        "strategies": build_teaching_strategies(
            resolve_strategies(["inquiry", "cra"]),
            domains,
            provenance="subject_intelligence_core.demo",
            default_domain="general",
            application_template="Apply {name} while teaching {primary}.",
        ),
        "health": core_health(),
    }


__all__ = [
    "SUBJECT_INTELLIGENCE_CORE_SMOKE_OK",
    "SHARED_STRATEGY_CATALOGUE",
    "core_health",
    "demo_capabilities",
    "detect_from_catalogue",
    "detect_domains",
    "prerequisite_hints",
    "concept_graph_from_uli",
    "build_teaching_strategies",
    "resolve_strategies",
    "recommend_visuals_from_catalogue",
    "competency_graph",
    "from_domain_prereqs",
    "analytics_event_template",
    "from_analysis",
    "validate_misconception_rows",
    "validate_diagram_rows",
    "validate_accessibility_rows",
]
