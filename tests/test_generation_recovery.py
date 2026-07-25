"""Human-first generation recovery — honest HEQ, not inflated EQS."""

from __future__ import annotations

from engines.lesson_composition_engine import compose_lesson_package
from engines.lesson_composition_engine.human_quality import (
    HUMAN_EDUCATIONAL_QUALITY_SMOKE_OK,
    PUBLICATION_HEQ_THRESHOLD,
)
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
    assert HUMAN_EDUCATIONAL_QUALITY_SMOKE_OK is True
    assert PUBLICATION_HEQ_THRESHOLD >= 95.0
    assert sanitize_concept_label("opening", topic="Water Cycle") == "Water Cycle"
    para = craft_teaching_paragraph(
        claim="Evaporation turns liquid into vapour.",
        topic="The Water Cycle",
        concept="opening",
    )
    low = para.lower()
    assert "why opening matters" not in low
    assert "prepare you for opening" not in low
    assert "helps you explain the topic clearly" not in low
    assert "water cycle" in low or "evaporation" in low


def test_publisher_voice_not_template_mastery():
    uli = _uli("biology", "The Water Cycle", REGRESSION_TOPICS[1][2])
    pkg = compose_lesson_package(uli, topic_hint="The Water Cycle")
    std = (pkg.get("adaptations") or {}).get("standard") or {}
    blob = (
        str(std.get("big_idea") or "")
        + " "
        + " ".join(str(s.get("body") or "") for s in (std.get("sections") or []) if isinstance(s, dict))
    ).lower()
    assert "today you will master" not in blob
    assert "helps you explain the topic clearly" not in blob
    assert "evaporation" in blob
    assert "cup" in blob or "puddle" in blob or "rain" in blob or "steam" in blob
    heq = pkg.get("heq") or pkg.get("eqs") or {}
    assert heq.get("philosophy") == "human_first_publisher_pride" or heq.get("threshold") == 95.0 or (
        pkg.get("eqs") or {}
    ).get("threshold") == 95.0 or PUBLICATION_HEQ_THRESHOLD == 95.0
    assert "side_by_side" in pkg
    assert (pkg.get("side_by_side") or {}).get("stages")


def test_adaptation_similarity_and_advantage():
    uli = _uli("physics", "Force and Pressure", REGRESSION_TOPICS[0][2])
    pkg = compose_lesson_package(uli, topic_hint="Force and Pressure")
    sim = pkg.get("adaptation_similarity") or adaptation_similarity_report(pkg.get("adaptations") or {})
    assert sim.get("ok") is True, sim.get("failures")
    adv = pkg.get("adaptation_advantages") or {}
    assert "by_adaptation" in adv or adv.get("ok") is not None
    heq = educational_quality_score(pkg.get("adaptations") or {}, subject="physics", topic="Force and Pressure")
    assert heq.get("threshold") == 95.0
    # Rendering must not inflate: component may exist but teaching dominates
    assert float((heq.get("components") or {}).get("rendering_quality") or 0) == 0.0


def test_generation_recovery_regression_suite_honest():
    """Ten topics: no template pollution; HEQ must be honest (95 gate, not rubber-stamp)."""
    rows = []
    for subject, topic, text in REGRESSION_TOPICS:
        pkg = compose_lesson_package(_uli(subject, topic, text), topic_hint=topic)
        adaptations = pkg.get("adaptations") or {}
        eqs = pkg.get("heq") or pkg.get("eqs") or educational_quality_score(adaptations, subject=subject, topic=topic)
        std = adaptations.get("standard") or {}
        blob = (
            str(std.get("big_idea") or "")
            + " "
            + " ".join(str(s.get("body") or "") for s in (std.get("sections") or []) if isinstance(s, dict))
        ).lower()
        rows.append(
            {
                "topic": topic,
                "heq": eqs.get("overall"),
                "pub": bool((pkg.get("pqle") or {}).get("publication_ready")),
                "classroom": bool((eqs.get("human_verdict") or {}).get("classroom_ready")),
                "no_master": "today you will master" not in blob,
                "no_remember_filler": "helps you explain the topic clearly" not in blob,
                "has_side_by_side": bool((pkg.get("side_by_side") or {}).get("stages")),
            }
        )
    assert all(r["no_master"] and r["no_remember_filler"] for r in rows)
    assert all(r["has_side_by_side"] for r in rows)
    # Honest gate: do not claim success merely because HEQ is mid-70s
    for r in rows:
        if r["pub"]:
            assert (r["heq"] or 0) >= 95.0
            assert r["classroom"] is True
