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
        "introduction",
        "extend",
        "stretch",
        "challenge",
    }
)

# Question stems / connector chrome must never become wall or vocab titles.
_JUNK_TITLE_RE = re.compile(
    r"(?i)^(?:"
    r"can you|do you|did you|have you|what (?:is|are|do|does)|"
    r"why (?:do|does|are|is)|how (?:do|does|are|is|can)|"
    r"name (?:some|the)|think of|look at|observe|"
    r"for example|this property|that property|reprint|"
    r"activity|caution|exercise|questions?|objectives?|"
    r"warm[\s-]?up|"
    # Textbook sentence fragments that OCR turns into "concept" titles
    r"in other words|in many practical|if one end|if the|if a|"
    r"when the|when a|when we|its si|its unit|solution we|"
    r"we are given|small quantities|one end of|as shown|as follows|"
    r"consider|suppose|let us|that is|therefore|hence|"
    r"in the next|on the other|to summarise|to summarize"
    r")\b"
)
_CHROME_TITLE_RE = re.compile(
    r"(?i)\b(?:reprint|ncert|cbse|\d{4}\s*[-–]\s*\d{2,4}|page\s*\d+)\b"
)
_FRAGMENT_TAIL_RE = re.compile(
    r"(?i)\b(it|the|a|an|of|to|for|and|or|we|is|are|that|this|these|those)$"
)
_PRONOUN_TITLE_RE = re.compile(r"(?i)^(its|this|that|these|those|our|their)\b")

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


def _recover_concept_from_idea(idea: str) -> str:
    """Best short concept name from a teaching sentence (definitional opener only)."""
    idea_l = _plain(idea)
    if not idea_l:
        return ""
    cm = re.match(
        r"(?i)^([A-Z][A-Za-z0-9][A-Za-z0-9'/\- ]{1,40}?)\s+(?:is|are|means)\b",
        idea_l,
    )
    if not cm:
        return ""
    cand = cm.group(1).strip()
    # Reject recovered fragments too ("In other words is…")
    if _JUNK_TITLE_RE.match(cand) or _PRONOUN_TITLE_RE.match(cand) or _FRAGMENT_TAIL_RE.search(cand):
        return ""
    if len(cand.split()) > 4:
        return ""
    return cand


def normalize_wall_title(title: str, *, idea: str = "") -> str:
    """Turn section chrome into a short teachable concept name (or '')."""
    raw = _plain(title)
    if not raw:
        return ""
    # "Understanding Evaporation" → "Evaporation"
    raw = re.sub(r"(?i)^(?:understanding|concept|idea|topic|section)\s*[:\-–]?\s*", "", raw).strip()
    raw = re.sub(r"(?i)^(?:worked example|practice|summary)\s*[:\-–]?\s*", "", raw).strip()
    # "Gold is Gold" / "X is X is …" titles
    m = re.match(r"(?i)^([A-Za-z][A-Za-z\- ]{1,40}?)\s+is\s+\1\b", raw)
    if m:
        raw = m.group(1).strip()
    low = raw.lower().rstrip(".?!")
    bad = (
        low in _NON_TERM_TITLES
        or bool(_JUNK_TITLE_RE.match(raw))
        or bool(_CHROME_TITLE_RE.search(raw))
        or bool(_PRONOUN_TITLE_RE.match(raw))
        or bool(_FRAGMENT_TAIL_RE.search(raw))
        or raw.endswith(("…", "..."))
        or bool(re.search(r"(?i)\b(ror|∝|\d+\.\d+)\b", raw))  # OCR maths debris
    )
    if bad:
        raw = _recover_concept_from_idea(idea)
        if not raw:
            return ""
    if raw.endswith("?"):
        return ""
    # Incomplete question cut mid-phrase ("Can you name some metals that")
    if re.search(r"(?i)\b(that|these|those|which|who)$", raw):
        return ""
    words = raw.split()
    # Real concept names are short noun phrases — not sentence openings.
    if len(words) > 5 or len(words) < 1:
        return ""
    # Reject titles that are clearly the start of a clause (capitalised mid-sentence OCR).
    if words[0].lower() in {"if", "when", "while", "because", "although", "since", "as"}:
        recovered = _recover_concept_from_idea(idea)
        return normalize_wall_title(recovered, idea="") if recovered else ""
    try:
        from engines.lesson_composition_engine.vocab_quality import is_junk_term

        if is_junk_term(raw):
            return ""
    except Exception:
        pass
    if raw.isupper() and len(raw) > 2:
        raw = raw.title()
    return raw[:1].upper() + raw[1:] if raw else ""


