"""
Render structured vocabulary, worksheet, and lesson objects with native Streamlit UI.
Guarantees visible sections, colors, and diagrams (not dependent on HTML in markdown).
"""

from __future__ import annotations

import html
import json
from typing import Any

import streamlit as st

from content_renderer import _render_mermaid

_CARD_COLORS = ["#e6f7f8", "#fff8e1", "#f3e5f5", "#e8f5e9", "#fce4ec", "#e3f2fd"]
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
    """Deterministic hub-and-spoke SVG built from the lesson's own sections.

    Guarantees a real, labelled educational diagram (never a blank box) when the
    AI fails to return a valid mermaid/svg diagram.
    """
    from concept_map_builder import build_vocabulary_concept_map_svg

    topic = (
        lesson.get("topic")
        or lesson.get("title")
        or (lesson.get("big_idea") or "Lesson")[:40]
    )
    terms = []
    for section in lesson.get("sections") or []:
        t = (section.get("title") or "").strip()
        if t and t.lower() not in {x.lower() for x in terms}:
            terms.append(t)
    if not terms:
        for kp in lesson.get("key_points") or lesson.get("objectives") or []:
            if isinstance(kp, str) and kp.strip():
                terms.append(kp.strip()[:24])
    return build_vocabulary_concept_map_svg(
        {"topic": topic, "word_wall": [{"term": t} for t in terms[:8]]}
    )


