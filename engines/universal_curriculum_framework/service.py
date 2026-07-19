"""REST-shaped API facade for Universal Curriculum Framework."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.board_registry import list_boards
from engines.universal_curriculum_framework.competency import list_competencies
from engines.universal_curriculum_framework.curriculum_model import catalogue, get_curriculum_model
from engines.universal_curriculum_framework.curriculum_registry import list_packages, load_package
from engines.universal_curriculum_framework.diagrams import list_diagrams
from engines.universal_curriculum_framework.formulas import list_formulae
from engines.universal_curriculum_framework.glossary import find_term
from engines.universal_curriculum_framework.import_pipeline import import_curriculum, IMPORTERS
from engines.universal_curriculum_framework.indexing import index_package
from engines.universal_curriculum_framework.metadata import curriculum_metadata, migrate_version
from engines.universal_curriculum_framework.prerequisites import previous_current_future, build_dependency_graph
from engines.universal_curriculum_framework.question_bank import list_questions
from engines.universal_curriculum_framework.search import search_curriculum
from engines.universal_curriculum_framework.validation import validate_package


def api_import_curriculum(source: str, payload: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    return import_curriculum(source, payload, dry_run=bool(kwargs.get("dry_run")))


def api_validate_curriculum(package: dict[str, Any] | None = None, package_id: str = "") -> dict[str, Any]:
    doc = package or load_package(package_id)
    if not doc:
        return {"ok": False, "error": "not_found"}
    return {"ok": True, "validation": validate_package(doc)}


def api_search_curriculum(query: str, **kwargs: Any) -> dict[str, Any]:
    return search_curriculum(query, board_id=str(kwargs.get("board_id") or ""), limit=int(kwargs.get("limit") or 20))


def api_retrieve_topic(package_id: str, topic_id: str) -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "package_not_found"}
    for t in pkg.get("topics") or []:
        if t.get("topic_id") == topic_id:
            return {"ok": True, "topic": t}
    return {"ok": False, "error": "topic_not_found"}


def api_retrieve_competency(package_id: str, competency_id: str = "") -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "not_found"}
    comps = list_competencies(pkg)
    if competency_id:
        comps = [c for c in comps if c.get("competency_id") == competency_id]
    return {"ok": True, "competencies": comps}


def api_retrieve_formula(package_id: str, **kwargs: Any) -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "not_found"}
    return {"ok": True, "formulae": list_formulae(pkg, domain=str(kwargs.get("domain") or ""))}


def api_retrieve_figure(package_id: str) -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "not_found"}
    return {"ok": True, "diagrams": list_diagrams(pkg)}


def api_retrieve_question_bank(package_id: str, **kwargs: Any) -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "not_found"}
    return {"ok": True, "questions": list_questions(pkg, official_only=bool(kwargs.get("official_only")))}


def api_retrieve_glossary(package_id: str, query: str = "") -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "not_found"}
    if query:
        return {"ok": True, "terms": find_term(pkg, query)}
    return {"ok": True, "terms": pkg.get("glossary") or []}


def api_retrieve_learning_objectives(package_id: str, topic_id: str = "") -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "not_found"}
    rows = []
    for t in pkg.get("topics") or []:
        if topic_id and t.get("topic_id") != topic_id:
            continue
        rows.append({"topic_id": t.get("topic_id"), "objectives": t.get("objectives")})
    return {"ok": True, "objectives": rows}


def api_retrieve_prerequisites(package_id: str, topic_id: str = "") -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "not_found"}
    if topic_id:
        for t in pkg.get("topics") or []:
            if t.get("topic_id") == topic_id:
                return {"ok": True, **previous_current_future(t)}
        return {"ok": False, "error": "topic_not_found"}
    return {"ok": True, "graph": build_dependency_graph(pkg)}


def api_retrieve_curriculum_metadata(package_id: str = "") -> dict[str, Any]:
    if package_id:
        return curriculum_metadata(package_id)
    return {"ok": True, "catalogue": catalogue(), "boards": list_boards(), "importers": list(IMPORTERS)}


def api_index_curriculum(package_id: str) -> dict[str, Any]:
    return index_package(package_id)


def api_migrate_curriculum(package_id: str, new_version: str, **kwargs: Any) -> dict[str, Any]:
    return migrate_version(package_id, new_version, changes=kwargs.get("changes"))


def api_get_model(package_id: str) -> dict[str, Any]:
    return get_curriculum_model(package_id)
