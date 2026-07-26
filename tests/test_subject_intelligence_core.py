"""Subject Intelligence Core Services — unit and compatibility tests."""

from __future__ import annotations

from engines.subject_intelligence_core import (
    SUBJECT_INTELLIGENCE_CORE_SMOKE_OK,
    SHARED_STRATEGY_CATALOGUE,
    SubjectIntelligenceCoreEngine,
    core_health,
    demo_capabilities,
)
from engines.subject_intelligence_core.accessibility import build_accessibility_guidance
from engines.subject_intelligence_core.assessment import build_revision_summary
from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue
from engines.subject_intelligence_core.misconceptions import detect_from_catalogue
from engines.subject_intelligence_core.pedagogy import build_teaching_strategies, resolve_strategies
from engines.subject_intelligence_core.taxonomy import detect_domains, prerequisite_hints
from engines.subject_intelligence_core.tutor_metadata import socratic_block
from engines.subject_intelligence_core.validation import (
    finding_seed,
    map_seed_severity_to_uliqe_cap,
    validate_misconception_rows,
)


def test_sics_smoke():
    assert SUBJECT_INTELLIGENCE_CORE_SMOKE_OK is True
    health = core_health()
    assert health["ok"] is True
    assert health["strategy_catalogue_size"] == len(SHARED_STRATEGY_CATALOGUE)
    assert len(health["modules"]) >= 10


def test_strategy_resolution_and_builder():
    frameworks = resolve_strategies(["inquiry", "cra", "retrieval_practice"])
    assert [f["id"] for f in frameworks] == ["inquiry", "cra", "retrieval_practice"]
    strategies = build_teaching_strategies(
        frameworks,
        [{"domain": "algebra", "score": 1}],
        provenance="test.teaching",
        default_domain="general",
        application_template="Apply {name} while teaching {primary}.",
    )
    assert strategies[0]["application"] == "Apply Inquiry-Based Learning while teaching algebra."
    assert strategies[0]["provenance"] == "test.teaching"


def test_misconception_framework():
    catalogue = (
        {
            "misconception_id": "test.x",
            "label": "Demo",
            "domain": "general",
            "patterns": [r"force\s+is\s+needed\s+to\s+keep"],
            "correction": "Fix it",
            "related_concepts": ["inertia"],
        },
    )
    hits = detect_from_catalogue(
        catalogue,
        "a force is needed to keep moving",
        provenance="test.misc",
    )
    assert hits and hits[0]["misconception_id"] == "test.x"
    assert validate_misconception_rows(hits)["ok"] is True


def test_taxonomy_and_diagrams():
    markers = {"forces": ("force",), "motion": ("velocity",)}
    domains = detect_domains("force and velocity", markers)
    assert {d["domain"] for d in domains} == {"forces", "motion"}
    prereq = prerequisite_hints(domains, (("motion", "forces"),), provenance="test.prereq")
    assert prereq["edges"]
    visuals = recommend_visuals_from_catalogue(
        domains,
        {"forces": [{"visual_type": "force_diagram", "label": "FBD"}]},
        provenance="test.vis",
    )
    assert visuals[0]["visual_type"] == "force_diagram"


def test_accessibility_tutor_validation_helpers():
    rows = build_accessibility_guidance(
        [{"recommendation": "cognitive_load_reduction", "detail": "chunk", "owner": "AIE"}],
        uli=None,
        attach_reading_band_to="cognitive_load_reduction",
    )
    assert "reading_band" in rows[0]
    assert socratic_block(["Why?"])["mode"] == "socratic"
    seed = finding_seed("ULIQE.TEST.001", "error", "x")
    assert seed["severity"] == "error"
    assert map_seed_severity_to_uliqe_cap("critical") == "warning"
    rev = build_revision_summary(
        [{"domain": "forces"}],
        [{"misconception_id": "m1"}],
        retrieval_prompts=["Recall"],
        provenance="test.rev",
    )
    assert rev["misconception_review_ids"] == ["m1"]


def test_optional_engine_and_demo():
    demo = demo_capabilities()
    assert demo["health"]["ok"] is True
    bundle = SubjectIntelligenceCoreEngine().process({})
    assert bundle.ok is True
    assert "sics" in bundle.payload
