"""Mapping — UCF ↔ CIE / KIE shapes (preserve official IDs)."""

from __future__ import annotations

from typing import Any


def ucf_topic_to_cie_concept(topic: dict[str, Any]) -> dict[str, Any]:
    """Project a UCF topic into CIE ConceptNode-compatible dict."""
    structure = topic.get("structure") or {}
    taxonomy = topic.get("taxonomy") or {}
    prereq = topic.get("prerequisites") or {}
    source = topic.get("source_labels") or {}
    cie_id = source.get("cie_concept_id") or topic.get("topic_id", "").replace("ucf.", "")
    return {
        "concept_id": cie_id,
        "title": topic.get("title") or "",
        "definition": ((topic.get("objectives") or {}).get("knowledge") or [""])[0],
        "subject": structure.get("subject") or "",
        "grade_range": [structure.get("grade")] if structure.get("grade") else [],
        "chapter": int(structure.get("chapter_number") or 0),
        "chapter_title": structure.get("chapter") or "",
        "topic": structure.get("topic") or "",
        "bloom": taxonomy.get("blooms") or "understand",
        "dok": taxonomy.get("dok") or "",
        "prerequisites": list(prereq.get("previous_concepts") or []),
        "competency_ids": [c.get("competency_id") for c in (topic.get("competencies") or []) if isinstance(c, dict)],
        "keywords": [],
        "board": (topic.get("board") or {}).get("board_name") or "Unknown",
        "original_term": source.get("original_term") or "",
        "ucf_topic_id": topic.get("topic_id"),
    }


def ucf_package_to_cie_payload(package: dict[str, Any]) -> dict[str, Any]:
    topics = package.get("topics") or []
    concepts = [ucf_topic_to_cie_concept(t) for t in topics]
    return {
        "curriculum_id": package.get("package_id"),
        "board": (package.get("board") or {}).get("board_name"),
        "concepts": concepts,
        "learning_objectives": [
            {
                "outcome_id": f"lo.{c['concept_id']}",
                "statement": c.get("definition") or "",
                "concept_ids": [c["concept_id"]],
                "bloom": c.get("bloom"),
                "dok": c.get("dok"),
            }
            for c in concepts
        ],
        "competencies": [
            comp
            for t in topics
            for comp in (t.get("competencies") or [])
        ],
        "prerequisites": [
            edge
            for t in topics
            for edge in ((t.get("prerequisites") or {}).get("edges") or [])
        ],
        "source": "ucf",
        "schema": "ucf/1.0→cie",
    }


def kie_package_hint(package: dict[str, Any]) -> dict[str, Any]:
    """Fields KIE may attach when emitting UCF."""
    return {
        "ucf_ready": True,
        "preferred_importer": "kie_package",
        "preserves_official_questions": True,
        "package_id": package.get("package_id"),
    }
