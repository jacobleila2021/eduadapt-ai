"""Lesson Wall — the Master teaching cards every learner must know.

The square tab boxes (concept cards) are the single source of truth for:
vocabulary, exam long answers, voice reading, and every adaptation.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

# Titles that are still useful teaching cards but should not become vocab "terms".
_NON_TERM_TITLES = frozenset(
    {
        "worked examples",
        "worked example",
        "common mistakes to avoid",
        "common mistakes",
        "common misconceptions",
        "quick revision",
        "what you have learnt",
        "must know",
        "big idea",
    }
)

_SKIP_ROLES = frozenset(
    {
        "practice_question",
        "exam_question",
        "hots_question",
        "assessment",
        "exit_ticket",
        "concept_primer",
    }
)

_KEEP_ROLES = frozenset(
    {
        "",
        "concept",
        "introduction",
        "worked_example",
        "summary",
        "revision",
        "real_life_example",
        "common_misconception",
    }
)


def _plain(text: str) -> str:
    raw = str(text or "")
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"[*_`#]+", "", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def extract_lesson_wall(lesson: Mapping[str, Any] | None) -> list[dict[str, str]]:
    """Build wall cards from Master lesson sections (title + teaching idea)."""
    # Prefer a wall already attached (idempotent).
    existing = list((lesson or {}).get("lesson_wall") or [])
    if existing:
        out = []
        for row in existing:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title") or "").strip()
            idea = str(row.get("idea") or row.get("body") or "").strip()
            if title and idea:
                out.append(
                    {
                        "title": title,
                        "idea": idea,
                        "hex": str(row.get("hex") or "#2563EB"),
                        "icon": str(row.get("icon") or ""),
                    }
                )
        if out:
            return out[:12]

    items: list[dict[str, str]] = []
    for index, section in enumerate((lesson or {}).get("sections") or []):
        if not isinstance(section, dict):
            continue
        role = str(section.get("role") or "").lower()
        if section.get("presentation_only") or role.startswith("presentation_"):
            continue
        if role.endswith("_support") or role in _SKIP_ROLES:
            continue
        if role not in _KEEP_ROLES and role:
            continue
        body = _plain(section.get("body") or "")
        title = _plain(section.get("title") or f"Section {index + 1}")
        # Drop lens cues / chrome titles
        if title.lower().startswith("how you will learn"):
            continue
        if not body or len(body.split()) < 8:
            continue
        idea = body
        if len(idea) > 720:
            idea = idea[:717].rsplit(" ", 1)[0] + "…"
        items.append(
            {
                "title": title,
                "idea": idea,
                "hex": str(section.get("hex") or "#2563EB"),
                "icon": f"{index + 1:02d}",
            }
        )
        if len(items) >= 12:
            break
    return items


def wall_vocab_terms(wall: list[Mapping[str, str]], *, topic: str = "") -> list[dict[str, str]]:
    """Turn wall cards into vocabulary rows (definition = wall teaching text)."""
    del topic
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for card in wall:
        title = str(card.get("title") or "").strip()
        idea = str(card.get("idea") or "").strip()
        if not title or not idea:
            continue
        low = title.lower().rstrip(".")
        if low in _NON_TERM_TITLES or low in seen:
            continue
        # Split "Evaporation and Transpiration" only when both halves are short terms.
        parts = re.split(r"\s+and\s+", title, maxsplit=1, flags=re.I)
        if len(parts) == 2 and all(1 <= len(p.split()) <= 3 for p in parts):
            # Keep the combined card as the study definition for each half if possible.
            for part in parts:
                term = part.strip(" .")
                key = term.lower()
                if not term or key in seen or key in _NON_TERM_TITLES:
                    continue
                # Prefer the sentence in the idea that mentions this term.
                defn = idea
                for sent in re.split(r"(?<=[.!?])\s+", idea):
                    if term.lower() in sent.lower():
                        defn = sent.strip()
                        break
                seen.add(key)
                rows.append(
                    {
                        "term": term,
                        "definition": defn,
                        "example": idea,
                        "lesson_context": idea,
                        "simple_explanation": defn,
                        "academic_definition": defn,
                    }
                )
            continue
        seen.add(low)
        # First sentence as crisp definition; full card as example/context.
        first = re.split(r"(?<=[.!?])\s+", idea)[0].strip()
        rows.append(
            {
                "term": title,
                "definition": first or idea,
                "example": idea,
                "lesson_context": idea,
                "simple_explanation": first or idea,
                "academic_definition": first or idea,
            }
        )
    return rows[:12]


def wall_long_answers(
    wall: list[Mapping[str, str]],
    *,
    topic: str = "",
    limit: int = 4,
) -> list[dict[str, Any]]:
    """8-mark exam answers taken verbatim from lesson-wall teaching text."""
    out: list[dict[str, Any]] = []
    for i, card in enumerate(wall):
        title = str(card.get("title") or "").strip()
        idea = str(card.get("idea") or "").strip()
        if not title or not idea:
            continue
        low = title.lower()
        if low in {"common mistakes to avoid", "common mistakes", "common misconceptions"}:
            continue
        if i == 1:
            prompt = (
                f"Apply '{title}' to one everyday situation from the lesson and "
                f"show each step."
            )
        else:
            prompt = f"Explain '{title}' in detail with examples from the lesson."
        answer = idea if idea.endswith((".", "!", "?")) else idea + "."
        out.append(
            {
                "question": prompt,
                "marks": 8,
                "lines": 10,
                "model_answer": answer,
                "bloom": "application" if i == 1 else "understanding",
                "source": "lesson_wall",
                "topic": topic,
            }
        )
        if len(out) >= limit:
            break
    return out


def wall_narration_text(wall: list[Mapping[str, str]]) -> str:
    """Voice reading = wall cards in order (what the learner needs to know)."""
    chunks: list[str] = []
    for card in wall:
        title = str(card.get("title") or "").strip()
        idea = str(card.get("idea") or "").strip()
        if not idea:
            continue
        if title and title.lower() not in idea.lower()[: len(title) + 8]:
            chunks.append(f"{title}. {idea}")
        else:
            chunks.append(idea)
    return " ".join(chunks)
