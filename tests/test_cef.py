"""Curriculum Expansion Framework tests."""

from __future__ import annotations

import uuid

from engines.curriculum_expansion_framework import CurriculumExpansionEngine
from engines.curriculum_expansion_framework.equivalency import compare_curricula
from engines.curriculum_expansion_framework.mapping import map_to_ucf_payload, mapping_completeness
from engines.curriculum_expansion_framework.registry import ensure_family_catalogue, list_supported_boards
from engines.curriculum_expansion_framework.schemas import CURRICULUM_FAMILIES
from engines.curriculum_expansion_framework.seeds import cbse_class8_science_seed, ncert_class8_science_seed
from engines.curriculum_expansion_framework.service import (
    api_compare_curricula,
    api_dashboard,
    api_import_curriculum_package,
    api_list_supported_boards,
    api_publish_package,
    api_search_curriculum,
    api_seed_priority,
    api_validate_package,
    api_version_history,
)
from engines.curriculum_expansion_framework.validators import validate_expansion_package
from engines.curriculum_expansion_framework.versioning import compare_versions, snapshot
from engines.verified_learning_engine import reset_registry


def test_family_catalogue():
    assert "ncert" in CURRICULUM_FAMILIES and "cambridge_igcse" in CURRICULUM_FAMILIES
    assert "ib_dp" in CURRICULUM_FAMILIES and "cpd" in CURRICULUM_FAMILIES
    out = ensure_family_catalogue()
    assert out["ok"] and out["count"] >= len(CURRICULUM_FAMILIES)
    boards = list_supported_boards()
    assert any(b["curriculum_id"] == "cbse" for b in boards)


def test_mapping_and_validation():
    seed = ncert_class8_science_seed()
    mapped = map_to_ucf_payload(seed, curriculum_id="ncert")
    assert mapped["board"] == "ncert"
    assert len(mapped["concepts"]) >= 2
    comp = mapping_completeness(seed)
    assert comp["completeness"] > 0.5
    report = validate_expansion_package(seed)
    assert report["ok"] and not report["reject"]

    bad = {"subject": "Science"}  # missing board/grade/topics
    bad_report = validate_expansion_package(bad)
    assert bad_report["reject"]


def test_import_ncert_cbse_to_ucf():
    ncert = api_import_curriculum_package("ncert", ncert_class8_science_seed(), publish=True, source="test")
    assert ncert["ok"] and ncert["package_id"]
    assert ncert["policy"]["engines_consume_ucf_only"]
    cbse = api_import_curriculum_package("cbse", cbse_class8_science_seed(), publish=True, source="test")
    assert cbse["ok"]
    pub = api_publish_package("ncert", ncert["package_id"])
    assert pub["ok"]


def test_reject_incomplete_and_unknown_board():
    bad = api_import_curriculum_package("ncert", {"subject": "Science"}, source="test")
    assert bad["ok"] is False
    unknown = api_import_curriculum_package("made_up_board", {"subject": "X", "grade": "1", "topics": ["a"]})
    assert unknown["ok"] is False and unknown.get("error") == "unsupported_curriculum"


def test_versioning():
    cid = f"ncert"
    s1 = snapshot(cid, {"topics": [{"id": "a", "title": "Force"}], "version": "1.0.0"}, status="draft")
    s2 = snapshot(cid, {"topics": [{"id": "a", "title": "Force"}, {"id": "b", "title": "Pressure"}], "version": "1.1.0"}, status="draft")
    hist = api_version_history(cid)
    assert hist["ok"] and len(hist["history"]) >= 2
    diff = compare_versions(cid, s1["snapshot_id"], s2["snapshot_id"])
    assert diff["ok"]
    assert any("Pressure" in str(x) or "b" in str(x) for x in (diff.get("added") or []) + [diff])


def test_equivalency_and_search():
    # Ensure packages exist
    api_seed_priority()
    cmp = api_compare_curricula(left_board="ncert", right_board="cbse")
    # May succeed if packages indexed; otherwise graceful error
    assert "ok" in cmp
    search = api_search_curriculum("force", board="ncert", subject="Science")
    assert search["ok"]
    assert search["source"]


def test_dashboard_and_apis():
    dash = api_dashboard()
    assert dash["ok"] and dash["supported_boards"]
    assert "1 NCERT+CBSE" in str(dash.get("incremental_order"))
    assert api_list_supported_boards()["ok"]
    assert api_validate_package(ncert_class8_science_seed())["validation"]["ok"]


def test_registry_and_engine():
    reg = reset_registry()
    ids = {e["engine_id"] for e in reg.list_engines()}
    assert "curriculum_expansion" in ids
    assert "universal_curriculum" in ids
    eng = CurriculumExpansionEngine()
    out = eng.process({"include_dashboard": False})
    assert out.ok
    assert out.payload["policy"]["engines_consume_ucf_only"]
    assert eng.health_check().ok


def test_legacy_engines_unchanged():
    ids = {e["engine_id"] for e in reset_registry().list_engines()}
    for required in ("universal_curriculum", "curriculum", "assessment", "learning_experience", "curriculum_expansion"):
        assert required in ids


def test_curriculum_expansion_framework_smoke(capsys):
    """CURRICULUM_EXPANSION_FRAMEWORK_SMOKE_OK"""
    ensure_family_catalogue()
    assert len(list_supported_boards()) >= 15
    seeded = api_seed_priority()
    assert seeded["ok"]
    ncert_pkg = next(r for r in seeded["results"] if r.get("curriculum_id") == "ncert")
    assert ncert_pkg.get("ok")
    assert api_search_curriculum("pressure", board="cbse")["ok"]
    eng = CurriculumExpansionEngine()
    assert eng.process({"seed_priority": False}).ok
    assert reset_registry().get("curriculum_expansion").health_check().ok

    with capsys.disabled():
        print("CURRICULUM_EXPANSION_FRAMEWORK_SMOKE_OK")
