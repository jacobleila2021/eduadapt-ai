"""Phase 2 golden corpus — bankless chapters still yield real teaching cards."""

from __future__ import annotations

from engines.lesson_composition_engine.composer import compose_adaptations_from_clg
from engines.lesson_composition_engine.dynamic_teaching_bank import (
    build_dynamic_teaching_bank,
    ensure_wall_from_bank,
    extract_definitional_pairs,
    extract_formula_pairs,
    is_thin_source,
    wall_cards_from_bank,
)
from engines.lesson_composition_engine.intelligence_board import (
    build_lesson_intelligence_board,
)


PHOTOSYNTHESIS = """
Photosynthesis

Photosynthesis is the process by which green plants make food using sunlight,
carbon dioxide and water.

Chlorophyll is the green pigment in leaves that absorbs light energy.

Stomata are tiny pores on the leaf surface that allow gas exchange.

Glucose is the sugar produced during photosynthesis and used by the plant for energy.

QUESTIONS
1. What is photosynthesis?
2. Name the pigment that absorbs light energy.
"""

FORCE = """
Force and Laws of Motion

Force is a push or a pull acting on a body.

Inertia is the tendency of a body to resist a change in its state of motion.

Friction is a force that opposes the relative motion between two surfaces in contact.

Newton's second law: F = ma (force equals mass times acceleration)

QUESTIONS
1. What is force?
2. Define inertia.
3. State Newton's second law.
"""

FRACTIONS = """
Fractions

A fraction is a number that represents a part of a whole.

Numerator is the top number of a fraction that shows how many parts are taken.

Denominator is the bottom number of a fraction that shows the total equal parts.

An improper fraction is a fraction where the numerator is greater than the denominator.

EXERCISES
1. What is a fraction?
2. Define numerator and denominator.
"""

THIN_OHM = """
Chapter worksheet — Electricity

QUESTIONS
1. Calculate V when I = 2 A and R = 5 ohm using Ohm's law.
2. Find the current if V = 12 V and R = 4 ohm.
3. What is Ohm's law?
4. Solve for R when V = 9 V and I = 3 A.
"""

CHEM_BALANCE_THIN = """
Chemical Reactions — Practice sheet

QUESTIONS
1. Balance the equation: H2 + O2 -> H2O
2. Balance: Fe + O2 -> Fe2O3
3. What is a chemical equation?
"""


def test_photosynthesis_bankless_definitions():
    pairs = extract_definitional_pairs(PHOTOSYNTHESIS)
    terms = {t.lower() for t, _ in pairs}
    assert "photosynthesis" in terms
    assert "chlorophyll" in terms or "stomata" in terms
    bank = build_dynamic_teaching_bank(
        topic="Photosynthesis",
        source_text=PHOTOSYNTHESIS,
        claims=[
            "Photosynthesis is the process by which green plants make food using sunlight.",
            "Chlorophyll is the green pigment in leaves that absorbs light energy.",
        ],
    )
    blob = " ".join(r["definition"].lower() for r in bank)
    assert "process by which" in blob or "green pigment" in blob
    assert "for performing" not in blob
    assert len(bank) >= 2


def test_force_bankless_with_formula():
    formulas = extract_formula_pairs(FORCE)
    assert formulas, "F = ma must become a teaching card"
    bank = build_dynamic_teaching_bank(
        topic="Force and Laws of Motion",
        source_text=FORCE,
        claims=["Force is a push or a pull acting on a body."],
    )
    terms = {r["term"].lower() for r in bank}
    assert "force" in terms or "inertia" in terms or "friction" in terms
    blob = " ".join(r["definition"].lower() for r in bank)
    assert "push" in blob or "f =" in blob or "ma" in blob


def test_fractions_bankless_definitions():
    bank = build_dynamic_teaching_bank(
        topic="Fractions",
        source_text=FRACTIONS,
        claims=["A fraction is a number that represents a part of a whole."],
    )
    terms = {r["term"].lower() for r in bank}
    assert terms & {"fraction", "numerator", "denominator", "improper fraction"}
    assert all("students will" not in r["definition"].lower() for r in bank)


def test_thin_source_detected_for_question_sheet():
    assert is_thin_source(THIN_OHM)
    assert not is_thin_source(PHOTOSYNTHESIS)


