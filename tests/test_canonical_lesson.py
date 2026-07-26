"""Master Lesson Architecture (v3.3) — ONE canonical lesson, presentation-only
adaptations, locked Essential Learning Core, hard curriculum-fidelity gate."""

from __future__ import annotations

import copy

import pytest

from engines.lesson_composition_engine.canonical import (
    CANONICAL_ROLE_SEQUENCE,
    PRESENTATION_LENSES,
    augment_support_version,
    build_canonical_lesson,
    derive_presentation_adaptation,
    extract_essential_learning_core,
    freeze_canonical,
    validate_curriculum_fidelity,
)

BOARD = {
    "topic": "The Water Cycle",
    "subject": "science",
    "verified_claims": [
        "The water cycle is the continuous movement of water between the earth and the sky.",
        "Evaporation happens when the sun heats water in rivers, lakes and seas.",
        "Condensation forms clouds when water vapour cools high in the sky.",
        "Precipitation returns water to the ground as rain, snow or hail.",
        "Collection gathers water in rivers, lakes and oceans so the cycle can begin again.",
    ],
    "concepts": ["evaporation", "condensation", "precipitation", "collection"],
    "misconceptions": [
        {
            "label": "clouds are made of smoke",
            "correction": "clouds are tiny drops of condensed water vapour.",
        }
    ],
    "learning_goals": ["Students will explain the stages of the water cycle."],
    "examples": ["Rain filling a village pond after a hot week is the water cycle at work."],
    "assessment_objectives": ["Explain each stage of the water cycle in order."],
}

SVG = "<svg xmlns='http://www.w3.org/2000/svg'><title>cycle</title></svg>"


@pytest.fixture(scope="module")
def canonical():
    return build_canonical_lesson(BOARD, flowchart_svg=SVG, concept_map_svg=SVG)


@pytest.fixture(scope="module")
def core(canonical):
    return extract_essential_learning_core(canonical, BOARD)


@pytest.fixture(scope="module")
def frozen(canonical, core):
    return freeze_canonical(canonical, core)


def test_canonical_lesson_contains_complete_mandated_sequence(canonical):
    roles = [s["role"] for s in canonical["sections"]]
    present = [r for r in CANONICAL_ROLE_SEQUENCE if r in roles]
    # Every mandated stage exists…
    for role in CANONICAL_ROLE_SEQUENCE:
        assert role in roles, f"canonical lesson missing mandated stage: {role}"
    # …and in the mandated order.
    filtered = [r for r in roles if r in present]
    collapsed = [r for i, r in enumerate(filtered) if i == 0 or filtered[i - 1] != r]
    assert collapsed == list(present)
    assert canonical["lce"]["canonical"] is True


def test_essential_learning_core_locked_with_hash(core):
    assert [c.lower() for c in core["concepts"]] == [
        "evaporation",
        "condensation",
        "precipitation",
        "collection",
    ]
    assert core["hash"]
    assert core["has_diagram"] is True


def test_frozen_lesson_is_read_only_copy(canonical, core, frozen):
    assert frozen["lce"]["frozen"] is True
    assert frozen["lce"]["canonical_hash"] == core["hash"]
    frozen2 = copy.deepcopy(frozen)
    frozen2["sections"][0]["body"] = "tampered"
    assert canonical["sections"][0]["body"] != "tampered"


@pytest.mark.parametrize("lens", ["visual", "auditory", "ell", "ld", "dyslexia"])
def test_adaptations_inherit_identical_curriculum(frozen, core, lens):
    page = derive_presentation_adaptation(frozen, core, lens)
    assert page["lce"]["derived_from_canonical"] is True
    assert page["lce"]["presentation_only"] is True
    report = validate_curriculum_fidelity(core, {lens: page})
    assert report["ok"], report["failures"]


def test_teacher_and_parent_add_guidance_without_altering_curriculum(frozen, core):
    teacher = augment_support_version(frozen, core, BOARD, "teacher")
    parent = augment_support_version(frozen, core, BOARD, "parent")
    assert any(s["role"] == "teacher_support" for s in teacher["sections"])
    assert any(s["role"] == "parent_support" for s in parent["sections"])
    report = validate_curriculum_fidelity(core, {"teacher": teacher, "parent": parent})
    assert report["ok"], report["failures"]


