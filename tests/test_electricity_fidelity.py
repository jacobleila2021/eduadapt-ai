"""Class 10 Electricity — Master Lesson fidelity (platform-wide repairs)."""

from __future__ import annotations

from engines.lesson_composition_engine.canonical import (
    build_canonical_lesson,
    derive_presentation_adaptation,
    extract_essential_learning_core,
    freeze_canonical,
)
from engines.lesson_composition_engine.composer import compose_worksheet_from_clg
from engines.lesson_composition_engine.vocab_quality import (
    ELECTRICITY_TERMS,
    canonical_definition,
    extract_source_assessment_prompts,
    extract_what_you_have_learnt,
)


SOURCE = """
Electricity

Electric current is the rate of flow of electric charge. The SI unit is the ampere.
Potential difference is measured in volts. Ohm's law states that V = IR.
Resistance depends on length, area and material.
Resistors may be joined in series or in parallel.
Electric power P = VI. The commercial unit of energy is the kilowatt hour.
1 kWh = 3.6 × 10^6 J.

What you have learnt
• Electric current is a flow of electrons; SI unit is ampere.
• Potential difference is measured in volts (V).
• Resistance opposes current; SI unit is ohm (Ω).
• Ohm's law: V is proportional to I at constant temperature.
• Resistors in series: R_s = R_1 + R_2 + R_3.
• Resistors in parallel: 1/R_p = 1/R_1 + 1/R_2 + 1/R_3.
• Electric power P = VI = I²R = V²/R.
• 1 kWh = 3.6 × 10^6 J.

QUESTIONS
1. On what factors does the resistance of a conductor depend?
2. Will current flow more easily through a thick wire or a thin wire of the same material?
3. An electric motor takes 5 A from a 220 V line. Determine the power of the motor.

EXERCISES
6. A copper wire has diameter 0.5 mm and resistivity of copper. Calculate the resistance.
10. How many 176 Ω resistors in parallel are required to carry 5 A on a 220 V line?
"""


def _board() -> dict:
    claims = [
        "Electric current is the rate of flow of electric charge through a conductor.",
        "Ohm's law states that V = IR at constant temperature.",
        "In series combination equivalent resistance is the sum of individual resistances.",
        "Electric power is the rate of consumption of electrical energy, P = VI.",
        "The commercial unit of electrical energy is the kilowatt hour.",
    ]
    return {
        "topic": "Electricity",
        "subject_key": "science",
        "concepts": [{"name": n} for n, _ in ELECTRICITY_TERMS[:6]],
        "verified_claims": claims,
        "claims": [{"text": c} for c in claims],
        "source_text": SOURCE,
        "assessment_outcomes": extract_source_assessment_prompts(SOURCE, topic="Electricity"),
        "learning_goals": ["Explain current, resistance, Ohm's law and electric power."],
        "examples": ["A 220 V bulb drawing 0.50 A has power 110 W."],
    }


def test_electricity_canonical_definitions():
    assert "ampere" in canonical_definition("Electric current").lower()
    assert "v=ir" in canonical_definition("Ohm's law").lower().replace(" ", "")
    assert "kwh" in canonical_definition("Kilowatt hour").lower().replace(" ", "") or "kilowatt" in canonical_definition(
        "Kilowatt hour"
    ).lower()


def test_what_you_have_learnt_extracted():
    bullets = extract_what_you_have_learnt(SOURCE)
    assert len(bullets) >= 5
    assert any("ohm" in b.lower() for b in bullets)


def test_source_assessment_prompts_include_calculations():
    prompts = extract_source_assessment_prompts(SOURCE, topic="Electricity")
    blob = " ".join(p["prompt"].lower() for p in prompts)
    assert "resistance" in blob
    assert any(
        k in blob for k in ("calculate", "determine", "power", "thick wire", "176")
    )


def test_master_lesson_has_full_concepts_and_no_hollow_answers():
    page = build_canonical_lesson(_board())
    roles = [str(s.get("role") or "") for s in page.get("sections") or []]
    assert roles.count("concept") >= 6
    assert "summary" in roles
    bodies = "\n".join(str(s.get("body") or "") for s in page["sections"])
    assert "say what it means" not in bodies.lower()
    assert "is a main idea in" not in bodies.lower()
    assert "ohm" in bodies.lower()
    assert "what you have learnt" in " ".join(
        str(s.get("title") or "") for s in page["sections"]
    ).lower() or any(s.get("role") == "summary" for s in page["sections"])


def test_derived_lenses_keep_summary_and_concepts():
    board = _board()
    master = build_canonical_lesson(board)
    core = extract_essential_learning_core(master, board)
    frozen = freeze_canonical(master, core)
    visual = derive_presentation_adaptation(frozen, core, "visual")
    roles = [str(s.get("role") or "") for s in visual.get("sections") or []]
    assert "concept" in roles
    assert "summary" in roles
    assert (visual.get("lce") or {}).get("concepts")


def test_worksheet_prefers_textbook_prompts():
    clg = {
        "topic": "Electricity",
        "subject_key": "science",
        "core_concepts": [{"name": n, "explanation": d} for n, d in ELECTRICITY_TERMS[:8]],
        "facts": [{"text": c} for c in _board()["verified_claims"]],
        "claim_texts": _board()["verified_claims"],
        "assessment_outcomes": extract_source_assessment_prompts(SOURCE, topic="Electricity"),
        "vocabulary": [{"term": n, "definition": d} for n, d in ELECTRICITY_TERMS[:6]],
    }
    sheet = compose_worksheet_from_clg(clg)
    short = " ".join(str(q.get("question") or "") for q in sheet.get("short_answer") or [])
    assert "say what it means" not in short.lower()
    answers = " ".join(str(q.get("model_answer") or "") for q in sheet.get("short_answer") or [])
    assert "is a main idea in" not in answers.lower()
    hots = " ".join(str(q.get("question") or "") for q in sheet.get("hots") or [])
    assert "acid" not in hots.lower()
    assert "ohm" in hots.lower() or "series" in hots.lower() or "power" in hots.lower()
