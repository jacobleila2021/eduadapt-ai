"""
Local analytics for lesson complexity, reading level, and objectives.
Uses text statistics so teachers get instant feedback before AI generation.
Prefers explicit Class/Grade labels from the filename or lesson text over
raw Flesch–Kincaid when a curriculum grade is stated (e.g. Class 8 PDF).
"""

from __future__ import annotations

import re

import textstat

# Explicit curriculum labels beat readability estimates for Indian board PDFs.
_GRADE_PATTERNS = (
    # "Grade 6", "Class VI", and lesson-plan style "Grade Level: 6"
    r"(?i)\b(?:class|grade|std\.?|standard)\s*(?:level)?\s*[-–:]?\s*([0-9]{1,2})\b",
    r"(?i)\b(?:class|grade|std\.?|standard)\s*(?:level)?\s*[-–:]?\s*([IVXLC]{1,6})\b",
    r"(?i)\b(?:year|yr\.?)\s*([0-9]{1,2})\b",
)

_ROMAN = {
    "i": 1,
    "ii": 2,
    "iii": 3,
    "iv": 4,
    "v": 5,
    "vi": 6,
    "vii": 7,
    "viii": 8,
    "ix": 9,
    "x": 10,
    "xi": 11,
    "xii": 12,
}


def _roman_or_int(token: str) -> int | None:
    raw = (token or "").strip().lower()
    if not raw:
        return None
    if raw.isdigit():
        n = int(raw)
        return n if 1 <= n <= 12 else None
    return _ROMAN.get(raw)


def detect_stated_grade(*sources: str) -> int | None:
    """Return Class/Grade 1–12 when the upload name or lesson text states it."""
    for source in sources:
        text = source or ""
        if not text.strip():
            continue
        # Prefer filename-style hits in the first 400 chars + full name separately
        for pattern in _GRADE_PATTERNS:
            for match in re.finditer(pattern, text):
                grade = _roman_or_int(match.group(1))
                if grade is not None:
                    return grade
    return None


def count_learning_objectives(text: str) -> int:
    """
    Estimate how many learning objectives appear in the lesson.

    Looks for numbered objectives, bullet lists with action verbs,
    and common section headings teachers use.

    Args:
        text: Full lesson text.

    Returns:
        Estimated count of learning objectives (minimum 1 if lesson exists).
    """
    if not text.strip():
        return 0

    patterns = [
        r"(?im)^\s*(?:objective|learning goal|learning outcome|swbat|students will)\b",
        r"(?im)^\s*\d+[\.\)]\s*(?:students will|learners will|i can|we will)\b",
        r"(?im)^\s*[-•*]\s*(?:students will|learners will|understand|explain|analyze|describe)\b",
    ]

    matches = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            matches.add(match.start())

    # Fallback: count sentences with strong instructional verbs
    if not matches:
        verb_pattern = (
            r"\b(explain|describe|identify|compare|analyze|evaluate|"
            r"create|demonstrate|apply|summarize|predict)\b"
        )
        sentences = re.split(r"[.!?]+", text)
        verb_hits = sum(1 for s in sentences if re.search(verb_pattern, s, re.I))
        return max(1, min(verb_hits, 8))

    return max(1, len(matches))


def compute_lesson_complexity_score(text: str) -> int:
    """
    Calculate a 0–100 complexity score using readability and structure.

    Higher scores mean more challenging lessons for typical Grades 3–11.

    Args:
        text: Full lesson text.

    Returns:
        Integer score from 0 to 100.
    """
    if not text.strip():
        return 0

    words = textstat.lexicon_count(text, removepunct=True)
    sentences = max(textstat.sentence_count(text), 1)
    syllables = textstat.syllable_count(text)

    avg_word_length = sum(len(w) for w in text.split()) / max(words, 1)
    avg_sentence_length = words / sentences
    syllables_per_word = syllables / max(words, 1)

    # Weighted blend of structural difficulty signals
    raw = (
        min(avg_word_length / 8, 1.0) * 30
        + min(avg_sentence_length / 25, 1.0) * 35
        + min(syllables_per_word / 2, 1.0) * 20
        + min(textstat.flesch_kincaid_grade(text) / 12, 1.0) * 15
    )

    return int(round(min(100, max(0, raw))))


def estimate_reading_level(text: str, *, source_name: str = "") -> str:
    """
    Return a teacher-friendly reading level label.

    Prefer an explicit Class/Grade from the filename or lesson text
    (e.g. "Exploring Science Class 8.pdf" → Grade 8). Fall back to
    Flesch–Kincaid only when no curriculum grade is stated.

    Args:
        text: Full lesson text.
        source_name: Original upload filename when available.

    Returns:
        String like "Grade 6" or "College level".
    """
    if not text.strip() and not (source_name or "").strip():
        return "N/A"

    stated = detect_stated_grade(source_name or "", text[:4000] if text else "")
    if stated is not None:
        return f"Grade {stated}"

    if not text.strip():
        return "N/A"

    grade = textstat.flesch_kincaid_grade(text)
    grade_rounded = max(1, round(grade))

    if grade_rounded <= 12:
        return f"Grade {grade_rounded}"
    return "College level"


def build_analytics_report(text: str, *, source_name: str = "") -> dict:
    """
    Bundle all analytics into one dictionary for the UI.

    Args:
        text: Extracted lesson text.
        source_name: Upload filename used to resolve Class/Grade labels.

    Returns:
        Dict with complexity_score, reading_level, and objective_count.
    """
    stated = detect_stated_grade(source_name or "", (text or "")[:4000])
    return {
        "complexity_score": compute_lesson_complexity_score(text),
        "reading_level": estimate_reading_level(text, source_name=source_name),
        "objective_count": count_learning_objectives(text),
        "grade_source": "document_label" if stated is not None else "readability",
        "stated_grade": stated,
    }
