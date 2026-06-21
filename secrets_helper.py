"""
Read and validate OpenAI API keys from .env and session input.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"

PLACEHOLDER_MARKERS = (
    "your-key-here",
    "your-real-key",
    "sk-your-",
    "paste-your-key",
)


def reload_env() -> None:
    """Reload .env so a new key is picked up without restarting."""
    load_dotenv(dotenv_path=ENV_PATH, override=True)


def is_placeholder_key(value: str) -> bool:
    """Return True if the value is an example key, not a real one."""
    if not value:
        return True
    lower = value.strip().lower()
    return any(marker in lower for marker in PLACEHOLDER_MARKERS)


def is_valid_openai_key(value: str) -> bool:
    """Return True when the string looks like a real OpenAI API key."""
    cleaned = (value or "").strip()
    return (
        cleaned.startswith("sk-")
        and len(cleaned) >= 20
        and not is_placeholder_key(cleaned)
    )


def _normalize_key(key: str) -> str:
    """Fix common paste mistakes (double dash, hidden whitespace)."""
    if key.startswith("sk-proj--"):
        key = "sk-proj-" + key[len("sk-proj--") :]
    return "".join(key.split())


def read_api_key_from_env_file() -> str:
    """
    Read OPENAI_API_KEY from .env.

    Supports OPENAI_API_KEY=sk-... or a lone sk-... line.
    """
    reload_env()
    key = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    if is_valid_openai_key(key):
        return _normalize_key(key)

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
            return _normalize_key(candidate)

    return ""


def read_api_key() -> str:
    """Alias used by ai_generator — always reads from .env first."""
    return read_api_key_from_env_file()
