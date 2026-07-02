"""
Normalise lesson section titles — replace generic AI placeholders with real concept names.
"""

from __future__ import annotations

import re

GENERIC_TITLE_RE = re.compile(
    r"^(?:core\s+)?concept\s*#?\d+|section\s*\d+|part\s*\d+|topic\s*\d+|"
    r"key\s+idea\s*\d+|learning\s+point\s*\d+|idea\s*\d+|unit\s*\d+|"
    r"chapter\s*\d+|lesson\s*\d+|step\s*\d+|stage\s*\d+",
    re.I,
)


def normalize_section_title(title: str, body: str = "", index: int = 0) -> str:
    """Turn 'Core Concept 1' into a short, meaningful title from section content."""
    title = (title or "").strip()
    if title and not GENERIC_TITLE_RE.match(title):
        return _short_title(title)

    body = (body or "").strip()
    if body:
        for line in re.split(r"\n+", body):
            line = line.strip()
            if line.startswith(("- ", "* ", "• ")):
                candidate = line[2:].strip().split(".")[0]
                if len(candidate) > 8:
                    return _short_title(candidate)
        plain = re.sub(r"\s+", " ", body)
        first = re.split(r"(?<=[.!?])\s+", plain)[0].strip()
        if len(first) > 15:
            words = first.split()
            if len(words) > 8:
                return _short_title(" ".join(words[:7]))
            return _short_title(first.rstrip("."))

    if title:
        return _short_title(title)
    return f"Key Idea {index + 1}"


def _short_title(text: str, max_len: int = 42) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= max_len:
        return text
    trimmed = text[: max_len - 3].rsplit(" ", 1)[0]
    return trimmed.rstrip(".,;:-") + "..."
