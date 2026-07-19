"""Incremental seed packages — NCERT + CBSE first (framework validation)."""

from __future__ import annotations

from typing import Any


def ncert_class8_science_seed() -> dict[str, Any]:
    """Verified pilot-aligned seed — Force & Pressure concepts (not full corpus)."""
    return {
        "board": "ncert",
        "subject": "Science",
        "grade": "8",
        "academic_year": "2025-26",
        "version": "1.0.0",
        "languages": ["en"],
        "licensing": {"status": "ncert_restricted", "note": "Official NCERT reuse requires clearance"},
        "units": [{"id": "u1", "title": "Force and Pressure"}],
        "chapters": [{"id": "ch11", "title": "Force and Pressure", "number": 11}],
        "topics": [
            {
                "id": "c8sci.force",
                "title": "Force",
                "definition": "A push or a pull on an object",
                "objectives": ["Define force", "Identify push and pull"],
                "competencies": ["comp.force.identify"],
                "bloom": "understand",
                "dok": "2",
                "prerequisites": [],
                "chapter_title": "Force and Pressure",
            },
            {
                "id": "c8sci.pressure",
                "title": "Pressure",
                "definition": "Force acting per unit area",
                "objectives": ["Define pressure", "Relate force and area"],
                "competencies": ["comp.pressure.calculate"],
                "bloom": "apply",
                "dok": "2",
                "prerequisites": ["c8sci.force"],
                "chapter_title": "Force and Pressure",
            },
        ],
        "learning_objectives": [
            "Define force as a push or a pull",
            "Explain pressure as force per unit area",
        ],
        "competencies": ["comp.force.identify", "comp.pressure.calculate"],
        "blooms": "understand",
        "dok": "2",
        "prerequisites": [{"from": "c8sci.force", "to": "c8sci.pressure"}],
        "assessment_mappings": [{"type": "formative", "topic": "Force"}],
        "official_questions": [
            {"question_id": "ncert_fp_1", "text": "What is force?", "official_answer": "A push or a pull", "source": "NCERT"},
        ],
        "formulae": [{"formula_id": "eq_pressure", "latex": "P = F/A", "name": "Pressure"}],
        "figures": [{"diagram_id": "fig_force", "alt_text": "Push and pull examples", "path": ""}],
        "glossary": [{"term": "force", "definition": "A push or a pull"}, {"term": "pressure", "definition": "Force per unit area"}],
        "accessibility": {"profiles": ["dyslexia", "adhd"], "alt_text_required": True},
    }


def cbse_class8_science_seed() -> dict[str, Any]:
    """CBSE aligns to NCERT texts for Class 8 Science — same verified core, CBSE provenance."""
    seed = ncert_class8_science_seed()
    seed["board"] = "cbse"
    seed["licensing"] = {"status": "cbse_ncert_aligned", "note": "CBSE follows NCERT; licensing still restricted"}
    seed["assessment_mappings"] = [{"type": "board_exam", "topic": "Force and Pressure", "board": "CBSE"}]
    seed["official_questions"] = [
        {
            "question_id": "cbse_fp_1",
            "text": "Define pressure and state its SI unit.",
            "official_answer": "Force per unit area; pascal (Pa)",
            "source": "CBSE-aligned",
        }
    ]
    return seed


def cambridge_lower_secondary_science_stub() -> dict[str, Any]:
    """Deprecated stub — use seeds_international.cambridge_lower_secondary_science_seed."""
    from engines.curriculum_expansion_framework.seeds_international import cambridge_lower_secondary_science_seed

    return cambridge_lower_secondary_science_seed()


def seed_priority_packages() -> list[tuple[str, dict[str, Any]]]:
    """Incremental order step 1: NCERT + CBSE."""
    return [
        ("ncert", ncert_class8_science_seed()),
        ("cbse", cbse_class8_science_seed()),
    ]


def seed_indian_boards_packages() -> list[tuple[str, dict[str, Any]]]:
    """Incremental order step 3: ICSE, ISC, Kerala, NIOS."""
    from engines.curriculum_expansion_framework.seeds_indian_boards import seed_indian_boards_packages as _pkgs

    return _pkgs()


def seed_international_packages() -> list[tuple[str, dict[str, Any]]]:
    """Incremental order step 4: Cambridge + IB."""
    from engines.curriculum_expansion_framework.seeds_international import seed_international_packages as _pkgs

    return _pkgs()


def seed_higher_ed_packages() -> list[tuple[str, dict[str, Any]]]:
    """Incremental order step 5: university + professional learning."""
    from engines.curriculum_expansion_framework.seeds_higher_ed import seed_higher_ed_packages as _pkgs

    return _pkgs()
