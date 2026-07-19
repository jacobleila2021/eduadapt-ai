"""Curriculum Intelligence Engine tests."""

from __future__ import annotations

from engines.curriculum_engine import CurriculumEngine
from engines.curriculum_intelligence_engine.intelligence import (
    analyze_lesson_context,
    compare_boards,
    get_runtime,
    search,
)
from engines.curriculum_intelligence_engine.model import normalize_programme, supported_curricula
from engines.curriculum_intelligence_engine.prerequisites import detect_gaps
from engines.curriculum_intelligence_engine import service as cie_api
from engines.verified_learning_engine import reset_registry


def test_supported_curricula_catalogue():
    rows = supported_curricula()
    names = {r["name"] for r in rows}
    assert "CBSE" in names
    assert "IB MYP" in names
    assert "Cambridge IGCSE" in names
    assert normalize_programme("myp") == "IB MYP"


def test_ontology_graph_loads():
    rt = get_runtime()
    assert len(rt["graph"].concepts) >= 10
    assert len(rt["graph"].outcomes) >= 3
    assert len(rt["competencies"]) >= 1
    force = rt["graph"].get_concept("c8sci.force")
    assert force is not None
    chain = rt["graph"].prerequisite_chain("c8sci.pressure")
    assert "c8sci.force" in chain


def test_prerequisite_gaps():
    rt = get_runtime()
    gaps = detect_gaps(rt["graph"], "c8sci.pressure", mastered=[])
    assert gaps["has_gaps"]
    assert "c8sci.force" in gaps["missing_prerequisites"]
    ok = detect_gaps(rt["graph"], "c8sci.pressure", mastered=["c8sci.motion_intro", "c8sci.force"])
    assert not ok["has_gaps"]


def test_cross_curriculum_compare():
    cmp = compare_boards("CBSE", "Cambridge")
    assert cmp["equivalent_topics"]
    assert cmp["coverage"]["mapped_to_b"] >= 1


def test_search_force_and_pressure():
    hit = search("Class 8 Force and Pressure CBSE")
    assert hit["count"] >= 1
    assert hit["primary"] is not None
    assert hit["primary"]["prerequisites"]


def test_analyze_lesson_enrichment():
    cie = analyze_lesson_context(
        lesson_text="Pressure is force per unit area. P = F/A. Friction opposes motion.",
        topic="Force and Pressure",
        board="CBSE",
        grade="8",
        subject="Science",
    )
    assert cie["matched_concepts"]
    assert cie["unified_path"]["curriculum"] == "CBSE"
    assert cie["policy"]["does_not_generate_lessons"] is True


def test_api_retrieve_chapter():
    ch = cie_api.api_retrieve_chapter(11)
    assert ch["count"] >= 1
    assert any("force" in (c.get("title") or "").lower() for c in ch["concepts"])


def test_curriculum_engine_includes_cie():
    eng = CurriculumEngine()
    out = eng.process(
        {
            "lesson_text": "The cell is the basic unit of life. Plant cells have chloroplasts.",
            "topic": "Cell Structure",
            "grade": "8",
        }
    )
    assert out.ok
    assert "knowledge" in out.payload
    assert "curriculum_intelligence" in out.payload
    cie = out.payload["curriculum_intelligence"]
    assert cie.get("matched_concepts") or cie.get("graph_stats", {}).get("concepts", 0) > 0


def test_curriculum_still_registered():
    reg = reset_registry()
    rows = {e["engine_id"]: e for e in reg.list_engines()}
    assert "curriculum" in rows
    assert rows["curriculum"]["enabled"] is True


def test_health():
    h = CurriculumEngine().health_check()
    assert h.ok
    assert "concepts=" in (h.detail or "")
