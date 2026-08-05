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


def _idea_fingerprint(idea: str) -> str:
    """Normalise teaching prose for clone detection."""
    text = re.sub(r"[^a-z0-9\s]", " ", (idea or "").lower())
    text = re.sub(r"\s+", " ", text).strip()
    return text[:96]


def dedupe_lesson_wall(
    wall: list[Mapping[str, str]] | None,
    *,
    min_idea_words: int = 6,
) -> list[dict[str, str]]:
    """Drop empty / recycled cards so the wall teaches distinct ideas."""
    out: list[dict[str, str]] = []
    seen_titles: set[str] = set()
    seen_ideas: set[str] = set()
    for card in wall or []:
        if not isinstance(card, dict):
            continue
        title = str(card.get("title") or "").strip()
        idea = str(card.get("idea") or card.get("body") or "").strip()
        if not title or not idea or len(idea.split()) < min_idea_words:
            continue
        tkey = title.lower()
        ikey = _idea_fingerprint(idea)
        if tkey in seen_titles:
            continue
        if ikey and ikey in seen_ideas:
            continue
        # Near-clone: share a long common prefix with an existing card.
        if any(
            ikey[:48] == prev[:48]
            for prev in seen_ideas
            if len(ikey) >= 48 and len(prev) >= 48
        ):
            continue
        seen_titles.add(tkey)
        if ikey:
            seen_ideas.add(ikey)
        row = dict(card)
        row["title"] = title
        row["idea"] = idea
        out.append(row)
    return out


def apply_wall_definitions_to_vocab(
    vocabulary: Mapping[str, Any] | None,
    wall: list[Mapping[str, str]] | None,
) -> dict[str, Any]:
    """Force word-wall definitions to reuse Lesson Wall teaching text."""
    page = dict(vocabulary or {})
    cards = list(wall or [])
    if not cards:
        return page
    wall_rows = wall_vocab_terms(cards)
    by_term = {
        str(r.get("term") or "").strip().lower(): r
        for r in wall_rows
        if str(r.get("term") or "").strip()
    }
    word_wall = []
    for row in page.get("word_wall") or []:
        if not isinstance(row, dict):
            continue
        item = dict(row)
        key = str(item.get("term") or "").strip().lower()
        match = by_term.get(key)
        if not match:
            for wkey, wrow in by_term.items():
                if key and (key in wkey or wkey in key):
                    match = wrow
                    break
        if match:
            defn = str(match.get("definition") or match.get("lesson_context") or "")
            ctx = str(match.get("lesson_context") or defn)
            if defn:
                item["definition"] = defn
                item["simple_explanation"] = defn
                item["academic_definition"] = defn
                item["lesson_context"] = ctx
                item["example"] = item.get("example") or ctx
                item["source"] = "lesson_wall"
        word_wall.append(item)
    # Ensure wall terms appear even if vocab composer dropped them.
    have = {str(r.get("term") or "").strip().lower() for r in word_wall}
    for wrow in wall_rows:
        key = str(wrow.get("term") or "").strip().lower()
        if key and key not in have:
            word_wall.append(dict(wrow, source="lesson_wall"))
            have.add(key)
        if len(word_wall) >= 12:
            break
    page["word_wall"] = word_wall[:12]
    page["lesson_wall"] = [dict(c) for c in cards]
    return page


def ensure_shared_lesson_wall(
    adaptations: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """Repair-first: stamp the Master Lesson Wall onto every adaptation page.

    Downstream polish (PQLE / fidelity) sometimes rebuilds lens pages without
    copying ``lesson_wall``. Missing stamps must never quarantine a teachable
    Master — re-attach the shared wall before the confidence gate runs.
    """
    if not isinstance(adaptations, dict):
        return []
    wall = adaptations.get("_lesson_wall")
    if not isinstance(wall, list) or not wall:
        std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
        wall = std.get("lesson_wall") if isinstance(std.get("lesson_wall"), list) else []
    if not isinstance(wall, list) or not wall:
        try:
            std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
            wall = extract_lesson_wall(std)
        except Exception:
            wall = []
    wall = dedupe_lesson_wall(wall if isinstance(wall, list) else [])
    if not wall:
        return []
    adaptations["_lesson_wall"] = [dict(c) for c in wall]
    for key, page in list(adaptations.items()):
        if str(key).startswith("_") or not isinstance(page, dict):
            continue
        page = dict(page)
        page["lesson_wall"] = [dict(c) for c in wall]
        adaptations[key] = page
    return wall


def wall_surface_parity_issues(
    wall: list[Mapping[str, str]] | None,
    *,
    vocabulary: Mapping[str, Any] | None = None,
    worksheet: Mapping[str, Any] | None = None,
    narration: str = "",
    min_cards: int = 3,
) -> list[str]:
    """Phase 1: vocab / exam / voice must say the same science as the wall."""
    cards = dedupe_lesson_wall(wall)
    issues: list[str] = []
    if len(cards) < min_cards:
        issues.append(
            f"Lesson Wall is too thin (need at least {min_cards} teachable cards)."
        )
    ideas = [str(c.get("idea") or "") for c in cards]
    wall_tok = {t for t in re.findall(r"[a-z]{4,}", " ".join(ideas).lower())}
    if vocabulary and wall_tok:
        vocab = vocabulary if isinstance(vocabulary, dict) else {}
        vblob = " ".join(
            f"{r.get('term') or ''} {r.get('definition') or ''} {r.get('lesson_context') or ''}"
            for r in (vocab.get("word_wall") or [])
            if isinstance(r, dict)
        )
        vtok = {t for t in re.findall(r"[a-z]{4,}", vblob.lower())}
        if vblob and len(wall_tok & vtok) < 2:
            issues.append("Vocabulary does not reuse Lesson Wall teaching language.")

    if worksheet and wall_tok:
        sheet = worksheet if isinstance(worksheet, dict) else {}
        long_blob = " ".join(
            str(r.get("model_answer") or "")
            for r in (sheet.get("long_answer") or [])
            if isinstance(r, dict)
        )
        if long_blob:
            ltok = {t for t in re.findall(r"[a-z]{4,}", long_blob.lower())}
            if len(wall_tok & ltok) < 2:
                issues.append("Exam long answers do not reuse Lesson Wall teaching language.")
            if not any(
                str(r.get("source") or "") == "lesson_wall"
                for r in (sheet.get("long_answer") or [])
                if isinstance(r, dict)
            ):
                issues.append("Exam long answers are not sourced from the Lesson Wall.")

    if narration and wall_tok:
        ntok = {t for t in re.findall(r"[a-z]{4,}", narration.lower())}
        if len(wall_tok & ntok) < 2:
            issues.append("Reading narration does not reuse Lesson Wall teaching language.")
    return issues
