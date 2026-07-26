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
    # Every mandated Master Lesson Contract stage exists…
    for role in CANONICAL_ROLE_SEQUENCE:
        assert role in roles, f"canonical lesson missing mandated stage: {role}"
    # …and in the mandated order.
    filtered = [r for r in roles if r in present]
    collapsed = [r for i, r in enumerate(filtered) if i == 0 or filtered[i - 1] != r]
    assert collapsed == list(present)
    assert canonical["lce"]["canonical"] is True
    assert canonical["lce"]["master_lesson"] is True
    titles = {s["title"] for s in canonical["sections"]}
    for expected in (
        "Lesson Introduction",
        "What You Will Learn",
        "Must Know",
        "Worked Examples",
        "Diagrams",
        "Vocabulary",
        "Practice Questions",
        "Exam Questions",
        "HOTS Questions",
        "Summary",
        "Quick Revision",
        "I Understand This",
    ):
        assert expected in titles, f"missing Master Contract title: {expected}"


def test_essential_learning_core_locked_with_hash(core):
    assert [c.lower() for c in core["concepts"]] == [
        "evaporation",
        "condensation",
        "precipitation",
        "collection",
    ]
    assert core["hash"]
    assert core["has_diagram"] is True
    for role in (
        "introduction",
        "essential_learning",
        "exam_question",
        "hots_question",
        "exit_ticket",
    ):
        assert role in core["master_contract_roles"]


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
    assert page["lce"]["master_lesson_inherited"] is True
    report = validate_curriculum_fidelity(core, {"standard": frozen, lens: page})
    assert report["ok"], report["failures"]


def test_teacher_and_parent_add_guidance_without_altering_curriculum(frozen, core):
    teacher = augment_support_version(frozen, core, BOARD, "teacher")
    parent = augment_support_version(frozen, core, BOARD, "parent")
    assert any(s["role"] == "teacher_support" for s in teacher["sections"])
    assert any("Teacher Notes" in str(s.get("title")) for s in teacher["sections"])
    assert any(s["role"] == "parent_support" for s in parent["sections"])
    report = validate_curriculum_fidelity(
        core, {"standard": frozen, "teacher": teacher, "parent": parent}
    )
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
    page["sections"] = [s for s in page["sections"] if s.get("role") != "visual"]
    report = validate_curriculum_fidelity(core, {"visual": page})
    assert not report["ok"]
    assert any("diagram" in f or "mandatory" in f or "master contract" in f for f in report["failures"])


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
    # LD: one idea per bullet; dyslexia: reading strips + Lexend.
    ld_bodies = "\n".join(s["body"] for s in pages["ld"]["sections"])
    assert "\n-" in ld_bodies or ld_bodies.startswith("- ")
    assert "Lexend" in str(pages["dyslexia"]["presentation"].get("font_family"))
    dys_multi = [
        s["body"]
        for s in pages["dyslexia"]["sections"]
        if s["role"] in {"objective", "summary", "essential_learning"}
    ]
    assert any("\n" in b for b in dys_multi)
    assert any(s["role"] == "decoding_support" for s in pages["dyslexia"]["sections"])
    # Visual anchors to the diagram; auditory rehearses aloud; ELL supports glossary.
    assert any(s["role"] == "visual_support" for s in pages["visual"]["sections"])
    blob_aud = " ".join(s["body"] for s in pages["auditory"]["sections"]).lower()
    assert "aloud" in blob_aud or "listen" in blob_aud
    assert any(s["role"] == "language_support" for s in pages["ell"]["sections"])
    # All carry the identical curriculum at Mainstream educational depth.
    report = validate_curriculum_fidelity(core, {"standard": frozen, **pages})
    assert report["ok"], report["failures"]
    assert report.get("educational_parity", {}).get("ok") is True


def test_compose_adaptation_from_board_routes_through_canonical():
    from engines.lesson_composition_engine.board_adaptations import (
        compose_adaptation_from_board,
    )

    std = compose_adaptation_from_board(BOARD, "standard", flowchart_svg=SVG)
    vis = compose_adaptation_from_board(BOARD, "visual", flowchart_svg=SVG)
    assert std["lce"]["frozen"] is True
    assert vis["lce"]["derived_from_canonical"] is True
    core = extract_essential_learning_core(std, BOARD)
    assert validate_curriculum_fidelity(core, {"standard": std, "visual": vis})["ok"]


def test_no_lens_may_bypass_canonical(frozen, core):
    for lens in PRESENTATION_LENSES:
        page = derive_presentation_adaptation(frozen, core, lens)
        assert page["lce"].get("derived_from_canonical") is True
        assert page["lce"].get("canonical_hash") == core["hash"]


def test_educational_parity_rejects_gutted_adaptation(frozen, core):
    from engines.lesson_composition_engine.canonical import validate_educational_parity

    thin = derive_presentation_adaptation(frozen, core, "ell")
    # Keep roles but gut curriculum bodies — accessibility must not erase depth.
    thin["sections"] = [
        {**s, "body": "Short." if s.get("role") in {
            "introduction", "objective", "essential_learning", "concept",
            "worked_example", "visual", "vocabulary", "real_life_example",
            "common_misconception", "summary", "revision", "exit_ticket",
            "practice_question", "exam_question", "hots_question", "assessment",
        } else s.get("body")}
        for s in thin["sections"]
    ]
    report = validate_educational_parity(core, {"standard": frozen, "ell": thin})
    assert not report["ok"]
    assert any("depth" in f for f in report["failures"])


def test_force_example_no_concept_may_disappear():
    """Non-negotiable rule: every Force concept survives every adaptation."""
    board = {
        "topic": "Force",
        "subject": "science",
        "verified_claims": [
            "A force is a push or a pull on an object.",
            "Contact force acts when objects touch, such as friction.",
            "Friction opposes motion between surfaces in contact.",
            "Gravitational force pulls objects towards the Earth.",
            "Effects of force include changing speed, direction or shape.",
        ],
        "concepts": [
            "Force",
            "Contact Force",
            "Friction",
            "Gravitational Force",
            "Effects of Force",
        ],
        "misconceptions": [
            {
                "label": "force is only needed to start motion",
                "correction": "forces also change speed, direction and shape while objects move.",
            }
        ],
        "learning_goals": ["Explain force and its effects with examples."],
        "examples": ["Pushing a school bag and a ball falling to the ground both show force."],
        "assessment_objectives": ["Describe contact and non-contact forces with examples."],
    }
    canonical = build_canonical_lesson(board, flowchart_svg=SVG, concept_map_svg=SVG)
    core = extract_essential_learning_core(canonical, board)
    frozen = freeze_canonical(canonical, core)
    required = [
        "force",
        "contact force",
        "friction",
        "gravitational force",
        "effects of force",
    ]
    assert [c.lower() for c in core["concepts"]] == required
    pages = {
        "standard": frozen,
        **{
            lens: derive_presentation_adaptation(frozen, core, lens)
            for lens in ("visual", "auditory", "ell", "ld", "dyslexia")
        },
    }
    for key, page in pages.items():
        blob = " ".join(
            f"{s.get('title')} {s.get('body')}" for s in page["sections"]
        ).lower()
        for concept in required:
            assert concept in blob, f"{key} missing concept: {concept}"
    assert validate_curriculum_fidelity(core, pages)["ok"]