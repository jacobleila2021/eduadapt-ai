"""Phase 4 international ingestion — Cambridge + IB."""

from __future__ import annotations

from engines.curriculum_expansion_framework.seeds_international import (
    cambridge_as_a_level_physics_seed,
    cambridge_igcse_physics_seed,
    cambridge_lower_secondary_science_seed,
    cambridge_primary_science_seed,
    ib_dp_physics_seed,
    ib_myp_sciences_seed,
    ib_pyp_science_seed,
    seed_international_packages,
)
from engines.curriculum_expansion_framework.service import api_seed_international
from engines.curriculum_expansion_framework.validators import validate_expansion_package
from engines.curriculum_migration_framework.service import (
    api_compare_curricula,
    api_ingest_international,
    api_search_curriculum,
)
from engines.verified_learning_engine import reset_registry


PROGRAMMES = (
    "cambridge_primary",
    "cambridge_lower_secondary",
    "cambridge_igcse",
    "cambridge_as_a_level",
    "ib_pyp",
    "ib_myp",
    "ib_dp",
)


def test_international_seeds_validate():
    seeds = {cid: fn() for cid, fn in [
        ("cambridge_primary", cambridge_primary_science_seed),
        ("cambridge_lower_secondary", cambridge_lower_secondary_science_seed),
        ("cambridge_igcse", cambridge_igcse_physics_seed),
        ("cambridge_as_a_level", cambridge_as_a_level_physics_seed),
        ("ib_pyp", ib_pyp_science_seed),
        ("ib_myp", ib_myp_sciences_seed),
        ("ib_dp", ib_dp_physics_seed),
    ]}
    for cid, seed in seeds.items():
        assert seed["board"] == cid
        report = validate_expansion_package(seed)
        assert report["ok"], (cid, report.get("errors"))
    assert len(seed_international_packages()) == 7


def test_cef_seed_international():
    out = api_seed_international()
    assert out["ok"] and out["phase"] == "international"
    assert set(out["boards"]) == set(PROGRAMMES)
    assert "cambridge" in out["families"] and "ib" in out["families"]
    for row in out["results"]:
        assert row.get("ok"), row


def test_cmif_ingest_international():
    out = api_ingest_international(via_cmif=True, publish=True)
    assert out["ok"] and out["phase"] == 4 and out["via"] == "cmif"
    boards = [(r.get("job") or {}).get("board") for r in out["results"]]
    assert set(boards) == set(PROGRAMMES)
    for row in out["results"]:
        assert row.get("ok"), row
        stages = set(row.get("stages") or row.get("job", {}).get("stages_done") or [])
        assert "publish" in stages and "map_ucf" in stages


def test_ib_and_cambridge_assessment_meta():
    igcse = cambridge_igcse_physics_seed()
    assert any(m.get("type") == "igcse_paper" for m in igcse["assessment_mappings"])
    dp = ib_dp_physics_seed()
    types = {m.get("type") for m in dp["assessment_mappings"]}
    assert "dp_paper_1" in types and "internal_assessment" in types
    myp = ib_myp_sciences_seed()
    assert len(myp.get("myp_criteria") or []) == 4


def test_cross_family_compare():
    api_seed_international()
    search = api_search_curriculum("forces", board="cambridge_igcse")
    assert search["ok"]
    cmp = api_compare_curricula("cambridge_igcse", "ib_myp")
    assert "ok" in cmp


def test_no_engine_changes_required():
    ids = {e["engine_id"] for e in reset_registry().list_engines()}
    for required in ("universal_curriculum", "curriculum_expansion", "curriculum_migration"):
        assert required in ids


def test_cmif_phase4_international_smoke(capsys):
    """CMIF_PHASE4_INTERNATIONAL_SMOKE_OK"""
    assert api_seed_international()["ok"]
    out = api_ingest_international(via_cmif=True, publish=True)
    assert out["ok"]
    assert set((r.get("job") or {}).get("board") for r in out["results"]) == set(PROGRAMMES)

    with capsys.disabled():
        print("CMIF_PHASE4_INTERNATIONAL_SMOKE_OK")
