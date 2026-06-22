"""
Render structured vocabulary, worksheet, and lesson objects with native Streamlit UI.
Guarantees visible sections, colors, and diagrams (not dependent on HTML in markdown).
"""

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


def _render_svg(svg: str) -> None:
    if not svg or not svg.strip():
        return
    import streamlit.components.v1 as components

    components.html(
        f'<div style="text-align:center;padding:8px;">{svg.strip()}</div>',
        height=260,
        scrolling=True,
    )


def render_vocabulary(data: Any) -> None:
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
                    st.markdown(f"#### {emoji} **{term}**")
                    st.markdown(
                        f'<div style="background:{color};padding:10px;border-radius:8px;'
                        f'border-left:4px solid #008C95;">{word.get("definition", "")}</div>',
                        unsafe_allow_html=True,
                    )
                    visual = word.get("visual_description") or word.get("visual", "")
                    if visual:
                        st.caption(f"🎨 Picture in your mind: {visual}")

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
    for index, sentence in enumerate(fill_blanks, 1):
        st.markdown(f"{index}. {sentence}")

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

    mermaid = vocab.get("mermaid_diagram") or vocab.get("mermaid", "")
    if mermaid:
        st.markdown("### Concept Map")
        _render_mermaid(mermaid)


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
    st.markdown("### Part A — Short Answer")
    for index, item in enumerate(sheet.get("short_answer") or [], 1):
        marks = item.get("marks", 2)
        st.markdown(f"**Q{index}. ({marks} marks)** {item.get('question', '')}")
        for _ in range(int(item.get("lines", 3))):
            st.markdown("_________________________________________________________")
        st.markdown("")

    # Part B — Long answer
    st.markdown("### Part B — Long Answer")
    for index, item in enumerate(sheet.get("long_answer") or [], 1):
        marks = item.get("marks", 6)
        st.markdown(f"**Q{index}. ({marks} marks)** {item.get('question', '')}")
        for _ in range(int(item.get("lines", 8))):
            st.markdown("_________________________________________________________")
        st.markdown("")

    # Part C — Diagram
    diagram = sheet.get("diagram_question") or {}
    if diagram:
        st.markdown("### Part C — Diagram Question")
        st.markdown(
            f"**({diagram.get('marks', 4)} marks)** {diagram.get('question', '')}"
        )
        svg = diagram.get("svg_diagram") or diagram.get("svg", "")
        if svg:
            _render_svg(svg)
        st.markdown("_Label the diagram above on your answer sheet._")

    # Part D — Vocab in context
    st.markdown("### Part D — Vocabulary in Context")
    for index, item in enumerate(sheet.get("vocab_questions") or [], 1):
        marks = item.get("marks", 1)
        st.markdown(f"**{index}. ({marks} mark)** {item.get('question', '')}")
        st.markdown("Answer: _________________________________")

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

    mermaid = lesson.get("mermaid_diagram") or lesson.get("mermaid", "")
    if mermaid:
        st.markdown("#### 📊 Concept Diagram")
        _render_mermaid(mermaid)

    svg = lesson.get("svg_diagram") or lesson.get("svg", "")
    if svg:
        st.markdown("#### 🎨 Study Diagram")
        _render_svg(svg)

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
    if summary:
        st.markdown("#### Visual Summary")
        cols = st.columns(min(len(summary), 4) or 1)
        for index, item in enumerate(summary):
            with cols[index % len(cols)]:
                icon = item.get("icon", "🔵")
                idea = item.get("idea", "")
                color = item.get("color_name", "")
                st.markdown(f"{icon} **{color}**")
                st.caption(idea)


def vocabulary_to_text(data: Any) -> str:
    vocab = _as_dict(data) or {}
    lines = [f"# Vocabulary — {vocab.get('topic', 'Lesson')}", ""]
    lines.append("## Word Wall")
    for word in vocab.get("word_wall") or []:
        lines.append(f"- **{word.get('term', '')}**: {word.get('definition', '')}")
    lines.append("\n## Flashcards")
    for card in vocab.get("flashcards") or []:
        lines.append(f"- Front: {card.get('front', '')} | Back: {card.get('back', '')}")
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
