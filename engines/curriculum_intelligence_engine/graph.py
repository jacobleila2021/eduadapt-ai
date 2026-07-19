"""Curriculum knowledge graph — nodes, edges, traversal."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from engines.curriculum_intelligence_engine.schemas import (
    ConceptNode,
    CrossCurriculumLink,
    LearningOutcome,
    PrerequisiteEdge,
)


class CurriculumKnowledgeGraph:
    """In-memory directed graph for concepts, outcomes, and cross-links."""

    def __init__(self) -> None:
        self.concepts: dict[str, ConceptNode] = {}
        self.outcomes: dict[str, LearningOutcome] = {}
        self.prerequisites: list[PrerequisiteEdge] = []
        self.cross_links: list[CrossCurriculumLink] = []
        self._children: dict[str, list[str]] = defaultdict(list)  # prereq → dependents
        self._parents: dict[str, list[str]] = defaultdict(list)  # concept → prereqs

    def add_concept(self, node: ConceptNode) -> None:
        self.concepts[node.concept_id] = node

    def add_outcome(self, outcome: LearningOutcome) -> None:
        self.outcomes[outcome.outcome_id] = outcome

    def add_prerequisite(self, edge: PrerequisiteEdge) -> None:
        self.prerequisites.append(edge)
        self._children[edge.from_concept].append(edge.to_concept)
        self._parents[edge.to_concept].append(edge.from_concept)

    def add_cross_link(self, link: CrossCurriculumLink) -> None:
        self.cross_links.append(link)

    def get_concept(self, concept_id: str) -> ConceptNode | None:
        return self.concepts.get(concept_id)

    def prerequisite_chain(self, concept_id: str) -> list[str]:
        """Return ordered prerequisites (roots first) for a concept."""
        if concept_id not in self.concepts:
            return []
        visited: set[str] = set()
        order: list[str] = []

        def dfs(cid: str) -> None:
            for parent in self._parents.get(cid, []):
                if parent not in visited:
                    dfs(parent)
            if cid not in visited and cid != concept_id:
                visited.add(cid)
                order.append(cid)

        dfs(concept_id)
        return order

    def dependents(self, concept_id: str) -> list[str]:
        return list(self._children.get(concept_id, []))

    def missing_prerequisites(self, concept_id: str, mastered: set[str] | None = None) -> list[str]:
        mastered = mastered or set()
        return [p for p in self.prerequisite_chain(concept_id) if p not in mastered]

    def bfs_related(self, concept_id: str, depth: int = 2) -> list[str]:
        if concept_id not in self.concepts:
            return []
        seen = {concept_id}
        q: deque[tuple[str, int]] = deque([(concept_id, 0)])
        out: list[str] = []
        while q:
            cid, d = q.popleft()
            if d > 0:
                out.append(cid)
            if d >= depth:
                continue
            node = self.concepts.get(cid)
            neighbors = list(self._parents.get(cid, [])) + list(self._children.get(cid, []))
            if node:
                neighbors.extend(node.related_concepts)
            for n in neighbors:
                if n not in seen and n in self.concepts:
                    seen.add(n)
                    q.append((n, d + 1))
        return out

    def cross_links_for(self, concept_id: str, board: str | None = None) -> list[dict[str, Any]]:
        rows = [c for c in self.cross_links if c.concept_id == concept_id]
        if board:
            b = board.lower()
            rows = [c for c in rows if c.board.lower() == b]
        return [c.to_dict() for c in rows]

    def path_summary(self, concept_id: str) -> dict[str, Any]:
        node = self.concepts.get(concept_id)
        if not node:
            return {}
        return {
            "concept_id": concept_id,
            "title": node.title,
            "curriculum_path": {
                "chapter": node.chapter,
                "chapter_title": node.chapter_title,
                "topic": node.topic or node.title,
                "concept": node.title,
            },
            "prerequisites": self.prerequisite_chain(concept_id),
            "dependents": self.dependents(concept_id),
            "related": node.related_concepts,
            "learning_outcomes": [
                o.to_dict()
                for o in self.outcomes.values()
                if concept_id in o.concept_ids
            ],
            "cross_curriculum": self.cross_links_for(concept_id),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "concept_count": len(self.concepts),
            "outcome_count": len(self.outcomes),
            "prerequisite_edges": len(self.prerequisites),
            "cross_links": len(self.cross_links),
            "concepts": [c.to_dict() for c in self.concepts.values()],
            "outcomes": [o.to_dict() for o in self.outcomes.values()],
            "prerequisites": [e.to_dict() for e in self.prerequisites],
            "cross_maps": [c.to_dict() for c in self.cross_links],
        }