def test_gate_fails_when_concept_removed(frozen, core):
    page = derive_presentation_adaptation(frozen, core, "visual")
    page["sections"] = [
        {**s, "body": s["body"].replace("condensation", "").replace("Condensation", "")}
        for s in page["sections"]
        if "Condensation" not in str(s.get("title"))
    ]
    report = validate_curriculum_fidelity(core, {"visual": page})
    assert not report["ok"]
    assert any("concept" in f or "claims" in f for f in report["failures"])


def test_gate_fails_when_sequence_changed(frozen, core):
    page = derive_presentation_adaptation(frozen, core, "auditory")
    secs = page["sections"]
    summary_idx = next(i for i, s in enumerate(secs) if s["role"] == "summary")
    obj_idx = next(i for i, s in enumerate(secs) if s["role"] == "objective")
    secs[summary_idx], secs[obj_idx] = secs[obj_idx], secs[summary_idx]
    report = validate_curriculum_fidelity(core, {"auditory": page})
    assert not report["ok"]
    assert any("sequence" in f for f in report["failures"])


def test_gate_fails_when_diagram_removed(frozen, core):
    page = derive_presentation_adaptation(frozen, core, "visual")
    page["svg_diagram"] = ""
    page["flowchart_svg"] = ""
    report = validate_curriculum_fidelity(core, {"visual": page})
    assert not report["ok"]
    assert any("diagram" in f for f in report["failures"])


def test_worksheet_questions_must_map_to_taught_concepts(core):
    good = {"short_answer": [{"question": "Explain how evaporation begins the water cycle."}]}
    bad = {"short_answer": [{"question": "Name the seven wonders of the ancient world."}]}
    assert validate_curriculum_fidelity(core, {"worksheet": good})["ok"]
    assert not validate_curriculum_fidelity(core, {"worksheet": bad})["ok"]


def test_presentation_lenses_differ_only_in_presentation(frozen, core):
    pages = {
        lens: derive_presentation_adaptation(frozen, core, lens)
        for lens in ("ld", "dyslexia", "visual", "auditory", "ell")
    }
    # LD: one idea per bullet; dyslexia: one sentence per line + Lexend.
    ld_bodies = "\n".join(s["body"] for s in pages["ld"]["sections"])
    assert "\n-" in ld_bodies or ld_bodies.startswith("- ")
    assert "Lexend" in str(pages["dyslexia"]["presentation"].get("font_family"))
    # Multi-sentence sections are split one sentence per line for dyslexia.
    dys_multi = [
        s["body"]
        for s in pages["dyslexia"]["sections"]
        if s["role"] in {"objective", "summary", "essential_learning"}
    ]
    assert any("\n" in b for b in dys_multi)
    # Visual anchors to the diagram; auditory rehearses aloud; ELL supports key words.
    assert any(s["role"] == "visual_support" for s in pages["visual"]["sections"])
    blob_aud = " ".join(s["body"] for s in pages["auditory"]["sections"]).lower()
    assert "aloud" in blob_aud
    assert any(s["role"] == "language_support" for s in pages["ell"]["sections"])
    # All carry the identical curriculum.
    report = validate_curriculum_fidelity(core, pages)
    assert report["ok"], report["failures"]


def test_compose_adaptation_from_board_routes_through_canonical():
    from engines.lesson_composition_engine.board_adaptations import (
        compose_adaptation_from_board,
    )

    std = compose_adaptation_from_board(BOARD, "standard", flowchart_svg=SVG)
    vis = compose_adaptation_from_board(BOARD, "visual", flowchart_svg=SVG)
    assert std["lce"]["frozen"] is True
    assert vis["lce"]["derived_from_canonical"] is True
    core = extract_essential_learning_core(std, BOARD)
    assert validate_curriculum_fidelity(core, {"visual": vis})["ok"]


def test_no_lens_may_bypass_canonical(frozen, core):
    for lens in PRESENTATION_LENSES:
        page = derive_presentation_adaptation(frozen, core, lens)
        assert page["lce"].get("derived_from_canonical") is True
        assert page["lce"].get("canonical_hash") == core["hash"]
