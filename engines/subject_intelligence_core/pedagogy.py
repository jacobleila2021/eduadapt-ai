"""Shared pedagogy strategy catalogue and builders."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

# Canonical strategy catalogue — packs select subsets / aliases.
SHARED_STRATEGY_CATALOGUE: tuple[dict[str, str], ...] = (
    {"id": "inquiry", "name": "Inquiry-Based Learning", "family": "inquiry"},
    {"id": "direct_instruction", "name": "Direct Instruction", "family": "explicit"},
    {"id": "explicit_instruction", "name": "Explicit Instruction", "family": "explicit"},
    {"id": "guided_discovery", "name": "Guided Discovery", "family": "inquiry"},
    {"id": "socratic", "name": "Socratic Learning", "family": "dialogic"},
    {"id": "cra", "name": "Concrete–Representational–Abstract", "family": "representation"},
    {"id": "worked_examples", "name": "Worked Examples", "family": "scaffolding"},
    {"id": "retrieval_practice", "name": "Retrieval Practice", "family": "memory"},
    {"id": "spaced_learning", "name": "Spaced Learning", "family": "memory"},
    {"id": "spaced_practice", "name": "Spaced Practice", "family": "memory"},
    {"id": "reflection", "name": "Reflection", "family": "metacognition"},
    {"id": "problem_based", "name": "Problem-Based Learning", "family": "inquiry"},
    {"id": "project_based", "name": "Project-Based Learning", "family": "inquiry"},
    {"id": "collaborative", "name": "Collaborative Learning", "family": "social"},
    {"id": "poe", "name": "Predict–Observe–Explain", "family": "inquiry"},
    {"id": "cer", "name": "Claim–Evidence–Reasoning", "family": "inquiry"},
    {"id": "gradual_release", "name": "Gradual Release of Responsibility", "family": "scaffolding"},
    {"id": "productive_struggle", "name": "Productive Struggle", "family": "scaffolding"},
    {"id": "interleaving", "name": "Interleaving", "family": "memory"},
    {"id": "multiple_representations", "name": "Multiple Representations", "family": "representation"},
    {"id": "conceptual_change", "name": "Conceptual Change", "family": "metacognition"},
    {"id": "experimental_investigation", "name": "Experimental Investigation", "family": "inquiry"},
    {"id": "visual_learning", "name": "Visual Learning", "family": "representation"},
    {"id": "concept_mapping", "name": "Concept Mapping", "family": "representation"},
    {"id": "systems_thinking", "name": "Systems Thinking", "family": "systems"},
    {"id": "structure_function", "name": "Structure–Function Relationships", "family": "systems"},
    {"id": "cause_effect", "name": "Cause–Effect Analysis", "family": "systems"},
    {"id": "scientific_investigation", "name": "Scientific Investigation", "family": "inquiry"},
)


def resolve_strategies(framework_ids: Sequence[str]) -> list[dict[str, str]]:
    by_id = {s["id"]: s for s in SHARED_STRATEGY_CATALOGUE}
    out: list[dict[str, str]] = []
    for fid in framework_ids:
        if fid in by_id:
            out.append({"id": by_id[fid]["id"], "name": by_id[fid]["name"]})
    return out


def build_teaching_strategies(
    frameworks: Sequence[Mapping[str, str]],
    domains: list[dict[str, Any]],
    *,
    provenance: str,
    default_domain: str,
    application_template: str,
) -> list[dict[str, Any]]:
    """
    Build pack teaching strategy metadata.

    ``application_template`` must include ``{name}`` and ``{primary}`` placeholders
    so each pack preserves its historical wording.
    """
    primary = domains[0]["domain"] if domains else default_domain
    return [
        {
            "framework": fw["id"],
            "name": fw["name"],
            "application": application_template.format(name=fw["name"], primary=primary),
            "provenance": provenance,
        }
        for fw in frameworks
    ]
