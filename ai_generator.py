"""
OpenAI integration — one focused call per output, full lesson analysis, validated JSON.
"""

import json
import os

from openai import APIStatusError, OpenAI, RateLimitError

from adaptation_specs import ADAPTATION_SPECS, OUTPUT_KEYS
from config import ENV_PATH, MAX_LESSON_CHARS
from lesson_processor import build_lesson_context, context_to_prompt
from secrets_helper import is_valid_openai_key, read_api_key_from_env_file, reload_env

LESSON_KEYS = [k for k in OUTPUT_KEYS if k not in ("vocabulary", "worksheet")]

DEPTH_RULES = """
DEPTH REQUIREMENTS (critical):
- Cover EVERY learning objective and key concept from the lesson analysis.
- Do NOT compress a long lesson into one page. Each lesson adaptation needs 6–10 sections.
- Each section body: minimum 80 words with concrete facts, examples, and steps.
- Students must be able to pass an exam using ONLY this material.
- Include worked examples where the subject requires them.
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
    """Turn API value into dict — handles double-encoded JSON strings."""
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
        # Wrap plain markdown as lesson structure
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
    if isinstance(error, APIStatusError) and error.status_code == 401:
        return (
            "OpenAI rejected the API key (401). Update key in sidebar or Streamlit Secrets. "
            f"Key file: {ENV_PATH}"
        )
    return f"OpenAI request failed: {error}"


def _lesson_prompt(adaptation_id: str, title: str, hint: str) -> str:
    return f"""You are AdaptEd AI. Create ONE comprehensive lesson adaptation.

Return ONLY valid JSON with a single top-level key "{adaptation_id}" whose value is an object:
{{
  "big_idea": "clear summary sentence",
  "mermaid_diagram": "flowchart TD with 4+ nodes, valid mermaid, no code fences",
  "svg_diagram": "<svg xmlns='http://www.w3.org/2000/svg' width='320' height='200'>labeled shapes in #008C95 and #0B2E59</svg>",
  "sections": [
    {{"title": "Introduction", "body": "80+ words", "box": "teal"}},
    {{"title": "Core Concept 1", "body": "80+ words with facts", "box": "blue"}},
    {{"title": "Core Concept 2", "body": "80+ words", "box": "blue"}},
    {{"title": "Examples", "body": "worked examples", "box": "green"}},
    {{"title": "Practice", "body": "questions with answers", "box": "green"}},
    {{"title": "Exam Focus", "body": "what to revise for tests", "box": "orange"}},
    {{"title": "Summary", "body": "recap all key points", "box": "orange"}}
  ],
  "visual_summary": [{{"icon": "🔵", "color_name": "Blue", "idea": "label"}}]
}}

Adaptation: {title}
Guidance: {hint}

{DEPTH_RULES}"""


def _vocabulary_prompt() -> str:
    return f"""You are AdaptEd AI. Build a complete vocabulary study page from the lesson analysis.

Return ONLY valid JSON with top-level key "vocabulary":
{{
  "topic": "...",
  "word_wall": [{{"term": "...", "definition": "...", "emoji": "...", "visual_description": "..."}}],
  "flashcards": [{{"front": "...", "back": "..."}}],
  "picture_words": [{{"term": "...", "color_cue": "...", "draw_this": "...", "label": "..."}}],
  "practice": [{{"term": "...", "pronunciation": "...", "syllables": "...", "sentence_blank": "..."}}],
  "self_test": {{"matching_prompt": "...", "fill_blanks": ["..."]}},
  "reference_chart": [{{"term": "...", "definition": "...", "synonym": "...", "exam_tip": "..."}}],
  "mermaid_diagram": "flowchart TD ..."
}}

Requirements: 12–15 word_wall terms, ALL sections filled, real content from lesson.
{DEPTH_RULES}"""


def _worksheet_prompt(terms: list) -> str:
    term_list = ", ".join(terms[:15]) if terms else "lesson vocabulary"
    return f"""You are AdaptEd AI. Build a rigorous exam worksheet.

Vocabulary terms to use: {term_list}

