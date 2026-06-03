"""
Read and validate OpenAI API keys from .env (handles common formatting mistakes).
"""

from pathlib import Path

from config import ENV_PATH

# Example/placeholder values that must never be sent to OpenAI
PLACEHOLDER_MARKERS = (
    "your-key-here",
    "your-real-key",
    "sk-your-",
    "paste-your-key",
)


def is_placeholder_key(value: str) -> bool:
    """Return True if the value is an example key, not a real one."""
    if not value:
        return True
    lower = value.strip().lower()
    return any(marker in lower for marker in PLACEHOLDER_MARKERS)


def is_valid_openai_key(value: str) -> bool:
    """Return True when the string looks like a real OpenAI API key."""
    cleaned = (value or "").strip()
    return cleaned.startswith("sk-") and len(cleaned) >= 20 and not is_placeholder_key(cleaned)


def read_api_key_from_env_file() -> str:
    """
    Read OPENAI_API_KEY from .env.

    Supports:
    - OPENAI_API_KEY=sk-...
    - A lone sk-... line (common copy/paste mistake)
    """
    if not ENV_PATH.exists():
        return ""

    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        candidate = ""
        if stripped.startswith("OPENAI_API_KEY="):
            candidate = stripped.split("=", 1)[1].strip().strip('"').strip("'")
        elif stripped.startswith("sk-"):
            candidate = stripped

        if is_valid_openai_key(candidate):
            return candidate

    return ""
