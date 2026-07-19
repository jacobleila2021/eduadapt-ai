"""Import pipeline — board sources → UCF packages."""

from __future__ import annotations

from typing import Any
import uuid

from engines.universal_curriculum_framework.board_registry import get_board
from engines.universal_curriculum_framework.curriculum_registry import save_package
from engines.universal_curriculum_framework.normalization import normalize_board_id, normalize_to_structure
from engines.universal_curriculum_framework.schemas import (
    AcademicStructure,
    BoardMetadata,
    CompetencyNode,
    LearningObjectivesBlock,
    PrerequisiteGraph,
    TaxonomyTags,
    UCFPackage,
    UCFTopic,
)
from engines.universal_curriculum_framework.validation import validate_package


IMPORTERS = (
    "ncert",
    "cbse",
    "icse",
    "isc",
    "cambridge",
    "ib",
    "nios",
    "state_board",
    "university",
    "professional",
    "kie_package",
    "cie_ontology",
)


def import_curriculum(source: str, payload: dict[str, Any] | None = None, *, dry_run: bool = False) -> dict[str, Any]:
    """
    Transform source content into a UCF package.
    source: importer id (ncert, cbse, kie_package, cie_ontology, ...)
    """
    payload = payload or {}
    source = (source or "").lower().strip()
    if source not in IMPORTERS and source not in ("pilot", "generic"):
        return {"ok": False, "error": "unknown_importer", "supported": list(IMPORTERS)}

    if source in ("kie_package",) or payload.get("package_id") and payload.get("text_chunks") is not None:
        package = _from_kie(payload)
    elif source in ("cie_ontology", "pilot") or payload.get("concepts"):
        package = _from_cie_or_pilot(payload, board_hint=source)
    else:
        package = _from_generic_board(source, payload)

    doc = package.to_dict()
    report = validate_package(doc)
    if not report["ok"]:
        return {"ok": False, "validation": report, "package": doc}
    if dry_run:
        return {"ok": True, "validation": report, "package": doc, "persisted": False}
    saved = save_package(package)
    return {"ok": True, "validation": report, "package_id": saved["package_id"], "path": saved["path"], "persisted": True}


def _from_kie(payload: dict[str, Any]) -> UCFPackage:
    board_id = normalize_board_id(
        str(
            (payload.get("curriculum") or {}).get("board")
            or payload.get("board")
            or "Unknown"
        )
    )
    board = get_board(board_id)
    cur = payload.get("curriculum") or {}
    structure = AcademicStructure(
        grade=str(cur.get("grade") or ""),
        subject=str(cur.get("subject") or ""),
        chapter=str(cur.get("chapter_title") or cur.get("chapter") or ""),
        chapter_number=int(cur.get("chapter") or 0) if str(cur.get("chapter") or "").isdigit() else 0,
        topic=str(cur.get("topic") or ""),
    )
    topics = []
    for i, concept in enumerate(payload.get("concepts") or ["general"]):
        cid = concept if isinstance(concept, str) else str(concept.get("id") or concept.get("name") or f"c{i}")
        title = concept if isinstance(concept, str) else str(concept.get("title") or concept.get("name") or cid)
        topics.append(
            UCFTopic(
                topic_id=f"ucf.{board_id}.{cid}",
                title=title,
                board=board,
                structure=structure,
                objectives=LearningObjectivesBlock(
                    knowledge=list(payload.get("learning_objectives") or [])[:5],
                    misconceptions=[],
                ),
                competencies=[CompetencyNode(competency_id=f"comp.{cid}", description=f"Demonstrate understanding of {title}")],
                taxonomy=TaxonomyTags(blooms="understand", dok="2"),
                source_labels={"kie_package_id": str(payload.get("package_id") or "")},
            )
        )
    return UCFPackage(
        package_id=str(payload.get("package_id") or f"ucf_kie_{uuid.uuid4().hex[:8]}"),
        board=board,
        structure=structure,
        topics=topics,
        formulae=[{"formula_id": f"eq_{i}", "latex": e.get("latex") if isinstance(e, dict) else str(e), "verification_engine": "sympy"} for i, e in enumerate(payload.get("equations") or [])],
        diagrams=[{"diagram_id": f"fig_{i}", "alt_text": "", "path": f.get("path") if isinstance(f, dict) else str(f)} for i, f in enumerate(payload.get("figures") or [])],
        glossary=[{"term_id": f"gl_{i}", "term": v.get("term") if isinstance(v, dict) else str(v), "definition": v.get("definition") if isinstance(v, dict) else ""} for i, v in enumerate(payload.get("vocabulary") or [])],
        questions=[{"question_id": f"q_{i}", "source": "official" if True else "ai", "text": q.get("text") if isinstance(q, dict) else str(q), "official": True} for i, q in enumerate(payload.get("questions") or [])],
        version=str(payload.get("version") or "1.0.0"),
    )