def clean_wall_idea(idea: str, *, title: str = "") -> str:
    """Repair duplicated 'X is X is …' and strip OCR chapter chrome."""
    text = _plain(idea)
    if not text:
        return ""
    # "Gold is Gold is the most ductile…" / "For example is (i) …"
    text = re.sub(
        r"(?i)\b([A-Za-z][A-Za-z\- ]{1,40}?)\s+is\s+\1\s+is\b",
        r"\1 is",
        text,
    )
    text = re.sub(r"(?i)^in other words is\s+", "", text)
    text = re.sub(r"(?i)^for example is\s+", "For example, ", text)
    text = re.sub(r"(?i)^extend is\s+extend is\s+", "", text)
    text = re.sub(r"(?i)^extend is\s+", "", text)
    text = re.sub(r"(?i)^solution we\b", "We", text)
    text = re.sub(r"(?i)\bRor\b", "R or", text)
    text = re.sub(r"(?i)\breprint\s+\d{4}.*$", "", text).strip()
    text = re.sub(r"(?i)\bI\s+n\s+Class\b", "In Class", text)
    # Drop unfinished equation debris / cut-off parentheses from OCR.
    if re.search(r"\(\d+\.\s*$", text) or re.search(r"(?i)=\s*ror\b", text):
        text = re.sub(r"\s*\(\d+\.?\s*$", "", text).strip()
        text = re.sub(r"(?i)\bror\b", "R or", text)
    # Incomplete worked-solution crumbs are not teaching cards.
    if re.match(r"(?i)^we are given\b", text) and len(text.split()) < 12:
        return ""
    # Drop pure question cards (wall teaches answers, not stems).
    if text.endswith("?") and len(text.split()) < 18:
        return ""
    if title and text.lower().startswith(title.lower()) and text.endswith("?"):
        return ""
    try:
        from engines.lesson_composition_engine.vocab_quality import (
            is_ocr_garbage_claim,
            is_teacher_facing_text,
            student_safe_definition,
        )

        if is_teacher_facing_text(text) or is_ocr_garbage_claim(text):
            return ""
        safe = student_safe_definition(text)
        if safe:
            text = safe
    except Exception:
        pass
    if len(text.split()) < 6:
        return ""
    if not text.endswith((".", "!", "?")):
        text += "."
    return text[:720]


def is_teachable_wall_card(card: Mapping[str, Any] | None) -> bool:
    if not isinstance(card, dict):
        return False
    title = normalize_wall_title(
        str(card.get("title") or ""),
        idea=str(card.get("idea") or card.get("body") or ""),
    )
    idea = clean_wall_idea(
        str(card.get("idea") or card.get("body") or ""),
        title=title,
    )
    return bool(title and idea)


def extract_lesson_wall(lesson: Mapping[str, Any] | None) -> list[dict[str, str]]:
    """Build wall cards from Master lesson sections (title + teaching idea)."""
    # Prefer a wall already attached (idempotent) — still scrub junk titles.
    existing = list((lesson or {}).get("lesson_wall") or [])
    if existing:
        out = []
        for row in existing:
            if not isinstance(row, dict):
                continue
            idea_raw = str(row.get("idea") or row.get("body") or "").strip()
            title = normalize_wall_title(str(row.get("title") or ""), idea=idea_raw)
            idea = clean_wall_idea(idea_raw, title=title)
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
            return dedupe_lesson_wall(out)[:12]

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
        title = normalize_wall_title(
            _plain(section.get("title") or f"Section {index + 1}"),
            idea=body,
        )
        if not title or title.lower().startswith("how you will learn"):
            continue
        idea = clean_wall_idea(body, title=title)
        if not idea:
            continue
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
    return dedupe_lesson_wall(items)


