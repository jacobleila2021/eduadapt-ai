"""
OpenAI integration — generates AdaptEd AI–aligned adaptations plus vocabulary & worksheet.
"""

import json
import os

from openai import APIStatusError, OpenAI, RateLimitError

from adaptation_specs import ADAPTATION_SPECS, OUTPUT_KEYS
from config import MAX_LESSON_CHARS, ENV_PATH
from secrets_helper import is_valid_openai_key, read_api_key_from_env_file, reload_env

BATCH_SIZE = 6


def _batch_keys(keys: list, size: int = BATCH_SIZE) -> list:
    return [keys[i : i + size] for i in range(0, len(keys), size)]


def _get_model() -> str:
    reload_env()
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def _spec_hints(keys: list) -> str:
    by_id = {s["id"]: s for s in ADAPTATION_SPECS}
    lines = []
    for key in keys:
        spec = by_id.get(key, {})
        lines.append(f"- **{key}** ({spec.get('title', key)}): {spec.get('hint', '')}")
    return "\n".join(lines)


def _build_system_prompt(keys: list) -> str:
    return f"""You are AdaptEd AI (EduAdapt backend), an expert instructional designer for neurodiverse learners.

Given a lesson, produce differentiated versions aligned with the AdaptEd AI platform.
Preserve all learning objectives and curriculum accuracy. Each version must be classroom-ready markdown.

Adaptation types to generate in this request:
{_spec_hints(keys)}

Return ONLY valid JSON with exactly these keys: {", ".join(keys)}
Each value must be a single markdown-formatted string with headings, bullets, and clear structure.
Do not omit any key."""


def _build_user_prompt(lesson_text: str) -> str:
    trimmed = lesson_text[:MAX_LESSON_CHARS]
    if len(lesson_text) > MAX_LESSON_CHARS:
        trimmed += "\n\n[Lesson truncated for processing. Adapt what is shown.]"
    return f"Adapt this lesson:\n\n{trimmed}"


def get_effective_api_key(override_api_key: str = "") -> str:
    """
    Resolve API key: .env file first, then session input, then environment variable.
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


def _call_openai(client: OpenAI, keys: list, lesson_text: str) -> dict:
    response = client.chat.completions.create(
        model=_get_model(),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _build_system_prompt(keys)},
            {"role": "user", "content": _build_user_prompt(lesson_text)},
        ],
        temperature=0.7,
        max_tokens=8000,
    )
    raw_content = response.choices[0].message.content
    if not raw_content:
        raise ValueError("OpenAI returned an empty response.")
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise ValueError("Could not parse AI response as JSON.") from error

    result = {}
    for key in keys:
        result[key] = parsed.get(key, "_No content generated for this section._")
    return result


def generate_adaptations(lesson_text: str, override_api_key: str = "") -> dict:
    """
    Call OpenAI to generate all adaptations in batches (18 AI outputs).

    Returns:
        Dictionary mapping adaptation id to markdown string.
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
        for batch in _batch_keys(OUTPUT_KEYS):
            merged.update(_call_openai(client, batch, lesson_text))
    except Exception as error:
        raise RuntimeError(format_openai_error(error)) from error

    return merged
