"""Universal Curriculum Framework (UCF) tests."""

from __future__ import annotations

from engines.universal_curriculum_framework import UniversalCurriculumEngine
from engines.universal_curriculum_framework.adapters import for_cie, for_lmas, for_ame, for_ale
from engines.universal_curriculum_framework.board_registry import list_boards, get_board
from engines.universal_curriculum_framework.import_pipeline import import_curriculum, IMPORTERS
from engines.universal_curriculum_framework.prerequisites import build_dependency_graph
from engines.universal_curriculum_framework.search import search_curriculum
from engines.universal_curriculum_framework.service import (
    api_import_curriculum,
    api_retrieve_curriculum_metadata,
    api_retrieve_prerequisites,
    api_search_curriculum,
    api_validate_curriculum,
)
from engines.universal_curriculum_framework.validation import validate_package
from engines.verified_learning_engine import get_registry, reset_registry


def test_boards_and_importers():
    assert len(list_boards()) >= 10
    assert get_board("cbse").board_name == "CBSE"
    assert "kie_package" in IMPORTERS and "cie_ontology" in IMPORTERS


def test_registry_includes_ucf():
    reg = reset_registry()
    ids = {e["engine_id"] for e in reg.list_engines()}
    assert "universal_curriculum" in ids
    assert "curriculum" in ids
    # CIE depends on UCF
    cur = next(e for e in reg.list_engines() if e["engine_id"] == "curriculum")
    assert "universal_curriculum" in (cur.get("depends_on") or [])


def test_import_pilot_and_validate():
    result = api_import_curriculum("cie_ontology", {"board": "cbse", "grade": "8", "subject": "Science"})
    assert result["ok"]
    assert result["validation"]["ok"]
    pid = result["package_id"]
    meta = api_retrieve_curriculum_metadata(pid)
    assert meta["ok"]
    val = api_validate_curriculum(package_id=pid)
    assert val["ok"] and val["validation"]["ready_to_import"]


def test_knowledge_graph_and_search():
    result = import_curriculum("cie_ontology", {"board": "ncert", "grade": "8", "subject": "Science"})
    assert result["ok"]
    from engines.universal_curriculum_framework.curriculum_registry import load_package

    pkg = load_package(result["package_id"])
    graph = build_dependency_graph(pkg)
    assert graph["nodes"]
    hits = search_curriculum("force", board_id="")
    assert hits["ok"]


def test_adapters_for_engines():
    result = import_curriculum("generic", {"board": "ib", "topic": "Inquiry", "grade": "10", "subject": "Science", "objectives": ["Ask questions"]})
    # generic not in IMPORTERS list as exact - use cambridge with payload
    result = import_curriculum("cambridge", {"topic": "Forces", "grade": "9", "subject": "Physics", "objectives": ["Describe force"]})
    assert result["ok"]
    pid = result["package_id"]
    assert for_cie(pid)["ok"] and for_cie(pid)["concepts"]
    assert for_lmas(pid)["ok"]
    assert for_ame(pid)["ok"]
    assert for_ale(pid)["ok"] and for_ale(pid)["prerequisite_graph"]["knowledge_graph"]


def test_engine_process():
    eng = UniversalCurriculumEngine()
    out = eng.process({"topic": "cells", "board": "CBSE"})
    assert out.ok
    assert out.payload["system"] == "UCF"
    assert out.payload["policy"]["board_expansion_via_importers_only"] is True
    assert out.payload["adapters"]["cie"]["ok"] or out.payload["ensure"]["ok"]


def test_cross_board_mapping_ids_stable():
    a = import_curriculum("cbse", {"topic": "Cell", "grade": "8", "subject": "Science", "objectives": ["Identify cell parts"]})
    b = import_curriculum("ib", {"topic": "Cell", "grade": "8", "subject": "Science", "objectives": ["Identify cell parts"]})
    assert a["ok"] and b["ok"]
    assert a["package_id"] != b["package_id"]


def test_validation_catches_missing_package_id():
    report = validate_package({"topics": []})
    assert report["ok"] is False
    assert "missing_package_id" in report["errors"]


def test_legacy_engines_remain():
    ids = {e["engine_id"] for e in get_registry().list_engines()}
    for required in ("universal_curriculum", "curriculum", "assessment", "learning_motivation", "ai_tutor"):
        assert required in ids


def test_ucf_smoke(capsys):
    """UCF_SMOKE_OK via standard pytest."""
    reg = reset_registry()
    assert reg.get("universal_curriculum").health_check().ok
    eng = UniversalCurriculumEngine()
    bundle = eng.process({})
    assert bundle.ok and bundle.payload["schema"] == "ucf/1.0"
    imported = api_import_curriculum("cie_ontology", {"board": "cbse", "grade": "8", "subject": "Science"})
    assert imported["ok"]
    assert api_search_curriculum("cell")["ok"]
    assert api_retrieve_prerequisites(imported["package_id"])["ok"]

    with capsys.disabled():
        print("UCF_SMOKE_OK")
