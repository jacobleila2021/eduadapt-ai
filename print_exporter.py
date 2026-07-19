"""
Print-optimised HTML — single version and combined package with cover + TOC.
"""

from __future__ import annotations

import html
from datetime import date
from typing import Any

from html_exporter import export_tab_html
from navigation import PILL_CATEGORIES, spec_by_id

NAVY = "#041B4D"
TEAL = "#14D9E5"


def _print_css() -> str:
    return """
  @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;600;700&display=swap');
  @page { margin: 1.5cm; }
  body { font-family: Lexend, Arial, sans-serif; font-size: 12pt; line-height: 1.75;
         color: #041B4D; max-width: 820px; margin: 0 auto; padding: 1rem; }
  h1 { color: #008C95; page-break-before: always; border-bottom: 3px solid #008C95;
       padding-bottom: 0.4rem; }
  h1:first-of-type { page-break-before: avoid; }
  h2 { color: #041B4D; page-break-after: avoid; }
  .cover { text-align: center; padding: 4rem 2rem; page-break-after: always;
            background: linear-gradient(135deg, #041B4D, #0a3d6e); color: white;
            border-radius: 12px; margin-bottom: 2rem; }
  .cover h1 { color: white; border: none; font-size: 2.2rem; }
  .cover .sub { color: #14D9E5; font-size: 1.1rem; margin-top: 1rem; }
  .toc { page-break-after: always; margin-bottom: 2rem; }
  .toc li { margin: 0.5rem 0; }
  .section { page-break-before: always; }
  .card { padding: 1rem; margin: 0.75rem 0; border-radius: 8px;
          border-left: 5px solid #008C95; page-break-inside: avoid; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #041B4D; color: white; padding: 0.5rem; }
  td { border: 1px solid #ccc; padding: 0.5rem; }
  @media print {
    body { background: white; }
    .no-print { display: none; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
"""


def _wrap_document(title: str, body: str, auto_print: bool = False) -> str:
    script = (
        "<script>window.onload=function(){setTimeout(function(){window.print();},400);};</script>"
        if auto_print
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>{_print_css()}</style></head><body>
{body}
<p class="no-print" style="margin-top:2rem;font-size:0.85rem;color:#666;">
  Alora AI — open in browser and press Ctrl+P (or Cmd+P) to print.</p>
{script}
</body></html>"""


def build_print_html_single(title: str, content: Any, spec_id: str, auto_print: bool = False) -> str:
    """Print-ready HTML for one adaptation."""
    inner = export_tab_html(title, content, spec_id)
    start = inner.find("<body>")
    end = inner.rfind("</body>")
    body = inner[start + 6 : end] if start >= 0 and end > start else inner
    return _wrap_document(f"Alora AI — {title}", body, auto_print=auto_print)


def build_print_html_all(
    adaptations: dict,
    lesson_text: str,
    base_name: str,
    content_for_spec,
    auto_print: bool = False,
) -> str:
    """Combined print package: cover, TOC, and primary category versions."""
    today = date.today().strftime("%d %B %Y")
    parts = [
        f'<div class="cover">',
        f'<h1>Alora AI</h1>',
        f'<p class="sub">Adaptive Learning Print Package</p>',
        f'<p>Lesson: {html.escape(base_name)}</p>',
        f'<p>Generated: {today}</p>',
        f'<p style="margin-top:2rem;font-size:0.95rem;">Built for Learning. Powered by Intelligence.</p>',
        f"</div>",
        '<div class="toc"><h2>Table of Contents</h2><ol>',
    ]

    printable_categories = list(PILL_CATEGORIES)

    for index, category in enumerate(printable_categories, 1):
        spec = spec_by_id(category["spec_ids"][0])
        if spec:
            parts.append(
                f'<li>{index}. {html.escape(category["label"])} — '
                f'{html.escape(spec["title"])}</li>'
            )
    parts.append("</ol></div>")

    for category in printable_categories:
        spec = spec_by_id(category["spec_ids"][0])
        if not spec:
            continue
        body = content_for_spec(spec, adaptations, lesson_text)
        section_html = export_tab_html(spec["title"], body, spec["id"])
        start = section_html.find("<body>")
        end = section_html.rfind("</body>")
        section_body = section_html[start + 6 : end] if start >= 0 else section_html
        parts.append(
            f'<div class="section"><h1>{html.escape(category["label"])}</h1>{section_body}</div>'
        )

    return _wrap_document(f"Alora AI Print Pack — {base_name}", "\n".join(parts), auto_print=auto_print)
