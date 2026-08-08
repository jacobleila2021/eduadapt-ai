"""Dynamic teaching bank — build term→definition packs from every upload.

Phase 2 / R10–R11: subject-agnostic extraction so Alora is not limited to the
five hand-authored CBSE banks. Curated banks still win when they match;
this fills the gap for every other lesson — including question-heavy PDFs.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

from engines.lesson_composition_engine.vocab_quality import (
    is_junk_term,
    is_ocr_garbage_claim,
    is_teacher_facing_text,
    repair_ocr_prose,
    student_safe_definition,
)

# Definitional openers common in NCERT / textbooks.
# Note: use `{m,n}?` (lazy quantifier). `{m,n?}?` does not match in Python re.
_TERM = r"[A-Z][A-Za-z0-9][A-Za-z0-9/ \-]{1,48}?"
_DEF_PATTERNS = (
    re.compile(
        rf"(?m)^\s*(?P<term>{_TERM})\s+"
        r"(?P<verb>is|are|means|refers to|is called|are called)\s+"
        r"(?P<body>.{12,220}?)(?:\.|$)",
        re.I | re.M,
    ),
    re.compile(
        rf"(?m)^\s*(?P<term>{_TERM})\s*[:\-–]\s+"
        r"(?P<body>.{12,220}?)(?:\.|$)",
        re.I | re.M,
    ),
    re.compile(
        rf"(?m)^\s*(?P<term>{_TERM})\s+"
        r"(?P<verb>is the|are the|is a|are a|is an|are an)\s+"
        r"(?P<body>.{12,220}?)(?:\.|$)",
        re.I | re.M,
    ),
    # Process language: "Photosynthesis is the process by which…"
    re.compile(
        rf"(?m)^\s*(?P<term>{_TERM})\s+"
        r"(?P<verb>is the process by which|is a process in which|is the process of)\s+"
        r"(?P<body>.{12,220}?)(?:\.|$)",
        re.I | re.M,
    ),
)

_HEADING_RE = re.compile(
    rf"(?m)^(?:#{{1,3}}\s+|\d+\.\d+\s+|•\s*|[-*]\s*)?(?P<term>{_TERM})\s*$"
)

# Bullet / numbered glossaries: "• Force — a push or a pull"
_BULLET_DEF_RE = re.compile(
    rf"(?m)^\s*(?:[-•*]|\d+[.)])\s*(?P<term>{_TERM})\s*[-–—:]\s+(?P<body>.{{12,220}}?)(?:\.|$)",
    re.I | re.M,
)

# Formula teaching lines: "Ohm's law: V = IR" / "F = ma (Newton's second law)"
# Formula body excludes parentheses so notes stay in the note group.
_FORMULA_RE = re.compile(
    r"(?im)^\s*(?:(?P<label>[A-Z][A-Za-z0-9' /\-]{2,40}?)\s*[:\-–]\s*)?"
    r"(?P<formula>[A-Za-z][A-Za-z0-9]*\s*=\s*[A-Za-z0-9\^\*{}/\s\+\-]{1,40}?)"
    r"(?:\s*[\(\[](?P<note>[^\)\]]{4,60})[\)\]])?"
    r"(?=\s|$)"
)

_QUESTION_START_RE = re.compile(
    r"(?im)^\s*(?:\d+[.)]\s*|q(?:uestion)?\s*\d*[\s:.)-]|mcq\s*[:.)-])"
)

_CHROME_TERM_BITS = (
    "activity",
    "chapter",
    "caution",
    "exercise",
    "question",
    "objective",
    "students will",
    "learning outcome",
)


def _unwrap_soft_breaks(text: str) -> str:
    """Join textbook line-wraps so definition sentences stay intact."""
    raw = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"(?<![.!?])\n(?=[a-z])", " ", raw)


def _clean_term(raw: str) -> str:
    t = repair_ocr_prose(str(raw or "")).strip(" .:;,-–*'\"")
    t = re.sub(r"\s+", " ", t)
    if not t or is_junk_term(t) or len(t.split()) > 6:
        return ""
    low = t.lower()
    if any(k in low for k in _CHROME_TERM_BITS):
        return ""
    if low in {"what", "which", "who", "when", "where", "how", "why", "name", "define", "explain"}:
        return ""
    return t[:1].upper() + t[1:] if t else ""


def _clean_definition(term: str, body: str) -> str:
    text = student_safe_definition(repair_ocr_prose(body) or "")
    if not text or is_ocr_garbage_claim(text) or is_teacher_facing_text(text):
        return ""
    if term.lower() not in text.lower() and len(text.split()) < 8:
        text = f"{term} is {text[0].lower() + text[1:]}" if text else ""
    text = text.strip()
    if not text.endswith((".", "!", "?")):
        text += "."
    if len(text.split()) < 5:
        return ""
    # Reject activity / chrome definitions even if they passed earlier filters.
    low = text.lower()
    if any(
        k in low
        for k in (
            "for performing",
            "collect the samples",
            "in the next section",
            "students will",
            "not to be republished",
        )
    ):
        return ""
    return text[:320]


def _score_def(term: str, definition: str) -> int:
    low = definition.lower()
    needle = term.lower()
    score = 2
    if low.startswith(needle + " is ") or low.startswith(needle + " are "):
        score += 6
    if " means " in low[:60] or " is the " in low[:60] or "process by which" in low:
        score += 3
    if "=" in definition and len(definition) < 80:
        score += 2  # formula cards are high value
    if is_ocr_garbage_claim(definition) or is_teacher_facing_text(definition):
        return -10
    if len(definition.split()) >= 10:
        score += 1
    return score


def _put(
    found: dict[str, tuple[int, str]],
    term: str,
    definition: str,
    *,
    min_score: int = 4,
) -> None:
    if not term or not definition:
        return
    score = _score_def(term, definition)
    key = term.lower()
    prev = found.get(key)
    if score >= min_score and (not prev or score > prev[0]):
        found[key] = (score, definition)


def extract_formula_pairs(text: str) -> list[tuple[str, str]]:
    """Pull (name, teaching sentence) from formula lines."""
    raw = _unwrap_soft_breaks(text)
    out: list[tuple[str, str]] = []
    for m in _FORMULA_RE.finditer(raw):
        formula = re.sub(r"\s+", " ", (m.group("formula") or "").strip())
        if not formula or formula.count("=") != 1:
            continue
        # Skip prose equalities that aren't symbolic (too many words on right)
        left, right = formula.split("=", 1)
        if len(right.split()) > 6:
            continue
        label = _clean_term(m.group("label") or "")
        note = (m.group("note") or "").strip()
        if label:
            term = label
            body = f"{term} is written as {formula}"
            if note:
                body += f" ({note})"
        else:
            # Use left-hand symbol as term when safe (V, F, I, …)
            sym = left.strip()
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9']{0,12}", sym):
                continue
            term = sym
            body = f"{term} equals {right.strip()} in the relation {formula}"
            if note:
                body += f" ({note})"
        definition = _clean_definition(term, body)
        if definition:
            out.append((term, definition))
    return out


def extract_definitional_pairs(text: str) -> list[tuple[str, str]]:
    """Pull (term, definition) pairs from source prose."""
    raw = _unwrap_soft_breaks(text)
    if len(raw.strip()) < 40:
        return []
    found: dict[str, tuple[int, str]] = {}

    for pat in _DEF_PATTERNS:
        for m in pat.finditer(raw):
            term = _clean_term(m.group("term"))
            body = m.group("body") if "body" in m.groupdict() else ""
            verb = m.groupdict().get("verb") or "is"
            if not term:
                continue
            prefix = raw[max(0, m.start() - 12) : m.start()].lower()
            if re.search(r"(?:^|\n)\s*\d+[.)]\s*$|what\s+$|which\s+$|name\s+$", prefix):
                continue
            definition = _clean_definition(term, f"{term} {verb} {body}".strip())
            _put(found, term, definition)

    for m in _BULLET_DEF_RE.finditer(raw):
        term = _clean_term(m.group("term"))
        definition = _clean_definition(term, f"{term} is {m.group('body')}".strip())
        _put(found, term, definition, min_score=3)

    for term, definition in extract_formula_pairs(raw):
        _put(found, term, definition, min_score=3)

    # Heading + following sentence as weak definitions
    lines = raw.splitlines()
    for i, line in enumerate(lines):
        hm = _HEADING_RE.match(line.strip())
        if not hm:
            continue
        term = _clean_term(hm.group("term"))
        if not term or term.lower() in found:
            continue
        for j in range(i + 1, min(i + 4, len(lines))):
            nxt = lines[j].strip()
            if len(nxt.split()) < 6:
                continue
            if _QUESTION_START_RE.match(nxt):
                break
            definition = _clean_definition(
                term, nxt if term.lower() in nxt.lower() else f"{term}: {nxt}"
            )
            _put(found, term, definition, min_score=3)
            break

    ranked = sorted(found.items(), key=lambda kv: (-kv[1][0], kv[0]))
    out: list[tuple[str, str]] = []
    for key, (_score, definition) in ranked[:20]:
        m = re.match(rf"(?i)^({re.escape(key)})\b", definition)
        term = m.group(1) if m else key.title()
        out.append((term, definition))
    return out


def is_thin_source(text: str, *, claims: Iterable[str] | None = None) -> bool:
    """True when the upload is mostly questions / stems, not teaching prose."""
    raw = str(text or "")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if not lines and not claims:
        return True
    q_lines = sum(1 for ln in lines if _QUESTION_START_RE.match(ln) or ln.endswith("?"))
    prose_defs = len(extract_definitional_pairs(raw))
    claim_list = [str(c) for c in (claims or []) if str(c).strip()]
    claim_defs = sum(
        1
        for c in claim_list
        if re.search(r"(?i)\b(is|are|means)\b", c) and len(c.split()) >= 8
    )
    if prose_defs + claim_defs >= 3:
        return False
    if not lines:
        return claim_defs < 2
    return (q_lines / max(1, len(lines))) >= 0.45 or (q_lines >= 4 and prose_defs < 2)


def _term_from_question(prompt: str) -> str:
    """Best-effort concept name from a question stem."""
    p = str(prompt or "").strip()
    patterns = (
        r"(?i)^\s*(?:what|define|explain|describe|state)\s+(?:is|are|the\s+term)?\s*(.+?)[\?\.]?\s*$",
        r"(?i)^\s*(?:name|give)\s+(?:one|the)?\s*(.+?)[\?\.]?\s*$",
        r"(?i)^\s*(?:calculate|find|determine|solve)\s+(.+?)[\?\.]?\s*$",
        r"(?i)^\s*balance(?:\s+the\s+equation)?\s*[:\s]+(.+)$",
    )
    for pat in patterns:
        m = re.match(pat, p)
        if not m:
            continue
        cand = _clean_term(m.group(1))
        if cand:
            return cand
    # Fallback: longest capitalized token span
    m = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b", p)
    if m:
        return _clean_term(m.group(1))
    return ""


def bank_from_questions_and_engines(
    *,
    source_text: str = "",
    artifacts: Iterable[Mapping[str, Any]] | None = None,
    assessment_prompts: Iterable[Any] | None = None,
) -> list[dict[str, str]]:
    """Thin-source bank: question stems + verified EngineResult answers."""
    from engines.lesson_pipeline import format_engine_answer

    out: list[dict[str, str]] = []
    seen: set[str] = set()

    # 1) Verified STEM artifacts → teaching cards
    for art in artifacts or []:
        if not isinstance(art, dict) or not art.get("ok"):
            continue
        ans = format_engine_answer(art)
        if not ans:
            continue
        payload = art.get("payload") or {}
        stem = str(
            payload.get("input")
            or payload.get("equation")
            or payload.get("expression")
            or payload.get("problem")
            or art.get("task_kind")
            or "Result"
        ).strip()
        term = _term_from_question(stem)
        if not term and "=" in stem:
            term = _clean_term(stem.split("=", 1)[0].strip())
        if not term:
            kind = str(art.get("task_kind") or "Computation").replace("_", " ")
            # Prefer a unique label from the stem over a generic "Solve" clone.
            stem_bits = re.findall(r"[A-Za-z][A-Za-z0-9]{0,12}", stem)
            term = _clean_term(stem_bits[0] if stem_bits else kind) or kind.title()
        if term.lower() in seen:
            # Disambiguate duplicate symbols (V, I, …) with a short stem tag.
            tag = re.sub(r"[^A-Za-z0-9]+", " ", stem)[:28].strip()
            alt = _clean_term(f"{term} {tag}") if tag else ""
            if not alt or alt.lower() in seen:
                continue
            term = alt
        body = f"For {stem}, the verified answer is {ans}".strip()
        definition = _clean_definition(term, body)
        if not definition or len(definition.split()) < 4:
            definition = body if body.endswith(".") else body + "."
        seen.add(term.lower())
        out.append(
            {
                "term": term,
                "definition": definition[:320],
                "source": "thin_source_engine",
            }
        )

    # 2) Assessment / numbered questions → placeholder teaching cards from stem language
    prompts: list[str] = []
    for row in assessment_prompts or []:
        if isinstance(row, dict):
            prompts.append(str(row.get("prompt") or row.get("question") or ""))
        else:
            prompts.append(str(row))
    raw = str(source_text or "")
    for m in re.finditer(
        r"(?im)^\s*(?:\d+[.)]\s*|q(?:uestion)?\s*\d*[\s:.)-]+)\s*(.+)$",
        raw,
    ):
        prompts.append(m.group(1).strip())
    for line in raw.splitlines():
        if line.strip().endswith("?") and len(line.split()) >= 4:
            prompts.append(line.strip())

    for prompt in prompts:
        prompt = prompt.strip()
        if len(prompt.split()) < 4:
            continue
        term = _term_from_question(prompt)
        if not term or term.lower() in seen or is_junk_term(term):
            continue
        # Prefer an engine answer that matches this prompt
        matched_def = ""
        try:
            from engines.lesson_pipeline import match_artifact_to_prompt

            art = match_artifact_to_prompt(prompt, list(artifacts or []))
            if art:
                matched_def = format_engine_answer(art)
        except Exception:
            matched_def = ""
        if matched_def:
            definition = matched_def if matched_def.endswith(".") else matched_def + "."
        else:
            # Honest thin card: state what the learner must explain (not a fake fact).
            definition = (
                f"{term} is a key idea assessed in this lesson. "
                f"Use the source definition and one clear example when you answer."
            )
            # Skip hollow coaching cards — only keep if we later get a real def.
            continue
        seen.add(term.lower())
        out.append(
            {
                "term": term,
                "definition": definition[:320],
                "source": "thin_source_question",
            }
        )
        if len(out) >= 12:
            break
    return out[:12]


def build_dynamic_teaching_bank(
    *,
    topic: str = "",
    source_text: str = "",
    claims: Iterable[str] | None = None,
    concepts: Iterable[Any] | None = None,
    stem_artifacts: Iterable[Mapping[str, Any]] | None = None,
    assessment_prompts: Iterable[Any] | None = None,
) -> list[dict[str, str]]:
    """Build a per-upload teaching bank: [{term, definition, source}]."""
    blob_parts = [str(source_text or "")]
    for c in claims or []:
        blob_parts.append(str(c))
    for item in concepts or []:
        if isinstance(item, dict):
            name = str(item.get("name") or item.get("term") or "").strip()
            expl = str(item.get("explanation") or item.get("definition") or "").strip()
            if name and expl:
                blob_parts.append(f"{name} is {expl}")
            elif name:
                blob_parts.append(name)
        else:
            blob_parts.append(str(item))
    blob = "\n".join(p for p in blob_parts if p and str(p).strip())

    pairs = extract_definitional_pairs(blob)
    for claim in claims or []:
        text = student_safe_definition(str(claim or ""))
        if not text or is_ocr_garbage_claim(text):
            continue
        m = re.match(
            r"(?i)^([A-Z][A-Za-z0-9][A-Za-z0-9\-/ ]{1,40}?)\s+(is|are|means)\s+(.+)$",
            text.strip(),
        )
        if not m:
            continue
        term = _clean_term(m.group(1))
        definition = _clean_definition(term, text)
        if term and definition and not any(term.lower() == t.lower() for t, _ in pairs):
            pairs.append((term, definition))

    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for term, definition in pairs:
        key = term.lower()
        if key in seen or is_junk_term(term):
            continue
        if not student_safe_definition(definition):
            continue
        seen.add(key)
        out.append(
            {
                "term": term,
                "definition": definition,
                "source": "dynamic_upload_bank",
            }
        )
        if len(out) >= 12:
            break

    # Thin-source fill: questions + engines when prose bank is weak.
    if is_thin_source(source_text, claims=claims) or len(out) < 3:
        thin = bank_from_questions_and_engines(
            source_text=source_text,
            artifacts=stem_artifacts,
            assessment_prompts=assessment_prompts,
        )
        for row in thin:
            key = str(row.get("term") or "").lower()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(dict(row))
            if len(out) >= 12:
                break
    return out


def bank_as_term_tuples(bank: Iterable[Mapping[str, str]]) -> list[tuple[str, str]]:
    return [
        (str(row.get("term") or "").strip(), str(row.get("definition") or "").strip())
        for row in bank
        if str(row.get("term") or "").strip() and str(row.get("definition") or "").strip()
    ]


def definition_from_dynamic_bank(term: str, bank: Iterable[Mapping[str, str]] | None) -> str:
    key = (term or "").strip().lower()
    if not key or not bank:
        return ""
    aliases = {
        key,
        key.rstrip("s"),
        key + "s" if not key.endswith("s") else key,
        key.replace(" ", "-"),
        key.replace("-", " "),
    }
    for row in bank:
        name = str(row.get("term") or "").strip().lower()
        if name in aliases:
            defn = student_safe_definition(str(row.get("definition") or ""))
            if defn:
                return defn
    return ""


def enrich_from_dynamic_bank(
    topic: str,
    existing: list[str],
    bank: Iterable[Mapping[str, str]] | None,
) -> list[tuple[str, str]]:
    """Fill missing concept names from the upload bank (any subject)."""
    del topic
    if not bank:
        return []
    have = {e.lower() for e in existing}
    out: list[tuple[str, str]] = []
    for term, definition in bank_as_term_tuples(bank):
        if term.lower() in have or is_junk_term(term):
            continue
        if not student_safe_definition(definition):
            continue
        out.append((term, definition))
        have.add(term.lower())
        if len(out) >= 10:
            break
    return out


def wall_cards_from_bank(
    bank: Iterable[Mapping[str, str]] | None,
    *,
    topic: str = "",
    limit: int = 8,
) -> list[dict[str, str]]:
    """Convert teaching-bank rows into Lesson Wall cards."""
    del topic
    cards: list[dict[str, str]] = []
    seen: set[str] = set()
    for i, row in enumerate(bank or []):
        term = str(row.get("term") or "").strip()
        definition = student_safe_definition(str(row.get("definition") or ""))
        if not term or not definition or term.lower() in seen or is_junk_term(term):
            continue
        if is_ocr_garbage_claim(definition):
            continue
        seen.add(term.lower())
        cards.append(
            {
                "title": term,
                "idea": definition if definition.endswith((".", "!", "?")) else definition + ".",
                "hex": "#2563EB",
                "icon": f"{i + 1:02d}",
                "source": str(row.get("source") or "dynamic_upload_bank"),
            }
        )
        if len(cards) >= limit:
            break
    return cards


_WEAK_WALL_BITS = (
    "for performing",
    "collect the samples",
    "in the next section",
    "students will",
    "not to be republished",
    "notice how",
    "core idea",
    "memory tip",
    "checkpoint",
)


def _wall_card_is_weak(card: Mapping[str, str]) -> bool:
    from engines.lesson_composition_engine.lesson_wall import is_teachable_wall_card

    idea = str(card.get("idea") or card.get("body") or "").strip().lower()
    title = str(card.get("title") or "").strip().lower()
    if not idea or len(idea.split()) < 6:
        return True
    if any(k in idea for k in _WEAK_WALL_BITS) or any(k in title for k in _WEAK_WALL_BITS):
        return True
    if is_ocr_garbage_claim(idea) or is_teacher_facing_text(idea):
        return True
    if not is_teachable_wall_card(card):
        return True
    return False


def ensure_wall_from_bank(
    wall: list[dict[str, str]] | None,
    bank: Iterable[Mapping[str, str]] | None,
    *,
    topic: str = "",
    min_cards: int = 3,
) -> list[dict[str, str]]:
    """Prefer teachable wall cards; replace OCR chrome / fill gaps from bank."""
    from engines.lesson_composition_engine.lesson_wall import (
        dedupe_lesson_wall,
        seed_curriculum_wall_cards,
    )

    current = [dict(c) for c in (wall or []) if str(c.get("title") or "").strip()]
    current = dedupe_lesson_wall(current)
    # Known CBSE chapters: curated bank is the Lesson Wall — OCR lab crumbs never win.
    curriculum = seed_curriculum_wall_cards(topic, limit=12)
    if len(curriculum) >= min_cards:
        return curriculum[:12]

    bank_cards = wall_cards_from_bank(bank, topic=topic, limit=12)
    if not bank_cards:
        bank_cards = curriculum

    # Drop weak / chrome clones; keep strong Master cards.
    strong = [c for c in current if not _wall_card_is_weak(c)]
    weak_count = len(current) - len(strong)

    if len(strong) >= min_cards and weak_count == 0:
        have = {str(c.get("title") or "").lower() for c in strong}
        for card in bank_cards:
            if card["title"].lower() in have:
                continue
            idea_l = card["idea"].lower()[:56]
            if any(str(c.get("idea") or "").lower()[:56] == idea_l for c in strong):
                continue
            strong.append(card)
            have.add(card["title"].lower())
            if len(strong) >= 10:
                break
        return strong[:12]

    # Thin or chrome-heavy wall — bank leads; keep leftover strong cards.
    filled = list(bank_cards) if bank_cards else seed_curriculum_wall_cards(topic, limit=12)
    have = {c["title"].lower() for c in filled}
    for card in strong:
        key = str(card.get("title") or "").lower()
        if key and key not in have:
            filled.append(card)
            have.add(key)
    if len(filled) < min_cards:
        for card in seed_curriculum_wall_cards(topic, limit=12):
            key = card["title"].lower()
            if key not in have:
                filled.append(card)
                have.add(key)
            if len(filled) >= min_cards:
                break
    return filled[:12]
