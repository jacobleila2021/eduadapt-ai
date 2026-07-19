"""Phase 5 higher education + professional learning pilots.

Pilot / college / foundation curricula and certification / corporate / CPD
frameworks. Pilot packages only — institution-specific corpora require
licence clearance before full ingest.
"""

from __future__ import annotations

from typing import Any


def _he_module(
    *,
    curriculum_id: str,
    programme: str,
    subject: str,
    year: str,
    stage: str,
    country: str = "",
    topics: list[dict[str, Any]],
    learning_objectives: list[str],
    assessment_mappings: list[dict[str, Any]],
    licensing: dict[str, Any],
    formulae: list[dict[str, Any]] | None = None,
    glossary: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prefix = curriculum_id.replace("_", "")[:10]
    comps = [c for t in topics for c in (t.get("competencies") or [])]
    pkg: dict[str, Any] = {
        "board": curriculum_id,
        "programme": programme,
        "subject": subject,
        "grade": year,
        "year": year,
        "stage": stage,
        "academic_year": "2025-26",
        "country": country,
        "version": "1.0.0-pilot",
        "languages": ["en"],
        "units": [{"id": f"{prefix}_u1", "title": subject}],
        "chapters": [{"id": f"{prefix}_m1", "title": topics[0]["title"] if topics else subject, "number": 1}],
        "topics": topics,
        "learning_objectives": learning_objectives,
        "competencies": comps,
        "blooms": "apply",
        "dok": "3",
        "prerequisites": [],
        "assessment_mappings": assessment_mappings,
        "official_questions": [
            {
                "question_id": f"{prefix}_q1",
                "text": learning_objectives[0] if learning_objectives else f"Explain a core idea in {subject}",
                "official_answer": "See authorised course materials / marking scheme",
                "source": f"{programme}-pilot",
            }
        ],
        "formulae": formulae or [],
        "figures": [{"diagram_id": f"{prefix}_fig1", "alt_text": f"{subject} concept diagram", "path": ""}],
        "glossary": glossary or [],
        "accessibility": {"alt_text_required": True, "profiles": ["adhd", "ell"]},
        "licensing": licensing,
    }
    if extra:
        pkg.update(extra)
    return pkg


# ── University / college / foundation ────────────────────────────────────


def university_intro_physics_seed() -> dict[str, Any]:
    """University foundation / Year-1 Physics pilot (mechanics)."""
    return _he_module(
        curriculum_id="university",
        programme="University",
        subject="Physics",
        year="1",
        stage="tertiary",
        country="IN",
        topics=[
            {
                "id": "university.newton_laws",
                "title": "Newton's laws of motion",
                "definition": "Fundamental laws relating force, mass and acceleration",
                "objectives": ["State Newton's laws", "Solve one-dimensional dynamics problems"],
                "competencies": ["comp.university.newton.apply"],
                "bloom": "apply",
                "dok": "3",
                "prerequisites": [],
                "chapter_title": "Classical mechanics",
            },
            {
                "id": "university.work_energy",
                "title": "Work and energy",
                "definition": "Work as force over displacement; mechanical energy conservation",
                "objectives": ["Define work and kinetic energy", "Apply energy conservation"],
                "competencies": ["comp.university.energy.apply"],
                "bloom": "apply",
                "dok": "3",
                "prerequisites": ["university.newton_laws"],
                "chapter_title": "Classical mechanics",
            },
        ],
        learning_objectives=[
            "Apply Newton's second law in one dimension",
            "Use work–energy relationships in simple systems",
        ],
        assessment_mappings=[
            {"type": "midterm", "topic": "Mechanics", "board": "University"},
            {"type": "end_semester", "topic": "Mechanics", "board": "University"},
        ],
        licensing={
            "status": "institution_restricted",
            "note": "University syllabi are institution-owned; pilot structural package only",
        },
        formulae=[
            {"formula_id": "uni_fma", "latex": "F = ma", "name": "Newton II"},
            {"formula_id": "uni_ke", "latex": "K = \\tfrac{1}{2}mv^2", "name": "Kinetic energy"},
        ],
        glossary=[
            {"term": "force", "definition": "A push or a pull; causes acceleration"},
            {"term": "work", "definition": "Energy transferred by a force acting through a displacement"},
        ],
        extra={"credits": "4", "level": "undergraduate"},
    )


def college_diploma_applied_science_seed() -> dict[str, Any]:
    """College / diploma applied science pilot."""
    return _he_module(
        curriculum_id="college",
        programme="College",
        subject="Applied Science",
        year="1",
        stage="tertiary",
        country="IN",
        topics=[
            {
                "id": "college.measurement",
                "title": "Measurement and units",
                "definition": "SI units and experimental uncertainty in applied contexts",
                "objectives": ["Use SI units", "Report simple uncertainties"],
                "competencies": ["comp.college.measurement"],
                "bloom": "understand",
                "dok": "2",
                "prerequisites": [],
                "chapter_title": "Laboratory foundations",
            },
            {
                "id": "college.force_applications",
                "title": "Forces in engineering contexts",
                "definition": "Practical applications of force and pressure in devices",
                "objectives": ["Identify forces in machines", "Relate pressure to design"],
                "competencies": ["comp.college.force_apps"],
                "bloom": "apply",
                "dok": "3",
                "prerequisites": ["college.measurement"],
                "chapter_title": "Applied mechanics",
            },
        ],
        learning_objectives=[
            "Apply SI measurement conventions in the lab",
            "Relate force and pressure to simple engineering examples",
        ],
        assessment_mappings=[
            {"type": "practical", "topic": "Measurement", "board": "College"},
            {"type": "theory_exam", "topic": "Applied mechanics", "board": "College"},
        ],
        licensing={
            "status": "institution_restricted",
            "note": "College diploma curricula vary by board/polytechnic — pilot only",
        },
        formulae=[{"formula_id": "col_p", "latex": "P = F/A", "name": "Pressure"}],
        glossary=[{"term": "SI unit", "definition": "International System of Units"}],
        extra={"award": "diploma", "level": "undergraduate"},
    )


def foundation_stem_bridge_seed() -> dict[str, Any]:
    """Foundation / bridging programme STEM pilot."""
    return _he_module(
        curriculum_id="foundation",
        programme="Foundation programme",
        subject="STEM Bridge",
        year="0",
        stage="foundation",
        country="IN",
        topics=[
            {
                "id": "foundation.algebra_basics",
                "title": "Algebra essentials",
                "definition": "Linear equations and rearrangement for STEM readiness",
                "objectives": ["Solve linear equations", "Rearrange scientific formulae"],
                "competencies": ["comp.foundation.algebra"],
                "bloom": "apply",
                "dok": "2",
                "prerequisites": [],
                "chapter_title": "Quantitative skills",
            },
            {
                "id": "foundation.force_intro",
                "title": "Introduction to forces",
                "definition": "Basic forces preparing for undergraduate physics",
                "objectives": ["Define force", "Distinguish contact and non-contact forces"],
                "competencies": ["comp.foundation.forces"],
                "bloom": "understand",
                "dok": "2",
                "prerequisites": ["foundation.algebra_basics"],
                "chapter_title": "Physical sciences bridge",
            },
        ],
        learning_objectives=[
            "Rearrange scientific formulae confidently",
            "Describe force as a push or a pull in STEM contexts",
        ],
        assessment_mappings=[
            {"type": "diagnostic", "topic": "Algebra", "board": "Foundation"},
            {"type": "progression_gate", "topic": "STEM Bridge", "board": "Foundation"},
        ],
        licensing={
            "status": "provider_restricted",
            "note": "Foundation programmes are provider-specific; pilot structural package",
        },
        formulae=[{"formula_id": "fnd_linear", "latex": "ax + b = 0", "name": "Linear equation"}],
        glossary=[{"term": "foundation", "definition": "Bridging programme before undergraduate study"}],
        extra={"pathway": "undergraduate_entry"},
    )


# ── Professional learning ────────────────────────────────────────────────


def professional_cert_stem_educator_seed() -> dict[str, Any]:
    """Professional certification — STEM educator competency pilot."""
    return _he_module(
        curriculum_id="professional_cert",
        programme="Certification provider",
        subject="STEM Pedagogy",
        year="CPD-1",
        stage="professional",
        topics=[
            {
                "id": "professional_cert.verified_teaching",
                "title": "Verified knowledge in teaching",
                "definition": "Present curriculum using authoritative sources; do not invent facts",
                "objectives": ["Cite verified sources", "Separate explanation from computation"],
                "competencies": ["comp.pro.verified_teaching"],
                "bloom": "evaluate",
                "dok": "3",
                "prerequisites": [],
                "chapter_title": "Professional standards",
            },
            {
                "id": "professional_cert.assessment_integrity",
                "title": "Assessment integrity",
                "definition": "Use official answer keys and rubrics when available",
                "objectives": ["Map items to competencies", "Avoid unverified mark schemes"],
                "competencies": ["comp.pro.assessment_integrity"],
                "bloom": "apply",
                "dok": "3",
                "prerequisites": ["professional_cert.verified_teaching"],
                "chapter_title": "Assessment practice",
            },
        ],
        learning_objectives=[
            "Uphold verified-curriculum teaching standards",
            "Align assessment practice to official keys where available",
        ],
        assessment_mappings=[
            {"type": "portfolio", "topic": "Verified teaching", "board": "Certification"},
            {"type": "proctored_quiz", "topic": "Assessment integrity", "board": "Certification"},
        ],
        licensing={
            "status": "provider_restricted",
            "note": "Certification body IP — pilot competency framework only",
        },
        glossary=[
            {"term": "verified knowledge", "definition": "Facts from authoritative curriculum or engines"},
        ],
        extra={"credential": "certificate", "cpd_hours": 12},
    )


def corporate_learning_safety_seed() -> dict[str, Any]:
    """Corporate learning — workplace safety / compliance pilot."""
    return _he_module(
        curriculum_id="corporate_learning",
        programme="Corporate learning",
        subject="Workplace Safety",
        year="L1",
        stage="professional",
        topics=[
            {
                "id": "corporate_learning.hazard_id",
                "title": "Hazard identification",
                "definition": "Recognise common workplace hazards and report channels",
                "objectives": ["List hazard types", "Use reporting procedures"],
                "competencies": ["comp.corp.hazard_id"],
                "bloom": "understand",
                "dok": "2",
                "prerequisites": [],
                "chapter_title": "Safety fundamentals",
            },
            {
                "id": "corporate_learning.emergency_response",
                "title": "Emergency response basics",
                "definition": "Initial actions for fire, medical and evacuation scenarios",
                "objectives": ["Follow evacuation routes", "Escalate incidents correctly"],
                "competencies": ["comp.corp.emergency"],
                "bloom": "apply",
                "dok": "2",
                "prerequisites": ["corporate_learning.hazard_id"],
                "chapter_title": "Emergency readiness",
            },
        ],
        learning_objectives=[
            "Identify and report workplace hazards",
            "Execute basic emergency response steps",
        ],
        assessment_mappings=[
            {"type": "scorm_quiz", "topic": "Hazard identification", "board": "Corporate"},
            {"type": "compliance_ack", "topic": "Emergency response", "board": "Corporate"},
        ],
        licensing={
            "status": "employer_restricted",
            "note": "Corporate L&D content is employer-owned; pilot framework only",
        },
        glossary=[{"term": "hazard", "definition": "A potential source of harm"}],
        extra={"delivery": "lms", "mandatory": True},
    )


def cpd_teacher_digital_seed() -> dict[str, Any]:
    """Continuing Professional Development — teacher digital pedagogy pilot."""
    return _he_module(
        curriculum_id="cpd",
        programme="Continuing Professional Development",
        subject="Digital Pedagogy",
        year="CPD",
        stage="professional",
        topics=[
            {
                "id": "cpd.accessible_design",
                "title": "Accessible lesson design",
                "definition": "Apply accessibility presentation standards without changing curriculum facts",
                "objectives": ["Choose accessible formats", "Preserve verified content"],
                "competencies": ["comp.cpd.a11y_design"],
                "bloom": "apply",
                "dok": "3",
                "prerequisites": [],
                "chapter_title": "Inclusive digital practice",
            },
            {
                "id": "cpd.adaptive_pathways",
                "title": "Adaptive learning pathways",
                "definition": "Use mastery signals to recommend revision — not invent new syllabus",
                "objectives": ["Interpret mastery indicators", "Plan revision from weak competencies"],
                "competencies": ["comp.cpd.adaptive"],
                "bloom": "analyze",
                "dok": "3",
                "prerequisites": ["cpd.accessible_design"],
                "chapter_title": "Data-informed teaching",
            },
        ],
        learning_objectives=[
            "Design accessible digital lessons that preserve verified curriculum",
            "Plan adaptive revision from mastery evidence",
        ],
        assessment_mappings=[
            {"type": "reflection", "topic": "Accessible design", "board": "CPD"},
            {"type": "micro_credential", "topic": "Adaptive pathways", "board": "CPD"},
        ],
        licensing={
            "status": "provider_restricted",
            "note": "CPD frameworks vary by regulator/provider — pilot only",
        },
        glossary=[
            {"term": "CPD", "definition": "Continuing Professional Development"},
            {"term": "mastery", "definition": "Evidence-based competency proficiency"},
        ],
        extra={"cpd_hours": 8, "credential": "micro_credential"},
    )


def seed_higher_ed_packages() -> list[tuple[str, dict[str, Any]]]:
    """CMIF/CEF Phase 5 — higher education + professional learning."""
    return [
        ("university", university_intro_physics_seed()),
        ("college", college_diploma_applied_science_seed()),
        ("foundation", foundation_stem_bridge_seed()),
        ("professional_cert", professional_cert_stem_educator_seed()),
        ("corporate_learning", corporate_learning_safety_seed()),
        ("cpd", cpd_teacher_digital_seed()),
    ]
