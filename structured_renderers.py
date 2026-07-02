"""
Render structured vocabulary, worksheet, and lesson objects with native Streamlit UI.
Guarantees visible sections, colors, and diagrams (not dependent on HTML in markdown).
"""

from __future__ import annotations

import html
import json
import re
from typing import Any

import streamlit as st

from content_renderer import _render_mermaid
from lesson_design import (
    ACCENT_INFO,
    ACCENT_INTRO,
    ACCENT_STORY,
    BG_MAIN,
    BORDER_SUBTLE,
    FONT_STACK,
    TEXT_BODY,
    accent_for_variant,
    classify_section,
    section_card_html,
)
_BOX_RENDERERS = {
    "teal": lambda t: st.info(t),
    "blue": lambda t: st.info(t),
    "green": lambda t: st.success(t),
    "orange": lambda t: st.warning(t),
    "intro": lambda t: st.info(f"**Introduction** — {t}"),
    "practice": lambda t: st.success(f"**Practice** — {t}"),
    "check": lambda t: st.warning(f"**Check** — {t}"),
}



def _coerce_dict(content: Any) -> dict | None:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        text = content.strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        if text and not text.startswith("_No content"):
            return {
                "big_idea": "Lesson content",
                "sections": [{"title": "Content", "body": text, "box": "teal"}],
                "mermaid_diagram": "",
                "svg_diagram": "",
                "visual_summary": [],
            }
    return None


def _as_dict(content: Any) -> dict | None:
    return _coerce_dict(content)


def _valid_mermaid(diagram: str) -> bool:
    """True only if the string looks like a real mermaid diagram (avoids blank boxes)."""
    if not diagram or not isinstance(diagram, str):
        return False
    text = diagram.strip().lower()
    if len(text) < 15:
        return False
    keywords = ("flowchart", "graph ", "graph\n", "mindmap", "sequencediagram", "timeline", "classdiagram")
    has_kind = any(k in text for k in keywords)
    has_edges = "-->" in text or "---" in text or "->>" in text
    return has_kind and has_edges


def _valid_svg_diagram(svg: str) -> bool:
    """Reject empty/placeholder SVGs (single circle, no labels, suspicious content)."""
    if not svg or not isinstance(svg, str):
        return False
    text = svg.strip().lower()
    if "<svg" not in text or "</svg>" not in text:
        return False
    if len(text) < 80:
        return False
    # Must contain at least one text label to be educational, not a random shape/flag.
    if "<text" not in text:
        return False
    shape_count = text.count("<rect") + text.count("<circle") + text.count("<path") + text.count("<line") + text.count("<polygon") + text.count("<ellipse")
    return shape_count >= 1


def _fallback_lesson_diagram(lesson: dict) -> str:
    """Deterministic labelled study SVG from lesson sections (never a blank box)."""
    from study_diagram_builder import build_study_diagram_svg

    return build_study_diagram_svg(lesson)


def _word_wall_card_html(word: dict) -> str:
    emoji = word.get("emoji", "📌")
    term = html.escape(word.get("term", "Term"))
    definition = html.escape(word.get("definition", ""))
    child_note = html.escape(
        word.get("child_friendly") or word.get("visual_description") or ""
    )
    example = html.escape(word.get("example") or word.get("example_sentence") or "")
    body_parts = [f"<strong>Definition:</strong> {definition}"]
    if child_note:
        body_parts.append(f"<strong>In simple words:</strong> {child_note}")
    if example:
        body_parts.append(f"<strong>Example:</strong> <em>{example}</em>")
    body = "<br/>".join(body_parts)
    return (
        f'<article class="alora-word-wall-card">'
        f'<p class="alora-word-wall-term">{emoji} {term}</p>'
        f'<div class="alora-word-wall-body">{body}</div>'
        f"</article>"
    )


def _lookup_answer(answer_key: list, ref: str) -> str:
    for item in answer_key or []:
        if item.get("question_ref", "").strip().lower() == ref.strip().lower():
            return item.get("model_answer", "")
        if ref.lower() in (item.get("question_ref") or "").lower():
            return item.get("model_answer", "")
    return ""


