"""Composition contracts — strict rules for LCE narrative and structure.

LLM prose (when used) must obey these contracts. Deterministic assembly always does.
"""

from __future__ import annotations

from engines.lesson_composition_engine.schemas import (
    CONCEPT_TEACHING_STEPS,
    SUBJECT_TEACHING_SEQUENCES,
    VOCAB_CARD_FIELDS,
)

NARRATIVE_VOICE = """
Write as an expert classroom teacher and NCERT-quality textbook author.
Use warm, clear, confident educational prose.
Never sound like ChatGPT, a chatbot, or a metadata dump.
Never say "In this lesson we will explore", "Let's dive in", "Delve", or "In conclusion".
Never invent equations, answers, diagrams, or curriculum facts.
Teach one idea per paragraph. Use smooth transitions between sections.
""".strip()

PARAGRAPH_RULES = """
PARAGRAPH QUALITY:
- Each paragraph teaches exactly one idea.
- Prefer 2–5 sentences; never a one-sentence fragment unless intentionally highlighted.
- Keep paragraphs under ~120 words.
- No repeated sentences. No disconnected headings without teaching prose beneath.
""".strip()

FLOW_RULES = """
LESSON FLOW (required):
Hook → Concept teaching → Worked example → Practice → Summary → Revision → Reflection → Application
Every concept follows: Concept → Simple explanation → Real-life example → Visual →
Worked example → Common misconception → Practice question → Reflection.
Never skip concept teaching steps.
""".strip()

VOCABULARY_CONTRACT = f"""
VOCABULARY CARD CONTRACT (every card must include):
{', '.join(VOCAB_CARD_FIELDS)}
- Term: large, bold, centered, Capitalized display form
- Pronunciation, part of speech, definition, simple explanation, example sentence
- Synonyms, antonyms, related concepts, difficulty, reading level
- Color-coded premium flashcard styling; picture when available
Never emit bare term/definition pairs without the full card fields.
""".strip()

VISUAL_CONTRACT = """
VISUAL PLACEMENT:
- Use UVIE / verified STEM visuals only. Never invent scientific diagrams.
- Place each visual immediately after the explanation it supports.
- Prefer professional SVG flowcharts and concept maps over Mermaid.
- Mermaid only when explicitly requested by the caller.
""".strip()

STEM_CONTRACT = """
STEM INTEGRITY (platform law):
- Inject EngineResult / official answers unchanged.
- Never alter balanced equations, solutions, or verified diagram payloads.
- Mathematics: Concrete → Visual → Representation → Symbols → Worked Example → Practice → Application
- Physics: Concept → Phenomenon → Experiment → Diagram → Formula → Example → Practice
- Chemistry: Concept → Particle view → Reaction → Equation → Diagram → Safety → Application
- Biology: Concept → Process → Diagram → Labels → Analogy → Application
""".strip()

ADAPTIVE_CONTRACT = """
ADAPTIVE VERSIONS:
Each version must be intentionally rewritten for its learner — never a recolor of the same text.
Accessibility improves learning without reducing curriculum depth.
Never simplify concepts below board/grade requirements.
""".strip()


def subject_sequence(subject: str) -> tuple[str, ...]:
    key = (subject or "general").strip().lower().replace(" ", "_")
    aliases = {
        "math": "mathematics",
        "maths": "mathematics",
        "science": "general",
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
    }
    key = aliases.get(key, key)
    return SUBJECT_TEACHING_SEQUENCES.get(key, SUBJECT_TEACHING_SEQUENCES["general"])


def build_narrative_contract(*, subject: str = "general", version_id: str = "standard") -> str:
    seq = " → ".join(subject_sequence(subject))
    steps = " → ".join(CONCEPT_TEACHING_STEPS)
    return "\n\n".join(
        [
            NARRATIVE_VOICE,
            PARAGRAPH_RULES,
            FLOW_RULES,
            f"SUBJECT SEQUENCE for {subject}: {seq}",
            f"CONCEPT STEPS (never skip): {steps}",
            STEM_CONTRACT,
            VISUAL_CONTRACT,
            VOCABULARY_CONTRACT if version_id == "vocabulary" else "",
            ADAPTIVE_CONTRACT,
            f"TARGET VERSION: {version_id}",
        ]
    ).strip()


def composition_prompt_block(blueprint: dict) -> str:
    """Inject into Teaching Layer prompts — LCE owns the educational writing contract."""
    subject = str(blueprint.get("subject") or "general")
    version = "standard"
    contract = build_narrative_contract(subject=subject, version_id=version)
    concepts = blueprint.get("concepts") or []
    objectives = blueprint.get("objectives") or []
    vocab = blueprint.get("vocabulary_terms") or []
    misconceptions = blueprint.get("misconceptions") or []
    lines = [
        "=== LESSON COMPOSITION ENGINE (LCE) CONTRACT ===",
        "You are composing under LCE authority. LCE is the final educational author.",
        "Do not invent curriculum. Compose from the verified blueprint below.",
        contract,
        "",
        f"TOPIC: {blueprint.get('topic') or ''}",
        f"SUBJECT: {subject}",
        f"GRADE: {blueprint.get('grade') or ''}",
        "OBJECTIVES:",
        *[f"- {o}" for o in objectives[:8]],
        "KEY CONCEPTS (teach each with full concept steps):",
        *[f"- {c}" for c in concepts[:10]],
        "VOCABULARY TO TEACH:",
        *[f"- {t}" for t in vocab[:15]],
        "MISCONCEPTIONS TO ADDRESS:",
        *[f"- {m}" for m in misconceptions[:6]],
        "TEACHING SEQUENCE:",
        " → ".join(blueprint.get("teaching_sequence") or subject_sequence(subject)),
        "=== END LCE CONTRACT ===",
    ]
    return "\n".join(lines)
