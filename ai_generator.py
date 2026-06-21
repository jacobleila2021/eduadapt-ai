"""
OpenAI integration — structured adaptations, vocabulary, and worksheet generation.
"""

import json
import os

from openai import APIStatusError, OpenAI, RateLimitError

from adaptation_specs import ADAPTATION_SPECS, OUTPUT_KEYS
from config import MAX_LESSON_CHARS, ENV_PATH
from secrets_helper import is_valid_openai_key, read_api_key_from_env_file, reload_env

BATCH_SIZE = 4
LESSON_KEYS = [k for k in OUTPUT_KEYS if k not in ("vocabulary", "worksheet")]


def _batch_keys(keys: list, size: int = BATCH_SIZE) -> list:
    return [keys[i : i + size] for i in range(0, len(keys), size)]


def _get_model() -> str:
    reload_env()
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def _trim_lesson(lesson_text: str) -> str:
    trimmed = lesson_text[:MAX_LESSON_CHARS]
    if len(lesson_text) > MAX_LESSON_CHARS:
        trimmed += "\n\n[Lesson truncated for processing. Adapt what is shown.]"
    return trimmed


def _parse_response(raw: str, keys: list) -> dict:
    if not raw:
        raise ValueError("OpenAI returned an empty response.")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("Could not parse AI response as JSON.") from error

    result = {}
    for key in keys:
        value = parsed.get(key)
        if value is None:
            result[key] = "_No content generated for this section._"
        else:
            result[key] = value
    return result


def _chat(client: OpenAI, system: str, user: str, max_tokens: int = 8000) -> str:
    response = client.chat.completions.create(
        model=_get_model(),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.6,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response.")
    return content


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
            "OpenAI rejected the API key (401). Create a new key at "
            "https://platform.openai.com/api-keys and update .env or sidebar, then retry. "
            f"Key file: {ENV_PATH}"
        )
    return f"OpenAI request failed: {error}"


def _lesson_system_prompt(keys: list) -> str:
    by_id = {s["id"]: s for s in ADAPTATION_SPECS}
    hints = "\n".join(
        f"- **{k}** ({by_id[k]['title']}): {by_id[k]['hint']}" for k in keys if k in by_id
    )
    return f"""You are AdaptEd AI, an expert instructional designer.

Adapt the lesson for each key below. Return ONLY valid JSON with exactly these keys: {", ".join(keys)}

Each key's value MUST be an object (not a string) with this structure:
{{
  "big_idea": "one clear sentence",
  "mermaid_diagram": "valid mermaid flowchart syntax WITHOUT code fences",
  "svg_diagram": "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='180'>...</svg> with teal #008C95 and navy #0B2E59 fills and text labels",
  "sections": [
    {{"title": "Introduction", "body": "content", "box": "teal"}},
    {{"title": "Explain", "body": "content", "box": "blue"}},
    {{"title": "Practice", "body": "content", "box": "green"}},
    {{"title": "Check", "body": "content", "box": "orange"}}
  ],
  "visual_summary": [{{"icon": "🔵", "color_name": "Blue", "idea": "short label"}}]
}}

Adaptation hints:
{hints}

Include real lesson content in sections — not placeholders."""


def _vocabulary_system_prompt() -> str:
    return """You are AdaptEd AI. Build a standalone vocabulary study page from the lesson.

Return ONLY valid JSON with this exact structure:
{
  "topic": "lesson topic title",
  "word_wall": [
    {"term": "...", "definition": "simple student definition", "emoji": "💧", "visual_description": "vivid picture to imagine"}
  ],
  "flashcards": [{"front": "term", "back": "definition + example sentence"}],
  "picture_words": [{"term": "...", "color_cue": "blue arrow", "draw_this": "what to sketch", "label": "label on diagram"}],
  "practice": [{"term": "...", "pronunciation": "...", "syllables": "...", "sentence_blank": "The ___ moves upward."}],
  "self_test": {
    "matching_prompt": "Match letters to numbers: A. term1 ... 1. definition ...",
    "fill_blanks": ["sentence with ___ blank"]
  },
  "reference_chart": [{"term": "...", "definition": "...", "synonym": "...", "exam_tip": "..."}],
  "mermaid_diagram": "flowchart TD linking all terms to main concept"
}

Requirements:
- 10 to 12 word_wall terms from the lesson
- Every section must be filled with real content
- Do not omit any key"""


