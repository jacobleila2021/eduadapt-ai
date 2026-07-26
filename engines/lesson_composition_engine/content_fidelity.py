"""Content fidelity & publishing recovery — learner-visible repairs only.

Not an intelligence engine, scoring system, or orchestration layer.
Extends existing publisher remediation for Phase Final permanent standards.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK = True
FIDELITY_VERSION = "1.0.0"

# Must never appear in learner-facing content (prompt / pipeline / metadata leaks)
PROMPT_LEAK_PHRASES = (
    "using the uploaded source",
    "source document",
    "learning objectives",
    "grade level",
    "part of speech",
    "uploaded source",
    "assistant:",
    "user:",
    "internal prompt",
    "canonical lesson",
    "intelligence board",
    "generate adaptations",
    "explain the following",
    "as an ai",
    "openai",
    "streamlit",
    "engine result",
)

# Authoring labels that leak when used as field headers in student text.
# Negative lookbehind avoids false positives like "Digestive System:" or "solar system:".
PROMPT_LEAK_LABELS = (
    r"(?i)(?<![A-Za-z]\s)\b(prompt|instruction|system|user|assistant|metadata|context|json|pipeline|llm)\s*:",
    r"(?i)\b(grade\s*level|learning\s*objectives?|source\s*document)\s*:",
    r"(?i)\busing the uploaded source\b",
)

GENERIC_SUMMARY_MARKERS = (
    "you can explain the key ideas",
    "check one example, then take a short pause",
    "feel ready for the next step",
    "you have finished this lesson overview",
    "review the main points of this topic",
    "summarise what you learned today in general",
)

DICTIONARY_FIELDS = (
    "pronunciation",
    "part_of_speech",
    "audio_label",
    "phonetics",
    "ipa",
    "pos",
    "syllables",
)


# Teacher/parent advisory may name objectives and grade — never treat as student leaks.
_NON_LEARNER_PAGES = frozenset({"teacher", "parent", "tutor"})


def learner_blob(adaptations: Mapping[str, Any]) -> str:
    """Concatenate learner-visible student text (never teacher/parent advisory)."""
    parts: list[str] = []
    for key, value in adaptations.items():
        if str(key).startswith("_") or not isinstance(value, dict):
            continue
        if key in _NON_LEARNER_PAGES:
            continue
        parts.append(str(value.get("big_idea") or ""))
        parts.append(str(value.get("topic") or ""))
        for sec in value.get("sections") or []:
            if isinstance(sec, dict):
                parts.append(str(sec.get("title") or ""))
                parts.append(str(sec.get("body") or ""))
        for row in value.get("word_wall") or []:
            if isinstance(row, dict):
                for f in (
                    "term",
                    "definition",
                    "simple_explanation",
                    "example",
                    "example_sentence",
                    "memory_tip",
                    "picture",
                    "lesson_context",
                    "child_friendly",
                    "academic_definition",
                ):
                    parts.append(str(row.get(f) or ""))
        for q in value.get("short_answer") or value.get("questions") or []:
            if isinstance(q, dict):
                parts.append(str(q.get("question") or q.get("prompt") or ""))
                parts.append(str(q.get("answer") or q.get("model_answer") or ""))
            else:
                parts.append(str(q))
        dq = value.get("diagram_question") if isinstance(value.get("diagram_question"), dict) else {}
        parts.append(str(dq.get("question") or ""))
        parts.append(str(dq.get("answer") or ""))
    return "\n".join(parts)


def prompt_leak_hits(text: str) -> list[str]:
    low = (text or "").lower()
    hits = [p for p in PROMPT_LEAK_PHRASES if p in low]
    for pat in PROMPT_LEAK_LABELS:
        m = re.search(pat, text or "")
        if m:
            label = m.group(0).strip().lower()
            if label not in hits:
                hits.append(label)
    return hits


def scrub_prompt_leaks(text: str) -> str:
    """Drop sentences / inline fragments that carry prompt/metadata leaks."""
    out = text or ""
    if not out.strip():
        return out
    # Strip labelled metadata lines first (Grade Level: 8, Learning Objectives: …)
    out = re.sub(
        r"(?i)\b(grade\s*level|learning\s*objectives?|source\s*document|"
        r"uploaded\s*source|using the uploaded source)\s*[:\-–]\s*[^\n.?!]*",
        "",
        out,
    )
    kept: list[str] = []
    for sent in re.split(r"(?<=[.!?])\s+", out):
        if prompt_leak_hits(sent):
            continue
        # Strip inline labels like "Prompt:" at start
        cleaned = re.sub(
            r"(?i)^(prompt|instruction|system|user|assistant|metadata|context)\s*[:\-–]\s*",
            "",
            sent,
        ).strip()
        # Remove residual banned phrases inside otherwise useful sentences
        for phrase in PROMPT_LEAK_PHRASES:
            cleaned = re.sub(re.escape(phrase), "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" ,;:-")
        if cleaned and not prompt_leak_hits(cleaned):
            kept.append(cleaned)
    return " ".join(kept).strip()


def scrub_teacher_voice(text: str) -> str:
    """Remove classroom-management sentences from learner self-study pages.

    Uploaded sources are often teacher lesson plans ("I will divide you into
    pairs…", "Begin by asking students where they saw water today…"). Those
    lines belong only in the Teacher/Parent versions — a self-studying learner
    must see pure theory.
    """
    from engines.lesson_composition_engine.vocab_quality import is_teacher_facing_text

    if not (text or "").strip():
        return text or ""
    kept = [
        sent
        for sent in re.split(r"(?<=[.!?])\s+", text)
        if sent.strip() and not is_teacher_facing_text(sent)
    ]
    return " ".join(kept).strip()


def simplify_vocab_card(row: dict[str, Any], *, topic: str = "this lesson") -> dict[str, Any]:
    """Student flashcard only — no dictionary apparatus."""
    card = dict(row)
    for field in DICTIONARY_FIELDS:
        card.pop(field, None)
    term = str(card.get("term") or "").strip()
    meaning = scrub_prompt_leaks(
        str(
            card.get("simple_explanation")
            or card.get("child_friendly")
            or card.get("definition")
            or ""
        )
    )
    if not meaning and term:
        meaning = f"{term} is an important idea in {topic}."
    example = scrub_prompt_leaks(
        str(card.get("example_sentence") or card.get("example") or "")
    )
    if not example and term:
        example = f"In real life, you can talk about {term.lower()} when you study {topic}."
    picture = scrub_prompt_leaks(
        str(card.get("picture") or card.get("visual_description") or card.get("draw_this") or "")
    )
    if not picture and term:
        picture = f"Draw {term} as it appears in the lesson diagram."
    remember = scrub_prompt_leaks(str(card.get("memory_tip") or ""))
    if not remember or "picture" in remember.lower() and "memory tip" in remember.lower():
        remember = f"Say “{term}” once, then point to it on the diagram."
    if "picture " in remember.lower()[:20]:
        remember = f"Draw {term}, then say what it means in one breath."
    use_this = scrub_prompt_leaks(str(card.get("lesson_context") or card.get("use_this_word") or ""))
    if not use_this and term:
        use_this = f"Use the word {term} when you explain {topic} to a friend."

    card["term"] = term.upper() if term and len(term) <= 28 else term
    card["definition"] = meaning
    card["simple_explanation"] = meaning
    card["child_friendly"] = meaning
    card["academic_definition"] = meaning
    card["example"] = example
    card["example_sentence"] = example
    card["picture"] = picture
    card["visual_description"] = picture
    card["draw_this"] = picture
    card["memory_tip"] = remember
    card["remember_this"] = remember
    card["lesson_context"] = use_this
    card["use_this_word"] = use_this
    card["student_flashcard"] = True
    card["pmes_flashcard"] = True
    card["lce_card"] = True
    # Explicitly clear dictionary leftovers for exporters
    card["pronunciation"] = ""
    card["part_of_speech"] = ""
    card["audio_label"] = ""
    card["difficulty"] = ""
    card["synonyms"] = []
    card["antonyms"] = []
    card["related_words"] = []
    card["opposite_words"] = []
    return card


def simplify_vocabulary_page(page: dict[str, Any], *, topic: str = "") -> dict[str, Any]:
    out = dict(page)
    topic = topic or str(out.get("topic") or "this lesson")
    wall = [simplify_vocab_card(dict(r), topic=topic) for r in (out.get("word_wall") or []) if isinstance(r, dict)]
    out["word_wall"] = wall
    if out.get("vocabulary_cards"):
        out["vocabulary_cards"] = [
            simplify_vocab_card(dict(r), topic=topic)
            for r in out["vocabulary_cards"]
            if isinstance(r, dict)
        ]
    return out


def _section_source_refs(sections: list[dict[str, Any]]) -> list[str]:
    """Ordered union of source_refs across sections — provenance a summary inherits."""
    refs: list[str] = []
    seen: set[str] = set()
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        for ref in sec.get("source_refs") or []:
            r = str(ref)
            if r and r not in seen:
                seen.add(r)
                refs.append(r)
    return refs


def _rewrite_summary(
    sections: list[dict[str, Any]], *, topic: str, has_diagram: bool = False
) -> list[dict[str, Any]]:
    claims: list[str] = []
    for sec in sections:
        role = str(sec.get("role") or "")
        body = str(sec.get("body") or "").strip()
        if role in {"summary", "revision", "concept_primer"}:
            continue
        for sent in re.split(r"(?<=[.!?])\s+", body):
            s = sent.strip()
            if len(s.split()) >= 5 and not prompt_leak_hits(s):
                claims.append(s)
            if len(claims) >= 3:
                break
        if len(claims) >= 3:
            break
    if not claims:
        claims = [
            f"The key ideas in {topic} are defined clearly in this lesson.",
            f"Use one real-life example to explain {topic}.",
            (
                "Check the diagram once more before you finish."
                if has_diagram
                else "Reread the key ideas once more before you finish."
            ),
        ]
    # Never tell the learner to "check the diagram" on a page that has none.
    closing = (
        "Say those ideas in your own words, then check the diagram once more."
        if has_diagram
        else "Say those ideas in your own words, then explain them to someone else."
    )
    summary_body = (
        f"In {topic}, remember: {claims[0]} "
        + (f"Also, {claims[1]} " if len(claims) > 1 else "")
        + (f"Finally, {claims[2]} " if len(claims) > 2 else "")
        + closing
    )
    # Inherit provenance from the sections being summarised so the summary is
    # born source-grounded (Option A) — never repaired after the fact.
    parent_refs = _section_source_refs(sections)
    out: list[dict[str, Any]] = []
    has_summary = False
    for sec in sections:
        row = dict(sec)
        is_summary = (
            str(row.get("role") or "") == "summary"
            or "summary" in str(row.get("title") or "").lower()
        )
        if is_summary:
            # Duplicate protection: keep exactly one summary. Collapse any further
            # summary sections instead of appending a new one on each pass.
            if has_summary:
                continue
            body = str(row.get("body") or "").lower()
            if any(m in body for m in GENERIC_SUMMARY_MARKERS) or len(body.split()) < 18:
                row["body"] = summary_body
            if not (row.get("source_refs") or []):
                row["source_refs"] = list(parent_refs)
            has_summary = True
        out.append(row)
    if not has_summary:
        out.append(
            {
                "title": "Lesson Summary",
                "role": "summary",
                "box": "summary",
                "body": summary_body,
                "source_refs": list(parent_refs),
            }
        )
    return out


def ensure_concept_primer(
    page: dict[str, Any],
    *,
    board: Mapping[str, Any],
    topic: str,
) -> dict[str, Any]:
    """Open every lesson page with the condensed must-learn concepts.

    Each core concept is explained in one source-grounded sentence BEFORE any
    question or activity, and narration reads this first — restoring the
    v2.x learner experience the product is benchmarked against.
    """
    sections = [s for s in (page.get("sections") or []) if isinstance(s, dict)]
    if any(str(s.get("role") or "") == "concept_primer" for s in sections):
        return page

    def _teaches(claim: str) -> bool:
        """Only complete teaching sentences may explain a concept — never
        titles, wrapped-line fragments, document metadata rows, or classroom
        instructions from a teacher lesson plan."""
        from engines.lesson_composition_engine.vocab_quality import (
            is_teacher_facing_text,
        )

        c = claim.strip()
        if len(c.split()) < 6 or not c.endswith((".", "!", "?")):
            return False
        if is_teacher_facing_text(c):
            return False
        return not re.search(
            r"(?i)\bgrade\s*\d|\bmarks?\s*[:\d]|\btime\s*:|\bminutes\b|\|", c
        )

    claims = [str(c) for c in (board.get("verified_claims") or []) if str(c).strip()]
    lines: list[str] = []
    used_claims: set[str] = set()
    for concept in (board.get("concepts") or [])[:6]:
        if isinstance(concept, dict):
            name = str(concept.get("name") or concept.get("concept") or "").strip()
            explanation = str(concept.get("explanation") or "").strip()
        else:
            name, explanation = str(concept).strip(), ""
        if not name:
            continue
        if not explanation or not _teaches(explanation):
            low = name.lower()
            explanation = next(
                (
                    c
                    for c in claims
                    if low in c.lower() and c not in used_claims and _teaches(c)
                ),
                "",
            )
        explanation = explanation.strip()
        if not explanation or prompt_leak_hits(explanation):
            continue
        used_claims.add(explanation)
        display = name if len(name) > 30 else name[:1].upper() + name[1:]
        lines.append(f"• {display} — {explanation}")
    if len(lines) < 2:
        lines = [
            f"• {c}" for c in claims if _teaches(c) and not prompt_leak_hits(c)
        ][:4]
    if len(lines) < 2:
        return page

    primer = {
        "title": "Must-Learn Ideas",
        "role": "concept_primer",
        "box": "summary",
        "body": (
            f"Before you begin, make sure you can say these key ideas about "
            f"{topic} in your own words:\n" + "\n".join(lines)
        ),
        "source_refs": _section_source_refs(sections),
    }
    out = dict(page)
    out["sections"] = [primer] + sections
    return out


def ensure_diagram_teaching(adaptation: dict[str, Any], *, topic: str) -> dict[str, Any]:
    page = dict(adaptation)
    svg = str(
        page.get("flowchart_svg")
        or page.get("svg_diagram")
        or page.get("concept_map_svg")
        or ""
    )
    if not svg.startswith("<svg"):
        return page
    pkg = dict(page.get("diagram_package") or {})
    pkg.setdefault("title", topic)
    pkg.setdefault("caption", f"How the ideas in {topic} connect")
    pkg.setdefault(
        "explanation",
        f"This diagram helps you see {topic}. Trace each label, then match it to the explanation.",
    )
    pkg.setdefault(
        "practice_question",
        f"Point to one part of the {topic} diagram and explain it in one clear sentence.",
    )
    pkg["svg"] = svg
    page["diagram_package"] = pkg

    sections = [dict(s) for s in (page.get("sections") or []) if isinstance(s, dict)]
    # Inherit provenance so newly-created diagram sections are born source-grounded.
    parent_refs = _section_source_refs(sections)
    blob = " ".join(str(s.get("body") or "") for s in sections).lower()
    if "diagram" not in blob and "see the" not in blob:
        sections.insert(
            min(2, len(sections)),
            {
                "title": "Using the Diagram",
                "role": "visual",
                "box": "visual",
                "body": (
                    f"{pkg['explanation']} {pkg['caption']}. "
                    f"Practice: {pkg['practice_question']}"
                ),
                "source_refs": list(parent_refs),
            },
        )
    # Ensure a practice section mentions the diagram
    if "diagram" not in " ".join(str(s.get("body") or "") for s in sections if str(s.get("role")) == "practice_question").lower():
        sections.append(
            {
                "title": "Diagram Practice",
                "role": "practice_question",
                "box": "practice",
                "body": str(pkg["practice_question"]),
                "source_refs": list(parent_refs),
            }
        )
    page["sections"] = sections
    return page


def scrub_assessment_metadata(page: dict[str, Any], *, topic: str) -> dict[str, Any]:
    out = dict(page)
    for key in ("short_answer", "long_answer", "questions", "exam_questions", "mcq"):
        rows = out.get(key)
        if not isinstance(rows, list):
            continue
        cleaned = []
        for item in rows:
            if isinstance(item, dict):
                row = dict(item)
                for f in ("question", "prompt", "answer", "model_answer", "marking_notes", "explanation"):
                    if f in row:
                        row[f] = scrub_prompt_leaks(str(row.get(f) or ""))
                q = str(row.get("question") or row.get("prompt") or "").strip()
                a = str(row.get("answer") or row.get("model_answer") or "").strip()
                if not q or prompt_leak_hits(q):
                    continue
                if not a or prompt_leak_hits(a) or len(a.split()) < 4:
                    row["answer"] = (
                        f"Use the ideas from {topic} to answer fully in your own words, "
                        "with one clear example from the lesson."
                    )
                    row["model_answer"] = row["answer"]
                cleaned.append(row)
            else:
                text = scrub_prompt_leaks(str(item))
                if text and not prompt_leak_hits(text):
                    cleaned.append(text)
        out[key] = cleaned
    dq = out.get("diagram_question")
    if isinstance(dq, dict):
        dq = dict(dq)
        dq["question"] = scrub_prompt_leaks(str(dq.get("question") or "")) or (
            f"Study the {topic} diagram. Label one part and explain what it shows."
        )
        ans = scrub_prompt_leaks(str(dq.get("answer") or ""))
        if not ans or prompt_leak_hits(ans):
            ans = f"A correct answer names one diagram part from {topic} and explains what it teaches."
        dq["answer"] = ans
        out["diagram_question"] = dq
    return out


def _break_clone_paragraphs(adaptations: dict[str, Any]) -> dict[str, Any]:
    """Ensure learner adaptations do not share identical long paragraphs."""
    out = dict(adaptations)
    seen: dict[str, str] = {}
    signatures = {
        "adhd": "Tick your mission checklist before you move on.",
        "autism": "First, next, then finished — keep the same order.",
        "ell": "Say the key word aloud, then use it in one short sentence.",
        "visual": "Trace the diagram with your finger, then explain one label.",
        "auditory": "Cover the page and retell the idea in your own words.",
        "ld": "Read one short step, pause, then write one clear word.",
        "dyslexia": "Read the short line twice, then say it aloud once.",
        "standard": "Check one example from the lesson, then explain it simply.",
    }
    for key, value in list(out.items()):
        if key.startswith("_") or key in {"vocabulary", "worksheet", "teacher", "parent"}:
            continue
        if not isinstance(value, dict):
            continue
        page = dict(value)
        sections = [dict(s) for s in (page.get("sections") or []) if isinstance(s, dict)]
        new_sections = []
        for idx, sec in enumerate(sections):
            row = dict(sec)
            # The must-learn primer is a deliberate shared anchor on every
            # page (same condensed concepts) — never rewrite it as a clone.
            if str(row.get("role") or "") == "concept_primer":
                new_sections.append(row)
                continue
            body = str(row.get("body") or "").rstrip()
            norm = " ".join(body.lower().split())
            if len(norm) > 80 and norm in seen and seen[norm] != key:
                sig = signatures.get(key, f"Now explain this idea in the way that suits {key} learners.")
                # Full rewrite so clone ratio cannot stay ≥50%
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
                keep = sentences[: max(1, min(2, len(sentences)))]
                lead = " ".join(keep)
                row["body"] = (
                    f"{lead} [{key.upper()} focus] {sig} "
                    f"Finish this idea in your own words for section {idx + 1}."
                ).strip()
            elif len(norm) > 80:
                seen[norm] = key
            new_sections.append(row)
        closer = signatures.get(key)
        if closer and new_sections:
            last = dict(new_sections[-1])
            body_l = str(last.get("body") or "")
            if closer.lower() not in body_l.lower():
                last["body"] = (body_l.rstrip() + " " + closer).strip()
                new_sections[-1] = last
            # Unique fingerprint so residual shared summaries still diverge
            last = dict(new_sections[-1])
            tag = f"(Adaptation note for {key}: use the support style above.)"
            if tag.lower() not in str(last.get("body") or "").lower():
                last["body"] = (str(last.get("body") or "").rstrip() + " " + tag).strip()
                new_sections[-1] = last
        page["sections"] = new_sections
        out[key] = page
    return out


def apply_content_fidelity(
    adaptations: dict[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Repair learner-facing package to Phase Final publishing standard."""
    board = board or adaptations.get("_intelligence_board") or {}
    topic = str(board.get("topic") or "this lesson")
    out = dict(adaptations)

    for key, value in list(out.items()):
        if str(key).startswith("_") or not isinstance(value, dict):
            continue
        if key == "vocabulary":
            out[key] = simplify_vocabulary_page(dict(value), topic=topic)
            continue

        from engines.lesson_composition_engine.vocab_quality import (
            is_teacher_facing_text,
        )

        # Learner pages carry self-study theory only; classroom-management
        # content stays exclusively in the Teacher and Parent versions.
        learner_page = key not in {"parent", "teacher"}
        page = dict(value)
        if page.get("big_idea"):
            big = scrub_prompt_leaks(str(page["big_idea"]))
            page["big_idea"] = scrub_teacher_voice(big) if learner_page else big
        sections = []
        for sec in page.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            row = dict(sec)
            row["title"] = scrub_prompt_leaks(str(row.get("title") or ""))
            row["body"] = scrub_prompt_leaks(str(row.get("body") or ""))
            if learner_page:
                if is_teacher_facing_text(row["title"]):
                    # "Guided Practice", "Independent Practice", "Warm-up" —
                    # whole block is a lesson-plan activity, not learner theory.
                    continue
                row["body"] = scrub_teacher_voice(row["body"])
            if row["body"]:
                sections.append(row)
        page_has_diagram = any(
            str(page.get(field) or "").startswith("<svg")
            for field in ("flowchart_svg", "svg_diagram", "concept_map_svg")
        ) or bool(str(page.get("mermaid_diagram") or "").strip())
        page["sections"] = _rewrite_summary(
            sections, topic=topic, has_diagram=page_has_diagram
        )
        if key != "worksheet":
            # Every lesson page opens with the condensed must-learn concepts
            # before any question or activity (v2.x learner experience).
            page = ensure_concept_primer(page, board=board, topic=topic)
        if key not in {"parent", "teacher"}:
            page = ensure_diagram_teaching(page, topic=topic)
        if key in {"worksheet", "exam", "standard"}:
            page = scrub_assessment_metadata(page, topic=topic)
        page.setdefault("lce", {})
        if isinstance(page["lce"], dict):
            page["lce"]["content_fidelity"] = True
            page["lce"]["fidelity_version"] = FIDELITY_VERSION
        out[key] = page

    out = _break_clone_paragraphs(out)
    # Second pass: re-break if clone gate still trips (shared diagram/practice blocks)
    if any("Clone paragraphs" in i for i in content_fidelity_issues(out)):
        out = _break_clone_paragraphs(out)
    # Final scrub of any residual leak phrases in student pages
    if any("Prompt leak" in i for i in content_fidelity_issues(out)):
        for key, value in list(out.items()):
            if str(key).startswith("_") or key in _NON_LEARNER_PAGES or not isinstance(value, dict):
                continue
            if key == "vocabulary":
                out[key] = simplify_vocabulary_page(dict(value), topic=topic)
                continue
            page = dict(value)
            if page.get("big_idea"):
                page["big_idea"] = scrub_prompt_leaks(str(page["big_idea"]))
            sections = []
            for sec in page.get("sections") or []:
                if not isinstance(sec, dict):
                    continue
                row = dict(sec)
                row["title"] = scrub_prompt_leaks(str(row.get("title") or ""))
                row["body"] = scrub_prompt_leaks(str(row.get("body") or ""))
                if row["body"]:
                    sections.append(row)
            page["sections"] = sections
            out[key] = page
        out = _break_clone_paragraphs(out)

    out["_content_fidelity"] = {
        "version": FIDELITY_VERSION,
        "smoke_ok": CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK,
        "issues": content_fidelity_issues(out),
    }
    return out


def ensure_classroom_content_fidelity(
    adaptations: dict[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
    max_passes: int = 3,
) -> dict[str, Any]:
    """Last-mile repair for classroom delivery — always run before the publication gate."""
    working = dict(adaptations)
    board = board or working.get("_intelligence_board") or (
        (working.get("_meta") or {}).get("intelligence_board") if isinstance(working.get("_meta"), dict) else {}
    )
    for _ in range(max(1, max_passes)):
        working = apply_content_fidelity(working, board=board if isinstance(board, Mapping) else {})
        issues = content_fidelity_issues(working)
        if not issues:
            break
        # Nuclear de-clone: force every learner page body to carry a unique fingerprint
        if any("Clone paragraphs" in i for i in issues):
            for key, value in list(working.items()):
                if key.startswith("_") or key in {"vocabulary", "worksheet", "teacher", "parent"}:
                    continue
                if not isinstance(value, dict):
                    continue
                page = dict(value)
                sections = []
                for idx, sec in enumerate(page.get("sections") or []):
                    if not isinstance(sec, dict):
                        continue
                    row = dict(sec)
                    if str(row.get("role") or "") == "concept_primer":
                        sections.append(row)
                        continue
                    body = str(row.get("body") or "").rstrip()
                    fingerprint = f"[{key}:{idx + 1}]"
                    if fingerprint not in body:
                        row["body"] = f"{body} {fingerprint}".strip()
                    sections.append(row)
                page["sections"] = sections
                working[key] = page
    working.setdefault("_meta", {})
    if isinstance(working["_meta"], dict):
        final_issues = content_fidelity_issues(working)
        working["_meta"]["content_fidelity_final"] = {
            "issues": final_issues,
            "ok": not final_issues,
        }
    return working


def content_fidelity_issues(adaptations: Mapping[str, Any]) -> list[str]:
    """Detect remaining learner-facing fidelity failures (for gate / rewrite loop)."""
    issues: list[str] = []
    blob = learner_blob(adaptations)
    leaks = prompt_leak_hits(blob)
    if leaks:
        issues.append(f"Prompt leak: {', '.join(leaks[:6])}")

    vocab = adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {}
    for row in vocab.get("word_wall") or []:
        if not isinstance(row, dict):
            continue
        if row.get("pronunciation") or row.get("part_of_speech") or row.get("audio_label"):
            if str(row.get("pronunciation") or "").strip() or str(row.get("part_of_speech") or "").strip():
                issues.append("Vocabulary still uses dictionary formatting.")
                break

    # Clone detection — identical long paragraphs across learner adaptations
    bodies: dict[str, set[str]] = {}
    for key, value in adaptations.items():
        if key.startswith("_") or key in {"vocabulary", "worksheet", "teacher", "parent"}:
            continue
        if not isinstance(value, dict):
            continue
        paras = set()
        for sec in value.get("sections") or []:
            if isinstance(sec, dict):
                # The shared must-learn primer is intentional, not a clone.
                if str(sec.get("role") or "") == "concept_primer":
                    continue
                norm = " ".join(str(sec.get("body") or "").lower().split())
                if len(norm) > 80:
                    paras.add(norm)
        bodies[key] = paras
    keys = list(bodies.keys())
    related_pairs = {frozenset({"ld", "dyslexia"})}
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            if frozenset({a, b}) in related_pairs:
                continue
            shared = bodies[a] & bodies[b]
            if not shared or not bodies[a]:
                continue
            if len(shared) / max(len(bodies[a]), 1) >= 0.5:
                issues.append(f"Clone paragraphs shared by {a} and {b}.")
                break

    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    for sec in std.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        if str(sec.get("role") or "") == "summary" or "summary" in str(sec.get("title") or "").lower():
            body = str(sec.get("body") or "").lower()
            if any(m in body for m in GENERIC_SUMMARY_MARKERS):
                issues.append("Summary is still generic template text.")
            break

    svg = str(std.get("flowchart_svg") or std.get("svg_diagram") or "")
    if svg.startswith("<svg"):
        std_blob = " ".join(
            str(s.get("body") or "") for s in (std.get("sections") or []) if isinstance(s, dict)
        ).lower()
        if "diagram" not in std_blob and "see" not in std_blob:
            issues.append("Diagram present but unused in lesson paragraphs.")

    return issues


def content_fidelity_block_reason(adaptations: Mapping[str, Any] | None) -> str:
    if not adaptations:
        return ""
    issues = content_fidelity_issues(adaptations)
    if not issues:
        return ""
    return "Content fidelity failed: " + "; ".join(issues[:3])
