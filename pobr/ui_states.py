"""Shared empty / loading / error UI copy for beta polish."""

from __future__ import annotations


def empty_lesson_html() -> str:
    return """
<div class="pobr-empty" style="background:#FFF9EE;border:1px solid #E2D6C2;border-radius:16px;
padding:1.5rem 1.6rem;color:#1C2A3A;font-family:Candara,Calibri,sans-serif;">
  <h3 style="margin:0 0 0.4rem;color:#0B2E59;font-family:Georgia,serif;">No lesson yet</h3>
  <p style="margin:0;line-height:1.55;">Upload a lesson or open a sample, then choose
  <strong>Generate Adaptations</strong>. Your publisher-quality versions will appear here.</p>
</div>
""".strip()


def loading_generation_caption() -> str:
    return (
        "Building your lesson pack — verified knowledge first, then teaching adaptations. "
        "This usually takes a few minutes. Keep this tab open."
    )


def export_error_caption(detail: str = "") -> str:
    base = "Export could not finish. Try Download This Version (Word) or Print HTML, then retry the ZIP pack."
    return f"{base} {detail}".strip()


def zip_soft_fail_caption() -> str:
    return (
        "The full ZIP pack is temporarily unavailable. "
        "You can still download Word, Print HTML, PDF, or Save Pack for this version."
    )
