"""
OpenAI integration for generating differentiated lesson versions.
"""

import json
import os

from openai import APIStatusError, OpenAI, RateLimitError

from config import MAX_LESSON_CHARS, OPENAI_MODEL
from secrets_helper import is_valid_openai_key, read_api_key_from_env_file


# Keys returned by the model (must match JSON schema in the prompt)
OUTPUT_KEYS = [
    "dyslexia_friendly",
    "adhd_friendly",
    "simplified",
    "advanced_learner",
    "english_language_learner",
    "classroom_activities",
    "teacher_notes",
]


def _build_system_prompt() -> str:
    """
    Instructions that tell GPT how to adapt lessons for diverse learners.
    """
    return """You are EduAdapt AI, an expert instructional designer for U.S. teachers (Grades 3–11).

Given a lesson, produce differentiated versions that are classroom-ready, accurate, and age-appropriate.

Guidelines:
- Dyslexia-Friendly: short paragraphs, bullet points, bold key terms, sans-serif-friendly spacing cues, avoid dense blocks.
- ADHD-Friendly: clear headings, numbered steps, frequent checkpoints, visual breaks, concise chunks.
- Simplified: lower vocabulary, shorter sentences, same core concepts.
- Advanced Learner: extension questions, deeper analysis, enrichment tasks.
- English Language Learner: visuals described in text, glossary, sentence frames, cognates where helpful.
- Classroom Activities: exactly THREE distinct, interactive activities (title + steps + materials + time estimate each).
- Teacher Notes: grouping suggestions, accommodation tips, assessment ideas, and quick differentiation moves.

Return ONLY valid JSON with these exact keys:
dyslexia_friendly, adhd_friendly, simplified, advanced_learner, english_language_learner, classroom_activities, teacher_notes

Each value must be a single markdown-formatted string."""


def _build_user_prompt(lesson_text: str) -> str:
    """
    Wrap the lesson text for the user message, with length guard.
    """
    trimmed = lesson_text[:MAX_LESSON_CHARS]
    if len(lesson_text) > MAX_LESSON_CHARS:
        trimmed += "\n\n[Lesson truncated for processing. Adapt what is shown.]"

    return f"Adapt this lesson:\n\n{trimmed}"


def get_effective_api_key(override_api_key: str = "") -> str:
    """
    Resolve the API key at runtime.

    Priority:
    1) Valid key from .env file (always wins over stale session values)
    2) Valid key passed by UI (session input)
    3) Valid OPENAI_API_KEY environment variable
    """
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
    """Return True if an OpenAI API key is configured."""
    return bool(get_effective_api_key(override_api_key))


def format_openai_error(error: Exception) -> str:
    """
    Turn OpenAI API errors into clear teacher-friendly messages.

    Args:
        error: Exception raised by the OpenAI client.

    Returns:
        Human-readable error text for the UI.
    """
    if isinstance(error, RateLimitError):
        return (
            "OpenAI rate limit (429): too many requests or not enough account credit. "
            "Wait 1–2 minutes, then try again. Check billing at "
            "https://platform.openai.com/account/billing"
        )

    if isinstance(error, APIStatusError) and error.status_code == 429:
        body = str(error.body).lower() if error.body else ""
        if "insufficient_quota" in body or "quota" in body:
            return (
                "OpenAI quota exceeded (429): add payment method or credits at "
                "https://platform.openai.com/account/billing then try again."
            )
        return (
            "OpenAI rate limit (429): wait 1–2 minutes and try again. "
            "If this keeps happening, check usage at "
            "https://platform.openai.com/usage"
        )

    return f"OpenAI request failed: {error}"


def generate_adaptations(lesson_text: str, override_api_key: str = "") -> dict:
    """
    Call OpenAI to generate all differentiated outputs in one request.

    Args:
        lesson_text: Extracted plain text from the uploaded lesson.

    Returns:
        Dictionary mapping output keys to markdown strings.

    Raises:
        ValueError: If API key is missing or the model returns invalid JSON.
        RuntimeError: If the OpenAI API call fails.
    """
    api_key = get_effective_api_key(override_api_key)
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Add OPENAI_API_KEY to your .env file."
        )

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": _build_user_prompt(lesson_text)},
            ],
            temperature=0.7,
        )
    except Exception as error:
        raise RuntimeError(format_openai_error(error)) from error

    raw_content = response.choices[0].message.content
    if not raw_content:
        raise ValueError("OpenAI returned an empty response.")

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise ValueError("Could not parse AI response as JSON.") from error

    result = {}
    for key in OUTPUT_KEYS:
        result[key] = parsed.get(key, "_No content generated for this section._")

    return result


# Explicit exports used by app.py
__all__ = ["generate_adaptations", "get_effective_api_key", "validate_api_key"]
