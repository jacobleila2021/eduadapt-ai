"""
OpenAI integration — chunked long-lesson analysis, parallel adaptations, validated JSON.
"""

from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

try:
    from openai import APIStatusError, RateLimitError
except ImportError:  # older/newer openai SDK layouts on Streamlit Cloud
    try:
        from openai._exceptions import APIStatusError, RateLimitError
    except ImportError:
        APIStatusError = Exception
        RateLimitError = Exception

from adaptation_specs import ADAPTATION_SPECS, OUTPUT_KEYS
from config import (
    ENV_PATH,
    MAX_LESSON_CHARS,
    OPENAI_MAX_RETRIES,
    OPENAI_TIMEOUT_SECONDS,
)
from lesson_processor import build_lesson_context, context_to_prompt
from knowledge.prompts import (
    AUDITORY_SECTION_RULES,
    BOARD_EXAM_READINESS_RULES,
    BULLET_SECTION_RULES,
    CLASSROOM_TEACHING_RULES,
    DEPTH_RULES,
    DIFFERENTIATION_RULES,
    ENGINE_RULES,
    RAG_CITATION_RULES,
    SECTION_TITLE_RULES,
    TEACHER_ANSWER_RULES,
    VISUAL_PRACTICE_RULES,
)
from secrets_helper import is_valid_openai_key, read_api_key_from_env_file, reload_env

CLASSROOM_LESSON_KEYS = frozenset(
    {"standard", "ld", "ell", "visual", "auditory", "teacher", "adhd", "autism"}
)
LESSON_KEYS = [k for k in OUTPUT_KEYS if k not in ("vocabulary", "worksheet")]
MAX_PARALLEL_LESSONS = 4


