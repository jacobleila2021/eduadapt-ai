"""Teaching Policy Pack — canonical Teaching Layer system rules and RAG blocks.

Single source of truth for lesson depth, verified-engine, source-grounding,
differentiation, and curriculum enrichment policy strings used by generation.
"""

from __future__ import annotations

from knowledge.types import OfficialMcq, RagHit

# ---------------------------------------------------------------------------
# Teaching Policy Pack (byte-identical relocates from ai_generator.py)
# ---------------------------------------------------------------------------

DEPTH_RULES = """
DEPTH REQUIREMENTS (critical):
- Cover EVERY learning objective and key concept from the lesson analysis.
- Do NOT compress a long lesson into a topic list or one-page summary.
- Each classroom lesson adaptation needs 6–10 teachable sections.
- Each section body: minimum 120 words OR at least 8 substantive bullets totaling 120+ words, with concrete facts, examples, and steps.
- Students must be able to pass a board/exam using ONLY this material.
- Include worked examples where the subject requires them.
- Include an explicit section titled "Exam Practice" or "Board Check" with board-style questions.
- DIAGRAMS: follow VISUALIZATION PRIORITY in the user prompt. Prefer empty mermaid_diagram and svg_diagram (""): Alora injects built coloured flowcharts. If verified engine/NCERT visuals exist, leave both empty. Do not invent complex SVG.
- ACCURACY: all diagram and content facts must be scientifically and historically correct.
- Each learner version must be MEASURABLY DIFFERENT in presentation (structure, scaffolding, layout) while preserving the same exam-critical concepts and terminology.
"""

CLASSROOM_TEACHING_RULES = """
CLASSROOM TEACHING FLOW (mandatory for classroom adaptations):
- Write as a teacher would teach in class — not a condensation of topics.
- Required flow (use real concept titles from the source; do not invent facts):
  1) Hook / Learning Goal
  2) Teach core concepts (one teachable segment per major idea)
  3) Guided practice (worked with the class)
  4) Independent practice
  5) Mastery / Check Understanding
  6) Exam Practice / Board Check
  7) Summary / Next Steps
- Each section must be deliverable aloud as a classroom segment (optional timing cue like "5–8 minutes" is encouraged).
- Never replace teaching with vague outlines, truncated blurbs ending in "...", or one-line stubs.
"""

BOARD_EXAM_READINESS_RULES = """
BOARD / EXAM READINESS (mandatory for classroom adaptations):
- Preserve exam-accurate terminology from the source (scaffold definitions beside terms; do not replace terms with childish substitutes).
- Include board-style practice: at least 4 short-answer and 2 longer/HOTS-style questions grounded in SOURCE_CLAIMS.
- Provide model answers or clear answer cues for every practice question (teacher key fields when generating teacher adaptation).
- A student who studies ONLY this adaptation must be able to attempt those questions in an exam without needing the Mainstream tab.
- Do NOT invent official board keys; when OFFICIAL_ANSWER_BANK / ENGINE_ARTIFACTS exist, copy them unchanged.
- When no official bank is present, create practice-from-source questions labelled as practice (not "official key").
"""

ENGINE_RULES = """
VERIFIED KNOWLEDGE FIRST (mandatory when ENGINE_ARTIFACTS are provided):
- Use ONLY the provided ENGINE_ARTIFACTS for equations, balancing, numeric answers, plotted functions, and physics diagrams.
- NEVER invent coefficients, balanced equations, exact solutions, graph shapes, or scientific diagrams when artifacts/verified visuals exist.
- You may explain, simplify language, and adapt reading level — but do NOT change computed results.
- If a STEM fact is missing from ENGINE_ARTIFACTS, write NEED_ENGINE:{type}:{request} instead of guessing.
- Prefer verified_visuals (NCERT figures, Matplotlib, Schemdraw, GeoGebra, RDKit, physics diagrams) over AI-drawn mermaid/SVG.
"""

RAG_CITATION_RULES = """
SOURCE GROUNDING:
- The uploaded SOURCE_CLAIMS are authoritative. Do not add factual claims that are absent from them.
- Add source_refs containing valid uploaded block IDs to structured metadata for every section, definition, example, question, answer, teacher note, and parent note.
- source_refs are internal QA metadata only. Never print "Source:", "Source detail:", block IDs, claim IDs, file paths, or reference notes in learner/teacher-facing text.
- RETRIEVED_SOURCES are optional enrichment. Cite them only when present and never claim official curriculum alignment without them.
- Missing external curriculum citations is not an error; continue from the uploaded source.
- Official answer-bank values and deterministic ENGINE_ARTIFACTS must be copied unchanged.
"""

DIFFERENTIATION_RULES = """
DIFFERENTIATION (minimum 80% unique presentation from standard version; SAME exam coverage):
- ADHD: short teachable chunks, checkpoints, movement breaks, numbered steps only — keep full concept and exam practice depth.
- Autism Support: predictable routine, literal language, calm transitions, same color pattern every section — keep exam terminology.
- Visual Learner: colour-coded stages, icon labels, diagram-first layout — keep full exam practice.
- Auditory Learner: full prose paragraphs (120+ words per section), listen-and-repeat scripts, call-and-response cues — NOT bullet lists; keep exam practice.
- Dyslexia Smart: grade-matched conceptual depth and exam vocabulary; accessibility via chunking, bold **key terms**, 6–10 substantive bullets per section, spacing — NEVER collapse secondary content to Grade 3–4 childish language; NEVER drop exam-critical concepts.
- ELL: glossary scaffolds and sentence frames beside accurate exam terms — do not remove board vocabulary.
- Dyslexia (legacy): bullet points, bold keywords, extra white space cues, no dense paragraphs — same coverage as Mainstream.
"""