Return ONLY valid JSON with top-level key "worksheet":
{{
  "header": {{"subject": "...", "topic": "...", "time_allowed": "45-60 minutes", "total_marks": 40}},
  "short_answer": [{{"question": "...", "marks": 2, "lines": 4}}],
  "long_answer": [{{"question": "...", "marks": 8, "lines": 10}}],
  "diagram_question": {{"question": "...", "marks": 5, "svg_diagram": "<svg ...></svg>"}},
  "vocab_questions": [{{"question": "...", "marks": 2}}],
  "student_checklist": ["..."],
  "teacher_differentiation": "...",
  "answer_key": [{{"question_ref": "Part A Q1", "model_answer": "...", "marks_notes": "..."}}]
}}

Requirements:
- 8 short_answer, 4 long_answer (exam-level), 6 vocab_questions
- Questions must test ALL major concepts from the lesson analysis
- Model answers detailed enough for marking
{DEPTH_RULES}"""


def _extract_key(raw: str, key: str) -> dict:
    parsed = json.loads(raw)
    value = parsed.get(key)
    if value is None:
        raise ValueError(f"AI response missing '{key}' key.")
    return _coerce_dict(value)


def _valid_vocabulary(vocab: dict) -> bool:
    return bool(vocab.get("word_wall")) and len(vocab.get("word_wall") or []) >= 5


def _valid_worksheet(sheet: dict) -> bool:
    return bool(sheet.get("short_answer")) and len(sheet.get("short_answer") or []) >= 4


def _valid_lesson(lesson: dict) -> bool:
    sections = lesson.get("sections") or []
    return bool(lesson.get("big_idea")) and len(sections) >= 3


def generate_adaptations(lesson_text: str, override_api_key: str = "") -> dict:
    """
    Full pipeline: analyze long lessons, then one API call per output (validated).
    """
    api_key = get_effective_api_key(override_api_key)
    if not api_key:
        raise ValueError(
            f"OpenAI API key not found. Add it in the sidebar or edit {ENV_PATH}."
        )

    client = OpenAI(api_key=api_key)
    model = _get_model()
    merged = {}
    meta = {}

    try:
        context = build_lesson_context(client, lesson_text, model)
        meta["lesson_context"] = context
        user_prompt = context_to_prompt(context, lesson_text[:MAX_LESSON_CHARS])

        by_id = {s["id"]: s for s in ADAPTATION_SPECS}

        # Vocabulary first (worksheet depends on it)
        for attempt in range(2):
            raw = _chat(client, _vocabulary_prompt(), user_prompt, max_tokens=7000)
            vocab = _extract_key(raw, "vocabulary")
            if _valid_vocabulary(vocab):
                merged["vocabulary"] = vocab
                break
        if "vocabulary" not in merged:
            merged["vocabulary"] = vocab  # best effort

        # Worksheet
        terms = [w.get("term", "") for w in merged["vocabulary"].get("word_wall") or []]
        for attempt in range(2):
            raw = _chat(client, _worksheet_prompt(terms), user_prompt, max_tokens=7000)
            sheet = _extract_key(raw, "worksheet")
            if _valid_worksheet(sheet):
                merged["worksheet"] = sheet
                break
        if "worksheet" not in merged:
            merged["worksheet"] = sheet

        # One call per lesson adaptation (reliable JSON)
        for key in LESSON_KEYS:
            spec = by_id.get(key, {})
            raw = _chat(
                client,
                _lesson_prompt(key, spec.get("title", key), spec.get("hint", "")),
                user_prompt,
                max_tokens=7000,
            )
            lesson = _extract_key(raw, key)
            if not _valid_lesson(lesson):
                # Retry once
                raw = _chat(
                    client,
                    _lesson_prompt(key, spec.get("title", key), spec.get("hint", "")),
                    user_prompt,
                    max_tokens=7000,
                )
                lesson = _extract_key(raw, key)
            merged[key] = lesson

        merged["_meta"] = meta
    except Exception as error:
        raise RuntimeError(format_openai_error(error)) from error

    return merged


def quality_report(adaptations: dict) -> dict:
    """Summary shown to teacher after generation."""
    vocab = _coerce_dict(adaptations.get("vocabulary", {}))
    sheet = _coerce_dict(adaptations.get("worksheet", {}))
    ctx = (adaptations.get("_meta") or {}).get("lesson_context", {})
    lesson_ok = sum(
        1 for k in LESSON_KEYS
        if _valid_lesson(_coerce_dict(adaptations.get(k, {})))
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
