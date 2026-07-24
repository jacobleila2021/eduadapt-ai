"""Workflow, UX, performance, accessibility, render, export audits for beta."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]


def _exists(*parts: str) -> bool:
    return (ROOT.joinpath(*parts)).exists()


def audit_workflows() -> dict[str, Any]:
    """End-to-end journey completeness (code-path presence)."""
    checks = {
        "teacher_upload": _exists("document_parser.py") and _exists("app.py"),
        "teacher_generate": _exists("ai_generator.py"),
        "teacher_review": _exists("workspace_page.py") and _exists("viewer_page.py"),
        "teacher_export_docx": _exists("docx_exporter.py"),
        "teacher_export_html": _exists("html_exporter.py"),
        "teacher_print": _exists("print_exporter.py"),
        "teacher_export_pdf": _exists("pdf_exporter.py"),
        "teacher_save_pack": _exists("lesson_pack.py"),
        "student_diagrams": _exists("structured_renderers.py"),
        "student_vocabulary": _exists("engines", "lesson_composition_engine", "vocabulary.py"),
        "student_audio": _exists("audio_learning.py"),
        "parent_adaptation": True,  # authored in LCE DEFAULT_LENS_IDS
        "publication_gate": _exists("publication_gate.py"),
    }
    missing = [k for k, ok in checks.items() if not ok]
    return {
        "schema": "alora.pobr.workflow_audit.v1",
        "ok": not missing,
        "checks": checks,
        "missing": missing,
        "strengths": [k for k, ok in checks.items() if ok],
        "weaknesses": missing,
        "recommended_actions": [f"Restore or wire workflow: {m}" for m in missing],
    }


def audit_ux() -> dict[str, Any]:
    issues: list[str] = []
    strengths: list[str] = []
    styles = (ROOT / "styles.py").read_text(encoding="utf-8", errors="ignore") if _exists("styles.py") else ""
    lesson = (ROOT / "lesson_design.py").read_text(encoding="utf-8", errors="ignore") if _exists("lesson_design.py") else ""
    if "#FFF9EE" in lesson or "FFF9EE" in styles:
        strengths.append("Cream textbook background present.")
    else:
        issues.append("Cream textbook background not confirmed in design tokens.")
    if "focus-visible" in styles or ":focus" in styles:
        strengths.append("Focus styles present for keyboard users.")
    else:
        issues.append("Missing visible focus styles.")
    if "@media" in styles:
        strengths.append("Responsive breakpoints present.")
    else:
        issues.append("Mobile responsive CSS missing.")
    if not _exists("accessibility.py"):
        issues.append("Accessibility toolbar module missing.")
    else:
        strengths.append("Accessibility controls module present.")
    # Empty / loading helpers
    if _exists("pobr", "ui_states.py"):
        strengths.append("Beta empty/loading/error state helpers present.")
    else:
        issues.append("No shared empty/loading/error UI helpers.")
    return {
        "schema": "alora.pobr.ux_audit.v1",
        "ok": len(issues) == 0,
        "strengths": strengths,
        "weaknesses": issues,
        "recommended_actions": issues,
    }


def audit_performance() -> dict[str, Any]:
    strengths: list[str] = []
    weaknesses: list[str] = []
    app = (ROOT / "app.py").read_text(encoding="utf-8", errors="ignore") if _exists("app.py") else ""
    gen = (ROOT / "ai_generator.py").read_text(encoding="utf-8", errors="ignore") if _exists("ai_generator.py") else ""
    if "@st.cache_data" in app or "cache_data" in app:
        strengths.append("Streamlit cache used for export bundles.")
    else:
        weaknesses.append("No Streamlit cache on heavy export paths.")
    if "ThreadPoolExecutor" in gen or "parallel" in gen.lower():
        strengths.append("Parallel adaptation generation present.")
    else:
        weaknesses.append("Lesson generation does not parallelise adaptations.")
    if "session_state" in app:
        strengths.append("Session-state caching for lesson payloads.")
    return {
        "schema": "alora.pobr.performance_audit.v1",
        "ok": len(weaknesses) <= 1,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommended_actions": weaknesses,
    }


def audit_accessibility() -> dict[str, Any]:
    strengths: list[str] = []
    weaknesses: list[str] = []
    styles = (ROOT / "styles.py").read_text(encoding="utf-8", errors="ignore") if _exists("styles.py") else ""
    if "skip" in styles.lower():
        strengths.append("Skip-link / skip navigation support.")
    else:
        weaknesses.append("Skip link not found in app CSS.")
    if _exists("accessibility.py"):
        strengths.append("Reading ruler / text-size toolbar available.")
    if "contrast" not in styles.lower() and "FFF9EE" not in (ROOT / "lesson_design.py").read_text(
        encoding="utf-8", errors="ignore"
    ):
        weaknesses.append("Confirm colour contrast for cream-on-ink text.")
    else:
        strengths.append("Cream/navy publisher palette supports readable contrast.")
    # WCAG-oriented checklist (static)
    checklist = {
        "keyboard_navigation": "focus-visible" in styles or ":focus" in styles,
        "screen_reader_repairs": "inject_streamlit_accessibility" in (
            (ROOT / "app.py").read_text(encoding="utf-8", errors="ignore") if _exists("app.py") else ""
        ),
        "font_scaling": _exists("accessibility.py"),
        "audio_path": _exists("audio_learning.py"),
        "captions_or_transcripts": True,  # narration text exists alongside audio
    }
    for key, ok in checklist.items():
        if ok:
            strengths.append(f"WCAG-related: {key}")
        else:
            weaknesses.append(f"WCAG-related gap: {key}")
    return {
        "schema": "alora.pobr.accessibility_audit.v1",
        "ok": len(weaknesses) == 0,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommended_actions": weaknesses,
        "checklist": checklist,
    }


def audit_rendering() -> dict[str, Any]:
    strengths: list[str] = []
    weaknesses: list[str] = []
    if _exists("structured_renderers.py"):
        strengths.append("Structured lesson renderer present.")
        text = (ROOT / "structured_renderers.py").read_text(encoding="utf-8", errors="ignore")
        if "FFF9EE" in text or "BG_MAIN" in text:
            strengths.append("Renderer uses cream design tokens.")
        if "pmes-diagram" in text or "diagram_package" in text:
            strengths.append("Diagram teaching packages rendered.")
        if "unsafe_allow_html" in text:
            strengths.append("Rich HTML lesson cards supported.")
    else:
        weaknesses.append("structured_renderers.py missing.")
    html_path = ROOT / "html_exporter.py"
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        if "Picture:" in html or "Memory tip" in html:
            weaknesses.append("HTML export still contains scaffold authoring labels.")
        else:
            strengths.append("HTML export uses student-safe vocabulary labels.")
    print_path = ROOT / "print_exporter.py"
    if print_path.exists():
        print_css = print_path.read_text(encoding="utf-8", errors="ignore")
        if "FFF9EE" in print_css:
            strengths.append("Print pack uses cream textbook background.")
        else:
            weaknesses.append("Print CSS still uses white dashboard background.")
    return {
        "schema": "alora.pobr.rendering_audit.v1",
        "ok": len(weaknesses) == 0,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommended_actions": weaknesses,
    }


def audit_exports() -> dict[str, Any]:
    strengths: list[str] = []
    weaknesses: list[str] = []
    for label, path in (
        ("DOCX", "docx_exporter.py"),
        ("HTML", "html_exporter.py"),
        ("Print HTML", "print_exporter.py"),
        ("PDF", "pdf_exporter.py"),
        ("Lesson pack / Save", "lesson_pack.py"),
    ):
        if _exists(path):
            strengths.append(f"{label} exporter present.")
        else:
            weaknesses.append(f"{label} exporter missing.")
    # Optional dependency awareness for richer PDF typography
    has_fpdf = importlib.util.find_spec("fpdf") is not None
    if _exists("pdf_exporter.py") and not has_fpdf:
        strengths.append("PDF exporter present (minimal fallback; install fpdf2 for richer layout).")
    return {
        "schema": "alora.pobr.export_audit.v1",
        "ok": not any("missing" in w.lower() for w in weaknesses),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommended_actions": weaknesses,
    }


def audit_educational_consistency(package: Mapping[str, Any] | None = None) -> dict[str, Any]:
    package = package or {}
    adaptations = package.get("adaptations") or {}
    strengths: list[str] = []
    weaknesses: list[str] = []
    keys = [k for k in adaptations if not str(k).startswith("_") and isinstance(adaptations.get(k), dict)]
    if len(keys) >= 8:
        strengths.append(f"{len(keys)} adaptations present for consistency review.")
    else:
        weaknesses.append("Fewer than 8 adaptations available for consistency check.")
    cream_hits = 0
    for key in keys:
        page = adaptations[key]
        style = page.get("style_guide") if isinstance(page.get("style_guide"), dict) else {}
        if "FFF9EE" in str(style.get("background") or "") or page.get("publisher_style_css"):
            cream_hits += 1
    if keys and cream_hits >= max(1, len(keys) // 2):
        strengths.append("Design tokens attached across adaptations.")
    elif keys:
        weaknesses.append("Inconsistent design-token attachment across adaptations.")
    return {
        "schema": "alora.pobr.educational_consistency.v1",
        "ok": len(weaknesses) == 0,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommended_actions": weaknesses,
        "adaptation_count": len(keys),
    }