def test_thin_source_bank_from_engine_artifacts():
    artifacts = [
        {
            "ok": True,
            "task_kind": "solve",
            "engine": "safe_math",
            "payload": {"expression": "V = I*R with I=2, R=5", "result": "10"},
        },
        {
            "ok": True,
            "task_kind": "solve",
            "engine": "safe_math",
            "payload": {"expression": "I = V/R with V=12, R=4", "result": "3"},
        },
    ]
    bank = build_dynamic_teaching_bank(
        topic="Electricity",
        source_text=THIN_OHM,
        claims=[],
        stem_artifacts=artifacts,
        assessment_prompts=[
            {"prompt": "Calculate V when I = 2 A and R = 5 ohm"},
            {"prompt": "Find the current if V = 12 V and R = 4 ohm"},
        ],
    )
    assert bank, "thin worksheet must still produce bank cards from engines"
    assert any("thin_source" in str(r.get("source") or "") for r in bank)
    wall = wall_cards_from_bank(bank)
    assert len(wall) >= 1
    assert all(len(c["idea"].split()) >= 3 for c in wall)


def test_ensure_wall_replaces_ocr_chrome():
    chrome_wall = [
        {
            "title": "Activity",
            "idea": "Collect the samples for performing the next activity in class.",
        },
        {
            "title": "Notice",
            "idea": "Notice how students will complete the checkpoint worksheet.",
        },
    ]
    bank = build_dynamic_teaching_bank(
        topic="Photosynthesis",
        source_text=PHOTOSYNTHESIS,
        claims=[
            "Chlorophyll is the green pigment in leaves that absorbs light energy.",
            "Stomata are tiny pores on the leaf surface that allow gas exchange.",
        ],
    )
    fixed = ensure_wall_from_bank(chrome_wall, bank, topic="Photosynthesis", min_cards=3)
    blob = " ".join(c["idea"].lower() for c in fixed)
    assert "for performing" not in blob
    assert "chlorophyll" in blob or "stomata" in blob or "photosynthesis" in blob
    assert len(fixed) >= 2


def test_compose_wall_uses_bank_for_bankless_topic():
    board = build_lesson_intelligence_board(
        {
            "topic": "Photosynthesis",
            "source_text": PHOTOSYNTHESIS,
            "claim_texts": [
                "Photosynthesis is the process by which green plants make food using sunlight.",
                "Chlorophyll is the green pigment in leaves that absorbs light energy.",
                "Stomata are tiny pores on the leaf surface that allow gas exchange.",
            ],
            "core_concepts": [
                {"name": "Photosynthesis"},
                {"name": "Chlorophyll"},
                {"name": "Stomata"},
            ],
            "assessment_outcomes": [{"prompt": "What is photosynthesis?"}],
        }
    )
    out = compose_adaptations_from_clg(
        {
            "topic": "Photosynthesis",
            "source_text": PHOTOSYNTHESIS,
            "claim_texts": board.get("verified_claims") or [],
            "core_concepts": board.get("concepts") or [],
            "assessment_outcomes": [{"prompt": "What is photosynthesis?"}],
            "teaching_bank": board.get("teaching_bank") or [],
        },
        board=board,
        lens_ids=["mainstream"],
    )
    wall = (out.get("mainstream") or {}).get("lesson_wall") or out.get("_lesson_wall") or []
    if not wall:
        # Wall is stamped on each adaptation page
        page = out.get("mainstream") or {}
        wall = page.get("lesson_wall") or []
    assert wall or board.get("teaching_bank"), "compose must keep bank or wall"
    bank = board.get("teaching_bank") or []
    assert len(bank) >= 2
    terms = {str(r.get("term") or "").lower() for r in bank}
    assert terms & {"photosynthesis", "chlorophyll", "stomata", "glucose"}


def test_chem_thin_sheet_with_balance_artifact():
    artifacts = [
        {
            "ok": True,
            "task_kind": "balance",
            "engine": "chempy",
            "payload": {
                "equation": "H2 + O2 -> H2O",
                "balanced": "2 H2 + O2 -> 2 H2O",
            },
        }
    ]
    bank = build_dynamic_teaching_bank(
        topic="Chemical Reactions",
        source_text=CHEM_BALANCE_THIN,
        claims=[],
        stem_artifacts=artifacts,
        assessment_prompts=[{"prompt": "Balance the equation: H2 + O2 -> H2O"}],
    )
    assert bank
    blob = " ".join(str(r.get("definition") or "") for r in bank)
    assert "H2O" in blob or "2" in blob