def _word_illustration_svg(term: str, emoji: str, color: str) -> str:
    safe = html.escape(term[:24])
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="280" height="140" viewBox="0 0 280 140" role="img" aria-label="{safe}">
      <rect x="8" y="8" width="264" height="124" rx="14" fill="{color}" stroke="#0F766E" stroke-width="2"/>
      <text x="140" y="58" text-anchor="middle" font-size="36">{emoji}</text>
      <text x="140" y="98" text-anchor="middle" font-size="14" fill="#334155" font-family="Verdana,sans-serif">{safe}</text>
    </svg>
    """


def _lookup_answer(answer_key: list, ref: str) -> str:
    for item in answer_key or []:
        if item.get("question_ref", "").strip().lower() == ref.strip().lower():
            return item.get("model_answer", "")
        if ref.lower() in (item.get("question_ref") or "").lower():
            return item.get("model_answer", "")
    return ""


def _show_answer_button(label: str, answer: str, key: str) -> None:
    if not answer:
        return
    reveal_key = f"revealed_{key}"
    if st.button(f"Show Answer — {label}", key=f"btn_{key}", type="secondary"):
        st.session_state[reveal_key] = True
    if st.session_state.get(reveal_key):
        st.success(answer)


def _render_svg(svg: str, height: int = 260) -> None:
    if not svg or not svg.strip():
        return
    st.markdown(
        f'<div style="display:flex;justify-content:center;align-items:center;'
        f'max-width:100%;overflow-x:auto;padding:1rem 0;">{svg.strip()}</div>',
        unsafe_allow_html=True,
    )


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
    st.caption("Study each section in order before attempting the Worksheet tab.")

    # --- 1. Word Wall ---
    st.markdown("### 1. Word Wall — Study First")
    word_wall = vocab.get("word_wall") or []
    if not word_wall:
        st.warning("No word wall terms generated.")
    else:
        cols = st.columns(2)
        for index, word in enumerate(word_wall):
            color = _CARD_COLORS[index % len(_CARD_COLORS)]
            with cols[index % 2]:
                with st.container(border=True):
                    emoji = word.get("emoji", "📌")
                    term = word.get("term", "Term")
                    st.markdown(
                        f'<div style="color:#000000;font-weight:800;font-size:1.15rem;">'
                        f'{emoji} {html.escape(term)}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        _word_illustration_svg(term, emoji, color),
                        unsafe_allow_html=True,
                    )
                    definition = word.get("definition", "")
                    child_note = word.get("child_friendly") or word.get("visual_description") or ""
                    example = word.get("example") or word.get("example_sentence") or ""
                    st.markdown(
                        f'<div style="background:{color};padding:12px;border-radius:8px;'
                        f'border-left:4px solid #0F766E;color:#000000;font-weight:500;'
                        f'font-size:1rem;line-height:1.6;">'
                        f'<strong style="color:#000000;">Definition:</strong> '
                        f'{html.escape(definition)}'
                        + (
                            f'<br/><strong style="color:#000000;">In simple words:</strong> '
                            f'{html.escape(child_note)}'
                            if child_note
                            else ""
                        )
                        + (
                            f'<br/><strong style="color:#000000;">Example:</strong> '
                            f'<em style="color:#000000;">{html.escape(example)}</em>'
                            if example
                            else ""
                        )
                        + "</div>",
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
    st.markdown("### 3. Picture Words — Visual Memory")
    picture_words = vocab.get("picture_words") or []
    if picture_words:
        st.table(
            [
                {
                    "Term": row.get("term", ""),
                    "Color cue": row.get("color_cue", ""),
                    "Draw / imagine": row.get("draw_this") or row.get("visual", ""),
                    "Label": row.get("label", ""),
                }
                for row in picture_words
            ]
        )

    # --- 4. Say · Spell · Use ---
    st.markdown("### 4. Say It · Spell It · Use It")
    practice = vocab.get("practice") or vocab.get("say_spell_use") or []
    for item in practice:
        term = item.get("term", "")
        st.markdown(f"**{term}** — *{item.get('pronunciation', '')}* ({item.get('syllables', '')})")
        blank = item.get("sentence_blank") or item.get("sentence", "")
        if blank:
            st.markdown(f"_{blank}_")

    # --- 5. Self-Test ---
    st.markdown("### 5. Match & Review (Self-Test)")
    self_test = vocab.get("self_test") or {}
    matching = self_test.get("matching_prompt", "") or self_test.get("matching", "")
    if matching:
        st.markdown(matching if isinstance(matching, str) else str(matching))
    fill_blanks = self_test.get("fill_blanks") or []
    flashcards = vocab.get("flashcards") or []
    for index, sentence in enumerate(fill_blanks, 1):
        st.markdown(f"{index}. {sentence}")
        if index <= len(flashcards):
            ans = flashcards[index - 1].get("back") or flashcards[index - 1].get("definition", "")
            _show_answer_button(f"Vocab Q{index}", ans, f"{key_prefix}_ans_{index}")

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
    from concept_map_builder import build_vocabulary_concept_map_svg, render_concept_map_streamlit

    render_concept_map_streamlit(vocab)
    with st.expander("Print-style flowchart (full diagram)", expanded=False):
        _render_svg(build_vocabulary_concept_map_svg(vocab))


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
    st.markdown("## 📝 Exam Practice Paper")
    col1, col2, col3 = st.columns(3)
    col1.metric("Subject", header.get("subject", "—"))
    col2.metric("Time allowed", header.get("time_allowed", "45 min"))
    col3.metric("Total marks", header.get("total_marks", "—"))
    st.text_input("Name", key=f"{key_prefix}_name", placeholder="Student name")
    st.text_input("Date", key=f"{key_prefix}_date", placeholder="Date")

    # Part A — Short answer
    answer_key = sheet.get("answer_key") or []
    st.markdown("### Part A — Short Answer")
    for index, item in enumerate(sheet.get("short_answer") or [], 1):
        marks = item.get("marks", 2)
        st.markdown(f"**Q{index}. ({marks} marks)** {item.get('question', '')}")
        for _ in range(int(item.get("lines", 3))):
            st.markdown("_________________________________________________________")
        ref = f"Part A Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_sa_{index}")
        st.markdown("")

    # Part B — Long answer
    st.markdown("### Part B — Long Answer")
    for index, item in enumerate(sheet.get("long_answer") or [], 1):
        marks = item.get("marks", 6)
        st.markdown(f"**Q{index}. ({marks} marks)** {item.get('question', '')}")
        for _ in range(int(item.get("lines", 8))):
            st.markdown("_________________________________________________________")
        ref = f"Part B Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_la_{index}")
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
        _show_answer_button("Part C", dia_ans, f"{key_prefix}_dia")

    # Part D — Vocab in context
    st.markdown("### Part D — Vocabulary in Context")
    for index, item in enumerate(sheet.get("vocab_questions") or [], 1):
        marks = item.get("marks", 1)
        st.markdown(f"**{index}. ({marks} mark)** {item.get('question', '')}")
        st.markdown("Answer: _________________________________")
        ref = f"Part D Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_vq_{index}")

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


def render_lesson(data: Any) -> None:
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

    big_idea = lesson.get("big_idea", "")
    if big_idea:
        st.info(f"💡 **Big Idea:** {big_idea}")

    svg = lesson.get("svg_diagram") or lesson.get("svg", "")
    mermaid = lesson.get("mermaid_diagram") or lesson.get("mermaid", "")
    has_good_mermaid = _valid_mermaid(mermaid)
    has_good_svg = _valid_svg_diagram(svg)

    if has_good_mermaid:
        st.markdown("#### 📊 Concept Diagram")
        _render_mermaid(mermaid)

    if has_good_svg:
        st.markdown("#### 🎨 Study Diagram")
        _render_svg(svg)

    if not has_good_mermaid and not has_good_svg:
        # Never show a blank/placeholder: build a real diagram from the lesson itself.
        st.markdown("#### 📊 Concept Diagram")
        _render_svg(_fallback_lesson_diagram(lesson))

    for section in lesson.get("sections") or []:
        title = section.get("title", "")
        body = section.get("body", "")
        box = (section.get("box") or "none").lower()
        if title:
            st.markdown(f"#### {title}")
        renderer = _BOX_RENDERERS.get(box)
        if renderer and body:
            renderer(body)
        elif body:
            st.markdown(body)

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
                f'<div style="background:#F4E9D8;border-left:5px solid {hex_color};'
                f'padding:0.65rem;border-radius:8px;">{icon} <strong>{color}</strong><br/>'
                f'<span style="font-size:0.9rem;">{html.escape(idea)}</span></div>',
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
    for item in vocab.get("practice") or []:
        lines.append(f"- {item.get('term', '')}: {item.get('sentence_blank', '')}")
    lines.append("\n## 5. Self-Test")
    self_test = vocab.get("self_test") or {}
    if self_test.get("matching_prompt"):
        lines.append(str(self_test["matching_prompt"]))
    for sentence in self_test.get("fill_blanks") or []:
        lines.append(f"- {sentence}")
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
