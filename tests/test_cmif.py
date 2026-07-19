"""CMIF — production curriculum migration & ingestion tests."""

from __future__ import annotations

import time

from engines.curriculum_expansion_framework.seeds import ncert_class8_science_seed
from engines.curriculum_migration_framework import CurriculumMigrationEngine
from engines.curriculum_migration_framework.licensing import compute_source_hash, sanitize_filename, verify_checksum
from engines.curriculum_migration_framework.mapper import map_to_ucf
from engines.curriculum_migration_framework.migration import run_migration
from engines.curriculum_migration_framework.normalizer import normalize_package
from engines.curriculum_migration_framework.schemas import PIPELINE_STAGES, SUPPORTED_BOARDS
from engines.curriculum_migration_framework.service import (
    api_dashboard,
    api_get_import_status,
    api_import_curriculum,
    api_list_supported_boards,
    api_search_curriculum,
    api_validate_curriculum,
    api_archive_curriculum,
    api_rollback_version,
)
from engines.curriculum_migration_framework.validator import validate_package
from engines.curriculum_migration_framework.versioning import save_version, version_history
from engines.verified_learning_engine import reset_registry


def _seed() -> dict:
    s = ncert_class8_science_seed()
    s["source_url"] = "https://example.test/ncert/class8/science"
    return s


def test_pipeline_stages_complete():
    assert len(PIPELINE_STAGES) >= 15
    assert PIPELINE_STAGES[0] == "import" and PIPELINE_STAGES[-1] == "publish"
    assert "ncert" in SUPPORTED_BOARDS and "cambridge" in SUPPORTED_BOARDS


def test_security_checksum_and_sanitize():
    seed = _seed()
    h = compute_source_hash(seed)
    assert verify_checksum(seed, h)["ok"]
    assert not verify_checksum(seed, "deadbeef")["ok"]
    assert ".." not in sanitize_filename("../evil/path.pdf")


def test_validate_reject_incomplete():
    bad = validate_package({"subject": "Science"}, provenance={"source_type": "json"})
    assert bad["reject"]
    good = validate_package(_seed(), provenance={"source_type": "json", "source_hash": "abc", "source_url": "x"})
    assert good["ok"]


def test_normalize_and_map():
    norm = normalize_package(_seed(), board="ncert")
    assert norm["board"] == "ncert" and norm["topics"]
    mapped = map_to_ucf(norm)
    assert mapped["ok"] and mapped["ucf_payload"]["board"] == "ncert"


def test_full_migration_pipeline():
    seed = _seed()
    out = api_import_curriculum(
        board="ncert",
        inline=seed,
        source_url="https://example.test/ncert",
        publish=True,
        role="system",
        lazy_index=True,
    )
    assert out["ok"], out
    assert out["job"]["status"] == "completed"
    # Every mandatory stage present
    done = set(out.get("stages") or out["job"].get("stages_done") or [])
    for stage in PIPELINE_STAGES:
        assert stage in done, f"missing stage {stage}"
    assert out["policy"]["never_generate_curriculum_with_ai"]
    assert out["policy"]["pipeline_mandatory"]


def test_reject_on_validation():
    out = run_migration(board="cbse", inline={"subject": "Science"}, source_url="cmif://bad", publish=False)
    assert out["ok"] is False
    assert out.get("job", {}).get("status") in ("rejected", "failed")


def test_versioning_immutable_publish():
    pid = "cmif_test_pkg"
    v1 = save_version(pid, {"title": "A", "version": "1.0.0"}, status="published")
    v2 = save_version(pid, {"title": "B", "version": "1.0.0"}, status="published")
    assert v1["ok"] and v2["ok"]
    assert v2["version"] != v1["version"]  # bumped — no overwrite
    hist = version_history(pid)
    assert len(hist["history"]) >= 2
    rb = api_rollback_version(pid, v1["version_id"])
    assert rb["ok"]
    assert api_archive_curriculum(pid)["ok"]


def test_search_dashboard_status():
    api_import_curriculum(board="cbse", inline=_seed(), source_url="https://example.test/cbse", publish=True, role="system", lazy_index=False)
    search = api_search_curriculum("force", board="cbse")
    assert search["ok"]
    dash = api_dashboard()
    assert dash["ok"] and dash["supported_boards"]
    assert api_list_supported_boards()["ok"]
    assert api_get_import_status()["ok"]


def test_performance_batch_inline():
    t0 = time.perf_counter()
    for i in range(3):
        seed = _seed()
        seed["package_id"] = f"perf_{i}"
        seed["topics"] = seed["topics"][:1]
        out = api_import_curriculum(
            board="ncert",
            inline=seed,
            source_url=f"cmif://perf/{i}",
            publish=False,
            role="system",
            lazy_index=True,
        )
        assert out["ok"]
    elapsed = time.perf_counter() - t0
    assert elapsed < 60  # loose bound for CI


def test_registry_and_engine():
    reg = reset_registry()
    ids = {e["engine_id"] for e in reg.list_engines()}
    assert "curriculum_migration" in ids
    assert "universal_curriculum" in ids
    assert "curriculum_expansion" in ids
    eng = CurriculumMigrationEngine()
    assert eng.health_check().ok
    out = eng.process({"include_dashboard": False})
    assert out.ok and out.payload["policy"]["pipeline_mandatory"]


def test_curriculum_migration_framework_smoke(capsys):
    """CURRICULUM_MIGRATION_FRAMEWORK_SMOKE_OK"""
    assert api_validate_curriculum(_seed(), provenance={"source_type": "json", "source_url": "x", "source_hash": "h"})["validation"]["ok"]
    result = api_import_curriculum(
        board="ncert",
        inline=_seed(),
        source_url="https://ncert.example/class8",
        publish=True,
        role="system",
    )
    assert result["ok"]
    assert set(PIPELINE_STAGES).issubset(set(result.get("stages") or result["job"].get("stages_done") or []))
    assert CurriculumMigrationEngine().process({"board": "cbse"}).ok
    assert reset_registry().get("curriculum_migration").health_check().ok

    with capsys.disabled():
        print("CURRICULUM_MIGRATION_FRAMEWORK_SMOKE_OK")
