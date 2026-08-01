"""Repair-first OCR chrome — never quarantine recoverable PDF debris."""

from __future__ import annotations

from engines.lesson_composition_engine.content_fidelity import (
    content_fidelity_block_reason,
    ensure_classroom_content_fidelity,
    scrub_ocr_chrome_prose,
)
from engines.lesson_composition_engine.vocab_quality import (
    METALS_NONMETALS_TERMS,
    canonical_definition,
    repair_ocr_prose,
)


def test_repair_strips_chapter_chrome():
    dirty = (
        "4CHAPTER Metals and Non-metals 41 Metals are lustrous and malleable. "
        "Y ou can beat aluminium into sheets. Science 41"
    )
    clean = repair_ocr_prose(dirty)
    assert "CHAPTER" not in clean.upper()
    assert "Y ou" not in clean
    assert "malleable" in clean.lower() or "lustrous" in clean.lower()


def test_scrub_drops_chrome_keeps_science():
    body = (
        "CHAPTER 3 Metals and Non-metals 41. Metals are good conductors of heat. "
        "Non-metals are generally brittle. not to be republished"
    )
    out = scrub_ocr_chrome_prose(body)
    assert "CHAPTER" not in out.upper()
    assert "republished" not in out.lower()
    assert "conductors" in out.lower() or "brittle" in out.lower()


def test_gate_does_not_quarantine_after_ocr_repair():
    adaptations = {
        "standard": {
            "topic": "Metals and Non-metals",
            "sections": [
                {
                    "title": "Understanding Metal",
                    "role": "concept",
                    "body": (
                        "4CHAPTER Metals are lustrous, malleable and ductile. "
                        "They are good conductors of heat and electricity."
                    ),
                },
                {
                    "title": "Understanding Non-metal",
                    "role": "concept",
                    "body": "Non-metals are generally dull and brittle. Y ou can crush sulphur easily.",
                },
            ],
            "lce": {"slim_theory": True, "textbook_theory": True},
        },
        "_meta": {},
    }
    repaired = ensure_classroom_content_fidelity(adaptations)
    reason = content_fidelity_block_reason(repaired)
    assert reason == "", reason
    blob = " ".join(
        str(s.get("body") or "") for s in repaired["standard"]["sections"]
    )
    assert "CHAPTER" not in blob.upper()
    assert "Y ou" not in blob


def test_metals_bank_definitions():
    assert "malleable" in canonical_definition("Metal").lower()
    assert "brittle" in canonical_definition("Non-metal").lower() or "poor conductors" in canonical_definition(
        "Non-metal"
    ).lower()
    assert len(METALS_NONMETALS_TERMS) >= 8