def _show_answer_button(label: str, answer: str, key: str, *, exam_style: bool = False) -> None:
    if not answer:
        return
    reveal_key = f"revealed_{key}"
    if st.button(f"Show Answer — {label}", key=f"btn_{key}", type="secondary"):
        st.session_state[reveal_key] = True
    if st.session_state.get(reveal_key):
        if exam_style:
            st.markdown(
                f'<div class="exam-answer-reveal">{html.escape(answer)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.success(answer)


def _extract_blank_answer(sentence: str) -> tuple[str, str]:
    """Pull the answer out of a fill-in-the-blank sentence's trailing brackets."""
    text = str(sentence)
    match = re.search(r"\(([^)]*)\)\s*([.!?]?)\s*$", text)
    if not match:
        return text, ""
    raw = match.group(1).strip()
    raw = re.sub(r"^(use|answer|ans|hint)\s*[:\-]\s*", "", raw, flags=re.IGNORECASE).strip()
    if not raw:
        return text, ""
    display = (text[: match.start()].rstrip() + match.group(2)).strip()
    return display, raw


def _clean_fill_blank_display(sentence: str) -> str:
    """Student-facing sentence — no bracket hints or stray dash blanks."""
    display, _ = _extract_blank_answer(sentence)
    text = display or str(sentence)
    text = re.sub(r"\s*\([^)]+\)", "", text)
    text = re.sub(r"[_\-]{3,}\s*\.", "________.", text)
    text = re.sub(r"[_\-]{3,}", "________", text)
    text = re.sub(r"________\s*\.\s*________\.?", "________.", text)
    text = re.sub(r"\.\s*\.", ".", text)
    text = re.sub(r"\s+\.", ".", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    if text and not text.endswith((".", "?", "!")):
        text += "."
    return text


def _clean_practice_blank(text: str) -> str:
    """Remove IPA guides and syllable counts from practice sentences."""
    cleaned = str(text or "").strip()
    cleaned = re.sub(r"—?\s*/[^/]+/\s*", " ", cleaned)
    cleaned = re.sub(r"\s*\(\d+\)\s*$", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def _build_matching_section(word_wall: list[dict]) -> dict:
    """Structured matching items — answers stored separately for Show Answer only."""
    import random

    pairs = [
        (w.get("term", ""), w.get("definition", ""))
        for w in word_wall[:8]
        if w.get("term") and w.get("definition")
    ]
    if not pairs:
        return {
            "matching_terms": [],
            "matching_definitions": [],
            "matching_answer_key": [],
        }

    indexed = list(enumerate(pairs, 1))
    shuffled = list(indexed)
    random.shuffle(shuffled)
    letters = "ABCDEFGH"

    matching_terms = [{"n": n, "term": term} for n, (term, _) in indexed]
    matching_definitions: list[dict] = []
    answer_key: list[dict] = []
    letter_for_number: dict[int, str] = {}

    for slot, (number, (term, definition)) in enumerate(shuffled):
        letter = letters[slot]
        matching_definitions.append({"letter": letter, "text": definition[:160]})
        letter_for_number[number] = letter

    for number, (term, _) in indexed:
        answer_key.append({"n": number, "letter": letter_for_number.get(number, "")})

    return {
        "matching_terms": matching_terms,
        "matching_definitions": matching_definitions,
        "matching_answer_key": answer_key,
    }


def _answer_fits_sentence(answer: str, sentence: str, word_wall: list[dict]) -> bool:
    """True when the answer plausibly completes the blank for this sentence."""
    if not answer:
        return False
    sent = sentence.lower()
    ans = answer.lower()
    if ans in sent.replace("________", ""):
        return True
    clue_words = set(re.findall(r"[a-z]{4,}", sent.replace("________", " ")))
    for word in word_wall:
        term = (word.get("term") or "").lower()
        defin = (word.get("definition") or "").lower()
        if ans == term:
            def_words = set(re.findall(r"[a-z]{4,}", defin))
            return len(clue_words & def_words) >= 2
        if ans in defin:
            def_words = set(re.findall(r"[a-z]{4,}", defin))
            if len(clue_words & def_words) >= 2:
                return True
    return len(ans.split()) <= 3 and any(w in sent for w in ans.split() if len(w) > 3)


def _infer_term_from_clue(sentence: str, word_wall: list[dict]) -> str:
    """Pick the word-wall term best described by the sentence clue."""
    clue = re.sub(r"________", " ", sentence.lower())
    clue_words = set(re.findall(r"[a-z]{4,}", clue))
    best_term = ""
    best_score = 0.0
    for word in word_wall:
        term = (word.get("term") or "").strip()
        if not term:
            continue
        defin = (word.get("definition") or "").lower()
        child = (word.get("child_friendly") or "").lower()
        def_words = set(re.findall(r"[a-z]{4,}", f"{defin} {child}"))
        if not clue_words or not def_words:
            continue
        overlap = len(clue_words & def_words) / max(len(clue_words), 1)
        if term.lower() in clue and "vocabulary word" not in clue:
            overlap += 0.35
        if overlap > best_score:
            best_score = overlap
            best_term = term
    return best_term if best_score >= 0.2 else ""


def _fill_blank_for_word(word: dict) -> tuple[str, str]:
    """Build a fill-in-the-blank sentence and its correct short answer."""
    term = (word.get("term") or "").strip()
    definition = (word.get("definition") or word.get("child_friendly") or "").strip()
    if not term:
        return "This key idea from the lesson is ________.", ""
    if definition:
        lowered = definition.lower()
        if "divide" in lowered or "dividing" in lowered:
            return (
                f"{term} is made of cells that can ________.",
                "divide",
            )
        if "water" in lowered and ("transport" in lowered or "carry" in lowered):
            return (
                f"{term} is responsible for transporting water and ________.",
                "minerals",
            )
        return (
            f"{definition.rstrip('.')}. The vocabulary word is ________.",
            term,
        )
    return (f"This key term from the lesson is ________.", term)


def _prepare_self_test(self_test: dict, word_wall: list[dict]) -> dict:
    """Ensure self-test has clean structured matching and semantically correct fill-blank answers."""
    data = dict(self_test or {})
    matching = _build_matching_section(word_wall)
    data["matching_terms"] = matching["matching_terms"]
    data["matching_definitions"] = matching["matching_definitions"]
    data["matching_answer_key"] = matching["matching_answer_key"]
    data.pop("matching_prompt", None)
    data.pop("matching", None)

    target_count = min(8, max(6, len(word_wall)))
    blanks = list(data.get("fill_blanks") or [])
    ai_answers = list(data.get("fill_blank_answers") or data.get("answers") or [])

    if len(blanks) < target_count:
        for index in range(len(blanks), target_count):
            sentence, answer = _fill_blank_for_word(word_wall[index % len(word_wall)])
            blanks.append(sentence)
            if len(ai_answers) <= index:
                ai_answers.append(answer)

    rebuilt: list[str] = []
    answers: list[str] = []
    for index, sentence in enumerate(blanks[:target_count], 1):
        raw = str(sentence).strip()
        text = _clean_fill_blank_display(raw)
        if "________" not in text:
            word = word_wall[(index - 1) % len(word_wall)]
            text, default_ans = _fill_blank_for_word(word)
            if len(ai_answers) < index:
                ai_answers.append(default_ans)
        rebuilt.append(text)

        probe = dict(data)
        probe["fill_blank_answers"] = ai_answers
        _, resolved = _resolve_fill_blank_answer(raw, index, probe, word_wall)
        if not resolved and index - 1 < len(ai_answers):
            candidate = str(ai_answers[index - 1] or "").strip()
            if candidate:
                canonical = _canonical_wall_term(candidate, _wall_term_map(word_wall))
                resolved = canonical or candidate
        if not resolved:
            word = word_wall[(index - 1) % len(word_wall)]
            _, resolved = _fill_blank_for_word(word)
        if not resolved and "vocabulary word" in text.lower():
            resolved = _infer_term_from_clue(text, word_wall)
        if resolved and not _answer_fits_sentence(resolved, text, word_wall):
            word = word_wall[(index - 1) % len(word_wall)]
            text, fallback = _fill_blank_for_word(word)
            rebuilt[-1] = text
            resolved = fallback
        answers.append(resolved or "")

    data["fill_blanks"] = rebuilt
    data["fill_blank_answers"] = answers
    return data


def _prepare_practice(word_wall: list[dict], topic: str = "") -> list[dict]:
    """Numbered say-spell-use items without pronunciation metadata."""
    items: list[dict] = []
    for word in word_wall[:8]:
        term = (word.get("term") or "").strip()
        if not term:
            continue
        example = (word.get("example") or word.get("example_sentence") or "").strip()
        if example and term.lower() in example.lower():
            blank = re.sub(re.escape(term), "________", example, count=1, flags=re.IGNORECASE)
        else:
            subject = topic or "this topic"
            blank = f"Write one sentence using ________ to explain {subject}."
        items.append({"term": term, "sentence_blank": blank})
    return items


def _render_self_test(self_test: dict, word_wall: list[dict], key_prefix: str) -> None:
    """Match & Review — answers revealed only via Show Answer buttons."""
    prepared = _prepare_self_test(self_test, word_wall)
    terms = prepared.get("matching_terms") or []
    definitions = prepared.get("matching_definitions") or []
    match_key = prepared.get("matching_answer_key") or []
    fill_blanks = prepared.get("fill_blanks") or []
    fill_answers = prepared.get("fill_blank_answers") or []

    if terms and definitions:
        st.markdown("**Part A — Matching**")
        st.caption("Match each numbered term to the correct lettered definition.")
        col_terms, col_defs = st.columns(2)
        with col_terms:
            st.markdown("**Terms**")
            for row in terms:
                st.markdown(f"{row['n']}. {row['term']}")
        with col_defs:
            st.markdown("**Definitions**")
            for row in definitions:
                st.markdown(f"{row['letter']}. {row['text']}")
        if match_key:
            compact = ", ".join(
                f"{row['n']} → {row['letter']}"
                for row in sorted(match_key, key=lambda item: item["n"])
                if row.get("letter")
            )
            if compact:
                _show_answer_button("Matching", compact, f"{key_prefix}_matching")

    if fill_blanks:
        st.markdown("**Part B — Fill in the blank**")
        for index, sentence in enumerate(fill_blanks, 1):
            display = _clean_fill_blank_display(sentence)
            st.markdown(f"{index}. {display}")
            ans = fill_answers[index - 1] if index - 1 < len(fill_answers) else ""
            if ans:
                _show_answer_button(f"Q{index}", ans, f"{key_prefix}_ans_{index}")


def _wall_term_map(word_wall: list[dict]) -> dict[str, str]:
    return {
        (w.get("term") or "").strip().lower(): (w.get("term") or "").strip()
        for w in word_wall
        if (w.get("term") or "").strip()
    }


def _canonical_wall_term(candidate: str, term_map: dict[str, str]) -> str:
    key = (candidate or "").strip().lower()
    return term_map.get(key, "") if key else ""


def _best_wall_term_for_sentence(sentence: str, word_wall: list[dict]) -> str:
    """Pick the longest word-wall term mentioned in the sentence."""
    text_lower = sentence.lower()
    term_map = _wall_term_map(word_wall)
    best = ""
    best_len = 0
    for key, term in term_map.items():
        if re.search(rf"\b{re.escape(key)}\b", text_lower):
            if len(term) > best_len:
                best_len = len(term)
                best = term
    return best


def _resolve_fill_blank_answer(
    sentence: str,
    index: int,
    self_test: dict,
    word_wall: list[dict],
) -> tuple[str, str]:
    """Return (display_sentence, correct_answer) for a fill-in-the-blank."""
    display, bracket_ans = _extract_blank_answer(sentence)
    term_map = _wall_term_map(word_wall)

    answers = self_test.get("fill_blank_answers") or self_test.get("answers") or []
    if index - 1 < len(answers):
        entry = answers[index - 1]
        if isinstance(entry, dict):
            explicit = (entry.get("answer") or entry.get("term") or "").strip()
        else:
            explicit = str(entry or "").strip()
        if explicit:
            canonical = _canonical_wall_term(explicit, term_map) if term_map else ""
            return display or sentence, canonical or explicit

    if bracket_ans:
        canonical = _canonical_wall_term(bracket_ans, term_map) if term_map else ""
        if canonical:
            return display, canonical
        if len(bracket_ans.split()) <= 6:
            return display, bracket_ans

    if term_map:
        matched = _best_wall_term_for_sentence(sentence, word_wall)
        if matched:
            return display or sentence, matched

    return display or sentence, ""


def _render_svg(svg: str, height: int = 260) -> None:
    if not svg or not svg.strip():
        return
    st.markdown(
        f'<div class="alora-study-diagram" style="display:flex;justify-content:center;'
        f'align-items:center;max-width:100%;overflow-x:auto;padding:1rem 0;">'
        f'{svg.strip()}</div>',
        unsafe_allow_html=True,
    )


def _render_picture_words(picture_words: list[dict], topic: str, key_prefix: str) -> None:
    """Picture Words — coloured vocabulary flowchart (replaces AI images)."""
    st.markdown("### 3. Picture Words — Visual Flowchart")
    if not picture_words:
        st.caption("No picture vocabulary generated.")
        return

    from flowchart_builder import build_vocabulary_flowchart, estimate_flowchart_height

    vocab_stub = {"topic": topic, "picture_words": picture_words}
    chart = build_vocabulary_flowchart(vocab_stub)
    st.caption("Colour-coded flowchart linking each term to the lesson topic.")
    _render_mermaid(chart, height=estimate_flowchart_height(chart))


def render_vocabulary(data: Any, key_prefix: str = "vocab") -> None:
    """Word Wall, Flashcards, Picture Words, Practice, Self-Test — always visible."""
    vocab = _coerce_dict(data)
    if not vocab or not vocab.get("word_wall"):
        st.error(
            "Vocabulary sections were not generated correctly. "
            "Click **Clear Session**, then **Generate Adaptations** again (~8–12 min)."
        )
        with st.expander("Technical details"):
            st.write(type(data).__name__, str(data)[:800] if data else "empty")
        return

    topic = vocab.get("topic", "Lesson Vocabulary")
    st.subheader(f"📖 {topic}")

    # --- 1. Word Wall ---
    st.markdown("### 1. Word Wall — Study First")
    word_wall = vocab.get("word_wall") or []
    if not word_wall:
        st.warning("No word wall terms generated.")
    else:
        cards = "".join(_word_wall_card_html(word) for word in word_wall)
        st.markdown(
            f'<div class="alora-word-wall">{cards}</div>',
            unsafe_allow_html=True,
        )

    # --- 2. Flashcards ---
    st.markdown("### 2. Flashcards — Term → Meaning")
    flashcards = vocab.get("flashcards") or []
    for index, card in enumerate(flashcards, 1):
        front = card.get("front") or card.get("term", "")
        back = card.get("back") or card.get("definition", "")
        with st.expander(f"Card {index}: **{front}** — tap to reveal"):
            st.write(back)

    # --- 3. Picture Words ---
    _render_picture_words(vocab.get("picture_words") or [], topic, key_prefix)

    # --- 4. Say · Spell · Use ---
    st.markdown("### 4. Say It · Spell It · Use It")
    practice = _prepare_practice(word_wall, topic) or vocab.get("practice") or []
    for index, item in enumerate(practice, 1):
        term = item.get("term", "")
        blank = _clean_practice_blank(item.get("sentence_blank") or item.get("sentence", ""))
        st.markdown(f"**{index}. {term}**")
        if blank:
            st.markdown(f"_{blank}_")

    # --- 5. Self-Test ---
    st.markdown("### 5. Match & Review (Self-Test)")
    self_test = vocab.get("self_test") or {}
    _render_self_test(self_test, word_wall, key_prefix)

    # --- 6. Quick Reference ---
    st.markdown("### 6. Quick Reference Chart")
    chart = vocab.get("reference_chart") or []
    if chart:
        st.table(
            [
                {
                    "Term": row.get("term", ""),
                    "Definition": row.get("definition", ""),
                    "Synonym": row.get("synonym", ""),
                    "Exam tip": row.get("exam_tip", ""),
                }
                for row in chart
            ]
        )

    # --- 7. Concept Map (built from Word Wall — does not need AI mermaid) ---
    st.markdown("---")
    st.markdown("### 7. Concept Map")
    st.caption("Study how all vocabulary terms connect to the main topic.")
    from concept_map_builder import render_concept_map_streamlit

    render_concept_map_streamlit(vocab)


def render_worksheet(data: Any, key_prefix: str = "worksheet") -> None:
    """Exam paper layout with short answer, long answer, checklist."""
    sheet = _coerce_dict(data)
    if not sheet or not sheet.get("short_answer"):
        st.error(
            "Worksheet sections were not generated correctly. "
            "Click **Clear Session**, then **Generate Adaptations** again."
        )
        with st.expander("Technical details"):
            st.write(type(data).__name__, str(data)[:800] if data else "empty")
        return

    header = sheet.get("header") or {}
    st.markdown(
        f"""
        <div class="exam-print-header">
          <p><strong>Subject:</strong> ______________________</p>
          <p><strong>Lesson:</strong> ______________________</p>
          <p><strong>Time:</strong> ______________________</p>
          <p><strong>Marks:</strong> ______________________</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text_input("Name", key=f"{key_prefix}_name", placeholder="Student name")
    st.text_input("Date", key=f"{key_prefix}_date", placeholder="Date")

    # Part A — Short answer
    answer_key = sheet.get("answer_key") or []
    st.markdown("### Part A — Short Answer")
    for index, item in enumerate(sheet.get("short_answer") or [], 1):
        marks = item.get("marks", 2)
        st.markdown(f"**Q{index}. ({marks} marks)** {item.get('question', '')}")
        st.text_area(
            f"Your answer — Q{index}",
            key=f"{key_prefix}_sa_input_{index}",
            height=int(item.get("lines", 3)) * 28,
            label_visibility="collapsed",
            placeholder="Type your answer here…",
        )
        ref = f"Part A Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_sa_{index}", exam_style=True)
        st.markdown("")

    # Part B — Long answer
    st.markdown("### Part B — Long Answer")
    for index, item in enumerate(sheet.get("long_answer") or [], 1):
        marks = item.get("marks", 6)
        st.markdown(f"**Q{index}. ({marks} marks)** {item.get('question', '')}")
        st.text_area(
            f"Your answer — long Q{index}",
            key=f"{key_prefix}_la_input_{index}",
            height=int(item.get("lines", 8)) * 24,
            label_visibility="collapsed",
            placeholder="Type your extended answer here…",
        )
        ref = f"Part B Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_la_{index}", exam_style=True)
        st.markdown("")

    # Part C — Diagram
    diagram = sheet.get("diagram_question") or {}
    if diagram:
        st.markdown("### Part C — Diagram Question")
        st.markdown(
            f"**({diagram.get('marks', 4)} marks)** {diagram.get('question', '')}"
        )
        svg = diagram.get("svg_diagram") or diagram.get("svg", "")
        if _valid_svg_diagram(svg):
            _render_svg(svg)
        st.markdown("_Label the diagram above on your answer sheet._")
        dia_ans = diagram.get("model_answer", "") or _lookup_answer(answer_key, "Part C")
        _show_answer_button("Part C", dia_ans, f"{key_prefix}_dia", exam_style=True)

    # Part D — Vocab in context
    st.markdown("### Part D — Vocabulary in Context")
    for index, item in enumerate(sheet.get("vocab_questions") or [], 1):
        marks = item.get("marks", 1)
        st.markdown(f"**{index}. ({marks} mark)** {item.get('question', '')}")
        st.text_input(
            f"Vocab answer {index}",
            key=f"{key_prefix}_vq_input_{index}",
            label_visibility="collapsed",
            placeholder="Type your answer…",
        )
        ref = f"Part D Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_vq_{index}", exam_style=True)

    # Part E — Student checklist
    st.markdown("### Part E — Exam Ready Checklist")
    for index, tip in enumerate(sheet.get("student_checklist") or []):
        st.checkbox(tip, key=f"{key_prefix}_check_{index}")

    # Teacher sections
    with st.expander("Teacher: Differentiation Map (Part F)"):
        st.markdown(sheet.get("teacher_differentiation", "—"))

    with st.expander("Teacher: Answer Key & Marking Guide (Part G)"):
        for item in sheet.get("answer_key") or []:
            ref = item.get("question_ref") or item.get("question", "")
            st.markdown(f"**{ref}**")
            st.write(item.get("model_answer", ""))
            notes = item.get("marks_notes") or item.get("notes", "")
            if notes:
                st.caption(notes)
        from docx_exporter import export_worksheet_docx

        st.download_button(
            "Download Teacher Word (with answer key)",
            data=export_worksheet_docx(sheet, include_teacher_key=True),
            file_name="exam_worksheet_teacher.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"{key_prefix}_teacher_docx",
        )


def _plain_lesson_text(raw: str) -> str:
    """Strip HTML/markdown artefacts so lesson text never shows raw tags."""
    if not raw:
        return ""
    text = html.unescape(str(raw))
    text = re.sub(r"<a[^>]*>.*?</a>", " ", text, flags=re.I | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def render_lesson(data: Any, spec_id: str | None = None) -> None:
    """Structured lesson with colored callouts, diagram, and sections."""
    lesson = _coerce_dict(data)
    if not lesson or not (lesson.get("sections") or lesson.get("big_idea")):
        st.error(
            "Lesson sections were not generated correctly. "
            "Use **Clear Session** → **Generate Adaptations** again."
        )
        if data:
            with st.expander("Raw content"):
                st.write(str(data)[:1500])
        return

    sections = lesson.get("sections") or []
    bullet_mode = spec_id in ("ld", "auditory")

    from flowchart_builder import (
        estimate_flowchart_height,
        resolve_lesson_concept_flowchart,
        resolve_lesson_study_flowchart,
    )

    concept_chart = resolve_lesson_concept_flowchart(lesson)
    study_chart = resolve_lesson_study_flowchart(lesson)

    st.markdown("#### 📊 Concept Diagram")
    st.caption("Colour-coded flowchart of the main lesson ideas.")
    _render_mermaid(concept_chart, height=estimate_flowchart_height(concept_chart))

    st.markdown("#### 🎨 Study Diagram")
    st.caption("Section flowchart with labelled facts from this lesson.")
    _render_mermaid(study_chart, height=estimate_flowchart_height(study_chart))

    big_idea = lesson.get("big_idea", "")
    if big_idea:
        st.markdown(
            section_card_html(
                "Big Idea",
                _plain_lesson_text(big_idea),
                "introduction",
                bullet_mode=bullet_mode,
            ),
            unsafe_allow_html=True,
        )

    for idx, section in enumerate(sections):
        title = section.get("title", "") or f"Section {idx + 1}"
        body = section.get("body", "")
        box = (section.get("box") or "none").lower()
        variant = classify_section(title, box, idx)
        st.markdown(f'<span id="sec_{idx}"></span>', unsafe_allow_html=True)
        if body:
            st.markdown(
                section_card_html(
                    title,
                    _plain_lesson_text(body),
                    variant,
                    bullet_mode=bullet_mode,
                ),
                unsafe_allow_html=True,
            )

    summary = lesson.get("visual_summary") or []
    st.markdown("#### Visual Summary — Colour Key")
    legend_defaults = [
        {"icon": "🟦", "color_name": "Topic", "idea": "Main lesson theme", "hex": "#334155"},
        {"icon": "🟩", "color_name": "Concept", "idea": "Core ideas to learn", "hex": "#0F766E"},
        {"icon": "🟨", "color_name": "Example", "idea": "Worked examples", "hex": "#F59E0B"},
        {"icon": "🟪", "color_name": "Vocabulary", "idea": "Key terms", "hex": "#8B5CF6"},
        {"icon": "🟥", "color_name": "Assessment", "idea": "Exam focus points", "hex": "#EF4444"},
    ]
    items = summary if summary else legend_defaults
    cols = st.columns(min(len(items), 5) or 1)
    for index, item in enumerate(items[:5]):
        with cols[index % len(cols)]:
            icon = item.get("icon", "🔵")
            idea = item.get("idea", "")
            color = item.get("color_name", "")
            hex_color = item.get("hex", "#0F766E")
            st.markdown(
                f'<div style="background:{BG_MAIN};border-left:6px solid {hex_color};'
                f'padding:0.75rem;border-radius:16px;color:{TEXT_BODY};">'
                f'{icon} <strong style="color:{TEXT_BODY};">{html.escape(color)}</strong><br/>'
                f'<span style="font-size:0.95rem;color:{TEXT_BODY};">{html.escape(idea)}</span></div>',
                unsafe_allow_html=True,
            )


def vocabulary_to_text(data: Any) -> str:
    vocab = _as_dict(data) or {}
    lines = [f"# Vocabulary — {vocab.get('topic', 'Lesson')}", ""]
    lines.append("## 1. Word Wall")
    for word in vocab.get("word_wall") or []:
        lines.append(f"- **{word.get('term', '')}**: {word.get('definition', '')}")
    lines.append("\n## 2. Flashcards")
    for card in vocab.get("flashcards") or []:
        lines.append(f"- Front: {card.get('front', '')} | Back: {card.get('back', '')}")
    lines.append("\n## 3. Picture Words")
    for row in vocab.get("picture_words") or []:
        lines.append(f"- {row.get('term', '')}: {row.get('draw_this', '')}")
    lines.append("\n## 4. Say · Spell · Use")
    practice = _prepare_practice(vocab.get("word_wall") or [], vocab.get("topic", ""))
    for index, item in enumerate(practice, 1):
        blank = _clean_practice_blank(item.get("sentence_blank", ""))
        lines.append(f"{index}. {item.get('term', '')}: {blank}")
    lines.append("\n## 5. Self-Test")
    self_test = _prepare_self_test(vocab.get("self_test") or {}, vocab.get("word_wall") or [])
    if self_test.get("matching_terms"):
        lines.append("Part A — Matching")
        for row in self_test["matching_terms"]:
            lines.append(f"{row['n']}. {row['term']}")
        for row in self_test.get("matching_definitions") or []:
            lines.append(f"{row['letter']}. {row['text']}")
    if self_test.get("fill_blanks"):
        lines.append("Part B — Fill in the blank")
        for index, sentence in enumerate(self_test["fill_blanks"], 1):
            lines.append(f"{index}. {_clean_fill_blank_display(sentence)}")
    lines.append("\n## 6. Quick Reference")
    for row in vocab.get("reference_chart") or []:
        lines.append(
            f"- **{row.get('term', '')}**: {row.get('definition', '')} "
            f"(Exam tip: {row.get('exam_tip', '')})"
        )
    lines.append("\n## 7. Concept Map")
    from concept_map_builder import _topic_and_terms

    topic, terms = _topic_and_terms(vocab)
    lines.append(f"Central topic: **{topic}**")
    lines.append("Linked terms: " + ", ".join(terms))
    lines.append("(Download HTML for the full coloured flowchart.)")
    return "\n".join(lines)


def worksheet_to_text(data: Any) -> str:
    sheet = _as_dict(data) or {}
    lines = ["# Exam Practice Worksheet", ""]
    for index, item in enumerate(sheet.get("short_answer") or [], 1):
        lines.append(f"Q{index}. ({item.get('marks', 2)} marks) {item.get('question', '')}")
    lines.append("\n## Long Answer")
    for index, item in enumerate(sheet.get("long_answer") or [], 1):
        lines.append(f"Q{index}. ({item.get('marks', 6)} marks) {item.get('question', '')}")
    return "\n".join(lines)


def lesson_to_text(data: Any) -> str:
    lesson = _as_dict(data)
    if not lesson:
        return str(data)
    parts = [f"Big Idea: {lesson.get('big_idea', '')}", ""]
    for section in lesson.get("sections") or []:
        parts.append(f"## {section.get('title', '')}")
        parts.append(section.get("body", ""))
    return "\n".join(parts)


def content_to_export(title: str, content: Any, spec_id: str) -> str:
    parsed = _coerce_dict(content) if spec_id != "original" else None
    if spec_id == "vocabulary":
        return f"# {title}\n\n{vocabulary_to_text(parsed or content)}"
    if spec_id == "worksheet":
        return f"# {title}\n\n{worksheet_to_text(parsed or content)}"
    if parsed:
        return f"# {title}\n\n{lesson_to_text(parsed)}"
    from content_renderer import strip_mermaid_for_export

    return f"# {title}\n\n{strip_mermaid_for_export(str(content))}"