def wall_vocab_terms(wall: list[Mapping[str, str]], *, topic: str = "") -> list[dict[str, str]]:
    """Turn wall cards into vocabulary rows (definition = wall teaching text)."""
    del topic
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for card in wall:
        idea_raw = str(card.get("idea") or "").strip()
        title = normalize_wall_title(str(card.get("title") or ""), idea=idea_raw)
        idea = clean_wall_idea(idea_raw, title=title)
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


_MARK8_EXAMPLES = {
    "evaporation": "For example, a puddle dries up on a sunny day.",
    "condensation": "For example, tiny water droplets form on a cold glass.",
    "precipitation": "For example, rain falls from clouds onto the ground.",
    "collection": "For example, rainwater gathers in a lake, river, or ocean.",
    "transpiration": "For example, water vapour leaves a plant's leaves into the air.",
    "water cycle": "For example, ocean water evaporates, forms clouds, then returns as rain.",
    "electric current": "For example, current flows through a torch bulb when the switch is on.",
    "potential difference": "For example, a 1.5 V cell provides potential difference across a circuit.",
    "resistance": "For example, a longer wire has more resistance than a shorter wire of the same material.",
    "ohm's law": "For example, if resistance doubles at constant voltage, current halves.",
    "malleability": "For example, aluminium can be beaten into thin foil sheets.",
    "ductility": "For example, copper can be drawn into thin electrical wire.",
}

_MARK8_WHY = {
    "evaporation": "It puts water into the air as vapour so condensation and clouds can form later.",
    "condensation": "It forms tiny cloud droplets that can later fall as precipitation.",
    "precipitation": "It returns water from clouds to the Earth's surface so the cycle can continue.",
    "collection": "It stores water in rivers, lakes, and oceans so evaporation can start again.",
    "transpiration": "It adds water vapour from plants into the air, feeding the water cycle.",
    "electric current": "It is the flow that makes bulbs, heaters, and motors work in a circuit.",
    "potential difference": "It is the driving 'push' that sets charges in motion in a conductor.",
    "resistance": "It controls how much current flows for a given potential difference.",
    "ohm's law": "It links voltage, current, and resistance so circuit values can be calculated.",
}


def _dedupe_answer_sentences(parts: list[str]) -> list[str]:
    """Drop near-duplicate lines (vapour/vapor clones, bullet repeats)."""
    out: list[str] = []
    seen: set[str] = set()
    for part in parts:
        text = re.sub(r"^[\s•\-]+", "", str(part or "")).strip()
        if not text:
            continue
        key = re.sub(r"[^a-z0-9]+", " ", text.lower())
        key = key.replace("vapor", "vapour")
        key = re.sub(r"\s+", " ", key).strip()[:90]
        if not key or key in seen:
            continue
        # Near-clone: high token overlap with an existing sentence.
        toks = set(key.split())
        if any(
            toks
            and len(toks & set(prev.split())) / max(1, min(len(toks), len(set(prev.split()))))
            >= 0.78
            for prev in seen
        ):
            continue
        seen.add(key)
        if not text.endswith((".", "!", "?")):
            text += "."
        out.append(text)
    return out


