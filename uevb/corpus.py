"""Benchmark corpus — subjects × curricula × adaptations (specs + sample ULI)."""

from __future__ import annotations

from typing import Any

from uevb.constants import ADAPTATIONS, CORPUS_SEEDS, CURRICULA, SUBJECTS


def build_sample_uli(
    *,
    subject: str,
    topic: str,
    concept: str,
    curriculum: str = "cbse",
) -> dict[str, Any]:
    """Deterministic ULI-shaped payload for corpus composition."""
    claim = f"{concept} is a precise idea in {topic}."
    example = f"A clear classroom or home example helps explain {concept.lower()}."
    return {
        "universal_profile": {
            "topic": topic,
            "subject": subject,
            "curriculum": curriculum,
            "concepts": [
                {"name": concept, "explanation": claim},
                {"name": topic.split()[0], "explanation": f"{topic} organises related ideas."},
                {"name": "Evidence", "explanation": "Lesson evidence keeps explanations accurate."},
            ],
            "claim_ledger": [
                {"text": claim},
                {"text": f"{topic} uses accurate definitions and examples."},
                {"text": example},
            ],
            "vocabulary": [
                {"term": concept, "definition": claim},
                {"term": topic.split()[0], "definition": f"A key part of {topic}."},
                {"term": "Evidence", "definition": "Support from the lesson."},
                {"term": "Example", "definition": "A real situation that shows the idea."},
            ],
            "learning_objectives": [f"Explain {concept} within {topic}."],
            "examples": [{"text": example}],
            "misconceptions": [
                {
                    "label": f"{concept} is often confused with a related everyday word",
                    "correction": f"Keep the lesson definition of {concept} precise.",
                }
            ],
            "prerequisites": [{"text": f"Know everyday language related to {topic}."}],
        }
    }


def build_sample_sif(*, subject: str, topic: str, concept: str) -> dict[str, Any]:
    return {
        "subject_key": subject if subject != "business_studies" else "business",
        "analysis": {
            "misconceptions": [
                {
                    "label": f"Learners mix up {concept} with a nearby idea",
                    "correction": f"Separate {concept} using lesson evidence.",
                }
            ],
            "assessment_hints": [
                {"prompt": f"Explain {concept} in your own words."},
                {"prompt": f"Give one real-life example from {topic}."},
                {"prompt": f"State one mistake to avoid about {concept}."},
                {"prompt": f"Connect {concept} to another idea in {topic}."},
            ],
            "prerequisites": [{"text": f"Basic familiarity with {topic}"}],
        },
    }


def build_sample_uvie(*, topic: str, concept: str) -> dict[str, Any]:
    return {
        "preferred_visuals": [
            {
                "caption": f"{topic} organiser showing {concept}",
                "kind": "flowchart",
                "visual_id": f"uvie_{concept.lower().replace(' ', '_')}",
            }
        ],
        "visuals": [],
    }


def iter_corpus_specs(
    *,
    subjects: tuple[str, ...] | None = None,
    curricula: tuple[str, ...] | None = None,
    max_topics_per_subject: int = 2,
) -> list[dict[str, Any]]:
    """Expand the full subject × curriculum matrix (topic seeds × curricula)."""
    subjects = subjects or SUBJECTS
    curricula = curricula or CURRICULA
    specs: list[dict[str, Any]] = []
    for subject in subjects:
        seeds = (CORPUS_SEEDS.get(subject) or [{"topic": subject.title(), "concept": "Core idea"}])[
            :max_topics_per_subject
        ]
        for seed in seeds:
            for curriculum in curricula:
                specs.append(
                    {
                        "subject": subject,
                        "curriculum": curriculum,
                        "topic": seed["topic"],
                        "concept": seed["concept"],
                        "adaptations": list(ADAPTATIONS),
                        "corpus_id": f"{subject}.{curriculum}.{seed['topic']}".replace(" ", "_").lower(),
                    }
                )
    return specs


def corpus_size(
    *,
    subjects: tuple[str, ...] | None = None,
    curricula: tuple[str, ...] | None = None,
    max_topics_per_subject: int = 2,
) -> dict[str, int]:
    specs = iter_corpus_specs(
        subjects=subjects, curricula=curricula, max_topics_per_subject=max_topics_per_subject
    )
    return {
        "lesson_specs": len(specs),
        "subjects": len(subjects or SUBJECTS),
        "curricula": len(curricula or CURRICULA),
        "adaptations_per_lesson": len(ADAPTATIONS),
        "adaptation_pages": len(specs) * len(ADAPTATIONS),
    }