def _from_cie_or_pilot(payload: dict[str, Any], *, board_hint: str = "cbse") -> UCFPackage:
    board = get_board(payload.get("board") or board_hint or "unknown")
    concepts = payload.get("concepts") or []
    # Load pilot ontology if empty
    if not concepts:
        try:
            from pathlib import Path
            import json
            from knowledge.paths import PROJECT_ROOT

            candidates = [
                PROJECT_ROOT / "engines" / "curriculum_intelligence_engine" / "data" / "pilot_ontology_class8_science.json",
                PROJECT_ROOT / "data" / "pilot_ontology_class8_science.json",
            ]
            for seed in candidates:
                if seed.is_file():
                    data = json.loads(seed.read_text(encoding="utf-8"))
                    concepts = data.get("concepts") or data.get("nodes") or data.get("concept_nodes") or []
                    # Some seeds nest under ontology
                    if not concepts and isinstance(data.get("ontology"), dict):
                        concepts = data["ontology"].get("concepts") or []
                    payload.setdefault("curriculum_id", data.get("curriculum_id") or "ncert_cbse_class8_science_v1")
                    if concepts:
                        break
        except Exception:  # noqa: BLE001
            concepts = []
        if not concepts:
            concepts = [
                {"id": "c8sci.force", "title": "Force", "prerequisites": [], "definition": "A push or a pull"},
                {"id": "c8sci.pressure", "title": "Pressure", "prerequisites": ["c8sci.force"], "definition": "Force per unit area"},
            ]
    structure = AcademicStructure(
        program="K-12",
        stage="secondary",
        grade=str(payload.get("grade") or "8"),
        subject=str(payload.get("subject") or "Science"),
    )
    topics: list[UCFTopic] = []
    concept_ids = []
    for c in concepts:
        if isinstance(c, str):
            c = {"id": c, "title": c}
        cid = str(c.get("concept_id") or c.get("id") or c.get("name") or f"concept_{i}")
        concept_ids.append(cid)
        prereqs = list(c.get("prerequisites") or [])
        topics.append(
            UCFTopic(
                topic_id=f"ucf.{cid}",
                title=str(c.get("title") or c.get("name") or cid),
                board=board,
                structure=AcademicStructure(
                    program=structure.program,
                    stage=structure.stage,
                    grade=structure.grade,
                    subject=structure.subject,
                    chapter_number=int(c.get("chapter") or 0),
                    chapter=str(c.get("chapter_title") or ""),
                    topic=str(c.get("topic") or ""),
                ),
                objectives=LearningObjectivesBlock(
                    knowledge=[str(c.get("definition") or f"Understand {c.get('title') or cid}")],
                    misconceptions=list(c.get("misconceptions") or []),
                    big_ideas=list(c.get("big_ideas") or []),
                ),
                competencies=[
                    CompetencyNode(
                        competency_id=str(x) if not isinstance(x, dict) else str(x.get("id") or x.get("competency_id")),
                        description=str(x) if not isinstance(x, dict) else str(x.get("description") or x.get("name") or ""),
                    )
                    for x in (c.get("competency_ids") or [f"comp.{cid}"])
                ],
                taxonomy=TaxonomyTags(blooms=str(c.get("bloom") or "understand"), dok=str(c.get("dok") or "2")),
                prerequisites=PrerequisiteGraph(
                    previous_concepts=prereqs,
                    current_concepts=[cid],
                    edges=[{"from": p, "to": cid, "relation": "requires"} for p in prereqs],
                ),
                source_labels={"cie_concept_id": cid, "original_term": str(c.get("original_term") or "")},
            )
        )
    pid = str(payload.get("curriculum_id") or payload.get("package_id") or f"ucf_{board.board_id}_{uuid.uuid4().hex[:8]}")
    return UCFPackage(package_id=pid, board=board, structure=structure, topics=topics, version="1.0.0")


def _from_generic_board(source: str, payload: dict[str, Any]) -> UCFPackage:
    board = get_board(source)
    norm = normalize_to_structure(payload)
    structure = AcademicStructure(
        grade=str(payload.get("grade") or ""),
        subject=str(payload.get("subject") or ""),
        chapter=str(payload.get("chapter_title") or ""),
        topic=str(payload.get("topic") or "General"),
    )
    topic = UCFTopic(
        topic_id=f"ucf.{board.board_id}.{uuid.uuid4().hex[:8]}",
        title=str(payload.get("topic") or payload.get("title") or "Imported topic"),
        board=board,
        structure=structure,
        objectives=LearningObjectivesBlock(knowledge=list(payload.get("objectives") or ["Understand the topic"])),
        competencies=[CompetencyNode(competency_id=f"comp.{board.board_id}.1", description="Apply core ideas")],
        source_labels={"importer": source, "hierarchy": str(norm.get("hierarchy"))},
    )
    return UCFPackage(
        package_id=str(payload.get("package_id") or f"ucf_{board.board_id}_{uuid.uuid4().hex[:8]}"),
        board=board,
        structure=structure,
        topics=[topic],
    )
