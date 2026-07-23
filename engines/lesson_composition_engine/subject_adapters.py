"""Subject adapters — reuse MIP/PIP/CIP/BIP/ELIP/SSIP/CSIP/CEIP/WLIP pedagogy hints.

LCE does not duplicate subject intelligence. It reads pack analysis and shapes teaching flow.
"""

from __future__ import annotations

from typing import Any

from engines.lesson_composition_engine.contracts import subject_sequence

PACK_HINTS = {
    "mathematics": {
        "pack": "MIP",
        "emphasis": "Concrete models before symbols; never dump symbolic expressions without teaching.",
        "diagram_roles": ["visual", "representation", "worked_example"],
    },
    "physics": {
        "pack": "PIP",
        "emphasis": "Start from a phenomenon, then experiment thinking, then formula.",
        "diagram_roles": ["phenomenon", "experiment", "diagram"],
    },
    "chemistry": {
        "pack": "CIP",
        "emphasis": "Particle view before equations; include safety when reactions appear.",
        "diagram_roles": ["particle_view", "reaction", "diagram", "safety"],
    },
    "biology": {
        "pack": "BIP",
        "emphasis": "Process → labelled diagram → analogy → application.",
        "diagram_roles": ["process", "diagram", "labels"],
    },
    "english": {
        "pack": "ELIP",
        "emphasis": "Integrate reading, vocabulary, grammar, writing, speaking, listening, literature.",
        "diagram_roles": ["reading", "vocabulary", "writing"],
    },
    "social_science": {
        "pack": "SSIP",
        "emphasis": "Timelines, maps, cause-effect, primary sources, citizenship, inquiry.",
        "diagram_roles": ["timeline", "map", "cause_effect"],
    },
    "computer_science": {
        "pack": "CSIP",
        "emphasis": "Algorithms, flowcharts, code blocks, memory diagrams, execution traces.",
        "diagram_roles": ["algorithm", "flowchart", "code", "memory"],
    },
    "commerce": {
        "pack": "CEIP",
        "emphasis": "Business scenarios, accounting tables, economic graphs, case studies.",
        "diagram_roles": ["scenario", "accounting", "graph", "case_study"],
    },
    "world_languages": {
        "pack": "WLIP",
        "emphasis": "Pronunciation, sentence building, culture, listening, speaking.",
        "diagram_roles": ["pronunciation", "sentence_building", "culture"],
    },
}


def normalize_subject(subject: str) -> str:
    key = (subject or "general").strip().lower().replace(" ", "_")
    aliases = {
        "math": "mathematics",
        "maths": "mathematics",
        "history": "social_science",
        "geography": "social_science",
        "civics": "social_science",
        "economics": "commerce",
        "business_studies": "commerce",
        "accountancy": "commerce",
        "hindi": "world_languages",
        "french": "world_languages",
        "sanskrit": "world_languages",
        "cs": "computer_science",
        "ict": "computer_science",
        "science": "general",
    }
    return aliases.get(key, key if key in PACK_HINTS or key == "general" else "general")


def detect_subject(
    *,
    profile: dict[str, Any] | None = None,
    sif: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> str:
    profile = profile or {}
    sif = sif or {}
    context = context or {}
    for source in (
        context.get("subject"),
        profile.get("subject"),
        (profile.get("curriculum_resolution") or {}).get("subject"),
        sif.get("subject_id"),
        (sif.get("detection") or {}).get("subject_id"),
    ):
        if source:
            return normalize_subject(str(source))
    return "general"


def load_sif_hints(uli_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read SIF enrichment already attached to meta — do not re-run packs."""
    uli_meta = uli_meta or {}
    sif = uli_meta.get("sif") or uli_meta.get("subject_intelligence") or {}
    if isinstance(sif, dict) and sif.get("analysis"):
        return sif
    return sif if isinstance(sif, dict) else {}


def subject_adapter_notes(subject: str, sif_analysis: dict[str, Any] | None = None) -> list[str]:
    subject = normalize_subject(subject)
    hints = PACK_HINTS.get(subject, {"pack": "SICS", "emphasis": "Teach with clear progressive structure."})
    notes = [
        f"Subject pack: {hints['pack']}",
        str(hints["emphasis"]),
        "Teaching sequence: " + " → ".join(subject_sequence(subject)),
    ]
    sif_analysis = sif_analysis or {}
    for misc in (sif_analysis.get("misconceptions") or [])[:3]:
        if isinstance(misc, dict):
            notes.append(f"Address misconception: {misc.get('label') or misc.get('id')}")
        else:
            notes.append(f"Address misconception: {misc}")
    pedagogy = sif_analysis.get("pedagogy") or sif_analysis.get("tutor_guidance") or {}
    if isinstance(pedagogy, dict) and pedagogy.get("strategies"):
        for s in pedagogy.get("strategies")[:3]:
            notes.append(f"Pedagogy: {s}")
    return notes


def subject_wrap_sections(subject: str, topic: str) -> list[dict[str, str]]:
    """Extra subject-flavoured framing sections (short)."""
    subject = normalize_subject(subject)
    frames = {
        "mathematics": [
            ("concrete", "Start with a concrete situation", f"Begin with a familiar quantity or picture that leads into {topic}."),
            ("symbols", "Move to symbols carefully", f"Only after the meaning is clear do we write {topic} with symbols."),
        ],
        "physics": [
            ("phenomenon", "Observe the phenomenon", f"Notice what happens in the physical world that relates to {topic}."),
            ("formula", "Name the relationship", f"Once the pattern is clear, we express {topic} with a careful formula from verified sources."),
        ],
        "chemistry": [
            ("particle_view", "Think in particles", f"Imagine what particles are doing when we study {topic}."),
            ("safety", "Stay safe", "Any practical or reaction talk includes classroom safety habits."),
        ],
        "biology": [
            ("process", "Follow the process", f"Trace the biological process behind {topic} step by step."),
            ("analogy", "Use a helpful analogy", f"A careful analogy can make {topic} easier to picture without changing the science."),
        ],
    }
    return [
        {"role": r, "title": t, "body": b}
        for r, t, b in frames.get(subject, [])
    ]
