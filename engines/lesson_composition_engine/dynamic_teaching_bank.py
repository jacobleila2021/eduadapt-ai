"""Dynamic teaching bank — build term→definition packs from every upload.

R10/R11: subject-agnostic concept extraction so Alora is not limited to the
five hand-authored CBSE banks. Curated banks still win when they match;
this fills the gap for every other lesson.
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
)

_HEADING_RE = re.compile(
    rf"(?m)^(?:#{{1,3}}\s+|\d+\.\d+\s+|•\s*|[-*]\s*)?(?P<term>{_TERM})\s*$"
)


def _unwrap_soft_breaks(text: str) -> str:
    """Join textbook line-wraps so definition sentences stay intact."""
    raw = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    # Join when a line ends mid-sentence (comma / no terminal punct).
    return re.sub(r"(?<![.!?])\n(?=[a-z])", " ", raw)


def _clean_term(raw: str) -> str:
    t = repair_ocr_prose(str(raw or "")).strip(" .:;,-–")
    t = re.sub(r"\s+", " ", t)
    if not t or is_junk_term(t) or len(t.split()) > 6:
        return ""
    # Reject activity / chapter chrome terms
    low = t.lower()
    if any(k in low for k in ("activity", "chapter", "caution", "exercise", "question")):
        return ""
    return t[:1].upper() + t[1:] if t else ""


def _clean_definition(term: str, body: str) -> str:
    text = student_safe_definition(repair_ocr_prose(body) or "")
    if not text or is_ocr_garbage_claim(text) or is_teacher_facing_text(text):
        return ""
    # Prefer definitions that actually teach the term
    if term.lower() not in text.lower() and len(text.split()) < 8:
        text = f"{term} is {text[0].lower() + text[1:]}" if text else ""
    text = text.strip()
    if not text.endswith((".", "!", "?")):
        text += "."
    if len(text.split()) < 5:
        return ""
    return text[:320]


def _score_def(term: str, definition: str) -> int:
    low = definition.lower()
    needle = term.lower()
    score = 2
    if low.startswith(needle + " is ") or low.startswith(needle + " are "):
        score += 6
    if " means " in low[:60] or " is the " in low[:60]:
        score += 3
    if is_ocr_garbage_claim(definition) or is_teacher_facing_text(definition):
        return -10
    if len(definition.split()) >= 10:
        score += 1
    return score


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
            # Skip question stems ("What is photosynthesis?")
            prefix = raw[max(0, m.start() - 12) : m.start()].lower()
            if re.search(r"(?:^|\n)\s*\d+[.)]\s*$|what\s+$|which\s+$|name\s+$", prefix):
                continue
            if term.lower() in {"what", "which", "who", "when", "where", "how", "why", "name"}:
                continue
            definition = _clean_definition(term, f"{term} {verb} {body}".strip())
            if not definition:
                continue
            score = _score_def(term, definition)
            key = term.lower()
            prev = found.get(key)
            if score >= 4 and (not prev or score > prev[0]):
                found[key] = (score, definition)

    # Heading + following sentence as weak definitions
    lines = raw.splitlines()
    for i, line in enumerate(lines):
        hm = _HEADING_RE.match(line.strip())
        if not hm:
            continue
        term = _clean_term(hm.group("term"))
        if not term or term.lower() in found:
            continue
        # Next non-empty line as candidate definition
        for j in range(i + 1, min(i + 4, len(lines))):
            nxt = lines[j].strip()
            if len(nxt.split()) < 6:
                continue
            definition = _clean_definition(
                term, nxt if term.lower() in nxt.lower() else f"{term}: {nxt}"
            )
            if definition and _score_def(term, definition) >= 3:
                found[term.lower()] = (_score_def(term, definition), definition)
            break

    ranked = sorted(found.items(), key=lambda kv: (-kv[1][0], kv[0]))
    out: list[tuple[str, str]] = []
    for key, (_score, definition) in ranked[:16]:
        # Restore display casing from the definition opener when possible.
        m = re.match(rf"(?i)^({re.escape(key)})\b", definition)
        term = m.group(1) if m else key.title()
        out.append((term, definition))
    return out


def build_dynamic_teaching_bank(
    *,
    topic: str = "",
    source_text: str = "",
    claims: Iterable[str] | None = None,
    concepts: Iterable[Any] | None = None,
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
    # Also mine claims with definition_from_claims-style subject lines
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
        if term and definition:
            if not any(term.lower() == t.lower() for t, _ in pairs):
                pairs.append((term, definition))

    # Topic itself is never a lone bank card
    topic_l = (topic or "").strip().lower()
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for term, definition in pairs:
        key = term.lower()
        if key in seen or key == topic_l or is_junk_term(term):
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
    del topic  # available for future topic filtering
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
