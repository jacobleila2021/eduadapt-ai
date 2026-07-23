"""Knowledge Layer orchestration for lesson generation."""

from __future__ import annotations

import re

from knowledge.pilot_config import ACTIVE_PILOT
from knowledge.prompts import (
    enrichment_policy_header,
    official_bank_to_prompt_block,
    rag_hits_to_prompt_block,
)
from knowledge.question_bank import (
    build_official_answer_key,
    match_exam_bundle,
    match_official_mcqs,
    official_items_to_worksheet_entries,
)
from knowledge.rag import KnowledgeRag

_rag_singleton: KnowledgeRag | None = None


def _grade_number(value: str) -> str:
    match = re.search(r"\b(?:grade|class|year)?\s*(\d{1,2})\b", str(value or ""), re.I)
    return match.group(1) if match else ""


def _scope_matches(lesson_text: str, context: dict | None) -> bool:
    """Use the fixed pilot corpus only when the upload is in that curriculum scope."""
    ctx = context or {}
    lesson_grade = _grade_number(str(ctx.get("grade_level") or ""))
    if not lesson_grade:
        lesson_grade = _grade_number(lesson_text[:600])
    pilot_grade = _grade_number(ACTIVE_PILOT.grade)
    if lesson_grade and pilot_grade and lesson_grade != pilot_grade:
        return False

    declared = re.search(r"\bsubject\s*:\s*([^\n|]+)", lesson_text[:600], re.I)
    if declared:
        subject = declared.group(1).strip().lower()
        pilot_subject = ACTIVE_PILOT.subject.lower()
        science_subjects = {
            "science",
            "general science",
            "biology",
            "chemistry",
            "physics",
            "earth science",
            "environmental science",
        }
        if pilot_subject == "science":
            return subject in science_subjects
        return pilot_subject in subject
    return True


def _hit_is_relevant(hit, topic: str, vocabulary_terms: list[str]) -> bool:
    """Reject broad semantic neighbours that do not share lesson anchors."""
    blob = f"{hit.chapter_title} {hit.text}".lower()
    topic_l = topic.strip().lower()
    if len(topic_l) >= 4 and topic_l in blob:
        return True
    anchors = {
        token
        for token in re.findall(r"[a-zA-Z]{4,}", f"{topic} {' '.join(vocabulary_terms)}")
        if token.lower() not in {"lesson", "students", "science", "grade", "class"}
    }
    return len({token.lower() for token in anchors if token.lower() in blob}) >= 2


def ensure_knowledge_index() -> dict:
    global _rag_singleton
    if _rag_singleton is None:
        _rag_singleton = KnowledgeRag(ACTIVE_PILOT)
    return _rag_singleton.ensure_index()


def _build_query(lesson_text: str, context: dict | None) -> str:
    ctx = context or {}
    parts = [
        str(ctx.get("topic") or ""),
        str(ctx.get("grade_level") or ""),
        " ".join(ctx.get("learning_objectives") or [])[:500],
        " ".join(ctx.get("vocabulary_terms") or [])[:300],
    ]
    for concept in (ctx.get("key_concepts") or [])[:6]:
        if isinstance(concept, dict):
            parts.append(str(concept.get("name") or ""))
    parts.append(lesson_text[:2000])
    return " ".join(p for p in parts if p).strip()


