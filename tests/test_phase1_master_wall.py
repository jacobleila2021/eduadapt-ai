"""Phase 1 — Freeze the one true Lesson Wall across all surfaces."""

from __future__ import annotations

from audio_learning import build_narration
from engines.lesson_composition_engine.composer import compose_adaptations_from_clg
from engines.lesson_composition_engine.confidence_gate import confidence_block_reason
from engines.lesson_composition_engine.lesson_wall import (
    apply_wall_definitions_to_vocab,
    dedupe_lesson_wall,
    wall_surface_parity_issues,
)


WATER_CYCLE = {
    "topic": "The Water Cycle",
    "subject_key": "science",
    "source_text": """
The Water Cycle
The water cycle is the continuous movement of water on, above, and below Earth's surface.
Evaporation is when liquid water turns into water vapour and rises into the air.
Condensation is when water vapour cools and changes back into tiny liquid droplets.
Precipitation is water that falls from clouds as rain, snow, sleet, or hail.
Collection is when water gathers in rivers, lakes, oceans, and groundwater.
""",
    "claim_texts": [
        "The water cycle is the continuous movement of water on, above, and below Earth's surface.",
        "Evaporation is when liquid water turns into water vapour and rises into the air.",
        "Condensation is when water vapour cools and changes back into tiny liquid droplets.",
        "Precipitation is water that falls from clouds as rain, snow, sleet, or hail.",
        "Collection is when water gathers in rivers, lakes, oceans, and groundwater.",
    ],
    "core_concepts": [
        {"name": "Evaporation", "explanation": "Evaporation is when liquid water turns into water vapour."},
        {"name": "Condensation", "explanation": "Condensation is when water vapour cools into droplets."},
        {"name": "Precipitation", "explanation": "Precipitation is rain, snow, sleet, or hail."},
        {"name": "Collection", "explanation": "Collection is water gathering in rivers and oceans."},
    ],
    "facts": [],
    "vocabulary": [],
    "assessment_outcomes": [],
}

METALS = {
    "topic": "Metals and Non-metals",
    "subject_key": "science",
    "source_text": """
Metals and Non-metals
Metals are elements that are usually shiny, malleable, ductile, and good conductors of heat and electricity.
Malleability is the property that allows metals to be hammered into thin sheets.
Ductility is the property that allows metals to be drawn into wires.
Non-metals are elements that are usually dull, brittle, and poor conductors of heat and electricity.
""",
    "claim_texts": [
        "Metals are elements that are usually shiny, malleable, ductile, and good conductors of heat and electricity.",
        "Malleability is the property that allows metals to be hammered into thin sheets.",
        "Ductility is the property that allows metals to be drawn into wires.",
        "Non-metals are elements that are usually dull, brittle, and poor conductors of heat and electricity.",
    ],
    "core_concepts": [
        {"name": "Metals", "explanation": "Metals are usually shiny, malleable, and conductive."},
        {"name": "Malleability", "explanation": "Malleability lets metals be hammered into sheets."},
        {"name": "Ductility", "explanation": "Ductility lets metals be drawn into wires."},
        {"name": "Non-metals", "explanation": "Non-metals are usually dull and poor conductors."},
    ],
    "facts": [],
    "vocabulary": [],
    "assessment_outcomes": [],
}

ELECTRICITY = {
    "topic": "Electricity",
    "subject_key": "science",
    "source_text": """
Electricity
Electric current is the flow of electric charge through a conductor.
Potential difference is the work done to move a unit charge between two points.
Resistance is the property of a conductor that opposes the flow of electric current.
Ohm's law: V = IR (potential difference equals current times resistance)
""",
    "claim_texts": [
        "Electric current is the flow of electric charge through a conductor.",
        "Potential difference is the work done to move a unit charge between two points.",
        "Resistance is the property of a conductor that opposes the flow of electric current.",
        "Ohm's law states that V = IR.",
    ],
    "core_concepts": [
        {"name": "Electric current", "explanation": "Electric current is the flow of electric charge."},
        {"name": "Potential difference", "explanation": "Potential difference is work done per unit charge."},
        {"name": "Resistance", "explanation": "Resistance opposes the flow of electric current."},
        {"name": "Ohm's law", "explanation": "Ohm's law states that V = IR."},
    ],
    "facts": [],
    "vocabulary": [],
    "assessment_outcomes": [],
}


