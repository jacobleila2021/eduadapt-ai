"""Production gates that must remain deterministic and network-free."""

from __future__ import annotations

import inspect
import json
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from engines.base import BaseEngine, EngineResultBundle
from engines.verified_learning_engine.engine_registry import EngineRegistry, reset_registry
from engines.verified_learning_engine.event_bus import EventBus
from engines.curriculum_intelligence_engine.intelligence import analyze_lesson_context
from engines.universal_curriculum_framework.intelligence import analyze_ucf_context
from flowchart_builder import build_vocabulary_visual_svg
from knowledge.service import _scope_matches
import knowledge.service as knowledge_service
from publication_gate import publication_allowed, publication_block_reason
from viewer_page import render_adaptation_viewer
from print_exporter import build_print_html_all
from structured_renderers import _build_matching_section
from navigation import PILL_CATEGORIES
from svg_sanitizer import sanitize_svg
from config import OPENAI_MAX_RETRIES, OPENAI_TIMEOUT_SECONDS
from engines.router import route
from engines.types import TaskKind, ToolTask, ValidationStatus

ROOT = Path(__file__).resolve().parents[1]


class _StubEngine(BaseEngine):
    layer = "test"

    def __init__(self, engine_id: str, priority: int) -> None:
        self.engine_id = engine_id
        self.priority = priority

    def process(self, context: dict) -> EngineResultBundle:
        return EngineResultBundle(engine_id=self.engine_id, ok=True)


def test_default_engine_order_respects_every_enabled_dependency():
    registry = reset_registry()
    ordered = [engine.engine_id for engine in registry.execution_order()]
    positions = {engine_id: index for index, engine_id in enumerate(ordered)}
    for row in registry.list_engines():
        if not row["enabled"]:
            continue
        for dependency in row["depends_on"]:
            assert positions[dependency] < positions[row["engine_id"]]


def test_engine_registry_fails_closed_for_missing_disabled_and_cyclic_dependencies():
    missing = EngineRegistry()
    missing.register(_StubEngine("consumer", 1), depends_on=["absent"])
    with pytest.raises(RuntimeError, match="Missing engine dependencies"):
        missing.execution_order()

    disabled = EngineRegistry()
    disabled.register(_StubEngine("source", 1), enabled=False)
    disabled.register(_StubEngine("consumer", 2), depends_on=["source"])
    with pytest.raises(RuntimeError, match="disabled"):
        disabled.execution_order()

    cyclic = EngineRegistry()
    cyclic.register(_StubEngine("a", 1), depends_on=["b"])
    cyclic.register(_StubEngine("b", 2), depends_on=["a"])
    with pytest.raises(RuntimeError, match="cycle"):
        cyclic.execution_order()


def test_event_handler_failure_is_recorded_for_recovery():
    bus = EventBus()

    def broken_handler(event):
        raise RuntimeError("simulated handler failure")

    bus.subscribe("LessonOpened", broken_handler)
    event = bus.emit("LessonOpened", session_id="audit-session")
    assert event.event_type == "LessonOpened"
    dead = bus.dead_letters(session_id="audit-session")
    assert len(dead) == 1
    assert dead[0]["error_type"] == "RuntimeError"


@pytest.mark.parametrize(
    ("subject", "grade", "expected"),
    [
        ("Mathematics", "8", False),
        ("Physics", "8", True),
        ("Chemistry", "8", True),
        ("Biology", "8", True),
        ("English", "8", False),
        ("Social Science", "8", False),
        ("Earth Science", "6", False),
    ],
)
def test_fixed_pilot_scope_isolated_by_subject_and_grade(subject, grade, expected):
    text = f"Grade Level: {grade} | Subject: {subject}\nA controlled audit lesson."
    assert _scope_matches(text, {"grade_level": grade}) is expected


@pytest.mark.parametrize(
    ("subject", "text"),
    [
        ("English", "The narrator reflects on social pressure and the current mood."),
        ("Social Science", "Political pressure contributed to the industrial revolution."),
    ],
)
def test_science_ontology_does_not_leak_into_other_subjects(subject, text):
    result = analyze_lesson_context(
        lesson_text=text,
        topic="Audit lesson",
        board="CBSE",
        grade="8",
        subject=subject,
    )
    assert result["scope_matched"] is False
    assert result["matched_concepts"] == []
    assert result["competencies"] == []
    assert result["next_concepts"] == []


def test_ucf_does_not_select_first_package_for_mismatched_scope():
    result = analyze_ucf_context(
        {"board": "CBSE", "grade": "8", "subject": "Audit Subject Missing"}
    )
    assert result["scope_matched"] is False
    assert result["package_id"] == ""


def test_publication_gate_blocks_every_known_failure_source():
    assert publication_allowed({"_meta": {"publish_qa": {"publish_blocked": False}}})
    adaptations = {
        "_meta": {
            "publish_qa": {
                "publish_blocked": True,
                "blocked_reason": "Unverified equation",
            }
        }
    }
    assert publication_block_reason(adaptations) == "Unverified equation"
    assert not publication_allowed(adaptations)
    assert not publication_allowed(quality={"publish_blocked": True})
    assert not publication_allowed(package={"vlie_validation": {"ok": False}})


