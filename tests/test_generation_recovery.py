"""Generation Recovery Sprint — regression against golden topics."""

from __future__ import annotations

from engines.lesson_composition_engine import compose_lesson_package
from engines.lesson_composition_engine.master_teacher import craft_teaching_paragraph
from engines.lesson_composition_engine.recovery import (
    GENERATION_RECOVERY_SMOKE_OK,
    adaptation_similarity_report,
    educational_quality_score,
    sanitize_concept_label,
)

REGRESSION_TOPICS = [
    ("physics", "Force and Pressure", "A force can change the shape or motion of an object. Pressure is force on a unit area. A sharp tip has high pressure."),
    ("biology", "The Water Cycle", "Evaporation turns liquid water into vapour. Condensation forms clouds. Precipitation returns water as rain. Collection gathers water in oceans."),
    ("mathematics", "Fractions", "A fraction shows parts of a whole. The numerator is the count of parts. The denominator is the total equal parts."),
    ("biology", "Photosynthesis", "Green plants make food using sunlight. Chlorophyll traps light. Carbon dioxide and water become glucose and oxygen."),
    ("biology", "Digestive System", "Digestion breaks food into nutrients. The stomach mixes food with acid. The small intestine absorbs nutrients."),
    ("physics", "Light", "Light travels in straight lines. Reflection bounces light. Refraction bends light when it enters a new medium."),
    ("geography", "Volcanoes", "Magma rises through cracks in the crust. Lava is magma that reaches the surface. Ash and gases can erupt violently."),
    ("history", "Trade Routes", "Trade routes connected cities across land and sea. Merchants carried goods, ideas, and culture along the routes."),
    ("mathematics", "Percentages", "A percentage is a number out of one hundred. 50 percent means half. Percentages compare parts of a whole."),
    ("environmental_science", "Waste Management", "Reduce means use less. Reuse means use again. Recycle means make new materials from used ones."),
]


def _uli(subject: str, topic: str, text: str) -> dict:
    claims = [{"text": s.strip()} for s in text.replace(". ", ".|").split("|") if s.strip()]
    concepts = []
    for claim in claims:
        # Prefer scientific head nouns from claims (not junk title fragments)
        for word in claim["text"].replace(",", " ").split():
            token = word.strip(".:;()[]\"'")
            if len(token) >= 5 and token[0].isupper():
                concepts.append({"name": token, "explanation": claim["text"]})
                break
    if not concepts:
        concepts = [{"name": topic, "explanation": text[:120]}]
    return {
        "universal_profile": {
            "topic": topic,
            "subject": subject,
            "concepts": concepts,
            "claim_ledger": claims,
            "key_concepts": concepts,
        },
        "claim_ledger": claims,
    }


def test_recovery_smoke_and_no_opening_pollution():
    assert GENERATION_RECOVERY_SMOKE_OK is True
    assert sanitize_concept_label("opening", topic="Water Cycle") == "Water Cycle"
    para = craft_teaching_paragraph(
        claim="Evaporation turns liquid into vapour.",
        topic="The Water Cycle",
        concept="opening",
    )
    low = para.lower()
    assert "why opening matters" not in low
    assert "prepare you for opening" not in low
    assert "water cycle" in low or "evaporation" in low


def test_pqle_formatting_only_preserves_meaning():
    uli = _uli("biology", "The Water Cycle", REGRESSION_TOPICS[1][2])
    pkg = compose_lesson_package(uli, topic_hint="The Water Cycle")
    assert pkg.get("pqle", {}).get("mode") == "formatting_only"
    std = (pkg.get("adaptations") or {}).get("standard") or {}
    blob = (std.get("big_idea") or "") + " ".join(
        str(s.get("body") or "") for s in (std.get("sections") or []) if isinstance(s, dict)
    )
    assert "why opening matters" not in blob.lower()
    assert "evaporation" in blob.lower() or "water" in blob.lower()


def test_adaptation_similarity_gate_reports():
    uli = _uli("physics", "Force and Pressure", REGRESSION_TOPICS[0][2])
    pkg = compose_lesson_package(uli, topic_hint="Force and Pressure")
    sim = pkg.get("adaptation_similarity") or adaptation_similarity_report(pkg.get("adaptations") or {})
    assert "failures" in sim
    assert "threshold" in sim
    assert sim.get("threshold") == 0.40
    # Recovery authorship must keep worst instructional clones under the gate
    assert sim.get("ok") is True, sim.get("failures")
    eqs = pkg.get("eqs") or educational_quality_score(pkg.get("adaptations") or {})
    assert "overall" in eqs
    assert "components" in eqs
    assert float(eqs["overall"]) >= 70.0


def test_generation_recovery_regression_suite():
    """Run the ten recovery topics; collect failures without soft-passing clones."""
    rows = []
    for subject, topic, text in REGRESSION_TOPICS:
        pkg = compose_lesson_package(_uli(subject, topic, text), topic_hint=topic)
        adaptations = pkg.get("adaptations") or {}
        eqs = pkg.get("eqs") or educational_quality_score(adaptations)
        sim = pkg.get("adaptation_similarity") or adaptation_similarity_report(adaptations)
        std = adaptations.get("standard") or {}
        blob = (
            str(std.get("big_idea") or "")
            + " "
            + " ".join(str(s.get("body") or "") for s in (std.get("sections") or []) if isinstance(s, dict))
        ).lower()
        rows.append(
            {
                "topic": topic,
                "eqs": eqs.get("overall"),
                "sim_ok": sim.get("ok"),
                "sim_failures": len(sim.get("failures") or []),
                "no_opening": "why opening matters" not in blob,
                "no_notice": "notice how" not in blob,
                "publication_ready": bool((pkg.get("pqle") or {}).get("publication_ready")),
                "contribution_log": pkg.get("contribution_log") or [],
            }
        )
    # Hard guarantees for recovery sprint
    assert all(r["no_opening"] for r in rows)
    assert all(r["no_notice"] for r in rows)
    assert all((r["eqs"] or 0) >= 70 for r in rows)
    assert all(r["sim_ok"] for r in rows), [r for r in rows if not r["sim_ok"]]
    by_topic = {r["topic"]: r for r in rows}
    assert by_topic["The Water Cycle"]["eqs"] >= 70
    assert by_topic["Force and Pressure"]["eqs"] >= 70
    # Upstream engines appear in contribution log
    engines = {c.get("engine") for c in by_topic["The Water Cycle"]["contribution_log"]}
    assert {"ULI", "SIF", "UVIE", "LCE", "PQLE"} <= engines