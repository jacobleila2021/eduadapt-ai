"""Ontology loader — build CIE graph from seed + optional KIE packages."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from engines.curriculum_intelligence_engine.graph import CurriculumKnowledgeGraph
from engines.curriculum_intelligence_engine.schemas import (
    Competency,
    ConceptNode,
    CrossCurriculumLink,
    CurriculumRef,
    LearningOutcome,
    PrerequisiteEdge,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_ONTOLOGY = DATA_DIR / "pilot_ontology_class8_science.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_graph_from_ontology(data: dict[str, Any]) -> CurriculumKnowledgeGraph:
    g = CurriculumKnowledgeGraph()
    board = data.get("board") or "Unknown"
    grade = str(data.get("grade") or "")
    subject = data.get("subject") or "Science"

    for raw in data.get("concepts") or []:
        g.add_concept(
            ConceptNode(
                concept_id=raw["concept_id"],
                title=raw["title"],
                definition=raw.get("definition") or "",
                subject=subject,
                grade_range=[grade] if grade else [],
                difficulty=raw.get("difficulty") or "medium",
                chapter=int(raw.get("chapter") or 0),
                chapter_title=raw.get("chapter_title") or "",
                topic=raw.get("topic") or raw["title"],
                bloom=raw.get("bloom") or "understand",
                dok=str(raw.get("dok") or ""),
                prerequisites=list(raw.get("prerequisites") or []),
                related_concepts=list(raw.get("related_concepts") or []),
                keywords=list(raw.get("keywords") or []),
                board=board,
                original_term=raw.get("original_term") or raw["title"],
            )
        )

    for raw in data.get("learning_outcomes") or []:
        g.add_outcome(
            LearningOutcome(
                outcome_id=raw["outcome_id"],
                statement=raw["statement"],
                bloom=raw.get("bloom") or "understand",
                dok=str(raw.get("dok") or "2"),
                concept_ids=list(raw.get("concept_ids") or []),
                success_criteria=list(raw.get("success_criteria") or []),
                board=board,
                grade=grade,
                subject=subject,
                chapter=int(raw.get("chapter") or 0),
                equivalent_ids=list(raw.get("equivalent_ids") or []),
            )
        )

    for raw in data.get("prerequisites") or []:
        g.add_prerequisite(
            PrerequisiteEdge(
                from_concept=raw["from_concept"],
                to_concept=raw["to_concept"],
                relation=raw.get("relation") or "requires",
                strength=float(raw.get("strength") or 1.0),
            )
        )

    for raw in data.get("cross_maps") or []:
        g.add_cross_link(
            CrossCurriculumLink(
                concept_id=raw["concept_id"],
                board=raw["board"],
                programme=raw.get("programme") or "",
                label=raw.get("label") or "",
                grade=str(raw.get("grade") or ""),
                notes=raw.get("notes") or "",
                link_type=raw.get("link_type") or "equivalent",
            )
        )

    return g


def load_competencies(data: dict[str, Any]) -> list[Competency]:
    out: list[Competency] = []
    for raw in data.get("competencies") or []:
        out.append(
            Competency(
                competency_id=raw["competency_id"],
                name=raw["name"],
                description=raw.get("description") or "",
                skills=list(raw.get("skills") or []),
                evidence=list(raw.get("evidence") or []),
                mastery_threshold=float(raw.get("mastery_threshold") or 0.8),
                assessment_methods=list(raw.get("assessment_methods") or []),
                related_concepts=list(raw.get("related_concepts") or []),
                accessibility_notes=list(raw.get("accessibility_notes") or []),
            )
        )
    return out


def curriculum_ref_from_ontology(data: dict[str, Any]) -> CurriculumRef:
    return CurriculumRef(
        curriculum_id=data.get("curriculum_id") or "unknown",
        board=data.get("board") or "Unknown",
        programme=data.get("programme") or "",
        grade=str(data.get("grade") or ""),
        subject=data.get("subject") or "",
        version=data.get("version") or "1.0.0",
        original_labels={
            "curriculum": data.get("curriculum") or "",
            "edition": data.get("edition") or "",
        },
    )


@lru_cache(maxsize=4)
def load_default_ontology() -> tuple[dict[str, Any], CurriculumKnowledgeGraph, tuple[Competency, ...]]:
    data = _load_json(DEFAULT_ONTOLOGY)
    graph = build_graph_from_ontology(data)
    comps = tuple(load_competencies(data))
    return data, graph, comps


def get_adaptations_map(data: dict[str, Any] | None = None) -> dict[str, Any]:
    if data is None:
        data, _, _ = load_default_ontology()
    return dict(data.get("adaptations") or {})
