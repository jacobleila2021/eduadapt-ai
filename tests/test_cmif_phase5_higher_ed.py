"""Phase 5 higher education + professional learning ingestion."""

from __future__ import annotations

from engines.curriculum_expansion_framework.seeds_higher_ed import (
    college_diploma_applied_science_seed,
    corporate_learning_safety_seed,
    cpd_teacher_digital_seed,
    foundation_stem_bridge_seed,
    professional_cert_stem_educator_seed,
    seed_higher_ed_packages,
    university_intro_physics_seed,
)
from engines.curriculum_expansion_framework.service import api_seed_higher_ed
from engines.curriculum_expansion_framework.validators import validate_expansion_package
from engines.curriculum_migration_framework.service import (
    api_compare_curricula,
    api_ingest_higher_ed,
    api_search_curriculum,
)
from engines.verified_learning_engine import reset_registry


PROGRAMMES = (
    "university",
    "college",
    "foundation",
    "professional_cert",
    "corporate_learning",
    "cpd",
)


def test_higher_ed_seeds_validate():
    seeds = {
        "university": university_intro_physics_seed(),
        "college": college_diploma_applied_science_seed(),
        "foundation": foundation_stem_bridge_seed(),
        "professional_cert": professional_cert_stem_educator_seed(),
        "corporate_learning": corporate_learning_safety_seed(),
        "cpd": cpd_teacher_digital_seed(),
    }
    for cid, seed in seeds.items():
        assert seed["board"] == cid
        report = validate_expansion_package(seed)
        assert report["ok"], (cid, report.get("errors"))
    assert len(seed_higher_ed_packages()) == 6


def test_cef_seed_higher_ed():
    out = api_seed_higher_ed()
    assert out["ok"] and out["phase"] == "higher_ed_professional"
    assert set(out["boards"]) == set(PROGRAMMES)
    assert "higher_ed" in out["families"] and "professional" in out["families"]
    for row in out["results"]:
        assert row.get("ok"), row


def test_cmif_ingest_higher_ed():
    out = api_ingest_higher_ed(via_cmif=True, publish=True)
    assert out["ok"] and out["phase"] == 5 and out["via"] == "cmif"
    boards = [(r.get("job") or {}).get("board") for r in out["results"]]
    assert set(boards) == set(PROGRAMMES)
    for row in out["results"]:
        assert row.get("ok"), row
        stages = set(row.get("stages") or row.get("job", {}).get("stages_done") or [])
        assert "publish" in stages


def test_professional_and_uni_metadata():
    uni = university_intro_physics_seed()
    assert uni.get("level") == "undergraduate" and any(f.get("latex") == "F = ma" for f in uni["formulae"])
    corp = corporate_learning_safety_seed()
    assert corp.get("mandatory") is True
    cpd = cpd_teacher_digital_seed()
    assert cpd.get("cpd_hours") == 8
    pro = professional_cert_stem_educator_seed()
    assert "verified" in (pro["topics"][0]["title"] or "").lower()


def test_search_and_compare():
    api_seed_higher_ed()
    assert api_search_curriculum("newton", board="university")["ok"]
    cmp = api_compare_curricula("university", "foundation")
    assert "ok" in cmp


def test_engines_unchanged():
    ids = {e["engine_id"] for e in reset_registry().list_engines()}
    for required in ("universal_curriculum", "curriculum_expansion", "curriculum_migration"):
        assert required in ids


def test_cmif_phase5_higher_ed_smoke(capsys):
    """CMIF_PHASE5_HIGHER_ED_SMOKE_OK"""
    assert api_seed_higher_ed()["ok"]
    out = api_ingest_higher_ed(via_cmif=True, publish=True)
    assert out["ok"]
    assert set((r.get("job") or {}).get("board") for r in out["results"]) == set(PROGRAMMES)

    with capsys.disabled():
        print("CMIF_PHASE5_HIGHER_ED_SMOKE_OK")
