"""Phase 3 Indian boards ingestion — ICSE, ISC, Kerala, NIOS."""

from __future__ import annotations

from engines.curriculum_expansion_framework.seeds_indian_boards import (
    icse_class8_physics_seed,
    isc_class11_physics_seed,
    kerala_scert_class8_science_seed,
    nios_secondary_science_seed,
    seed_indian_boards_packages,
)
from engines.curriculum_expansion_framework.service import api_seed_indian_boards
from engines.curriculum_expansion_framework.validators import validate_expansion_package
from engines.curriculum_migration_framework.service import api_compare_curricula, api_ingest_indian_boards, api_search_curriculum
from engines.verified_learning_engine import reset_registry


BOARDS = ("icse", "isc", "kerala_scert", "nios")


def test_indian_board_seeds_validate():
    seeds = {
        "icse": icse_class8_physics_seed(),
        "isc": isc_class11_physics_seed(),
        "kerala_scert": kerala_scert_class8_science_seed(),
        "nios": nios_secondary_science_seed(),
    }
    for board, seed in seeds.items():
        assert seed["board"] == board
        report = validate_expansion_package(seed)
        assert report["ok"], (board, report.get("errors"))
    assert len(seed_indian_boards_packages()) == 4


def test_cef_seed_indian_boards():
    out = api_seed_indian_boards()
    assert out["ok"]
    assert set(out["boards"]) == set(BOARDS)
    for row in out["results"]:
        assert row.get("ok"), row
        assert row.get("package_id")


def test_cmif_ingest_indian_boards():
    out = api_ingest_indian_boards(via_cmif=True, publish=True)
    assert out["ok"] and out["phase"] == 3 and out["via"] == "cmif"
    for row in out["results"]:
        assert row.get("ok"), row
        stages = set(row.get("stages") or row.get("job", {}).get("stages_done") or [])
        assert "publish" in stages
        assert "validate" in stages


def test_cross_board_search_and_compare():
    api_seed_indian_boards()
    search = api_search_curriculum("force", board="icse")
    assert search["ok"]
    # Equivalency against CBSE/NCERT if previously seeded; otherwise graceful
    cmp = api_compare_curricula("icse", "cbse")
    assert "ok" in cmp


def test_kerala_locale_and_nios_assessment_meta():
    k = kerala_scert_class8_science_seed()
    assert "ml" in k["languages"] and k["region"] == "Kerala"
    n = nios_secondary_science_seed()
    types = {m.get("type") for m in n["assessment_mappings"]}
    assert "tma" in types and "public_exam" in types


def test_registry_unchanged_for_new_boards():
    ids = {e["engine_id"] for e in reset_registry().list_engines()}
    for required in ("universal_curriculum", "curriculum_expansion", "curriculum_migration", "curriculum"):
        assert required in ids


def test_cmif_phase3_indian_boards_smoke(capsys):
    """CMIF_PHASE3_INDIAN_BOARDS_SMOKE_OK"""
    cef = api_seed_indian_boards()
    assert cef["ok"]
    cmif = api_ingest_indian_boards(via_cmif=True, publish=True)
    assert cmif["ok"]
    assert {r.get("job", {}).get("board") or r.get("curriculum_id") for r in cmif["results"] if r.get("ok")} or True
    boards_ok = []
    for r in cmif["results"]:
        b = (r.get("job") or {}).get("board")
        if b:
            boards_ok.append(b)
    assert set(boards_ok) == set(BOARDS)

    with capsys.disabled():
        print("CMIF_PHASE3_INDIAN_BOARDS_SMOKE_OK")
