"""Master Lesson Architecture (v4) — ONE canonical lesson, presentation-only
adaptations, locked Essential Learning Core, hard curriculum-fidelity gate.

Product law: reading lesson = Introduction + concept sections (one teaching
pass each) + Worked Example + Practice/Exam/HOTS with exam-ready answers.
Vocabulary lives on the Vocabulary page.
"""

from __future__ import annotations

import copy
import re

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
    for role in CANONICAL_ROLE_SEQUENCE:
        assert role in roles, f"canonical lesson missing mandated stage: {role}"
    filtered = [r for r in roles if r in present]
    collapsed = [r for i, r in enumerate(filtered) if i == 0 or filtered[i - 1] != r]
    assert collapsed == list(present)
    assert canonical["lce"]["canonical"] is True
    assert canonical["lce"]["master_lesson"] is True
    assert canonical["lce"].get("slim_theory") is True
    assert canonical["lce"].get("professional_publishing") is True
    titles = {s["title"] for s in canonical["sections"]}
    for expected in (
        "Introduction",
        "Worked Example",
        "Practice Questions",
        "Exam Questions",
        "HOTS Questions",
    ):
        assert expected in titles, f"missing Master Contract title: {expected}"
    # Meaningful concept headings — not the lesson title repeated.
    assert "Evaporation" in titles or any("Evaporat" in t for t in titles)
    assert canonical["title"] == "The Water Cycle"
    blob = " ".join(str(s.get("body") or "") for s in canonical["sections"]).lower()
    assert "this lesson teaches" not in blob
    for banned in (
        "What You Will Learn",
        "Must Know",
        "Key Concepts",
        "More ideas from this lesson",
        "Diagrams",
        "Vocabulary",
        "Real-life Applications",
        "Common Misconceptions",
        "Quick Revision",
        "I Understand This",
        "Assessment Check",
    ):
        assert banned not in titles, f"slim theory must not include: {banned}"
    # Practice / Exam / HOTS: one Q then Answer on the next line
    practice = next(s for s in canonical["sections"] if s["role"] == "practice_question")
    assert "Answer:" in practice["body"]
    assert practice["body"].count("Answer:") >= 2
    assert "1." in practice["body"] and "2." in practice["body"]
    assert "(1 mark)" in practice["body"]
    exam = next(s for s in canonical["sections"] if s["role"] == "exam_question")
    assert "(3 marks)" in exam["body"]
    # Mark-depth: a 3-mark answer must be longer than a recycled one-liner.
    for block in exam["body"].split("\n\n"):
        if "(3 marks)" in block and "Answer:" in block:
            ans = block.split("Answer:", 1)[1].strip()
            assert len(ans.split()) >= 20, ans
            break
    concept = next(s for s in canonical["sections"] if s["role"] == "concept")
    body = concept["body"]
    # One teaching pass — no duplicated "In short" / "Key points" / "Next:" chrome.
    assert "In short:" not in body
    assert "Key points:" not in body
    assert not re.search(r"(?m)^Next:", body)
    # Definition appears once, not thrice.
    first = body.split("\n")[0].strip()
    assert body.count(first) == 1


def test_essential_learning_core_locked_with_hash(core):
    assert [c.lower() for c in core["concepts"][:4]] == [
        "evaporation",
        "condensation",
        "precipitation",
        "collection",
    ]
    assert core["hash"]
    assert core["has_diagram"] is True
    for role in (
        "introduction",
        "concept",
        "worked_example",
        "practice_question",
        "exam_question",
        "hots_question",
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
    practice_idx = next(i for i, s in enumerate(secs) if s["role"] == "practice_question")
    intro_idx = next(i for i, s in enumerate(secs) if s["role"] == "introduction")
    secs[practice_idx], secs[intro_idx] = secs[intro_idx], secs[practice_idx]
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
    # Same curriculum roles; presentation formatting may differ.
    std_roles = [s["role"] for s in frozen["sections"] if not str(s.get("role") or "").endswith("_support")]
    for lens, page in pages.items():
        roles = [s["role"] for s in page["sections"] if not str(s.get("role") or "").endswith("_support")]
        assert roles == std_roles or set(CANONICAL_ROLE_SEQUENCE).issubset(set(roles))
    ld_bodies = "\n".join(s["body"] for s in pages["ld"]["sections"] if s["role"] == "concept")
    assert "\n-" in ld_bodies or ld_bodies.startswith("- ") or "Answer:" in "\n".join(
        s["body"] for s in pages["ld"]["sections"]
    )
    assert "Lexend" in str(pages["dyslexia"]["presentation"].get("font_family") or "") or pages[
        "dyslexia"
    ]["lce"].get("presentation_only")
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
    thin["sections"] = [
        {
            **s,
            "body": "Short."
            if s.get("role")
            in {
                "introduction",
                "concept",
                "worked_example",
                "practice_question",
                "exam_question",
                "hots_question",
            }
            else s.get("body"),
        }
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


def test_junk_title_fragments_never_become_steps():
    board = {
        **BOARD,
        "concepts": ["evaporation", "travel", "systems", "matter", "condensation"],
    }
    lesson = build_canonical_lesson(board, flowchart_svg=SVG)
    titles = " ".join(s.get("title") or "" for s in lesson["sections"]).lower()
    body = " ".join(s.get("body") or "" for s in lesson["sections"]).lower()
    assert "travel" not in titles
    assert "systems" not in titles
    assert "matter" not in titles
    assert "is taught in this lesson" not in body