def _mark8_answer(primary: Mapping[str, str], support: list[Mapping[str, str]], *, topic: str) -> str:
    """Focused 8-mark answer for ONE concept — never a dump of the whole wall."""
    del support  # other wall cards must not pollute this answer
    title = normalize_wall_title(
        str(primary.get("title") or ""),
        idea=str(primary.get("idea") or ""),
    )
    core = clean_wall_idea(str(primary.get("idea") or ""), title=title)
    if not title or not core:
        return ""
    key = title.lower()
    example = _MARK8_EXAMPLES.get(key, "")
    why = _MARK8_WHY.get(key, "")
    topic_bit = topic.strip() if topic else "this topic"
    parts = [
        core,
        example,
        why
        or (
            f"{title} matters in {topic_bit} because it is one of the key ideas "
            f"learners must explain with meaning and an everyday link."
        ),
    ]
    return " ".join(_dedupe_answer_sentences(parts))


def wall_long_answers(
    wall: list[Mapping[str, str]],
    *,
    topic: str = "",
    limit: int = 4,
) -> list[dict[str, Any]]:
    """8-mark exam answers built from teachable Lesson Wall cards."""
    cards: list[dict[str, str]] = []
    for card in wall or []:
        if not isinstance(card, dict):
            continue
        idea_raw = str(card.get("idea") or "").strip()
        title = normalize_wall_title(str(card.get("title") or ""), idea=idea_raw)
        idea = clean_wall_idea(idea_raw, title=title)
        if not title or not idea:
            continue
        if title.lower() in _NON_TERM_TITLES:
            continue
        cards.append({"title": title, "idea": idea})
    out: list[dict[str, Any]] = []
    for i, card in enumerate(cards):
        title = card["title"]
        answer = _mark8_answer(card, [], topic=topic)
        if not answer or len(answer.split()) < 20:
            continue
        display = title
        if title.lower() in {"water cycle", "electric current", "potential difference", "ohm's law"}:
            display = f"the {title}"
        if i == 1:
            prompt = (
                f"Apply {display} to one everyday situation. "
                f"State the meaning, give one example, and show each step."
            )
        else:
            prompt = (
                f"Explain {display}. "
                f"Give its meaning, one clear example, and why it matters"
                f"{f' in {topic}' if topic else ''}."
            )
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
    """Drop empty / recycled / junk-title cards so the wall teaches distinct ideas."""
    out: list[dict[str, str]] = []
    seen_titles: set[str] = set()
    seen_ideas: set[str] = set()
    for card in wall or []:
        if not isinstance(card, dict):
            continue
        idea_raw = str(card.get("idea") or card.get("body") or "").strip()
        title = normalize_wall_title(str(card.get("title") or ""), idea=idea_raw)
        idea = clean_wall_idea(idea_raw, title=title)
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


def seed_curriculum_wall_cards(topic: str = "", *, limit: int = 6) -> list[dict[str, str]]:
    """Fallback teachable cards from curated CBSE banks when OCR wall is junk."""
    from engines.lesson_composition_engine.vocab_quality import (
        ELECTRICITY_TERMS,
        METALS_NONMETALS_TERMS,
        WATER_CYCLE_TERMS,
    )

    topic_l = (topic or "").lower()
    bank: list[tuple[str, str]] = []
    if any(k in topic_l for k in ("water cycle", "evaporat", "precipitat", "condens")):
        bank = [(t, d) for t, d in WATER_CYCLE_TERMS if t.lower() != "water cycle"]
    elif any(k in topic_l for k in ("electric", "ohm", "circuit", "resistance", "current")):
        bank = list(ELECTRICITY_TERMS)
    elif any(k in topic_l for k in ("metal", "non-metal", "nonmetal", "malleab", "ductil")):
        bank = list(METALS_NONMETALS_TERMS)
    out: list[dict[str, str]] = []
    for i, (term, definition) in enumerate(bank[:limit]):
        title = normalize_wall_title(term, idea=definition)
        idea = clean_wall_idea(definition, title=title)
        if not title or not idea:
            continue
        out.append(
            {
                "title": title,
                "idea": idea,
                "hex": "#2563EB",
                "icon": f"{i + 1:02d}",
                "source": "curriculum_bank",
            }
        )
    return out


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