SECTION_TITLE_RULES = """
SECTION TITLES (critical — applies to ALL adaptations):
- NEVER use generic placeholders like "Core Concept 1", "Core Concept 2", "Section 3", or "Topic 1".
- Every section title MUST be the REAL concept name from the lesson (e.g. "Meristematic Tissue", "Evaporation", "Photosynthesis").
- Titles must be short (2-6 words), complete phrases that make sense on their own.
- If the lesson has more than 6 concepts, add sections "Concept 7", "Concept 8" etc. ONLY with the actual concept name as title.
"""

BULLET_SECTION_RULES = """
DYSLEXIA SMART FORMAT (ld adaptation only):
- Each section body MUST use markdown bullet points (- item) with 6-10 bullets per section.
- Each bullet: one complete exam-ready idea, 12–22 words, concrete facts — NOT one-word stubs.
- Total section body: minimum 120 words. Cover ALL concepts from the source lesson at source grade depth.
- Bold key exam terms using **term** markdown; add a short plain-language gloss in parentheses when helpful — keep the real term.
- Include Exam Practice / Board Check with the same board-style question depth as Mainstream.
"""

AUDITORY_SECTION_RULES = """
AUDITORY LEARNER FORMAT (auditory adaptation only):
- Use full prose paragraphs — NO bullet lists.
- Each section body: minimum 120 words with concrete facts, examples, and listen-and-repeat phrases.
- Include "Say:" and "Repeat:" call-and-response lines within paragraphs.
- Cover EVERY concept from the source lesson — chunk into extra sections if needed.
- Include Exam Practice / Board Check with spoken rehearsal of model answers.
"""

VISUAL_PRACTICE_RULES = """
VISUAL LEARNER PRACTICE FORMAT (visual adaptation only):
- In the Practice section, format each item as:
  Q1. [question on one line]
  A1. [answer on the next line]
  Q2. [question]
  A2. [answer]
- Provide at least 5 numbered Q/A pairs with full answers.
"""

TEACHER_ANSWER_RULES = """
TEACHER VERSION (teacher adaptation only):
Include these extra fields:
"answer_key": [
  {{"section": "Practice", "question": "Q1 ...", "model_answer": "Full correct answer", "marks": 2}},
  {{"section": "Examples", "question": "Worked example 1", "model_answer": "Complete solution", "marks": 3}}
],
"teacher_notes": "Differentiation tips, common misconceptions, grouping suggestions.",
"differentiation_map": "Which groups get which scaffolds."
- Provide a model_answer for EVERY practice question and worked example in the lesson.
- Minimum 8 answer_key entries covering all assessable content.
"""

# Strict official-curriculum citation policy (used when grounding_mode requires it).
# Byte-identical to the pre-consolidation knowledge.prompts.RAG_RULES body.
RAG_RULES = """
KNOWLEDGE LAYER — RETRIEVED SOURCES (mandatory when provided):
- Use RETRIEVED_SOURCES for curriculum facts, definitions, and processes.
- NEVER contradict retrieved NCERT / Exemplar / CBSE content.
- Cite every major curriculum claim inline using the provided citation tags, e.g. [NCERT Class 8 Science Ch.5 p.62].
- If a fact is not in RETRIEVED_SOURCES or the lesson excerpt, write NEED_SOURCE:{topic} instead of inventing.
- Official MCQ answers in OFFICIAL_ANSWER_BANK must be copied exactly — never change the keyed answer letter or value.
"""


def enrichment_policy_header(grounding_mode: str = "uploaded_source") -> str:
    """
    Mode-aware curriculum enrichment header for knowledge prompt_block.

    uploaded_source (default): optional enrichment — matches RAG_CITATION_RULES.
    official_curriculum_publish: strict retrieved-source citation — RAG_RULES.
    """
    if grounding_mode == "official_curriculum_publish":
        return RAG_RULES
    return RAG_CITATION_RULES


def rag_hits_to_prompt_block(hits: list[RagHit]) -> str:
    if not hits:
        return ""
    lines = ["RETRIEVED_SOURCES (cite these in explanations):"]
    for i, hit in enumerate(hits, start=1):
        lines.append(f"{i}. {hit.citation} — {hit.chapter_title}")
        lines.append(f"   {hit.text[:900]}")
    return "\n".join(lines)


def official_bank_to_prompt_block(items: list[OfficialMcq]) -> str:
    if not items:
        return ""
    lines = ["OFFICIAL_ANSWER_BANK (use exact official_answer — do NOT invent keys):"]
    for i, item in enumerate(items, start=1):
        lines.append(f"{i}. {item.item_id} | {item.source} | Ch.{item.chapter} | {item.topic}")
        lines.append(f"   Q: {item.question}")
        if item.options:
            lines.append(f"   Options: {' | '.join(item.options)}")
        lines.append(f"   official_answer: {item.official_answer}")
        lines.append(f"   explanation: {item.explanation}")
    return "\n".join(lines)
