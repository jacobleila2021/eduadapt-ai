"""Extraction stages: equations, questions, objectives, semantic chunking."""

from __future__ import annotations

import re
from typing import Any

from engines.knowledge_ingestion_engine.schemas import ExtractedEquation, ExtractedQuestion


_RE_CHEM = re.compile(
    r"([A-Z][a-z]?\d*(?:\s*[+\-]\s*[A-Z][a-z]?\d*)*)\s*(?:->|→|⟶|⇌|<=>)\s*([A-Z][a-z]?\d*(?:\s*[+\-]\s*[A-Z][a-z]?\d*)*)"
)
_RE_MATH_EQ = re.compile(
    r"(?:\$([^$]+)\$)|(?:\\\\\[(.+?)\\\\])|(?:([a-zA-Z0-9\(\)\^\+\-\*/\s]{1,40})\s*=\s*([a-zA-Z0-9\(\)\^\+\-\*/\s]{1,40}))"
)
_RE_QUESTION = re.compile(
    r"(?mi)^(?:Q\.?\s*\d+|Question\s+\d+|Exercise\s+\d+\.\d*|\[\d+\s*marks?\]|[A-D]\)|\d+\.\s+).{10,400}$"
)
_RE_MCQ_OPT = re.compile(r"(?m)^\s*[A-D][\).\:]\s+.+$")
_RE_OBJECTIVE = re.compile(
    r"(?i)(?:learning\s+objectives?|students?\s+will\s+be\s+able\s+to|after\s+this\s+lesson)[:\s]+(.{10,200})"
)
_RE_VOCAB = re.compile(r"\b([A-Z][a-z]{3,}(?:\s+[A-Z][a-z]{3,}){0,2})\b")


def extract_equations(text: str) -> list[dict[str, Any]]:
    eqs: list[ExtractedEquation] = []
    for m in _RE_CHEM.finditer(text or ""):
        raw = m.group(0)
        eqs.append(ExtractedEquation(latex=rf"\ce{{{raw}}}", kind="chemistry", raw=raw))
    for m in _RE_MATH_EQ.finditer(text or ""):
        body = next((g for g in m.groups() if g), "")
        if not body or len(body.strip()) < 3:
            continue
        if "->" in body or "→" in body:
            continue
        eqs.append(ExtractedEquation(latex=body.strip().replace("^", "^{}"), kind="math", raw=body.strip()))
    # Dedupe
    seen = set()
    out = []
    for e in eqs:
        key = e.raw.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(e.to_dict())
    return out[:40]


def extract_questions(text: str, *, chapter: int = 0, topic: str = "", source: str = "") -> list[dict[str, Any]]:
    qs: list[ExtractedQuestion] = []
    lines = (text or "").splitlines()
    for i, line in enumerate(lines):
        if not _RE_QUESTION.search(line.strip()):
            continue
        qtype = "mcq" if _RE_MCQ_OPT.search("\n".join(lines[i : i + 6])) else "short_answer"
        if re.search(r"assertion|reason", line, re.I):
            qtype = "assertion_reason"
        if re.search(r"hots|higher\s+order", line, re.I):
            qtype = "hots"
        if re.search(r"case\s+study", line, re.I):
            qtype = "case_study"
        marks_m = re.search(r"\[(\d+)\s*marks?\]", line, re.I)
        qs.append(
            ExtractedQuestion(
                question=line.strip()[:500],
                question_type=qtype,
                marks=int(marks_m.group(1)) if marks_m else 1,
                bloom="analyze" if qtype in ("hots", "case_study") else "remember",
                difficulty="hard" if qtype == "hots" else "medium",
                topic=topic,
                chapter=chapter,
                source=source,
            )
        )
    return [q.to_dict() for q in qs[:50]]


def extract_objectives_and_vocab(text: str) -> dict[str, Any]:
    objectives = []
    for m in _RE_OBJECTIVE.finditer(text or ""):
        objectives.append(m.group(1).strip())
    # Headings as concept proxies
    concepts = re.findall(r"(?m)^(?:#{1,3}\s+|\d+\.\d+\s+)([A-Z][^\n]{3,60})$", text or "")
    if not concepts:
        concepts = [c.strip() for c in _RE_VOCAB.findall(text or "") if len(c) > 4][:30]
    # Simple vocab: capitalized science-ish terms frequency
    vocab = []
    for term in concepts:
        if term not in vocab and len(term.split()) <= 3:
            vocab.append(term)
    return {
        "learning_objectives": objectives[:20],
        "concepts": list(dict.fromkeys(concepts))[:40],
        "vocabulary": vocab[:40],
    }


def semantic_chunks(
    pages: list[dict[str, Any]],
    *,
    board: str,
    grade: str,
    subject: str,
    source: str,
) -> list[dict[str, Any]]:
    """
    Chunk by concept/heading blocks rather than raw page alone.
    Falls back to page chunks when no headings.
    """
    chunks: list[dict[str, Any]] = []
    for page in pages or []:
        text = (page.get("text") or "").strip()
        if len(text) < 40:
            continue
        chapter = int(page.get("chapter") or 0)
        page_no = page.get("page")
        # Split on heading-like lines
        parts = re.split(r"(?m)(?=^(?:\d+\.\d+\s+|[A-Z][A-Za-z\s]{4,40})$)", text)
        if len(parts) <= 1:
            parts = [text]
        for j, part in enumerate(parts):
            part = part.strip()
            if len(part) < 60:
                continue
            title = part.splitlines()[0][:80] if part.splitlines() else f"chunk-{j}"
            chunks.append(
                {
                    "chunk_id": f"{Path_stem_safe(source)}-p{page_no}-c{j}",
                    "text": part[:4000],
                    "chapter": chapter,
                    "chapter_title": title,
                    "page_start": page_no,
                    "source": source,
                    "board": board,
                    "grade": grade,
                    "subject": subject,
                    "parent_id": f"page-{page_no}",
                    "chunk_by": "concept" if len(parts) > 1 else "page",
                }
            )
    return chunks


def Path_stem_safe(source: str) -> str:
    from pathlib import Path

    return re.sub(r"[^\w\-]+", "_", Path(source).stem)[:40]


def accessibility_metadata(text: str, figures: list[dict]) -> dict[str, Any]:
    words = re.findall(r"[A-Za-z']+", text or "")
    avg_len = (sum(len(w) for w in words) / len(words)) if words else 0
    # Rough reading grade proxy
    sentences = max(len(re.findall(r"[.!?]+", text or "")), 1)
    grade_est = round(0.39 * (len(words) / sentences) + 11.8 * (avg_len / 5) - 15.59, 1) if words else None
    for fig in figures or []:
        if not fig.get("alt_text"):
            fig["alt_text"] = fig.get("caption") or f"Educational figure on page {fig.get('page', '?')}"
    return {
        "reading_grade_estimate": grade_est,
        "vocabulary_difficulty": "high" if avg_len > 6.5 else "medium" if avg_len > 5 else "low",
        "language_complexity": avg_len,
        "figures_with_alt_placeholders": sum(1 for f in (figures or []) if f.get("alt_text")),
        "wcag_notes": "Alt text placeholders attached; teachers should refine descriptions",
    }