def test_viewer_contract_requires_explicit_content_and_identity():
    params = inspect.signature(render_adaptation_viewer).parameters
    for required in (
        "spec_id",
        "title",
        "content",
        "download_filename",
        "base_name",
        "api_key",
    ):
        assert required in params


def test_luxe_svg_is_valid_vector_with_accessible_name():
    svg = build_vocabulary_visual_svg(
        {
            "topic": "The Water Cycle",
            "picture_words": [{"term": "Evaporation"}],
        }
    )
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert root.attrib.get("role") == "img"
    assert root.attrib.get("aria-label")
    assert "feDropShadow" in svg


def test_streamlit_hides_public_exception_details_and_limits_uploads():
    config = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text("utf-8"))
    assert config["client"]["showErrorDetails"] is False
    assert config["server"]["maxUploadSize"] <= 50
    app_source = (ROOT / "app.py").read_text("utf-8")
    assert "st.code(traceback.format_exc())" not in app_source


def test_six_subject_audit_fixture_manifest_is_complete():
    manifest = json.loads(
        (ROOT / "tests" / "fixtures" / "production_audit_subjects.json").read_text(
            "utf-8"
        )
    )
    subjects = {row["subject"] for row in manifest["subjects"]}
    assert subjects == {
        "Mathematics",
        "Physics",
        "Chemistry",
        "Biology",
        "English",
        "Social Science",
    }
    assert all(row.get("source_text") for row in manifest["subjects"])
    assert "not a production curriculum corpus" in manifest["authority"]


def test_core_math_physics_chemistry_fixtures_are_exact_and_verified():
    math = route(
        ToolTask(kind=TaskKind.SOLVE_MATH, payload={"expression": "2*x + 3 = 11"})
    )
    physics = route(
        ToolTask(
            kind=TaskKind.CALCULATE_FORCE,
            payload={
                "problem": "A force of 100 N acts on area 0.5 m^2. "
                "Calculate pressure P=F/A"
            },
        )
    )
    chemistry = route(
        ToolTask(
            kind=TaskKind.BALANCE_EQUATION,
            payload={"equation": "H2 + O2 -> H2O"},
        )
    )
    assert math.validation == ValidationStatus.PASS
    assert math.payload["exact"] == "[4]"
    assert physics.validation == ValidationStatus.PASS
    assert physics.payload["exact"] == "200.0 Pa"
    assert chemistry.validation == ValidationStatus.PASS
    assert chemistry.payload["balanced"] == "2H2 + O2 -> 2H2O"
    assert chemistry.validation_detail == "Atom counts match"


def test_combined_print_pack_contains_all_nine_adaptations():
    adaptations = {
        spec_id: {"big_idea": spec_id, "sections": []}
        for category in PILL_CATEGORIES
        for spec_id in category["spec_ids"]
    }

    def content_for_spec(spec, values, lesson_text):
        return values.get(spec["id"], lesson_text)

    rendered = build_print_html_all(
        adaptations, "Original lesson", "Audit", content_for_spec
    )
    for category in PILL_CATEGORIES:
        assert category["label"] in rendered


def test_vocabulary_matching_order_is_stable_across_reruns():
    wall = [
        {"term": f"Term {index}", "definition": f"Definition {index}"}
        for index in range(1, 9)
    ]
    assert _build_matching_section(wall) == _build_matching_section(wall)


def test_svg_sanitizer_removes_scripts_events_and_external_urls():
    hostile = """
    <svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)" aria-label="Diagram">
      <script>alert(1)</script>
      <rect width="10" height="10" fill="url(https://evil.invalid/x.svg)"/>
      <text x="1" y="5">Safe label</text>
    </svg>
    """
    safe = sanitize_svg(hostile)
    assert safe
    assert "script" not in safe.lower()
    assert "onload" not in safe.lower()
    assert "evil.invalid" not in safe
    assert "Safe label" in safe


def test_chroma_failure_is_explicit_and_fails_closed(monkeypatch):
    class BrokenRag:
        def ensure_index(self):
            raise RuntimeError("simulated Chroma outage")

    monkeypatch.setattr(knowledge_service, "_rag_singleton", BrokenRag())
    result = knowledge_service.prepare_knowledge_for_lesson(
        "Grade Level: 8 | Subject: Science\nCells contain organelles.",
        {"topic": "Cell Structure", "grade_level": "8"},
    )
    assert result["index"]["backend"] == "unavailable"
    assert result["rag_hits"] == []
    assert any(
        warning.get("code") == "knowledge_index_unavailable"
        and warning.get("recovery")
        and warning.get("fallback_used") == "uploaded_source"
        for warning in result["retrieval_warnings"]
    )


def test_external_ai_calls_have_bounded_timeout_and_retries():
    assert 1 <= OPENAI_TIMEOUT_SECONDS <= 120
    assert 0 <= OPENAI_MAX_RETRIES <= 2
