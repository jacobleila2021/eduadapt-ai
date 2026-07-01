"""
OpenAI integration — chunked long-lesson analysis, parallel adaptations, validated JSON.
"""

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
from config import ENV_PATH, MAX_LESSON_CHARS
from lesson_processor import build_lesson_context, context_to_prompt
from secrets_helper import is_valid_openai_key, read_api_key_from_env_file, reload_env

LESSON_KEYS = [k for k in OUTPUT_KEYS if k not in ("vocabulary", "worksheet")]
MAX_PARALLEL_LESSONS = 4

DEPTH_RULES = """
DEPTH REQUIREMENTS (critical):
- Cover EVERY learning objective and key concept from the lesson analysis.
- Do NOT compress a long lesson into one page. Each lesson adaptation needs 6–10 sections.
- Each section body: minimum 80 words with concrete facts, examples, and steps.
- Students must be able to pass an exam using ONLY this material.
- Include worked examples where the subject requires them.
- DIAGRAM-FIRST: every adaptation MUST include mermaid_diagram AND svg_diagram.
- MERMAID: flowchart/mindmap of the whole lesson process or classification (4+ labelled nodes).
- SVG STUDY DIAGRAM: svg_diagram MUST be valid inline SVG with xmlns, width 720+, height 400+, at least 6 <text> labels naming REAL lesson parts (e.g. "Meristematic tissue", "Xylem", "Evaporation"). Use #0B2E59 and #008C95. Include grouped boxes, arrows, and bullet facts — never a single circle or decorative art.
- SECTION TITLES in sections[] MUST match the labels used in svg_diagram so the Study Diagram aligns with lesson content.
- ACCURACY: all diagram and content facts must be scientifically and historically correct.
- Each learner version must be MEASURABLY DIFFERENT: reading level, structure, vocabulary, layout, diagram density.
"""

DIFFERENTIATION_RULES = """
DIFFERENTIATION (minimum 80% unique from standard version):
- ADHD: short 2-minute chunks, checkpoints, movement breaks, numbered steps only.
- Autism Support: predictable routine, literal language, calm transitions, same color pattern every section.
- Visual Learner: 2+ diagrams, minimal prose, icon labels, color-coded stages.
- Auditory Learner: listen-and-repeat scripts, call-and-response, audio chunk headers.
- Neurodiversity Support: simplified vocabulary (Grade 3-4), reduced cognitive load, one idea per section.
- Dyslexia: bullet points, bold keywords, extra white space cues, no dense paragraphs.
"""


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


def _lesson_prompt(adaptation_id: str, title: str, hint: str) -> str:
    return f"""You are EduAdapt AI. Create ONE comprehensive lesson adaptation.

Return ONLY valid JSON with a single top-level key "{adaptation_id}" whose value is an object:
{{
  "big_idea": "clear summary sentence",
  "mermaid_diagram": "flowchart TD with 4+ nodes, valid mermaid, no code fences",
  "svg_diagram": "<svg xmlns='http://www.w3.org/2000/svg' width='720' height='480'>grouped labelled boxes with arrows and 6+ <text> labels from THIS lesson</svg>",
  "sections": [
    {{"title": "Introduction", "body": "80+ words", "box": "teal"}},
    {{"title": "Core Concept 1", "body": "80+ words with facts", "box": "blue"}},
    {{"title": "Core Concept 2", "body": "80+ words", "box": "blue"}},
    {{"title": "Examples", "body": "worked examples", "box": "green"}},
    {{"title": "Practice", "body": "questions with answers", "box": "green"}},
    {{"title": "Exam Focus", "body": "what to revise for tests", "box": "orange"}},
    {{"title": "Summary", "body": "recap all key points", "box": "orange"}}
  ],
  "visual_summary": [
    {{"icon": "🟦", "color_name": "Topic", "idea": "..."}},
    {{"icon": "🟩", "color_name": "Concept", "idea": "..."}},
    {{"icon": "🟨", "color_name": "Example", "idea": "..."}},
    {{"icon": "🟪", "color_name": "Vocabulary", "idea": "..."}},
    {{"icon": "🟥", "color_name": "Assessment", "idea": "..."}}
  ]
}}

Adaptation: {title}
Guidance: {hint}

{DEPTH_RULES}
{DIFFERENTIATION_RULES}"""


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
- SHORT answers (Part A) model_answer = 1–2 sentences MAX. Never a paragraph.
- LONG answers (Part B) model_answer = full paragraph, minimum 5 complete sentences, detailed and age-appropriate.
- Provide a model_answer for EVERY question AND a matching answer_key entry for Part A, Part B, Part D (refs like "Part A Q1", "Part B Q1", "Part D Q1").
- Answers must be factually correct and drawn from the lesson analysis.

Requirements:
- 8 short_answer, 4 long_answer (exam-level), 6 vocab_questions
- Questions must test ALL major concepts from the lesson analysis
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


