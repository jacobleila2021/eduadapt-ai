"""Phase 4 international pilots — Cambridge + IB programmes.

Pilot packages only (not full syllabi). Licensing restricted pending
Cambridge Assessment / IBO clearance for full corpus ingest.
"""

from __future__ import annotations

from typing import Any


def _science_forces_core(
    *,
    curriculum_id: str,
    programme: str,
    grade: str,
    subject: str = "Science",
    country: str = "UK",
    extra_topics: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    prefix = curriculum_id.replace("_", "")[:10]
    topics = [
        {
            "id": f"{curriculum_id}.forces",
            "title": "Forces",
            "definition": "Forces can change the motion or shape of an object",
            "objectives": ["Describe forces", "Identify contact and non-contact forces"],
            "competencies": [f"comp.{curriculum_id}.forces.describe"],
            "bloom": "understand",
            "dok": "2",
            "prerequisites": [],
            "chapter_title": "Forces",
        },
        {
            "id": f"{curriculum_id}.pressure",
            "title": "Pressure",
            "definition": "Force acting per unit area",
            "objectives": ["Define pressure", "Relate force and area"],
            "competencies": [f"comp.{curriculum_id}.pressure.apply"],
            "bloom": "apply",
            "dok": "2",
            "prerequisites": [f"{curriculum_id}.forces"],
            "chapter_title": "Forces",
        },
    ]
    if extra_topics:
        topics.extend(extra_topics)
    return {
        "board": curriculum_id,
        "programme": programme,
        "subject": subject,
        "grade": grade,
        "academic_year": "2025-26",
        "country": country,
        "version": "1.0.0-pilot",
        "languages": ["en"],
        "units": [{"id": f"{prefix}_u_forces", "title": "Forces and motion"}],
        "chapters": [{"id": f"{prefix}_ch_forces", "title": "Forces", "number": 1}],
        "topics": topics,
        "learning_objectives": [
            "Describe forces and their effects on motion",
            "Explain pressure as force per unit area",
        ],
        "competencies": [c for t in topics for c in (t.get("competencies") or [])],
        "blooms": "understand",
        "dok": "2",
        "prerequisites": [{"from": f"{curriculum_id}.forces", "to": f"{curriculum_id}.pressure"}],
        "assessment_mappings": [{"type": "programme_assessment", "topic": "Forces", "board": programme}],
        "official_questions": [
            {
                "question_id": f"{prefix}_f1",
                "text": "What can forces do to an object?",
                "official_answer": "Change its motion or shape",
                "source": f"{programme}-pilot",
            }
        ],
        "formulae": [{"formula_id": f"{prefix}_eq_p", "latex": "P = F/A", "name": "Pressure"}],
        "figures": [{"diagram_id": f"{prefix}_fig_f", "alt_text": "Force arrows on an object", "path": ""}],
        "glossary": [
            {"term": "force", "definition": "A push or a pull"},
            {"term": "pressure", "definition": "Force per unit area"},
        ],
        "accessibility": {"alt_text_required": True, "profiles": ["dyslexia", "ell"]},
    }


# ── Cambridge ────────────────────────────────────────────────────────────


def cambridge_primary_science_seed() -> dict[str, Any]:
    seed = _science_forces_core(
        curriculum_id="cambridge_primary",
        programme="Cambridge Primary",
        grade="6",
        subject="Science",
    )
    seed["stage"] = "primary"
    seed["licensing"] = {
        "status": "cambridge_restricted",
        "note": "Cambridge Primary curriculum — clearance required for full framework documents",
    }
    return seed


def cambridge_lower_secondary_science_seed() -> dict[str, Any]:
    seed = _science_forces_core(
        curriculum_id="cambridge_lower_secondary",
        programme="Cambridge Lower Secondary",
        grade="8",
        subject="Science",
    )
    seed["stage"] = "lower_secondary"
    seed["licensing"] = {
        "status": "cambridge_restricted",
        "note": "Cambridge Lower Secondary — pilot structural package only",
    }
    return seed


def cambridge_igcse_physics_seed() -> dict[str, Any]:
    seed = _science_forces_core(
        curriculum_id="cambridge_igcse",
        programme="Cambridge IGCSE",
        grade="10",
        subject="Physics",
        extra_topics=[
            {
                "id": "cambridge_igcse.momentum",
                "title": "Momentum",
                "definition": "Product of mass and velocity",
                "objectives": ["Define momentum", "Apply p = mv qualitatively"],
                "competencies": ["comp.cambridge_igcse.momentum"],
                "bloom": "apply",
                "dok": "3",
                "prerequisites": ["cambridge_igcse.forces"],
                "chapter_title": "Motion and forces",
            }
        ],
    )
    seed["stage"] = "igcse"
    seed["formulae"].append({"formula_id": "cam_igcse_p", "latex": "p = mv", "name": "Momentum"})
    seed["assessment_mappings"] = [
        {"type": "igcse_paper", "topic": "Forces", "board": "Cambridge IGCSE"},
        {"type": "multiple_choice", "topic": "Forces", "board": "Cambridge IGCSE"},
    ]
    seed["licensing"] = {
        "status": "cambridge_restricted",
        "note": "Cambridge IGCSE Physics — syllabus IP restricted; pilot labels only",
    }
    seed["official_questions"] = [
        {
            "question_id": "cam_igcse_f1",
            "text": "Define pressure and state its SI unit.",
            "official_answer": "Force per unit area; pascal (Pa)",
            "source": "Cambridge-IGCSE-pilot",
        }
    ]
    return seed


def cambridge_as_a_level_physics_seed() -> dict[str, Any]:
    seed = _science_forces_core(
        curriculum_id="cambridge_as_a_level",
        programme="Cambridge AS & A Level",
        grade="12",
        subject="Physics",
        extra_topics=[
            {
                "id": "cambridge_as_a_level.newton_laws",
                "title": "Newton's laws of motion",
                "definition": "Laws relating force, mass and acceleration",
                "objectives": ["State Newton's laws", "Apply F = ma"],
                "competencies": ["comp.cambridge_as_a_level.newton"],
                "bloom": "apply",
                "dok": "3",
                "prerequisites": ["cambridge_as_a_level.forces"],
                "chapter_title": "Dynamics",
            }
        ],
    )
    seed["stage"] = "as_a_level"
    seed["formulae"].append({"formula_id": "cam_aal_fma", "latex": "F = ma", "name": "Newton II"})
    seed["licensing"] = {
        "status": "cambridge_restricted",
        "note": "Cambridge International AS & A Level — clearance required for past papers/syllabus text",
    }
    return seed


# ── IB ───────────────────────────────────────────────────────────────────


def ib_pyp_science_seed() -> dict[str, Any]:
    """IB PYP — inquiry-oriented science pilot (forces as conceptual theme)."""
    seed = _science_forces_core(
        curriculum_id="ib_pyp",
        programme="IB PYP",
        grade="5",
        subject="Science",
        country="CH",
    )
    seed["stage"] = "pyp"
    seed["inquiry_focus"] = ["How the world works"]
    seed["learning_objectives"] = [
        "Explore how pushes and pulls affect objects",
        "Connect everyday examples to the idea of force",
    ]
    seed["assessment_mappings"] = [{"type": "pyp_exhibition_prep", "topic": "Forces", "board": "IB PYP"}]
    seed["licensing"] = {
        "status": "ibo_restricted",
        "note": "IBO PYP framework — official documents restricted; pilot conceptual package",
    }
    return seed


def ib_myp_sciences_seed() -> dict[str, Any]:
    seed = _science_forces_core(
        curriculum_id="ib_myp",
        programme="IB MYP",
        grade="9",
        subject="Sciences",
        country="CH",
        extra_topics=[
            {
                "id": "ib_myp.energy_transfer",
                "title": "Energy and forces",
                "definition": "Forces can transfer energy and change motion",
                "objectives": ["Relate force to energy transfer"],
                "competencies": ["comp.ib_myp.energy_forces"],
                "bloom": "understand",
                "dok": "2",
                "prerequisites": ["ib_myp.forces"],
                "chapter_title": "Forces and energy",
            }
        ],
    )
    seed["stage"] = "myp"
    seed["myp_criteria"] = ["A Knowing", "B Investigating", "C Communicating", "D Reflecting"]
    seed["assessment_mappings"] = [
        {"type": "myp_criterion_a", "topic": "Forces", "board": "IB MYP"},
        {"type": "myp_e_assessment", "topic": "Forces", "board": "IB MYP"},
    ]
    seed["licensing"] = {
        "status": "ibo_restricted",
        "note": "IB MYP Sciences — guide IP restricted; pilot structural package",
    }
    return seed


def ib_dp_physics_seed() -> dict[str, Any]:
    seed = _science_forces_core(
        curriculum_id="ib_dp",
        programme="IB Diploma Programme",
        grade="12",
        subject="Physics",
        country="CH",
        extra_topics=[
            {
                "id": "ib_dp.mechanics",
                "title": "Mechanics — forces and motion",
                "definition": "Quantitative study of forces, motion and momentum",
                "objectives": ["Apply Newton's laws", "Analyse free-body diagrams"],
                "competencies": ["comp.ib_dp.mechanics"],
                "bloom": "analyze",
                "dok": "3",
                "prerequisites": ["ib_dp.forces"],
                "chapter_title": "Mechanics",
            }
        ],
    )
    seed["stage"] = "dp"
    seed["formulae"].extend(
        [
            {"formula_id": "ib_dp_fma", "latex": "F = ma", "name": "Newton II"},
            {"formula_id": "ib_dp_p", "latex": "p = mv", "name": "Momentum"},
        ]
    )
    seed["assessment_mappings"] = [
        {"type": "dp_paper_1", "topic": "Mechanics", "board": "IB DP"},
        {"type": "dp_paper_2", "topic": "Mechanics", "board": "IB DP"},
        {"type": "internal_assessment", "topic": "Mechanics", "board": "IB DP"},
    ]
    seed["licensing"] = {
        "status": "ibo_restricted",
        "note": "IB DP Physics — subject guide and past papers restricted; pilot only",
    }
    seed["official_questions"] = [
        {
            "question_id": "ib_dp_m1",
            "text": "State Newton's second law of motion.",
            "official_answer": "The net force on a body equals the rate of change of its momentum",
            "source": "IB-DP-pilot",
        }
    ]
    return seed


def seed_international_packages() -> list[tuple[str, dict[str, Any]]]:
    """CMIF/CEF Phase 4 — Cambridge + IB programmes."""
    return [
        ("cambridge_primary", cambridge_primary_science_seed()),
        ("cambridge_lower_secondary", cambridge_lower_secondary_science_seed()),
        ("cambridge_igcse", cambridge_igcse_physics_seed()),
        ("cambridge_as_a_level", cambridge_as_a_level_physics_seed()),
        ("ib_pyp", ib_pyp_science_seed()),
        ("ib_myp", ib_myp_sciences_seed()),
        ("ib_dp", ib_dp_physics_seed()),
    ]