def _get_model() -> str:
    reload_env()
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def _chat(client: OpenAI, system: str, user: str, max_tokens: int = 8000) -> str:
    response = client.chat.completions.create(
        model=_get_model(),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.5,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response.")
    return content


def _coerce_dict(value) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        if text and not text.startswith("_No content"):
            return {
                "big_idea": "Key ideas from your lesson",
                "sections": [{"title": "Lesson Content", "body": text, "box": "teal"}],
                "mermaid_diagram": "",
                "svg_diagram": "",
                "visual_summary": [],
            }
    return {}


def get_effective_api_key(override_api_key: str = "") -> str:
    file_key = read_api_key_from_env_file()
    if file_key:
        return file_key
    session_key = (override_api_key or "").strip()
    if is_valid_openai_key(session_key):
        return session_key
    env_key = os.getenv("OPENAI_API_KEY", "").strip()
    if is_valid_openai_key(env_key):
        return env_key
    return ""


def validate_api_key(override_api_key: str = "") -> bool:
    return is_valid_openai_key(get_effective_api_key(override_api_key))


def format_openai_error(error: Exception) -> str:
    if isinstance(error, RateLimitError):
        return (
            "OpenAI rate limit (429): wait 1–2 minutes or check billing at "
            "https://platform.openai.com/account/billing"
        )
    if isinstance(error, APIStatusError) and getattr(error, "status_code", None) == 401:
        return (
            "OpenAI rejected the API key (401). Update key in sidebar or Streamlit Secrets. "
            f"Key file: {ENV_PATH}"
        )
    return f"OpenAI request failed: {error}"


def _lesson_prompt(
    adaptation_id: str, title: str, hint: str, *, suppress_ai_diagrams: bool = False
) -> str:
    extra_rules = SECTION_TITLE_RULES
    if adaptation_id == "ld":
        extra_rules += BULLET_SECTION_RULES
    elif adaptation_id == "auditory":
        extra_rules += AUDITORY_SECTION_RULES
    elif adaptation_id == "visual":
        extra_rules += VISUAL_PRACTICE_RULES
    elif adaptation_id == "teacher":
        extra_rules += TEACHER_ANSWER_RULES

    teacher_fields = ""
    if adaptation_id == "teacher":
        teacher_fields = """,
  "answer_key": [
    {{"section": "Practice", "question": "...", "model_answer": "...", "marks": 2}}
  ],
  "teacher_notes": "...",
  "differentiation_map": "..." """

    if suppress_ai_diagrams:
        diagram_fields = """  "mermaid_diagram": "",
  "svg_diagram": "",
  "diagram_source": "deterministic_engines","""
    else:
        diagram_fields = """  "mermaid_diagram": "flowchart TD with 4+ nodes, valid mermaid, no code fences",
  "svg_diagram": "<svg xmlns='http://www.w3.org/2000/svg' width='720' height='480'>grouped labelled boxes with arrows and 6+ <text> labels from THIS lesson</svg>",
  "diagram_source": "ai_illustration","""

    classroom_policy = ""
    if adaptation_id in CLASSROOM_LESSON_KEYS:
        classroom_policy = f"{CLASSROOM_TEACHING_RULES}\n{BOARD_EXAM_READINESS_RULES}"

    return f"""You are EduAdapt AI. Create ONE comprehensive lesson adaptation.

Return ONLY valid JSON with a single top-level key "{adaptation_id}" whose value is an object:
{{
  "big_idea": "clear summary sentence",
{diagram_fields}
  "sections": [
    {{"title": "Learning Goal", "body": "120+ words — what students will be able to do", "box": "teal"}},
    {{"title": "Meristematic Tissue", "body": "120+ words teachable classroom segment", "box": "blue"}},
    {{"title": "Permanent Tissue", "body": "120+ words teachable classroom segment", "box": "blue"}},
    {{"title": "Guided Practice", "body": "worked examples with the class", "box": "green"}},
    {{"title": "Independent Practice", "body": "questions students complete alone", "box": "green"}},
    {{"title": "Exam Practice", "body": "board-style short + long questions with model answers", "box": "orange"}},
    {{"title": "Summary", "body": "recap all key points for revision", "box": "orange"}}
  ],
  "visual_summary": [
    {{"icon": "🟦", "color_name": "Topic", "idea": "..."}},
    {{"icon": "🟩", "color_name": "Concept", "idea": "..."}},
    {{"icon": "🟨", "color_name": "Example", "idea": "..."}},
    {{"icon": "🟪", "color_name": "Vocabulary", "idea": "..."}},
    {{"icon": "🟥", "color_name": "Assessment", "idea": "..."}}
  ]{teacher_fields}
}}

Adaptation: {title}
Guidance: {hint}

{DEPTH_RULES}
{classroom_policy}
{ENGINE_RULES}
{RAG_CITATION_RULES}
{DIFFERENTIATION_RULES}
{extra_rules}"""


def _vocabulary_prompt() -> str:
    return f"""You are EduAdapt AI. Build a complete vocabulary study page from the lesson analysis.

Return ONLY valid JSON with top-level key "vocabulary" containing this object:
{{
  "topic": "...",
  "word_wall": [{{"term": "...", "definition": "...", "emoji": "...", "visual_description": "...", "child_friendly": "explain the word in very simple words a child understands", "example": "a clear example sentence using the term"}}],
  "flashcards": [{{"front": "...", "back": "..."}}],
  "picture_words": [{{"term": "...", "color_cue": "...", "draw_this": "vivid scene for illustration", "image_prompt": "optional extra detail for AI image", "label": "..."}}],
  "practice": [{{"term": "...", "sentence_blank": "Write a sentence using ________ ..."}}],
  "self_test": {{
    "fill_blanks": ["Meristematic tissue is made of cells that can ________."],
    "fill_blank_answers": ["Meristematic tissue"]
  }},
  "reference_chart": [{{"term": "...", "definition": "...", "synonym": "...", "exam_tip": "..."}}],
  "mermaid_diagram": "flowchart TD ..."
}}

Requirements: 12–15 word_wall terms, ALL sections filled, real content from lesson.
- fill_blank_answers MUST be the same length as fill_blanks; each entry is the word or phrase that correctly completes THAT blank (e.g. "divide", "minerals", or a vocabulary term).
- Every fill_blanks sentence MUST test a term from THIS lesson's word_wall — never reuse generic math/science examples from other subjects.
- practice: numbered sentence_blank only — no pronunciation or syllable fields.
- Provide at least 6 fill_blanks questions using ________ as the blank (no answer in brackets in the displayed sentence).
- Store correct terms only in fill_blank_answers (parallel array); never show answers inline in fill_blanks text.
- Do not include matching_prompt text with answers — matching is built automatically from word_wall.
- flashcards MUST pair each word_wall term (front) with its definition (back).
{ENGINE_RULES}
{RAG_CITATION_RULES}
{DEPTH_RULES}"""


def _worksheet_prompt(terms: list) -> str:
    term_list = ", ".join(terms[:15]) if terms else "lesson vocabulary"
    return f"""You are EduAdapt AI. Build a rigorous exam worksheet.

Vocabulary terms to use: {term_list}

Return ONLY valid JSON with top-level key "worksheet":
{{
  "header": {{"subject": "...", "topic": "...", "time_allowed": "45-60 minutes", "total_marks": 40}},
  "short_answer": [{{"question": "...", "marks": 2, "lines": 4, "model_answer": "ONE to TWO concise sentences only"}}],
  "long_answer": [{{"question": "...", "marks": 8, "lines": 10, "model_answer": "FULL multi-sentence paragraph (minimum 5 sentences) with detailed explanation"}}],
  "diagram_question": {{"question": "...", "marks": 5, "svg_diagram": "<svg ...></svg>", "model_answer": "what a labelled answer should show"}},
  "vocab_questions": [{{"question": "...", "marks": 2, "model_answer": "concise correct usage"}}],
  "student_checklist": ["..."],
  "teacher_differentiation": "...",
  "answer_key": [
    {{"question_ref": "Part A Q1", "model_answer": "...", "marks_notes": "..."}},
    {{"question_ref": "Part B Q1", "model_answer": "...", "marks_notes": "..."}},
    {{"question_ref": "Part D Q1", "model_answer": "...", "marks_notes": "..."}}
  ]
}}

CRITICAL ANSWER RULES:
- SUBJECT SCOPE: Every question must assess ONLY the TOPIC, GRADE, objectives, vocabulary,
  facts, and processes in the uploaded lesson. Never mix questions from another chapter or
  subject. Ignore any retrieved artifact whose topic does not directly match this lesson.
- DIAGRAM SCOPE: Only Part C may ask the learner to draw or label a diagram. Do not ask for
  diagrams in short, long, or vocabulary questions. Alora will attach a source-grounded
  concept organiser to Part C after lesson generation.
- SHORT answers (Part A) model_answer = 1–2 sentences MAX. Never a paragraph.
- LONG answers (Part B) model_answer = full paragraph, minimum 5 complete sentences, detailed and age-appropriate.
- Provide a model_answer for EVERY question AND a matching answer_key entry for Part A, Part B, Part D (refs like "Part A Q1", "Part B Q1", "Part D Q1").
- Answers must be factually correct and drawn from the lesson analysis.

Requirements:
- 8 short_answer, 4 long_answer (exam-level), 6 vocab_questions
- Questions must test ALL major concepts from the lesson analysis
{ENGINE_RULES}
{RAG_CITATION_RULES}
{DEPTH_RULES}"""


def _extract_key(raw: str, key: str) -> dict:
    parsed = json.loads(raw)
    value = parsed.get(key)
    if value is None:
        raise ValueError(f"AI response missing '{key}' key.")
    return _coerce_dict(value)


def _valid_vocabulary(vocab: dict) -> bool:
    return bool(vocab.get("word_wall")) and len(vocab.get("word_wall") or []) >= 5


def _sanitize_vocabulary(vocab: dict) -> dict:
    """Ensure flashcards, practice, and self-test align with the word wall."""
    from structured_renderers import (
        _prepare_practice,
        _prepare_self_test,
    )

    word_wall = vocab.get("word_wall") or []
    if not word_wall:
        return vocab

    vocab["flashcards"] = [
        {"front": w.get("term", ""), "back": w.get("definition", "")}
        for w in word_wall
        if w.get("term")
    ]
    vocab["practice"] = _prepare_practice(word_wall, vocab.get("topic", ""))
    vocab["self_test"] = _prepare_self_test(vocab.get("self_test") or {}, word_wall)

    return vocab


def _valid_worksheet(sheet: dict) -> bool:
    return bool(sheet.get("short_answer")) and len(sheet.get("short_answer") or []) >= 4


def _section_body_text(section: dict) -> str:
    if not isinstance(section, dict):
        return ""
    return str(section.get("body") or "").strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _has_exam_practice_section(sections: list) -> bool:
    markers = (
        "exam practice",
        "board check",
        "board practice",
        "exam focus",
        "board exam",
    )
    for section in sections:
        if not isinstance(section, dict):
            continue
        title = str(section.get("title") or "").lower()
        if any(m in title for m in markers):
            return True
        body = _section_body_text(section).lower()
        if "exam practice" in body or "board check" in body:
            return True
    return False


def _stub_bullet_ratio(body: str) -> float:
    """Fraction of markdown bullets that are too short to teach from."""
    bullets = re.findall(r"(?m)^\s*[-*]\s+(.+)$", body or "")
    if len(bullets) < 3:
        return 0.0
    stubby = sum(1 for b in bullets if _word_count(b) < 6)
    return stubby / len(bullets)


def _valid_lesson(lesson: dict, *, classroom: bool = False) -> bool:
    sections = lesson.get("sections") or []
    # Visuals are attached deterministically after generation. Requiring a
    # model-authored diagram here incorrectly rejected otherwise complete
    # adaptations and replaced them with raw extractive fallbacks.
    if not lesson.get("big_idea") or len(sections) < 6:
        return False
    if not classroom:
        return True

    bodies = [_section_body_text(s) for s in sections if isinstance(s, dict)]
    aggregate = " ".join(bodies)
    if _word_count(aggregate) < 500:
        return False

    thin_sections = 0
    for body in bodies:
        wc = _word_count(body)
        bullets = re.findall(r"(?m)^\s*[-*]\s+(.+)$", body)
        bullet_words = sum(_word_count(b) for b in bullets)
        substantive = wc >= 80 or (len(bullets) >= 6 and bullet_words >= 80)
        if not substantive:
            thin_sections += 1
        if _stub_bullet_ratio(body) > 0.5:
            return False
    if thin_sections > 2:
        return False

    if not _has_exam_practice_section(sections):
        pq = lesson.get("practice_questions") or []
        if not (isinstance(pq, list) and len(pq) >= 4):
            return False
    return True


def _lesson_fingerprint(lesson: dict) -> set[str]:
    text = json.dumps(lesson, sort_keys=True, default=str).lower()
    words = set(re.findall(r"[a-z]{5,}", text))
    return words


def _adaptation_difference_score(base: dict, adapted: dict) -> float:
    """0.0–1.0 — how different two adaptations are (target >= 0.80)."""
    if not base or not adapted:
        return 0.0
    a = _lesson_fingerprint(base)
    b = _lesson_fingerprint(adapted)
    if not a or not b:
        return 0.0
    overlap = len(a & b) / max(len(a | b), 1)
    return round(1.0 - overlap, 3)


def _fallback_vocabulary(context: dict) -> dict:
    """Build vocabulary from extracted lesson context when AI response is thin."""
    terms = list(context.get("vocabulary_terms") or [])
    for concept in context.get("key_concepts") or []:
        if isinstance(concept, dict) and concept.get("name"):
            terms.append(concept["name"])
    terms = list(dict.fromkeys(terms))[:15]

    word_wall = []
    for index, term in enumerate(terms):
        explanation = next(
            (
                c.get("explanation", "")
                for c in (context.get("key_concepts") or [])
                if isinstance(c, dict) and c.get("name") == term
            ),
            f"Important term from {context.get('topic', 'the lesson')}.",
        )
        word_wall.append(
            {
                "term": term,
                "definition": explanation[:300] if explanation else f"Key vocabulary: {term}",
                "emoji": ["💧", "🌿", "☀️", "📘", "🔬", "🌍"][index % 6],
                "visual_description": f"Imagine a clear labelled diagram showing {term}.",
                "child_friendly": f"{term} is an important idea from {context.get('topic', 'this lesson')}.",
                "example": (
                    f"We learned about {term} in "
                    f"{context.get('topic') or 'today’s lesson'}."
                ),
            }
        )

    flashcards = [{"front": w["term"], "back": w["definition"]} for w in word_wall]
    return {
        "topic": context.get("topic", "Lesson Vocabulary"),
        "word_wall": word_wall,
        "flashcards": flashcards,
        "picture_words": [
            {
                "term": w["term"],
                "color_cue": "teal highlight",
                "draw_this": w["visual_description"],
                "label": w["term"],
            }
            for w in word_wall
        ],
        "practice": [
            {
                "term": w["term"],
                "sentence_blank": f"Write one sentence using ________ to explain {context.get('topic', 'this topic')}.",
            }
            for w in word_wall[:8]
        ],
        "self_test": {
            "fill_blanks": [
                f"{w['definition'].rstrip('.')}. The vocabulary word is ________."
                for w in word_wall[: min(6, len(word_wall))]
            ],
            "fill_blank_answers": [w["term"] for w in word_wall[: min(6, len(word_wall))]],
        },
        "reference_chart": [
            {
                "term": w["term"],
                "definition": w["definition"][:120],
                "synonym": "—",
                "exam_tip": "Define clearly in exams.",
            }
            for w in word_wall
        ],
        "mermaid_diagram": f"flowchart TD\n  A[{context.get('topic', 'Topic')}] --> B[Key Terms]",
    }


def _fallback_worksheet(context: dict, vocab: dict) -> dict:
    terms = [w.get("term", "") for w in vocab.get("word_wall") or [] if w.get("term")]
    facts = context.get("facts_and_processes") or []
    short = []
    for index, fact in enumerate(facts[:8], 1):
        short.append(
            {
                "question": f"Using the uploaded source, explain: {fact[:120]}",
                "marks": 2,
                "lines": 4,
                "model_answer": fact[:500],
            }
        )
    if len(short) < 4:
        short.extend(
            [
                {
                    "question": "Name two key ideas stated in the uploaded source.",
                    "marks": 2,
                    "lines": 3,
                    "model_answer": "; ".join(facts[:2])[:500],
                },
                {
                    "question": "Summarise the main idea of the uploaded source.",
                    "marks": 2,
                    "lines": 3,
                    "model_answer": str((facts or [context.get("topic", "")])[0])[:500],
                },
            ]
        )
    return {
        "header": {
            "subject": context.get("topic", "Subject"),
            "topic": context.get("topic", "Topic"),
            "time_allowed": "45 minutes",
            "total_marks": 30,
        },
        "short_answer": short[:8],
        "long_answer": [
            {
                "question": f"Describe {context.get('topic', 'this topic')} in detail with examples.",
                "marks": 8,
                "lines": 10,
                "model_answer": " ".join(facts[:4])[:1200],
            },
            {
                "question": "Compare two ideas from the uploaded source.",
                "marks": 6,
                "lines": 8,
                "model_answer": " ".join(facts[1:4])[:1000],
            },
        ],
        "diagram_question": {
            "question": "Create a labelled organizer using only ideas from the uploaded source.",
            "marks": 4,
            "svg_diagram": "",
            "model_answer": "A correct organizer includes: " + ", ".join(terms[:6]),
        },
        "vocab_questions": [
            {"question": f"Use '{term}' correctly in a sentence.", "marks": 2}
            for term in terms[:6]
        ],
        "student_checklist": [
            "Read all questions before starting",
            "Allow 2 minutes per mark on long answers",
            "Review vocabulary tab before Part D",
        ],
        "teacher_differentiation": "Assign Parts A–B to all; Part D with word bank for ELL.",
        "answer_key": [
            {
                "question_ref": f"Short answer {index}",
                "model_answer": row.get("model_answer") or "",
                "marks_notes": f"{row.get('marks', 2)} marks",
            }
            for index, row in enumerate(short[:8], 1)
        ],
    }


def _generate_one_lesson(
    api_key: str,
    key: str,
    title: str,
    hint: str,
    user_prompt: str,
    baseline: dict | None = None,
    *,
    suppress_ai_diagrams: bool = False,
) -> tuple:
    client = OpenAI(
        api_key=api_key,
        timeout=OPENAI_TIMEOUT_SECONDS,
        max_retries=OPENAI_MAX_RETRIES,
    )
    sys_prompt = _lesson_prompt(key, title, hint, suppress_ai_diagrams=suppress_ai_diagrams)
    classroom = key in CLASSROOM_LESSON_KEYS
    raw = _chat(client, sys_prompt, user_prompt, max_tokens=9000)
    lesson = _extract_key(raw, key)
    if suppress_ai_diagrams:
        lesson["diagram_source"] = "deterministic_engines"
        lesson["mermaid_diagram"] = lesson.get("mermaid_diagram") or ""
        lesson["svg_diagram"] = lesson.get("svg_diagram") or ""

    def _retry(extra: str = "") -> dict:
        prompt = user_prompt + extra
        retry_raw = _chat(client, sys_prompt, prompt, max_tokens=9000)
        out = _extract_key(retry_raw, key)
        if suppress_ai_diagrams:
            out["mermaid_diagram"] = ""
            out["svg_diagram"] = ""
            out["diagram_source"] = "deterministic_engines"
        return out

    if not _valid_lesson(lesson, classroom=classroom):
        reminder = (
            "\n\nSTRICT RETRY: Produce a full classroom-teachable lesson (not a condensation). "
            "Each section ≥120 words or ≥8 substantive bullets totaling ≥120 words. "
            "Include an Exam Practice / Board Check section with board-style questions and "
            "model answers grounded only in SOURCE_CLAIMS. Keep exam terminology."
            if classroom
            else ""
        )
        lesson = _retry(reminder)
    if baseline and key not in ("standard", "vocabulary", "worksheet"):
        score = _adaptation_difference_score(baseline, lesson)
        if score < 0.80:
            lesson = _retry(
                f"\n\nIMPORTANT: Previous output was only {score:.0%} different from standard. "
                f"Regenerate with clearly distinct structure and scaffolds for {title} "
                f"while keeping the same exam coverage and terminology."
            )
    return key, lesson


def _context_from_universal_profile(profile: dict, lesson_text: str) -> dict:
    """Project the source-bound v3 profile into the legacy prompt contract."""
    claims = [
        row
        for row in profile.get("claim_ledger") or []
        if isinstance(row, dict) and row.get("text")
    ]

    def source_explanation(term: str) -> str:
        return next(
            (
                str(row.get("text"))
                for row in claims
                if re.search(rf"\b{re.escape(str(term))}\b", str(row.get("text")), re.I)
            ),
            f"{term} appears in the uploaded source.",
        )

    return {
        "topic": profile.get("topic") or profile.get("title") or "Uploaded lesson",
        "title": profile.get("title") or "Uploaded lesson",
        "grade_level": (profile.get("age_estimate") or {}).get("band") or "adaptive",
        "learning_objectives": [
            row.get("objective")
            for row in profile.get("learning_objectives") or []
            if isinstance(row, dict) and row.get("objective")
        ],
        "key_concepts": [
            {
                "name": row.get("concept"),
                "explanation": source_explanation(str(row.get("concept") or "")),
                "source_refs": row.get("source_refs") or [],
            }
            for row in profile.get("concepts") or []
            if isinstance(row, dict) and row.get("concept")
        ],
        "vocabulary_terms": [
            row.get("term")
            for row in profile.get("vocabulary") or []
            if isinstance(row, dict) and row.get("term")
        ],
        "facts_and_processes": [str(row.get("text")) for row in claims[:24]],
        "difficulty": profile.get("difficulty") or {},
        "language": profile.get("language") or "unknown",
        "source_char_count": len(lesson_text),
        "chunks_processed": 1,
        "source_bound": True,
    }


def _clean_source_units(profile: dict) -> list[str]:
    """Turn imperfect PDF extraction into readable, deduplicated source units."""
    units: list[str] = []
    seen: set[str] = set()
    for row in profile.get("claim_ledger") or []:
        if not isinstance(row, dict) or not row.get("text"):
            continue
        text = str(row.get("text") or "")
        text = re.sub(r"/?square\d*", " ", text, flags=re.I)
        text = re.sub(r"(?:Figure\s*\d+(?:\.\d+)+\s*){2,}", " ", text, flags=re.I)
        text = re.sub(r"\bFigure\s*\d+(?:\.\d+)+\b", " ", text, flags=re.I)
        text = re.sub(r"\bActivity\s*\d+(?:\.\d+)*\b", ". ", text, flags=re.I)
        text = re.sub(r"(\d+(?:\.\d+)+)(?=[A-Z][a-z])", r"\1. ", text)
        text = re.sub(r"(?<=[a-z)])(?=[A-Z][a-z])", ". ", text)
        text = re.sub(r"\s+", " ", text).strip(" .;:-")
        chunks = re.split(r"(?<=[.!?])\s+", text)
        for chunk in chunks:
            chunk = chunk.strip(" .;:-")
            if len(chunk) < 20:
                continue
            if len(chunk) > 360:
                words = chunk.split()
                chunks_to_add = [
                    " ".join(words[start : start + 52])
                    for start in range(0, len(words), 52)
                ]
            else:
                chunks_to_add = [chunk]
            for item in chunks_to_add:
                key = re.sub(r"\W+", "", item).lower()
                if len(item) >= 20 and key not in seen:
                    seen.add(key)
                    units.append(item.rstrip(".") + ".")
    return units[:36]


def _source_fallback_lesson(
    key: str, profile: dict, source_refs: list[str]
) -> dict:
    """Classroom-teachable, source-bound fallback — not a thin extractive summary."""
    topic = str(profile.get("topic") or profile.get("title") or "this topic")
    units = _clean_source_units(profile)
    if not units:
        units = [f"Review the readable material provided for {topic}."]

    def unit(i: int) -> str:
        return units[i % len(units)]

    def teach_block(start: int, title: str, box: str) -> dict:
        chunks = [unit(start + j) for j in range(min(3, len(units)))]
        body_parts = [
            f"Teach this segment aloud (about 5–8 minutes). Topic focus: {title}.",
            "",
        ]
        for idx, chunk in enumerate(chunks, start=1):
            body_parts.append(
                f"- **Idea {idx}:** {chunk} Ask students to restate the idea in one sentence."
            )
        body_parts.extend(
            [
                "",
                f"Check: Point to evidence in the uploaded material that supports each idea about {topic}.",
                "Scaffold: Preview key terms, then have students use each term in a full sentence.",
            ]
        )
        return {
            "title": title,
            "body": "\n".join(body_parts),
            "box": box,
            "source_refs": source_refs,
        }

    concept_titles = []
    for row in profile.get("key_concepts") or []:
        if isinstance(row, dict) and row.get("name"):
            concept_titles.append(str(row["name"]).strip())
        elif isinstance(row, str) and row.strip():
            concept_titles.append(row.strip())
    if not concept_titles:
        concept_titles = [f"Core idea {i + 1}" for i in range(min(3, len(units)))]
    concept_titles = concept_titles[:4]

    scaffolds = {
        "ld": (
            "Dyslexia Smart scaffolds: use spaced bullets, bold **key terms**, "
            "one idea per line, and a visible checklist. Keep exam vocabulary; "
            "add a short gloss in parentheses after each term."
        ),
        "ell": (
            "ELL scaffolds: preview glossary terms, sentence frames "
            "('The process of ___ is called ___'), and allow rehearsal before writing. "
            "Keep board terminology."
        ),
        "visual": (
            "Visual scaffolds: map each idea into a labelled sequence on the board; "
            "students redraw and label before answering."
        ),
        "auditory": (
            "Auditory scaffolds: Say: read each source idea aloud. "
            "Repeat: students echo, then explain in their own words."
        ),
        "teacher": (
            "Teacher note: verify each claim against the uploaded source before "
            "extending discussion; use the Exam Practice section for board-style marking."
        ),
        "standard": (
            "Mainstream classroom: teach each segment fully, then circulate during "
            "independent practice and close with Exam Practice."
        ),
    }
    support = scaffolds.get(
        key,
        "Use retrieval practice and source-based examples; do not invent STEM facts.",
    )

    short_qs = []
    for i in range(4):
        claim = unit(i)
        short_qs.append(
            f"**Q{i + 1} (Short, 2 marks):** Using the lesson on {topic}, explain: "
            f"{claim[:180]}\n"
            f"*Suggested answer:* Restate the idea accurately and name the related term "
            f"from the lesson."
        )
    long_qs = []
    for i in range(2):
        a, b = unit(i + 2), unit(i + 5)
        long_qs.append(
            f"**Q{i + 5} (Long/HOTS, 5 marks):** Compare and connect these ideas from "
            f"today's lesson: (1) {a[:140]} (2) {b[:140]}\n"
            f"*Suggested answer:* Describe both ideas, explain the link using lesson terms, "
            f"and give one real-world implication supported by the source."
        )

    sections = [
        {
            "title": "Learning Goal",
            "body": (
                f"By the end of this lesson, students will accurately explain the main "
                f"ideas in {topic}, use the lesson's exam terminology correctly, and "
                f"answer board-style questions using only this adaptation.\n\n"
                f"- State the learning goal aloud and write it on the board.\n"
                f"- Preview success criteria: define terms, explain processes, attempt Exam Practice.\n"
                f"- Source focus: {unit(0)}\n"
                f"- {support}"
            ),
            "box": "teal",
            "source_refs": source_refs,
        },
    ]
    boxes = ("blue", "cream", "blue", "orange")
    for idx, title in enumerate(concept_titles):
        sections.append(teach_block(idx * 2, title, boxes[idx % len(boxes)]))

    sections.extend(
        [
            {
                "title": "Guided Practice",
                "body": (
                    f"Work this with the class (8–10 minutes).\n\n"
                    f"- Read together: {unit(1)}\n"
                    f"- Model how to turn the idea into a 2-mark answer using lesson terms.\n"
                    f"- Ask two students to improve the answer using evidence from: {unit(3)}\n"
                    f"- Check misconceptions; keep ENGINE_ARTIFACTS / official facts unchanged if present.\n"
                    f"- {support}"
                ),
                "box": "green",
                "source_refs": source_refs,
            },
            {
                "title": "Independent Practice",
                "body": (
                    f"Students work alone or in pairs (8–10 minutes).\n\n"
                    f"- Write a short paragraph explaining: {unit(2)}\n"
                    f"- Add one labelled sketch or sequence if the topic is visual.\n"
                    f"- Self-check against: {unit(4)}\n"
                    f"- Teacher circulates with the checklist: term used? idea complete? evidence cited?\n"
                    f"- {support}"
                ),
                "box": "green",
                "source_refs": source_refs,
            },
            {
                "title": "Exam Practice",
                "body": (
                    "Board-style practice using ideas from today's uploaded lesson "
                    "(teacher-checked answers — not an official board mark scheme).\n\n"
                    + "\n\n".join(short_qs + long_qs)
                ),
                "box": "orange",
                "source_refs": source_refs,
            },
            {
                "title": "Review and Next Steps",
                "body": (
                    f"Close the lesson (3–5 minutes).\n\n"
                    f"- Recap: {unit(0)} / {unit(1)}\n"
                    f"- Students name three exam terms from {topic} and one board question they can now attempt.\n"
                    f"- Homework: revise Exam Practice answers without looking, then check against model cues.\n"
                    f"- {support}"
                ),
                "box": "purple",
                "source_refs": source_refs,
            },
        ]
    )

    # Ensure ≥6 sections even if concepts were sparse
    while len(sections) < 6:
        sections.insert(
            1,
            teach_block(len(sections), f"Teach: {topic}", "blue"),
        )

    answer_key = []
    if key == "teacher":
        for i, line in enumerate(short_qs + long_qs, start=1):
            answer_key.append(
                {
                    "section": "Exam Practice",
                    "question": f"Q{i}",
                    "model_answer": line.split("*Suggested answer:*")[-1].strip()
                    if "*Suggested answer:*" in line
                    else line.split("**Model answer")[-1].strip(": *"),
                    "marks": 2 if i <= 4 else 5,
                }
            )

    out = {
        "title": profile.get("title") or "Uploaded Lesson",
        "subtitle": key.replace("_", " ").title(),
        "big_idea": (
            f"Students build a classroom-ready, source-grounded understanding of {topic} "
            f"and can attempt board-style questions from this adaptation alone."
        ),
        "sections": sections,
        "mermaid_diagram": "",
        "svg_diagram": "",
        "diagram_source": "deterministic_engines",
        "source_refs": source_refs,
        "practice_questions": [
            {"question": f"Q{i + 1}", "source_bound": True} for i in range(6)
        ],
    }
    if answer_key:
        out["answer_key"] = answer_key
        out["teacher_notes"] = support
        out["differentiation_map"] = (
            "Apply ld/ell/visual/auditory scaffolds without reducing exam coverage."
        )
    return out


def _apply_v3_output_contract(
    value: dict,
    *,
    key: str,
    valid_source_refs: list[str],
    fallback_used: str = "none",
    retry_history: list[dict] | None = None,
) -> dict:
    """Attach valid source provenance to every generated factual unit."""
    refs = list(dict.fromkeys(valid_source_refs))[:40]
    default_refs = refs[:8]

    def clean_visible_text(text: str) -> str:
        lines = []
        for line in str(text or "").splitlines():
            if re.match(
                r"^\s*(?:source(?:\s+detail|\s+reference|\s+refs?)?s?|"
                r"citation|references?)\s*[:\-]",
                line,
                re.I,
            ):
                continue
            line = re.sub(
                r"\s*(?:\(|\[)?(?:source(?:\s+detail|\s+refs?)?|citation)"
                r"\s*:\s*(?:blk_|claim_|src_)[^)\]\n]*(?:\)|\])?\s*$",
                "",
                line,
                flags=re.I,
            )
            lines.append(line.rstrip())
        return "\n".join(lines).strip()

    def attach(node):
        if isinstance(node, dict):
            has_content = any(
                name in node
                for name in (
                    "body",
                    "definition",
                    "child_friendly",
                    "question",
                    "model_answer",
                    "answer",
                    "back",
                    "explanation",
                    "big_idea",
                    "guidance",
                    "teacher_guidance",
                    "parent_guidance",
                    "teacher_differentiation",
                    "summary",
                    "script",
                )
            )
            if has_content:
                supplied = [
                    ref for ref in node.get("source_refs") or [] if ref in refs
                ]
                node["source_refs"] = supplied or default_refs
            for field, child in list(node.items()):
                if isinstance(child, str) and field not in {
                    "source_ref",
                    "source_refs",
                }:
                    node[field] = clean_visible_text(child)
                else:
                    attach(child)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                if isinstance(child, str):
                    node[index] = clean_visible_text(child)
                else:
                    attach(child)

    output = dict(value or {})
    attach(output)
    output.setdefault("source_refs", default_refs)
    output["_contract"] = {
        "schema_version": "3.0.0",
        "adaptation_key": key,
        "grounding_mode": "uploaded_source",
        "completeness": "fallback" if fallback_used != "none" else "complete",
        "fallback_used": fallback_used,
        "retry_history": retry_history or [],
        "valid_source_refs": refs,
    }
    return output


def generate_adaptations(
    lesson_text: str,
    override_api_key: str = "",
    on_progress=None,
    *,
    source_envelope: dict | None = None,
    universal_profile: dict | None = None,
    grounding_mode: str = "uploaded_source",
) -> dict:
    """Full pipeline with progress callbacks for Streamlit UI."""
    api_key = get_effective_api_key(override_api_key)
    if not api_key:
        raise ValueError(
            f"OpenAI API key not found. Add it in the sidebar or edit {ENV_PATH}."
        )

    client = OpenAI(
        api_key=api_key,
        timeout=OPENAI_TIMEOUT_SECONDS,
        max_retries=OPENAI_MAX_RETRIES,
    )
    model = _get_model()
    merged = {}

    def step(message: str, fraction: float) -> None:
        if on_progress:
            on_progress(message, fraction)

    try:
        if not source_envelope:
            from engines.knowledge_ingestion_engine.universal_ingest import (
                ingest_source_bytes,
            )

            source_envelope = ingest_source_bytes(
                "lesson.txt", lesson_text.encode("utf-8")
            ).to_dict()
        if not universal_profile:
            from engines.universal_lesson.profile import (
                build_universal_lesson_profile,
            )

            universal_profile = build_universal_lesson_profile(
                source_envelope
            ).to_dict()
        source_refs = [
            str(block.get("block_id"))
            for block in source_envelope.get("blocks") or []
            if isinstance(block, dict) and block.get("block_id")
        ]
        step("Running verified STEM engines…", 0.02)
        from engines.lesson_pipeline import process_lesson_stem
        from engines.visualization.priority import (
            has_deterministic_visuals,
            inject_verified_visuals_into_lesson,
            select_preferred_visuals,
            visualization_prompt_rules,
        )

        topic_hint = " ".join(lesson_text.splitlines()[:5])[:200]
        stem = process_lesson_stem(lesson_text, topic=topic_hint)
        merged["_meta"] = {
            "engine_artifacts": stem["artifacts"],
            "stem_qa": stem["qa"],
            "stem_claims_found": stem["claims_found"],
            "routing_warnings": stem.get("routing_warnings") or [],
            "preferred_visuals": stem.get("preferred_visuals") or [],
            "biology_figures": stem.get("biology_figures") or [],
        }

        step("Building source-linked lesson profile…", 0.05)
        context = _context_from_universal_profile(universal_profile, lesson_text)
        merged["_meta"]["lesson_context"] = context
        merged["_meta"]["source_envelope"] = source_envelope
        merged["_meta"]["universal_profile"] = universal_profile

        # ULI Milestone 2.3 — feature-flagged (default OFF). Non-blocking.
        try:
            from engines.universal_lesson_intelligence.pipeline import (
                attach_uli_pipeline,
                is_uli_pipeline_enabled,
            )

            if is_uli_pipeline_enabled():
                attach_uli_pipeline(
                    merged["_meta"],
                    lesson_text=lesson_text,
                    source_envelope=source_envelope,
                    universal_profile=universal_profile,
                    stem_metadata={
                        "artifacts": stem.get("artifacts") or [],
                        "claims_found": stem.get("claims_found"),
                        "preferred_visuals": stem.get("preferred_visuals") or [],
                        "routing_warnings": stem.get("routing_warnings") or [],
                        "biology_figures": stem.get("biology_figures") or [],
                        "qa": stem.get("qa") or {},
                    },
                )
                uli_accessors = ((merged["_meta"].get("uli") or {}).get("accessors") or {})
                edu = uli_accessors.get("educational_structure") or {}
                if edu.get("topic") and not context.get("topic"):
                    context["topic"] = edu["topic"]
                    merged["_meta"]["lesson_context"] = context
        except Exception:
            merged["_meta"]["uli"] = {
                "enabled": False,
                "error": "uli_pipeline_attach_failed",
            }

        # Re-match biology figures with better topic from analysis
        if not merged["_meta"]["biology_figures"]:
            try:
                from knowledge.biology_figures import match_biology_figures

                figs = match_biology_figures(
                    lesson_text, topic=str(context.get("topic") or ""), limit=3
                )
                merged["_meta"]["biology_figures"] = figs
                preferred = select_preferred_visuals(stem["artifacts"], figs, max_visuals=6)
                merged["_meta"]["preferred_visuals"] = preferred
                viz = visualization_prompt_rules(preferred)
                if viz:
                    base = stem.get("prompt_block") or ""
                    # Drop prior viz rules if present, then append refreshed ones
                    stem["prompt_block"] = (base.split("VISUALIZATION")[0].rstrip() + "\n\n" + viz).strip()
            except Exception:
                pass

        step("Checking optional curriculum enrichment…", 0.08)
        from knowledge.service import enrich_worksheet_with_official_bank, prepare_knowledge_for_lesson

        curriculum_resolution = (
            universal_profile.get("curriculum_resolution") or {}
        )
        if curriculum_resolution.get("status") in {
            "recognized",
            "user_declared",
        }:
            knowledge = prepare_knowledge_for_lesson(
                lesson_text,
                context,
                grounding_mode=grounding_mode,
            )
        else:
            knowledge = {
                "pilot_id": None,
                "board": None,
                "grade": None,
                "subject": None,
                "book_title": None,
                "index": {
                    "indexed": 0,
                    "backend": "curriculum_unknown",
                    "message": "Curriculum enrichment was not requested.",
                },
                "rag_hits": [],
                "official_mcqs": [],
                "exam_bundle": {},
                "prompt_block": "",
                "citations": [],
                "scope_matched": False,
                "retrieval_warnings": [],
                "external_enrichment": {
                    "status": "no_hits",
                    "required": False,
                    "citation_notice": "No curriculum references available.",
                },
            }
        merged["_meta"]["knowledge"] = knowledge

        preferred = merged["_meta"].get("preferred_visuals") or []
        suppress_ai_diagrams = has_deterministic_visuals(preferred)

        # Teacher-approved factual cache: reuse Computation + Knowledge facts
        from knowledge.chapter_cache import (
            apply_approved_facts_to_meta,
            factual_fingerprint,
            load_approved_package,
        )

        topic_name = str(context.get("topic") or topic_hint or "")
        fp = factual_fingerprint(
            topic_name,
            merged["_meta"].get("engine_artifacts") or [],
            (knowledge.get("citations") if isinstance(knowledge, dict) else None) or [],
            str(source_envelope.get("source_hash") or ""),
        )
        approved = load_approved_package(fp)
        if approved and approved.get("approved"):
            merged["_meta"] = apply_approved_facts_to_meta(merged["_meta"], approved)
            preferred = merged["_meta"].get("preferred_visuals") or preferred
            suppress_ai_diagrams = has_deterministic_visuals(preferred)
            if approved.get("stem_prompt_block"):
                stem["prompt_block"] = approved["stem_prompt_block"]
            if (approved.get("knowledge") or {}).get("prompt_block"):
                knowledge = {**knowledge, **approved["knowledge"]}
                merged["_meta"]["knowledge"] = knowledge
            step("Reusing teacher-approved chapter facts…", 0.10)

        merged["_meta"]["factual_fingerprint"] = fp
        merged["_meta"]["chapter_approved"] = bool(approved and approved.get("approved"))

        from engines.universal_lesson.profile import profile_to_prompt_block

        user_prompt = (
            profile_to_prompt_block(universal_profile)
            + "\n\n---\n"
            + context_to_prompt(context, lesson_text[:MAX_LESSON_CHARS])
        )
        if stem.get("prompt_block"):
            user_prompt = user_prompt + "\n\n---\nENGINE_ARTIFACTS:\n" + stem["prompt_block"]
        if (
            knowledge.get("prompt_block")
            and (knowledge.get("external_enrichment") or {}).get("status")
            == "available"
        ):
            user_prompt = user_prompt + "\n\n---\n" + knowledge["prompt_block"]
        else:
            user_prompt += (
                "\n\nOPTIONAL_CURRICULUM_ENRICHMENT: unavailable. "
                "Continue from the uploaded source. Do not claim official alignment. "
                "Display: No curriculum references available."
            )
        if preferred:
            user_prompt = user_prompt + "\n\n" + visualization_prompt_rules(preferred)
        if merged["_meta"].get("chapter_approved"):
            user_prompt = (
                user_prompt
                + "\n\nCHAPTER_FACTS_LOCKED: Teacher-approved factual package in use. "
                "Change presentation only — do not alter equations, answers, or diagrams."
            )

        # --- Lesson Composition Engine 1.0 (primary educational composition) ---
        step("Composing lessons with Lesson Composition Engine…", 0.12)
        lce_package_obj = None
        lce_adaptations: dict = {}
        try:
            from engines.lesson_composition_engine import compose_lesson_package

            lce_package_obj = compose_lesson_package(
                lesson_text=lesson_text,
                universal_profile=universal_profile,
                meta=merged.get("_meta") or {},
                context=context,
            )
            versions = dict(lce_package_obj.versions or {})
            lce_adaptations = versions
            if lce_package_obj.vocabulary:
                lce_adaptations["vocabulary"] = lce_package_obj.vocabulary
            publisher_meta = getattr(lce_package_obj, "publisher_meta", None) or {}
            pqle_meta = publisher_meta.get("pqle") if isinstance(publisher_meta, dict) else {}
            merged["_meta"]["canonical_lesson_graph"] = (
                (publisher_meta.get("clg") if isinstance(publisher_meta, dict) else None) or {}
            )
            merged["_meta"]["intelligence_board"] = (
                (publisher_meta.get("intelligence_board") if isinstance(publisher_meta, dict) else None)
                or {}
            )
            merged["_meta"]["lce"] = {
                "ok": True,
                "version": getattr(lce_package_obj, "schema_version", "1.0.0"),
                "quality": (
                    lce_package_obj.quality.to_dict()
                    if getattr(lce_package_obj, "quality", None)
                    else {}
                ),
                "clg": merged["_meta"]["canonical_lesson_graph"],
                "intelligence_board": merged["_meta"]["intelligence_board"],
                "pqi": (publisher_meta.get("pqi") if isinstance(publisher_meta, dict) else None) or {},
                "pqle": pqle_meta or {
                    "publication_ready": bool(
                        (publisher_meta or {}).get("publication_ready", True)
                    ),
                    "reject_rendering": False,
                },
                "pmes": (publisher_meta.get("pmes") if isinstance(publisher_meta, dict) else None) or {},
                "editorial": (
                    (publisher_meta.get("editorial") if isinstance(publisher_meta, dict) else None)
                    or {}
                ),
                "mutates_curriculum": False,
                "frequency_vocab_used": False,
            }
            if getattr(lce_package_obj, "blueprint", None):
                merged["_meta"]["lce"]["blueprint"] = lce_package_obj.blueprint.to_dict()
        except Exception as lce_exc:  # noqa: BLE001
            merged["_meta"]["lce"] = {
                "ok": False,
                "error": str(lce_exc)[:300],
            }
            lce_adaptations = {}

        step("Building vocabulary study page…", 0.15)
        vocab = {}
        vocab_fallback = False
        if _valid_vocabulary(lce_adaptations.get("vocabulary") or {}):
            vocab = lce_adaptations["vocabulary"]
        else:
            for _ in range(2):
                try:
                    raw = _chat(client, _vocabulary_prompt(), user_prompt, max_tokens=7000)
                    vocab = _extract_key(raw, "vocabulary")
                except Exception:
                    vocab = {}
                if _valid_vocabulary(vocab):
                    break
            if not _valid_vocabulary(vocab):
                vocab = lce_adaptations.get("vocabulary") or _fallback_vocabulary(context)
                vocab_fallback = True
        merged["vocabulary"] = _apply_v3_output_contract(
            _sanitize_vocabulary(vocab),
            key="vocabulary",
            valid_source_refs=source_refs,
            fallback_used="lce" if (lce_adaptations.get("vocabulary") and not vocab_fallback) else (
                "source_extractive" if vocab_fallback else "none"
            ),
        )

        step("Building exam worksheet…", 0.25)
        terms = [w.get("term", "") for w in merged["vocabulary"].get("word_wall") or []]
        sheet = {}
        worksheet_fallback = False
        if _valid_worksheet(lce_adaptations.get("worksheet") or {}):
            sheet = lce_adaptations["worksheet"]
        else:
            for _ in range(2):
                try:
                    raw = _chat(client, _worksheet_prompt(terms), user_prompt, max_tokens=7000)
                    sheet = _extract_key(raw, "worksheet")
                except Exception:
                    sheet = {}
                if _valid_worksheet(sheet):
                    break
            if not _valid_worksheet(sheet):
                sheet = lce_adaptations.get("worksheet") or _fallback_worksheet(
                    context, merged["vocabulary"]
                )
                worksheet_fallback = True
        if (
            grounding_mode != "uploaded_source"
            and (knowledge.get("external_enrichment") or {}).get("status")
            == "available"
        ):
            sheet = enrich_worksheet_with_official_bank(sheet, knowledge)
        merged["worksheet"] = _apply_v3_output_contract(
            sheet,
            key="worksheet",
            valid_source_refs=source_refs,
            fallback_used="source_extractive" if worksheet_fallback else "none",
        )

        step("Creating lesson adaptations (parallel)…", 0.30)
        by_id = {s["id"]: s for s in ADAPTATION_SPECS}
        total = len(LESSON_KEYS)
        done = 0

        def _lce_or_generate(key: str, baseline: dict | None = None) -> tuple[dict, str]:
            """Prefer LCE composition; fall back to Educational Editor LLM / source fallback."""
            candidate = lce_adaptations.get(key) or {}
            classroom = key in CLASSROOM_LESSON_KEYS
            if _valid_lesson(candidate, classroom=classroom) or (
                key == "parent" and candidate.get("sections") and candidate.get("big_idea")
            ):
                return candidate, "lce"
            try:
                _, lesson = _generate_one_lesson(
                    api_key,
                    key,
                    by_id.get(key, {}).get("title", key),
                    by_id.get(key, {}).get("hint", ""),
                    user_prompt,
                    baseline,
                    suppress_ai_diagrams=suppress_ai_diagrams,
                )
            except Exception:
                lesson = {}
            if not _valid_lesson(lesson, classroom=classroom):
                if candidate:
                    return candidate, "lce_recovery"
                return (
                    _source_fallback_lesson(key, universal_profile, source_refs),
                    "classroom_source_fallback",
                )
            return lesson, "none"

        baseline_lesson, baseline_fallback = _lce_or_generate("standard")
        merged["standard"] = _apply_v3_output_contract(
            inject_verified_visuals_into_lesson(baseline_lesson, preferred),
            key="standard",
            valid_source_refs=source_refs,
            fallback_used=baseline_fallback,
        )
        done = 1
        step(f"Lesson adaptations… {done}/{total} complete", 0.30 + (0.65 * done / total))

        other_keys = [k for k in LESSON_KEYS if k != "standard"]
        # Prefer LCE for all keys first (no extra LLM). Only call LLM for gaps.
        pending_llm = []
        for key in other_keys:
            candidate = lce_adaptations.get(key) or {}
            classroom = key in CLASSROOM_LESSON_KEYS
            parent_ok = key == "parent" and candidate.get("sections") and candidate.get("big_idea")
            if _valid_lesson(candidate, classroom=classroom) or parent_ok:
                merged[key] = _apply_v3_output_contract(
                    inject_verified_visuals_into_lesson(candidate, preferred),
                    key=key,
                    valid_source_refs=source_refs,
                    fallback_used="lce",
                )
                done += 1
                step(
                    f"Lesson adaptations… {done}/{total} complete",
                    0.30 + (0.65 * done / total),
                )
            else:
                pending_llm.append(key)

        if pending_llm:
            with ThreadPoolExecutor(max_workers=MAX_PARALLEL_LESSONS) as pool:
                futures = {
                    pool.submit(
                        _generate_one_lesson,
                        api_key,
                        key,
                        by_id.get(key, {}).get("title", key),
                        by_id.get(key, {}).get("hint", ""),
                        user_prompt,
                        baseline_lesson,
                        suppress_ai_diagrams=suppress_ai_diagrams,
                    ): key
                    for key in pending_llm
                }
                for future in as_completed(futures):
                    key = futures[future]
                    fallback_used = "none"
                    retry_history: list[dict] = []
                    try:
                        _, lesson = future.result()
                    except Exception:
                        lesson = lce_adaptations.get(key) or _source_fallback_lesson(
                            key, universal_profile, source_refs
                        )
                        fallback_used = "classroom_source_fallback"
                        retry_history.append(
                            {
                                "attempts": 2,
                                "status": "failed",
                                "recovery": fallback_used,
                            }
                        )
                    if not _valid_lesson(
                        lesson, classroom=key in CLASSROOM_LESSON_KEYS
                    ):
                        lesson = lce_adaptations.get(key) or _source_fallback_lesson(
                            key, universal_profile, source_refs
                        )
                        fallback_used = "lce_recovery" if key in lce_adaptations else "classroom_source_fallback"
                    merged[key] = _apply_v3_output_contract(
                        inject_verified_visuals_into_lesson(lesson, preferred),
                        key=key,
                        valid_source_refs=source_refs,
                        fallback_used=fallback_used,
                        retry_history=retry_history,
                    )
                    done += 1
                    step(
                        f"Lesson adaptations… {done}/{total} complete",
                        0.30 + (0.65 * done / total),
                    )

        # Final LCE authorship polish (vocabulary upgrade + distinct adaptive versions)
        try:
            from engines.lesson_composition_engine import attach_lce_to_adaptations

            step("LCE editorial polish…", 0.88)
            # Merge LCE-only adaptive versions (ADHD / Autism / Dyslexia) even when
            # not in the default generate=True product set.
            for extra_key in ("adhd", "autism", "dyslexia"):
                candidate = lce_adaptations.get(extra_key)
                if isinstance(candidate, dict) and (
                    candidate.get("sections") or candidate.get("big_idea")
                ):
                    merged[extra_key] = _apply_v3_output_contract(
                        inject_verified_visuals_into_lesson(candidate, preferred),
                        key=extra_key,
                        valid_source_refs=source_refs,
                        fallback_used="lce",
                    )
            merged = attach_lce_to_adaptations(
                merged, lesson_text=lesson_text, reject_on_fail=False
            )
        except Exception as lce_attach_exc:  # noqa: BLE001
            merged.setdefault("_meta", {})
            merged["_meta"]["lce_attach_error"] = str(lce_attach_exc)[:300]

        # Hard QA publish gate
        from engines.qa.pipeline import validate_lesson_package
        from knowledge.service import inject_exam_practice_into_lessons

        # Attach exam practice for classroom tabs: official bank when available,
        # otherwise practice-from-source from the uploaded profile claims.
        merged = inject_exam_practice_into_lessons(
            merged, knowledge, universal_profile=universal_profile
        )
        merged["_meta"]["knowledge"] = knowledge
        merged["_meta"]["source_envelope"] = source_envelope
        merged["_meta"]["universal_profile"] = universal_profile
        merged["_meta"]["grounding_mode"] = grounding_mode
        merged["_meta"]["curriculum_reference_notice"] = (
            (knowledge.get("external_enrichment") or {}).get("citation_notice")
            or ""
        )
        for output_key in OUTPUT_KEYS:
            if output_key not in merged and output_key not in {
                "vocabulary",
                "worksheet",
            }:
                merged[output_key] = _source_fallback_lesson(
                    output_key, universal_profile, source_refs
                )
            if isinstance(merged.get(output_key), dict):
                contract = (merged[output_key].get("_contract") or {})
                merged[output_key] = _apply_v3_output_contract(
                    merged[output_key],
                    key=output_key,
                    valid_source_refs=source_refs,
                    fallback_used=str(contract.get("fallback_used") or "none"),
                    retry_history=contract.get("retry_history") or [],
                )

        # A diagram question must always include the exact diagram students are
        # asked to label. Build it deterministically from the completed,
        # source-grounded standard lesson instead of trusting model-authored SVG.
        worksheet = merged.get("worksheet") or {}
        diagram_question = worksheet.get("diagram_question") or {}
        if isinstance(worksheet, dict) and isinstance(diagram_question, dict):
            from study_diagram_builder import resolve_study_diagram_svg

            diagram_question["question"] = (
                "Study the source-grounded concept organiser below. Redraw it "
                "and label each main idea accurately."
            )
            diagram_question["svg_diagram"] = resolve_study_diagram_svg(
                merged.get("standard") or {}
            )
            diagram_question["model_answer"] = (
                "A correct response reproduces the organiser and labels the "
                "main ideas exactly as shown."
            )
            diagram_question["alt_text"] = (
                f"Labelled concept organiser for "
                f"{universal_profile.get('topic') or 'the uploaded lesson'}."
            )
            worksheet["diagram_question"] = diagram_question

        # Keep Computation Layer provenance attached before QA. Chapter-cache reuse
        # must not leave the publish gate comparing a different artifact set.
        verified_exact_values = []
        for artifact in stem.get("artifacts") or []:
            if not artifact.get("ok"):
                continue
            payload = artifact.get("payload") or {}
            for field_name in (
                "exact",
                "balanced",
                "balanced_equation",
                "solutions",
            ):
                value = payload.get(field_name)
                if value not in (None, "", [], {}):
                    verified_exact_values.append(
                        {
                            "task_kind": artifact.get("task_kind"),
                            "field": field_name,
                            "value": value,
                            "latex": artifact.get("latex") or "",
                        }
                    )
        merged["_meta"]["engine_artifacts"] = stem.get("artifacts") or []
        merged["_meta"]["verified_exact_values"] = verified_exact_values

        package_qa = validate_lesson_package(
            artifacts=stem["artifacts"],
            preferred_visuals=preferred,
            knowledge=knowledge,
            adaptations=merged,
            grounding_mode=grounding_mode,
            source_envelope=source_envelope,
        )
        merged["_meta"]["publish_qa"] = {
            "passed": package_qa.passed,
            "checks": package_qa.checks,
            "blocked_reason": package_qa.blocked_reason,
            "publish_blocked": package_qa.publish_blocked,
            "scorecard": getattr(package_qa, "scorecard", {}) or {},
        }
        if package_qa.publish_blocked:
            # Keep stem_qa aligned with hard gate
            merged["_meta"]["stem_qa"] = {
                **(merged["_meta"].get("stem_qa") or {}),
                "passed": False,
                "publish_blocked": True,
                "blocked_reason": package_qa.blocked_reason,
            }

        # EATS — post-pipeline educational acceptance (non-breaking; engines untouched)
        try:
            from eats import attach_eats_to_adaptations

            ctx = (merged.get("_meta") or {}).get("lesson_context") or {}
            merged = attach_eats_to_adaptations(
                merged,
                subject=str(ctx.get("subject") or ""),
                topic=str(ctx.get("topic") or ""),
                auto_revise=True,
                capture_screenshots=False,
            )
        except Exception:
            merged.setdefault("_meta", {})["eats_error"] = "acceptance_attach_failed"

        step("Done!", 1.0)
        try:
            from engines.universal_lesson_intelligence.pipeline import (
                finalize_lesson_bundle,
                is_uli_pipeline_enabled,
            )

            if is_uli_pipeline_enabled():
                finalize_lesson_bundle(
                    merged,
                    lesson_text=lesson_text,
                    source_envelope=source_envelope,
                )
        except Exception:
            merged.setdefault("_meta", {})["lesson_bundle_error"] = "finalize_failed"
    except Exception as error:
        raise RuntimeError(
            "Adaptation generation could not complete after safe fallbacks."
        ) from error

    return merged


def quality_report(adaptations: dict) -> dict:
    vocab = _coerce_dict(adaptations.get("vocabulary", {}))
    sheet = _coerce_dict(adaptations.get("worksheet", {}))
    ctx = (adaptations.get("_meta") or {}).get("lesson_context", {})
    lesson_ok = sum(
        1
        for k in LESSON_KEYS
        if _valid_lesson(
            _coerce_dict(adaptations.get(k, {})),
            classroom=k in CLASSROOM_LESSON_KEYS,
        )
    )
    stem_qa = (adaptations.get("_meta") or {}).get("stem_qa") or {}
    publish_qa = (adaptations.get("_meta") or {}).get("publish_qa") or {}
    stem_passed = stem_qa.get("passed", True)
    publish_blocked = bool(
        publish_qa.get("publish_blocked") or stem_qa.get("publish_blocked")
    )
    stem_artifacts = len((adaptations.get("_meta") or {}).get("engine_artifacts") or [])
    preferred_n = len((adaptations.get("_meta") or {}).get("preferred_visuals") or [])
    biology_n = len((adaptations.get("_meta") or {}).get("biology_figures") or [])
    knowledge = (adaptations.get("_meta") or {}).get("knowledge") or {}
    rag_hits = len(knowledge.get("rag_hits") or [])
    official_mcqs = len(knowledge.get("official_mcqs") or [])
    uli_meta = (adaptations.get("_meta") or {}).get("uli") or {}
    uli_certification = uli_meta.get("certification") if uli_meta.get("enabled") else None
    uli_quality_score = uli_meta.get("quality_score") if uli_meta.get("enabled") else None
    base_exam_ready = (
        _valid_vocabulary(vocab)
        and _valid_worksheet(sheet)
        and lesson_ok >= len(LESSON_KEYS) - 2
    )
    return {
        "pages_analyzed": ctx.get("chunks_processed", 1),
        "source_chars": ctx.get("source_char_count", 0),
        "objectives_found": len(ctx.get("learning_objectives") or []),
        "concepts_found": len(ctx.get("key_concepts") or []),
        "vocab_terms": len(vocab.get("word_wall") or []),
        "worksheet_short_q": len(sheet.get("short_answer") or []),
        "worksheet_long_q": len(sheet.get("long_answer") or []),
        "lessons_complete": lesson_ok,
        "lessons_total": len(LESSON_KEYS),
        "stem_artifacts": stem_artifacts,
        "stem_verified": stem_passed and not publish_blocked,
        "verified_visuals": preferred_n,
        "biology_figures": biology_n,
        "rag_citations": rag_hits,
        "official_mcqs": official_mcqs,
        "knowledge_pilot": knowledge.get("pilot_id"),
        "publish_blocked": publish_blocked,
        "publish_blocked_reason": publish_qa.get("blocked_reason")
        or stem_qa.get("blocked_reason"),
        "exam_ready": base_exam_ready and stem_passed and not publish_blocked,
        "adaptations_ready": base_exam_ready,
        "uli_enabled": bool(uli_meta.get("enabled")),
        "uli_certification": uli_certification,
        "uli_quality_score": uli_quality_score,
    }
