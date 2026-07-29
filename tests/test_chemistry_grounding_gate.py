"""Chemistry / uploaded-source grounding must not quarantine strong coverage."""

from __future__ import annotations

from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.qa.pipeline import validate_lesson_package


def test_acids_bases_style_grounding_at_82_percent_does_not_quarantine():
    source = ingest_source_bytes(
        "acids.txt",
        (
            "Acids, Bases and Salts. Acids turn blue litmus red. "
            "Bases turn red litmus blue. Salts form when acids react with bases."
        ).encode(),
    ).to_dict()
    ref = source["blocks"][0]["block_id"]
    # Simulate 151 grounded + 32 ungrounded presentation shells (≈82%).
    sections = [
        {"title": f"Idea {i}", "body": f"Acid base salt idea {i}.", "source_refs": [ref]}
        for i in range(151)
    ] + [
        {"title": f"Support {i}", "body": f"Extra support line {i}.", "source_refs": []}
        for i in range(32)
    ]
    adaptations = {
        "standard": {
            "big_idea": "Acids, bases and salts.",
            "source_refs": [ref],
            "sections": sections,
        }
    }
    report = validate_lesson_package(
        adaptations=adaptations,
        source_envelope=source,
        grounding_mode="uploaded_source",
    )
    grounding = next(c for c in report.checks if c["code"] == "source_grounding")
    assert grounding["coverage"] >= 80.0
    assert grounding["ok"] is True
    assert report.publish_blocked is False


def test_severe_grounding_gap_still_blocks():
    source = ingest_source_bytes(
        "acids.txt", b"Acids turn blue litmus red."
    ).to_dict()
    ref = source["blocks"][0]["block_id"]
    adaptations = {
        "standard": {
            "big_idea": "Acids.",
            "source_refs": [ref],
            "sections": [
                {"title": "A", "body": "Grounded.", "source_refs": [ref]},
                {"title": "B", "body": "Ungrounded one.", "source_refs": []},
                {"title": "C", "body": "Ungrounded two.", "source_refs": []},
                {"title": "D", "body": "Ungrounded three.", "source_refs": []},
            ],
        }
    }
    report = validate_lesson_package(
        adaptations=adaptations,
        source_envelope=source,
        grounding_mode="uploaded_source",
    )
    # 1/4 = 25% → critical quarantine
    assert report.publish_blocked is True
