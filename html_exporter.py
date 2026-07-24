"""
Rich HTML exports — LD-friendly print layout with colours and clear sections.
"""

import html
from typing import Any

from concept_map_builder import vocabulary_concept_map_html_block
from structured_renderers import _coerce_dict

_CARD_COLORS = ["#e6f7f8", "#fff8e1", "#f3e5f5", "#e8f5e9", "#fce4ec", "#e3f2fd"]
_BOX_COLORS = {
    "teal": ("#e6f7f8", "#008C95"),
    "blue": ("#e3f2fd", "#0B2E59"),
    "green": ("#e8f5e9", "#2e7d32"),
    "orange": ("#fff3e0", "#e65100"),
}


def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;600;700&display=swap');
  body {{
    font-family: Lexend, Arial, Verdana, sans-serif;
    font-size: 17px; line-height: 1.85; letter-spacing: 0.02em;
    color: #0B2E59; max-width: 820px; margin: 0 auto; padding: 2rem 1.5rem;
    background: #FFF9EE;
  }}
  h1 {{ color: #008C95; font-size: 1.75rem; border-bottom: 4px solid #008C95;
        padding-bottom: 0.5rem; margin-bottom: 1.5rem; }}
  h2 {{ color: #0B2E59; font-size: 1.25rem; margin-top: 2rem; page-break-after: avoid; }}
  h3 {{ color: #008C95; font-size: 1.1rem; }}
  .card {{ padding: 1rem 1.2rem; margin: 0.75rem 0; border-radius: 10px;
           border-left: 5px solid #008C95; page-break-inside: avoid; }}
  .big-idea {{ background: #e6f7f8; border-left-color: #008C95; font-weight: 600; }}
  .section-box {{ margin: 1rem 0; padding: 1rem; border-radius: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 15px; }}
  th {{ background: #0B2E59; color: white; padding: 0.6rem; text-align: left; }}
  td {{ border: 1px solid #c0c0c0; padding: 0.6rem; vertical-align: top; }}
  .answer-line {{ border-bottom: 2px dotted #008C95; height: 1.8rem; margin: 0.4rem 0; }}
  .meta {{ background: #0B2E59; color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; }}
  .concept-map {{ text-align: center; margin: 1.5rem auto 2rem; page-break-inside: avoid; }}
  .concept-map svg {{ max-width: 100%; height: auto; display: block; margin: 0 auto; }}
  @media print {{
    body {{ font-size: 13pt; background: #FFF9EE; }}
    h2 {{ page-break-before: auto; }}
    .concept-map svg {{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
  }}
</style></head><body>
<h1>{html.escape(title)}</h1>
{body}
<p style="margin-top:3rem;font-size:0.85rem;color:#666;">Alora AI — LD-friendly print pack</p>
</body></html>"""


def export_vocabulary_html(data: Any) -> str:
    vocab = _coerce_dict(data) or {}
    parts = [f'<p class="meta"><strong>Topic:</strong> {html.escape(vocab.get("topic", ""))}</p>']

    parts.append("<h2>1. Word Wall — Study First</h2>")
    for index, word in enumerate(vocab.get("word_wall") or []):
        bg = _CARD_COLORS[index % len(_CARD_COLORS)]
        parts.append(
            f'<div class="card" style="background:{bg}">'
            f'<h3>{html.escape(word.get("emoji", "📌"))} {html.escape(word.get("term", ""))}</h3>'
            f'<p>{html.escape(word.get("definition", ""))}</p>'
            f'<p><em>Draw this:</em> {html.escape(word.get("visual_description") or word.get("picture") or "")}</p></div>'
        )

    parts.append("<h2>2. Flashcards</h2><table><tr><th>Front</th><th>Back</th></tr>")
    for card in vocab.get("flashcards") or []:
        parts.append(
            f"<tr><td>{html.escape(card.get('front', ''))}</td>"
            f"<td>{html.escape(card.get('back', ''))}</td></tr>"
        )
    parts.append("</table>")

    parts.append("<h2>3. Picture Words — Lesson Visual</h2>")
    from flowchart_builder import build_vocabulary_visual_svg
    from svg_sanitizer import sanitize_svg

    visual = sanitize_svg(build_vocabulary_visual_svg(vocab))
    if visual:
        parts.append(f'<div class="concept-map">{visual}</div>')

    from structured_renderers import _clean_practice_blank, _prepare_practice, _prepare_self_test, _clean_fill_blank_display

    parts.append("<h2>4. Say · Spell · Use</h2>")
    practice = _prepare_practice(vocab.get("word_wall") or [], vocab.get("topic", ""))
    for index, item in enumerate(practice, 1):
        blank = _clean_practice_blank(item.get("sentence_blank", ""))
        parts.append(
            f"<p><strong>{index}. {html.escape(item.get('term', ''))}</strong> — "
            f"<em>{html.escape(blank)}</em></p>"
        )

    parts.append("<h2>5. Self-Test</h2>")
    st = _prepare_self_test(vocab.get("self_test") or {}, vocab.get("word_wall") or [])
    if st.get("matching_terms"):
        parts.append("<p><strong>Part A — Matching</strong></p>")
        for row in st["matching_terms"]:
            parts.append(f"<p>{row['n']}. {html.escape(row['term'])}</p>")
        for row in st.get("matching_definitions") or []:
            parts.append(f"<p>{row['letter']}. {html.escape(row['text'])}</p>")
    if st.get("fill_blanks"):
        parts.append("<p><strong>Part B — Fill in the blank</strong></p>")
        for index, sentence in enumerate(st["fill_blanks"], 1):
            parts.append(f"<p>{index}. {html.escape(_clean_fill_blank_display(sentence))}</p>")

    parts.append("<h2>6. Quick Reference</h2><table><tr><th>Term</th><th>Definition</th><th>Exam tip</th></tr>")
    for row in vocab.get("reference_chart") or []:
        parts.append(
            f"<tr><td>{html.escape(row.get('term', ''))}</td>"
            f"<td>{html.escape(row.get('definition', ''))}</td>"
            f"<td>{html.escape(row.get('exam_tip', ''))}</td></tr>"
        )
    parts.append("</table>")

    parts.append(vocabulary_concept_map_html_block(vocab))

    return _page(f"Vocabulary — {vocab.get('topic', 'Lesson')}", "\n".join(parts))


def export_worksheet_html(data: Any) -> str:
    sheet = _coerce_dict(data) or {}
    header = sheet.get("header") or {}
    parts = [
        f'<div class="meta">Subject: {html.escape(header.get("subject", ""))} | '
        f'Topic: {html.escape(header.get("topic", ""))} | '
        f'Time: {html.escape(header.get("time_allowed", ""))} | '
        f'Marks: {html.escape(str(header.get("total_marks", "")))}</div>',
        "<p>Name: _________________________ &nbsp; Date: _________________________</p>",
    ]

    parts.append("<h2>Part A — Short Answer</h2>")
    for index, item in enumerate(sheet.get("short_answer") or [], 1):
        parts.append(
            f"<p><strong>Q{index}. ({item.get('marks', 2)} marks)</strong> "
            f"{html.escape(item.get('question', ''))}</p>"
        )
        for _ in range(int(item.get("lines", 3))):
            parts.append('<div class="answer-line"></div>')

    parts.append("<h2>Part B — Long Answer</h2>")
    for index, item in enumerate(sheet.get("long_answer") or [], 1):
        parts.append(
            f"<p><strong>Q{index}. ({item.get('marks', 6)} marks)</strong> "
            f"{html.escape(item.get('question', ''))}</p>"
        )
        for _ in range(int(item.get("lines", 8))):
            parts.append('<div class="answer-line"></div>')

    diagram = sheet.get("diagram_question") or {}
    if diagram:
        parts.append("<h2>Part C — Diagram</h2>")
        parts.append(
            f"<p>({diagram.get('marks', 4)} marks) {html.escape(diagram.get('question', ''))}</p>"
        )
        from svg_sanitizer import sanitize_svg

        safe_svg = sanitize_svg(diagram.get("svg_diagram") or diagram.get("svg") or "")
        if safe_svg:
            parts.append(f'<div class="concept-map">{safe_svg}</div>')

    parts.append("<h2>Part D — Vocabulary in Context</h2>")
    for index, item in enumerate(sheet.get("vocab_questions") or [], 1):
        parts.append(
            f"<p>{index}. ({item.get('marks', 1)} mark) {html.escape(item.get('question', ''))}</p>"
        )
        parts.append('<div class="answer-line"></div>')

    parts.append("<h2>Part E — Exam Ready Checklist</h2><ul>")
    for tip in sheet.get("student_checklist") or []:
        parts.append(f"<li>{html.escape(str(tip))}</li>")
    parts.append("</ul>")

    return _page("Exam Practice Worksheet", "\n".join(parts))


def export_lesson_html(data: Any, title: str) -> str:
    lesson = _coerce_dict(data)
    parts = []
    if lesson:
        if lesson.get("big_idea"):
            parts.append(
                f'<div class="big-idea section-box">💡 Big Idea: {html.escape(lesson["big_idea"])}</div>'
            )
        for section in lesson.get("sections") or []:
            if not isinstance(section, dict):
                parts.append(f"<p>{html.escape(str(section))}</p>")
                continue
            box = (section.get("box") or "teal").lower()
            bg, border = _BOX_COLORS.get(box, _BOX_COLORS["teal"])
            parts.append(f"<h2>{html.escape(section.get('title', ''))}</h2>")
            body = html.escape(section.get("body", "")).replace("\n", "<br>")
            parts.append(
                f'<div class="section-box" style="background:{bg};border-left:5px solid {border}">'
                f"{body}</div>"
            )
        visual_summary = lesson.get("visual_summary")
        if visual_summary:
            parts.append("<h2>Visual Summary</h2>")
            if isinstance(visual_summary, str):
                parts.append(
                    f"<pre style='white-space:pre-wrap'>{html.escape(visual_summary)}</pre>"
                )
            elif isinstance(visual_summary, list):
                parts.append(
                    "<table><tr><th>Icon</th><th>Colour</th><th>Idea</th></tr>"
                )
                for item in visual_summary:
                    if isinstance(item, dict):
                        parts.append(
                            f"<tr><td>{html.escape(str(item.get('icon', '')))}</td>"
                            f"<td>{html.escape(str(item.get('color_name', '')))}</td>"
                            f"<td>{html.escape(str(item.get('idea', '')))}</td></tr>"
                        )
                    else:
                        parts.append(
                            f"<tr><td colspan='3'>{html.escape(str(item))}</td></tr>"
                        )
                parts.append("</table>")
            else:
                parts.append(f"<p>{html.escape(str(visual_summary))}</p>")
    else:
        parts.append(f"<p>{html.escape(str(data))}</p>")

    return _page(title, "\n".join(parts))


def export_tab_html(title: str, content: Any, spec_id: str) -> str:
    if spec_id == "vocabulary":
        return export_vocabulary_html(content)
    if spec_id == "worksheet":
        return export_worksheet_html(content)
    if spec_id == "original":
        body = html.escape(str(content)).replace("\n", "<br>")
        return _page(title, f"<div>{body}</div>")
    return export_lesson_html(content, title)