def prepare_knowledge_for_lesson(
    lesson_text: str,
    context: dict | None = None,
    *,
    grounding_mode: str = "uploaded_source",
) -> dict:
    """
    Resolve optional verified enrichment for a source lesson.
    Uploaded-source generation is independent of this result.
    Curriculum enrichment is an enhancement, not a dependency.
    """
    policy_header = enrichment_policy_header(grounding_mode)
    if not _scope_matches(lesson_text, context):
        return {
            "pilot_id": None,
            "board": None,
            "grade": None,
            "subject": None,
            "book_title": None,
            "index": {
                "indexed": 0,
                "backend": "scope_skipped",
                "message": "Uploaded lesson is outside the active pilot scope",
            },
            "rag_hits": [],
            "official_mcqs": [],
            "exam_bundle": {},
            "prompt_block": policy_header,
            "citations": [],
            "scope_matched": False,
            "grounding_mode": grounding_mode,
            "external_enrichment": {
                "status": "out_of_scope",
                "required": False,
                "citation_notice": "No curriculum references available.",
            },
            "retrieval_warnings": [],
        }

    global _rag_singleton
    if _rag_singleton is None:
        _rag_singleton = KnowledgeRag(ACTIVE_PILOT)

    query = _build_query(lesson_text, context)
    topic = str((context or {}).get("topic") or "")
    vocab_terms = list((context or {}).get("vocabulary_terms") or [])
    retrieval_warnings: list[dict] = []
    try:
        index_info = _rag_singleton.ensure_index()
        hits = [
            hit
            for hit in _rag_singleton.retrieve(query, k=6)
            if _hit_is_relevant(hit, topic, vocab_terms)
        ]
    except Exception:
        index_info = {
            "indexed": 0,
            "backend": "unavailable",
            "message": "Verified knowledge retrieval is temporarily unavailable",
        }
        hits = []
        retrieval_warnings.append(
            {
                "stage": "optional_curriculum_retrieval",
                "code": "knowledge_index_unavailable",
                "message": "Verified curriculum retrieval is temporarily unavailable.",
                "recovery": "Continue with the uploaded source and retry enrichment later.",
                "fallback_used": "uploaded_source",
            }
        )
    official_items = match_official_mcqs(topic, vocab_terms, limit=6)
    # Prefer Chroma semantic retrieval when available
    try:
        from knowledge.question_rag import semantic_match_questions

        semantic = semantic_match_questions(topic, lesson_text, limit=8)
        if semantic and official_items:
            # Semantic search may rank strict matches, but cannot introduce an
            # item that failed deterministic topic/vocabulary relevance.
            allowed = {it.item_id for it in official_items}
            ranked = [it for it in semantic if it.item_id in allowed]
            seen = {it.item_id for it in ranked}
            ranked.extend(it for it in official_items if it.item_id not in seen)
            official_items = ranked[:6]
    except Exception:
        retrieval_warnings.append(
            {
                "stage": "optional_question_retrieval",
                "code": "question_index_unavailable",
                "message": "Optional official question retrieval is unavailable.",
                "recovery": "Use source-derived assessment questions.",
                "fallback_used": "source_assessment",
            }
        )
    exam_bundle = match_exam_bundle(topic, vocab_terms, limit_per_type=2)

    rag_block = rag_hits_to_prompt_block(hits)
    official_block = official_bank_to_prompt_block(official_items)
    # Include typed exam sources in prompt
    bundle_lines = ["EXAM_QUESTION_BANK (official — use these; do not invent keys):"]
    for bkey, blist in exam_bundle.items():
        for it in blist:
            bundle_lines.append(
                f"- [{bkey}/{it.source}] {it.question[:160]} → {it.official_answer} "
                f"(marks={it.marks}, bloom={it.bloom})"
            )
    bundle_block = "\n".join(bundle_lines) if any(exam_bundle.values()) else ""
    prompt_parts = [policy_header]
    if rag_block:
        prompt_parts.append(rag_block)
    if official_block:
        prompt_parts.append(official_block)
    if bundle_block:
        prompt_parts.append(bundle_block)
    prompt_block = "\n\n".join(prompt_parts).strip()

    return {
        "pilot_id": ACTIVE_PILOT.pilot_id,
        "board": ACTIVE_PILOT.board,
        "grade": ACTIVE_PILOT.grade,
        "subject": ACTIVE_PILOT.subject,
        "book_title": ACTIVE_PILOT.book_title,
        "grounding_mode": grounding_mode,
        "index": index_info,
        "rag_hits": [
            {
                "chunk_id": h.chunk_id,
                "citation": h.citation,
                "chapter_title": h.chapter_title,
                "score": h.score,
                "excerpt": h.text[:400],
            }
            for h in hits
        ],
        "official_mcqs": [
            {
                "item_id": it.item_id,
                "source": it.source,
                "topic": it.topic,
                "question": it.question,
                "official_answer": it.official_answer,
                "citation": f"[{it.source} · {it.item_id}]",
            }
            for it in official_items
        ],
        "exam_bundle": {
            k: [
                {
                    "item_id": it.item_id,
                    "source": it.source,
                    "question_type": it.question_type,
                    "question": it.question,
                    "official_answer": it.official_answer,
                    "marks": it.marks,
                    "bloom": it.bloom,
                    "year": it.year,
                }
                for it in v
            ]
            for k, v in exam_bundle.items()
        },
        "prompt_block": prompt_block,
        "citations": [h.citation for h in hits],
        "scope_matched": True,
        "retrieval_warnings": retrieval_warnings,
        "external_enrichment": {
            "status": (
                "available"
                if hits or official_items
                else ("unavailable" if retrieval_warnings else "no_hits")
            ),
            "required": False,
            "citation_notice": (
                ""
                if hits or official_items
                else "No curriculum references available."
            ),
        },
    }