def _valid_lesson(lesson: dict) -> bool:
    sections = lesson.get("sections") or []
    has_diagram = bool(lesson.get("mermaid_diagram") or lesson.get("svg_diagram"))
    return bool(lesson.get("big_idea")) and len(sections) >= 3 and has_diagram


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
                "example": f"We learned about {term} in {context.get('topic', 'today\u2019s lesson')}.",
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
                "question": f"Explain: {fact[:120]}",
                "marks": 2,
                "lines": 4,
            }
        )
    if len(short) < 4:
        short.extend(
            [
                {"question": "Name two key ideas from this topic.", "marks": 2, "lines": 3},
                {"question": "Why is this topic important?", "marks": 2, "lines": 3},
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
            },
            {
                "question": "How would you apply these concepts in a real-world situation?",
                "marks": 6,
                "lines": 8,
            },
        ],
        "diagram_question": {
            "question": "Draw and label a diagram for this topic.",
            "marks": 4,
            "svg_diagram": "",
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
            {"question_ref": "Part A Q1", "model_answer": "See lesson objectives.", "marks_notes": "2 marks"}
        ],
    }


def _generate_one_lesson(
    api_key: str, key: str, title: str, hint: str, user_prompt: str, baseline: dict | None = None
) -> tuple:
    client = OpenAI(api_key=api_key)
    raw = _chat(client, _lesson_prompt(key, title, hint), user_prompt, max_tokens=7000)
    lesson = _extract_key(raw, key)
    if not _valid_lesson(lesson):
        raw = _chat(client, _lesson_prompt(key, title, hint), user_prompt, max_tokens=7000)
        lesson = _extract_key(raw, key)
    if baseline and key not in ("standard", "vocabulary", "worksheet"):
        score = _adaptation_difference_score(baseline, lesson)
        if score < 0.80:
            retry_prompt = user_prompt + f"\n\nIMPORTANT: Previous output was only {score:.0%} different from standard. Regenerate with clearly distinct structure, reading level, and diagrams for {title}."
            raw = _chat(client, _lesson_prompt(key, title, hint), retry_prompt, max_tokens=7000)
            lesson = _extract_key(raw, key)
    return key, lesson


def generate_adaptations(
    lesson_text: str,
    override_api_key: str = "",
    on_progress=None,
) -> dict:
    """Full pipeline with progress callbacks for Streamlit UI."""
    api_key = get_effective_api_key(override_api_key)
    if not api_key:
        raise ValueError(
            f"OpenAI API key not found. Add it in the sidebar or edit {ENV_PATH}."
        )

    client = OpenAI(api_key=api_key)
    model = _get_model()
    merged = {}

    def step(message: str, fraction: float) -> None:
        if on_progress:
            on_progress(message, fraction)

    try:
        step("Analyzing full lesson (all pages)…", 0.05)
        context = build_lesson_context(client, lesson_text, model)
        merged["_meta"] = {"lesson_context": context}
        user_prompt = context_to_prompt(context, lesson_text[:MAX_LESSON_CHARS])

        step("Building vocabulary study page…", 0.15)
        vocab = {}
        for _ in range(2):
            raw = _chat(client, _vocabulary_prompt(), user_prompt, max_tokens=7000)
            vocab = _extract_key(raw, "vocabulary")
            if _valid_vocabulary(vocab):
                break
        if not _valid_vocabulary(vocab):
            vocab = _fallback_vocabulary(context)
        merged["vocabulary"] = _sanitize_vocabulary(vocab)

        step("Building exam worksheet…", 0.25)
        terms = [w.get("term", "") for w in merged["vocabulary"].get("word_wall") or []]
        sheet = {}
        for _ in range(2):
            raw = _chat(client, _worksheet_prompt(terms), user_prompt, max_tokens=7000)
            sheet = _extract_key(raw, "worksheet")
            if _valid_worksheet(sheet):
                break
        if not _valid_worksheet(sheet):
            sheet = _fallback_worksheet(context, merged["vocabulary"])
        merged["worksheet"] = sheet

        step("Creating lesson adaptations (parallel)…", 0.30)
        by_id = {s["id"]: s for s in ADAPTATION_SPECS}
        total = len(LESSON_KEYS)
        done = 0

        std_spec = by_id.get("standard", {})
        _, baseline_lesson = _generate_one_lesson(
            api_key,
            "standard",
            std_spec.get("title", "standard"),
            std_spec.get("hint", ""),
            user_prompt,
            None,
        )
        merged["standard"] = baseline_lesson
        done = 1
        step(f"Lesson adaptations… {done}/{total} complete", 0.30 + (0.65 * done / total))

        other_keys = [k for k in LESSON_KEYS if k != "standard"]
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
                ): key
                for key in other_keys
            }
            for future in as_completed(futures):
                key, lesson = future.result()
                merged[key] = lesson
                done += 1
                step(
                    f"Lesson adaptations… {done}/{total} complete",
                    0.30 + (0.65 * done / total),
                )

        step("Done!", 1.0)
    except Exception as error:
        raise RuntimeError(format_openai_error(error)) from error

    return merged


def quality_report(adaptations: dict) -> dict:
    vocab = _coerce_dict(adaptations.get("vocabulary", {}))
    sheet = _coerce_dict(adaptations.get("worksheet", {}))
    ctx = (adaptations.get("_meta") or {}).get("lesson_context", {})
    lesson_ok = sum(
        1 for k in LESSON_KEYS if _valid_lesson(_coerce_dict(adaptations.get(k, {})))
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
        "exam_ready": (
            _valid_vocabulary(vocab)
            and _valid_worksheet(sheet)
            and lesson_ok >= len(LESSON_KEYS) - 2
        ),
    }