def _worksheet_system_prompt(vocab_terms: list) -> str:
    terms = ", ".join(vocab_terms[:12]) if vocab_terms else "key lesson terms"
    return f"""You are AdaptEd AI. Build an exam-ready worksheet from the lesson.

Use these vocabulary terms in Part D: {terms}

Return ONLY valid JSON with this exact structure:
{{
  "header": {{"subject": "...", "topic": "...", "time_allowed": "45 minutes", "total_marks": 30}},
  "short_answer": [{{"question": "...", "marks": 2, "lines": 3}}],
  "long_answer": [{{"question": "...", "marks": 6, "lines": 8}}],
  "diagram_question": {{
    "question": "Label the diagram...",
    "marks": 4,
    "svg_diagram": "<svg xmlns='http://www.w3.org/2000/svg' width='280' height='160'>simple outline</svg>"
  }},
  "vocab_questions": [{{"question": "Use [term] in a sentence explaining...", "marks": 1}}],
  "student_checklist": ["Read all questions first", "Allow 3 min per mark for long answers", "..."],
  "teacher_differentiation": "markdown text: which questions for dyslexia, ADHD, ELL, gifted",
  "answer_key": [{{"question_ref": "Part A Q1", "model_answer": "...", "marks_notes": "1 mark for..."}}]
}}

Requirements:
- 6 short_answer questions, 3 long_answer questions, 5 vocab_questions
- Real exam-style questions aligned to lesson objectives
- Do not omit any key"""


def _generate_lessons(client: OpenAI, lesson_text: str) -> dict:
    merged = {}
    user = f"Adapt this lesson:\n\n{_trim_lesson(lesson_text)}"
    for batch in _batch_keys(LESSON_KEYS):
        raw = _chat(client, _lesson_system_prompt(batch), user)
        merged.update(_parse_response(raw, batch))
    return merged


def _generate_vocabulary(client: OpenAI, lesson_text: str) -> dict:
    user = f"Extract and teach vocabulary from this lesson:\n\n{_trim_lesson(lesson_text)}"
    raw = _chat(client, _vocabulary_system_prompt(), user, max_tokens=6000)
    parsed = json.loads(raw)
    return parsed


def _generate_worksheet(client: OpenAI, lesson_text: str, vocabulary: dict) -> dict:
    terms = [w.get("term", "") for w in vocabulary.get("word_wall") or [] if w.get("term")]
    user = f"Create exam worksheet for this lesson:\n\n{_trim_lesson(lesson_text)}"
    raw = _chat(client, _worksheet_system_prompt(terms), user, max_tokens=6000)
    return json.loads(raw)


def generate_adaptations(lesson_text: str, override_api_key: str = "") -> dict:
    """
    Generate lesson adaptations, vocabulary, and worksheet (separate focused API calls).
    """
    api_key = get_effective_api_key(override_api_key)
    if not api_key:
        raise ValueError(
            f"OpenAI API key not found. Add it in the sidebar or edit {ENV_PATH} — "
            "line 1 must be: OPENAI_API_KEY=sk-your-key"
        )

    client = OpenAI(api_key=api_key)
    merged = {}

    try:
        merged.update(_generate_lessons(client, lesson_text))
        merged["vocabulary"] = _generate_vocabulary(client, lesson_text)
        merged["worksheet"] = _generate_worksheet(
            client, lesson_text, merged["vocabulary"]
        )
    except Exception as error:
        raise RuntimeError(format_openai_error(error)) from error

    return merged
