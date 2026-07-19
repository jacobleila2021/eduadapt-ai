"""Phase 3 Indian board pilot seeds — ICSE, ISC, Kerala SCERT, NIOS.

Pilot packages only (not full corpora). Content is structural metadata +
well-established topic labels with explicit licensing restrictions.
Engines consume UCF only after CEF/CMIF import.
"""

from __future__ import annotations

from typing import Any


def _base_force_pressure(*, board: str, grade: str, programme: str, subject: str = "Science") -> dict[str, Any]:
    """Shared verified physics concepts — board provenance differs."""
    prefix = board.replace("_", "")[:6]
    return {
        "board": board,
        "programme": programme,
        "subject": subject,
        "grade": grade,
        "academic_year": "2025-26",
        "country": "IN",
        "version": "1.0.0-pilot",
        "languages": ["en"],
        "units": [{"id": f"{prefix}_u_force", "title": "Force and Pressure"}],
        "chapters": [{"id": f"{prefix}_ch_fp", "title": "Force and Pressure", "number": 1}],
        "topics": [
            {
                "id": f"{board}.force",
                "title": "Force",
                "definition": "A push or a pull on an object",
                "objectives": ["Define force", "Distinguish contact and non-contact forces"],
                "competencies": [f"comp.{board}.force.identify"],
                "bloom": "understand",
                "dok": "2",
                "prerequisites": [],
                "chapter_title": "Force and Pressure",
            },
            {
                "id": f"{board}.pressure",
                "title": "Pressure",
                "definition": "Force acting per unit area",
                "objectives": ["Define pressure", "Relate force, area and pressure"],
                "competencies": [f"comp.{board}.pressure.apply"],
                "bloom": "apply",
                "dok": "2",
                "prerequisites": [f"{board}.force"],
                "chapter_title": "Force and Pressure",
            },
        ],
        "learning_objectives": [
            "Define force as a push or a pull",
            "Explain pressure as force per unit area",
        ],
        "competencies": [f"comp.{board}.force.identify", f"comp.{board}.pressure.apply"],
        "blooms": "understand",
        "dok": "2",
        "prerequisites": [{"from": f"{board}.force", "to": f"{board}.pressure"}],
        "assessment_mappings": [{"type": "board_exam", "topic": "Force and Pressure", "board": programme}],
        "official_questions": [
            {
                "question_id": f"{prefix}_fp_1",
                "text": "What is force?",
                "official_answer": "A push or a pull",
                "source": f"{programme}-pilot",
            }
        ],
        "formulae": [{"formula_id": f"{prefix}_eq_p", "latex": "P = F/A", "name": "Pressure"}],
        "figures": [{"diagram_id": f"{prefix}_fig_fp", "alt_text": "Force and pressure illustration", "path": ""}],
        "glossary": [
            {"term": "force", "definition": "A push or a pull"},
            {"term": "pressure", "definition": "Force per unit area"},
        ],
        "accessibility": {"profiles": ["dyslexia", "adhd"], "alt_text_required": True},
    }


def icse_class8_physics_seed() -> dict[str, Any]:
    """ICSE (CISCE) Class 8 Physics — Force & Pressure pilot."""
    seed = _base_force_pressure(board="icse", grade="8", programme="ICSE", subject="Physics")
    seed["region"] = "IN"
    seed["licensing"] = {
        "status": "cisce_restricted",
        "note": "CISCE/ICSE syllabus reuse requires publisher clearance; pilot labels only",
    }
    seed["official_questions"] = [
        {
            "question_id": "icse_fp_1",
            "text": "Define pressure and give its SI unit.",
            "official_answer": "Force per unit area; pascal (Pa)",
            "source": "ICSE-pilot",
        }
    ]
    return seed


def isc_class11_physics_seed() -> dict[str, Any]:
    """ISC (CISCE) Class 11 Physics — Force concepts pilot (senior secondary)."""
    seed = _base_force_pressure(board="isc", grade="11", programme="ISC", subject="Physics")
    seed["topics"].append(
        {
            "id": "isc.newton_laws",
            "title": "Newton's Laws of Motion",
            "definition": "Three laws relating force, mass and acceleration",
            "objectives": ["State Newton's laws", "Apply F = ma in simple cases"],
            "competencies": ["comp.isc.newton.apply"],
            "bloom": "apply",
            "dok": "3",
            "prerequisites": ["isc.force"],
            "chapter_title": "Laws of Motion",
        }
    )
    seed["chapters"].append({"id": "isc_ch_lom", "title": "Laws of Motion", "number": 2})
    seed["learning_objectives"].append("Apply Newton's second law in one dimension")
    seed["competencies"].append("comp.isc.newton.apply")
    seed["formulae"].append({"formula_id": "isc_eq_fma", "latex": "F = ma", "name": "Newton's second law"})
    seed["licensing"] = {
        "status": "cisce_restricted",
        "note": "ISC syllabus reuse requires clearance; pilot structural package",
    }
    seed["official_questions"] = [
        {
            "question_id": "isc_fma_1",
            "text": "State Newton's second law of motion.",
            "official_answer": "The rate of change of momentum is proportional to the applied force",
            "source": "ISC-pilot",
        }
    ]
    return seed


def kerala_scert_class8_science_seed() -> dict[str, Any]:
    """Kerala SCERT Class 8 Science — Force & Pressure pilot."""
    seed = _base_force_pressure(board="kerala_scert", grade="8", programme="Kerala State Board", subject="Science")
    seed["region"] = "Kerala"
    seed["languages"] = ["en", "ml"]
    seed["licensing"] = {
        "status": "scert_kerala_restricted",
        "note": "Kerala SCERT materials require official clearance for full ingest",
    }
    seed["glossary"].append({"term": "bala", "definition": "Force (regional terminology hint — UI/search only)"})
    seed["official_questions"] = [
        {
            "question_id": "kerala_fp_1",
            "text": "How is pressure related to force and area?",
            "official_answer": "Pressure equals force divided by area",
            "source": "Kerala-SCERT-pilot",
        }
    ]
    seed["accessibility"]["locale_hints"] = ["en-IN", "ml-IN"]
    return seed


def nios_secondary_science_seed() -> dict[str, Any]:
    """NIOS Secondary (Class 10 equivalent) Science — Force & Pressure pilot."""
    seed = _base_force_pressure(board="nios", grade="10", programme="NIOS", subject="Science")
    seed["programme_stage"] = "secondary"
    seed["licensing"] = {
        "status": "nios_restricted",
        "note": "NIOS open schooling materials — confirm redistribution rights before full corpus",
    }
    seed["assessment_mappings"] = [
        {"type": "tma", "topic": "Force and Pressure", "board": "NIOS"},
        {"type": "public_exam", "topic": "Force and Pressure", "board": "NIOS"},
    ]
    seed["official_questions"] = [
        {
            "question_id": "nios_fp_1",
            "text": "Define force and give two examples of push and pull.",
            "official_answer": "A push or a pull; examples depend on context (e.g. kicking a ball, opening a drawer)",
            "source": "NIOS-pilot",
        }
    ]
    return seed


def seed_indian_boards_packages() -> list[tuple[str, dict[str, Any]]]:
    """CMIF/CEF Phase 3 — Indian boards incremental packages."""
    return [
        ("icse", icse_class8_physics_seed()),
        ("isc", isc_class11_physics_seed()),
        ("kerala_scert", kerala_scert_class8_science_seed()),
        ("nios", nios_secondary_science_seed()),
    ]