def test_dedupe_lesson_wall_removes_recycled_clones():
    clone = "Evaporation is when liquid water turns into water vapour and rises into the air."
    wall = [
        {"title": "Evaporation", "idea": clone},
        {"title": "Also evaporation", "idea": clone},
        {
            "title": "Condensation",
            "idea": "Condensation is when water vapour cools into tiny liquid droplets in clouds.",
        },
    ]
    fixed = dedupe_lesson_wall(wall)
    assert len(fixed) == 2
    titles = {c["title"].lower() for c in fixed}
    assert "evaporation" in titles
    assert "condensation" in titles


def test_apply_wall_definitions_overrides_bank_defs():
    wall = [
        {
            "title": "Evaporation",
            "idea": "Evaporation is when liquid water turns into water vapour and rises.",
        }
    ]
    vocab = {
        "word_wall": [
            {
                "term": "Evaporation",
                "definition": "A generic atmosphere term unrelated to this lesson.",
            }
        ]
    }
    fixed = apply_wall_definitions_to_vocab(vocab, wall)
    defn = (fixed["word_wall"][0].get("definition") or "").lower()
    assert "vapour" in defn or "vapor" in defn
    assert "generic atmosphere" not in defn


def _assert_wall_surfaces_match(out: dict, *, must_tokens: tuple[str, ...]):
    wall = out.get("_lesson_wall") or []
    assert len(wall) >= 3, "Phase 1 requires at least 3 Lesson Wall cards"
    wall_blob = " ".join(str(c.get("idea") or "") for c in wall).lower()
    for tok in must_tokens:
        assert tok in wall_blob, f"wall missing {tok}"

    titles = [str(c.get("title") or "").strip().lower() for c in wall]
    for vid in ("standard", "ell", "parent", "visual", "auditory", "ld"):
        page = out.get(vid) or {}
        assert page.get("lesson_wall"), f"{vid} missing shared wall"
        page_titles = [
            str(c.get("title") or "").strip().lower() for c in (page.get("lesson_wall") or [])
        ]
        assert page_titles[:3] == titles[:3], f"{vid} wall drifted from Master"

    vocab = out.get("vocabulary") or {}
    vocab_blob = " ".join(
        str(w.get("definition") or "") for w in (vocab.get("word_wall") or [])
    ).lower()
    assert any(tok in vocab_blob for tok in must_tokens)

    sheet = out.get("worksheet") or {}
    long_q = sheet.get("long_answer") or []
    assert long_q
    assert any(str(q.get("source") or "") == "lesson_wall" for q in long_q)
    ans_blob = " ".join(str(q.get("model_answer") or "") for q in long_q).lower()
    assert any(tok in ans_blob for tok in must_tokens)

    speech = build_narration(out["standard"], "standard").lower()
    assert any(tok in speech for tok in must_tokens)

    parity = wall_surface_parity_issues(
        wall,
        vocabulary=vocab,
        worksheet=sheet,
        narration=speech,
        min_cards=3,
    )
    assert not parity, parity
    # Confidence gate should accept a wall-aligned package (diagram soft-ok).
    reason = confidence_block_reason(out)
    assert "Lesson Wall is too thin" not in reason
    assert "recycles" not in reason.lower()
    assert "Vocabulary does not reuse" not in reason
    assert "Exam long answers do not reuse" not in reason


def test_phase1_water_cycle_surfaces_share_wall_science():
    out = compose_adaptations_from_clg(WATER_CYCLE)
    _assert_wall_surfaces_match(out, must_tokens=("evaporat", "condens"))


def test_phase1_metals_surfaces_share_wall_science():
    out = compose_adaptations_from_clg(METALS)
    _assert_wall_surfaces_match(out, must_tokens=("malleab", "ductil"))


def test_phase1_electricity_surfaces_share_wall_science():
    out = compose_adaptations_from_clg(ELECTRICITY)
    _assert_wall_surfaces_match(out, must_tokens=("current", "resist"))
