"""Knowledge Ingestion Engine tests."""

from __future__ import annotations

from pathlib import Path

from engines.knowledge_ingestion_engine import KnowledgeIngestionEngine, ingest_document
from engines.knowledge_ingestion_engine.normalization import normalize_board, normalize_hierarchy
from engines.knowledge_ingestion_engine.stages.validate import validate_document
from engines.verified_learning_engine import reset_registry


def test_normalize_board():
    assert normalize_board("cbse") == "CBSE"
    assert normalize_board("ib") == "IB"
    h = normalize_hierarchy(chapter=8, chapter_title="Cell", concepts=["Nucleus"])
    assert h["internal"]["chapter"] == 8
    assert h["preserves_source_terminology"] is True


def test_validate_txt(tmp_path: Path):
    p = tmp_path / "lesson.txt"
    p.write_text("Chapter 8: Cell Structure\nStudents will be able to describe plant cells.\n1. What is a chloroplast?\n", encoding="utf-8")
    v = validate_document(p)
    assert v["ok"]
    assert v["content_hash"]


def test_ingest_markdown(tmp_path: Path):
    p = tmp_path / "cell.md"
    p.write_text(
        "# Cell Structure\n\n## Chloroplast\nPlant cells have chloroplast.\n\n"
        "Learning objectives: Students will be able to label a plant cell.\n\n"
        "1. What is the function of the vacuole?\n"
        "H2 + O2 -> H2O\n"
        "Solve x = 2\n",
        encoding="utf-8",
    )
    result = ingest_document(p, board="CBSE", grade="8", subject="Science", reindex=False)
    assert result["ok"]
    pkg = result["package"]
    assert pkg["schema_version"] == "1.0.0"
    assert pkg["text_chunks"]
    assert pkg["equations"] or pkg["questions"] or pkg["concepts"]
    assert Path(pkg["persisted_path"]).is_file()


def test_kie_registered_as_required_v3_source_stage():
    reg = reset_registry()
    rows = {e["engine_id"]: e for e in reg.list_engines()}
    assert "knowledge_ingestion" in rows
    assert rows["knowledge_ingestion"]["enabled"] is True
    assert "knowledge_ingestion" in rows["universal_curriculum"]["depends_on"]


def test_kie_engine_skip_without_path():
    eng = KnowledgeIngestionEngine()
    out = eng.process({})
    assert out.ok
    assert out.payload.get("skipped")
