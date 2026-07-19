"""Pilot curriculum scope — one book / one grade for school trust rollout."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PilotScope:
    pilot_id: str
    board: str
    grade: str
    subject: str
    book_title: str
    seed_file: str
    mcq_file: str
    chroma_collection: str


NCERT_CLASS8_SCIENCE_PILOT = PilotScope(
    pilot_id="ncert_cbse_class8_science_v1",
    board="CBSE",
    grade="8",
    subject="Science",
    book_title="NCERT Science Textbook for Class VIII",
    seed_file="ncert_class8_science.json",
    mcq_file="official_mcqs_class8_science.json",
    chroma_collection="ncert_class8_science",
)

ACTIVE_PILOT = NCERT_CLASS8_SCIENCE_PILOT