def enrich_worksheet_with_official_bank(worksheet: dict, knowledge: dict) -> dict:
    """
    Inject official MCQ items into worksheet — answers from bank only, not LLM.
    """
    from knowledge.question_bank import load_official_items

    item_ids = {row.get("official_item_id") for row in worksheet.get("official_mcqs") or []}
    matched_ids = {m["item_id"] for m in knowledge.get("official_mcqs") or []}
    items = [it for it in load_official_items() if it.item_id in matched_ids]

    if not items:
        return worksheet

    official_rows = official_items_to_worksheet_entries(items)
    sheet = dict(worksheet)

    existing_official = sheet.get("official_mcqs") or []
    new_rows = [r for r in official_rows if r.get("official_item_id") not in item_ids]
    sheet["official_mcqs"] = existing_official + new_rows

    # Prepend official items to short answer section (teacher-facing keys stay official)
    short = list(sheet.get("short_answer") or [])
    for row in new_rows:
        short.insert(
            0,
            {
                "question": row["question"],
                "marks": row["marks"],
                "lines": row["lines"],
                "model_answer": row["model_answer"],
                "source": row["source"],
                "citation": row["citation"],
            },
        )
    sheet["short_answer"] = short[:12]

    answer_key = list(sheet.get("answer_key") or [])
    answer_key = build_official_answer_key(items) + answer_key
    sheet["answer_key"] = answer_key
    sheet["_official_bank_applied"] = True
    return sheet


def inject_exam_practice_into_lessons(
    adaptations: dict,
    knowledge: dict,
    *,
    universal_profile: dict | None = None,
) -> dict:
    """Append Exam Practice for classroom adaptations.

    Prefer official bank items when present. When the bank is empty, attach
    practice-from-source board questions built from uploaded claims (no invented
    official keys).
    """
    if not isinstance(adaptations, dict):
        return adaptations

    classroom_keys = frozenset(
        {"standard", "ld", "ell", "visual", "auditory", "teacher", "adhd", "autism"}
    )
    exam_bundle = (knowledge or {}).get("exam_bundle") or {}
    lines: list[str] = []
    official = False
    for bkey, items in exam_bundle.items():
        for it in items or []:
            official = True
            lines.append(
                f"- **[{bkey}] {it.get('source', '')}** ({it.get('marks', 1)} marks, "
                f"{it.get('bloom', '')}): {it.get('question', '')} "
                f"— *Official answer: {it.get('official_answer', '')}*"
            )
    if not lines:
        for it in (knowledge or {}).get("official_mcqs") or []:
            official = True
            lines.append(
                f"- **{it.get('source', 'Official')}**: {it.get('question', '')} "
                f"— *Official answer: {it.get('official_answer', '')}*"
            )

    if not lines:
        profile = universal_profile or {}
        claims = []
        for row in profile.get("claim_ledger") or []:
            if isinstance(row, dict) and row.get("text"):
                claims.append(str(row["text"]).strip())
        if not claims:
            for unit in profile.get("source_units") or []:
                if isinstance(unit, str) and unit.strip():
                    claims.append(unit.strip())
        topic = str(profile.get("topic") or profile.get("title") or "this topic")
        if not claims:
            # Still ensure classroom tabs get an Exam Practice section marker;
            # generation/fallback already embeds practice-from-source content.
            claims = [
                f"Explain the main process in {topic} using accurate lesson terms.",
                f"Describe how two ideas in {topic} connect, with evidence from the lesson.",
                f"Define one key term from {topic} and give a classroom example.",
                f"Outline the steps or stages taught in the lesson on {topic}.",
                f"Compare two source ideas from {topic} and state one implication.",
                f"Write a short board-style answer summarising {topic}.",
            ]
        for i, claim in enumerate(claims[:6], start=1):
            marks = 2 if i <= 4 else 5
            kind = "Short" if i <= 4 else "Long/HOTS"
            lines.append(
                f"- **Q{i} ({kind}, {marks} marks, practice-from-source):** "
                f"Using only the uploaded lesson on {topic}, respond to: {claim[:220]} "
                f"— *Model cue: restate the claim with lesson terminology; do not invent facts.*"
            )

    if not lines:
        return adaptations

    if official:
        intro = (
            "Practice with official curriculum questions "
            "(keys from the answer bank — not invented):\n\n"
        )
        title = "Exam Practice (Official)"
    else:
        intro = (
            "Board-style practice grounded in the uploaded source "
            "(practice-from-source — not an official answer key):\n\n"
        )
        title = "Exam Practice"

    body = intro + "\n".join(lines[:12])
    out = dict(adaptations)
    for key, lesson in list(out.items()):
        if key.startswith("_") or key in ("vocabulary", "worksheet", "parent"):
            continue
        if key not in classroom_keys or not isinstance(lesson, dict):
            continue
        sections = list(lesson.get("sections") or [])
        if any(
            isinstance(s, dict)
            and any(
                m in str(s.get("title", "")).lower()
                for m in ("exam practice", "board check", "board practice")
            )
            for s in sections
        ):
            continue
        sections.append({"title": title, "body": body, "box": "orange"})
        lesson = dict(lesson)
        lesson["sections"] = sections
        out[key] = lesson
    return out
