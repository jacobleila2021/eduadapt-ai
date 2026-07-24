"""Defect taxonomy and auto-remediation for RC1 (uses existing polishers only)."""

from __future__ import annotations

from typing import Any, Mapping

# Severity by learner impact
CRITICAL = "critical"
HIGH = "high"
MEDIUM = "medium"
LOW = "low"


def classify_package_defects(package: Mapping[str, Any], *, corpus_id: str = "") -> list[dict[str, Any]]:
    """Detect defects from an already-composed package — no new validators."""
    defects: list[dict[str, Any]] = []
    adaptations = package.get("adaptations") or {}
    topic = str(
        (package.get("intelligence_board") or {}).get("topic")
        or (package.get("clg") or {}).get("topic")
        or corpus_id
        or "lesson"
    )

    def add(severity: str, code: str, detail: str, *, auto_fixable: bool = False) -> None:
        defects.append(
            {
                "severity": severity,
                "code": code,
                "detail": detail,
                "topic": topic,
                "corpus_id": corpus_id,
                "auto_fixable": auto_fixable,
            }
        )

    if not package.get("ok"):
        add(CRITICAL, "publication_not_ready", "Package failed publication_ready gate.", auto_fixable=True)

    pmes = package.get("pmes") or {}
    if pmes and pmes.get("approved") is False:
        add(CRITICAL, "pmes_rejected", "PMES did not approve the lesson.", auto_fixable=True)

    uevb = package.get("uevb") or {}
    if uevb and uevb.get("ok") is False:
        add(HIGH, "uevb_gate_failed", "UEVB release gate failed.", auto_fixable=True)

    peec = package.get("peec") or {}
    if peec and peec.get("ok") is False:
        plan = peec.get("remediation_plan") or []
        add(
            HIGH,
            "peec_open_items",
            f"PEEC still has {len(plan)} open experience items.",
            auto_fixable=True,
        )

    # Adaptation coverage — match production LCE / UEVB adaptation set
    required = (
        "standard",
        "vocabulary",
        "adhd",
        "autism",
        "dyslexia",
        "ell",
        "visual",
        "auditory",
        "teacher",
        "parent",
        "worksheet",
        "ld",
    )
    for key in required:
        if key not in adaptations or not isinstance(adaptations.get(key), dict):
            add(CRITICAL, "missing_adaptation", f"Missing adaptation: {key}", auto_fixable=False)

    # Learner-facing content defects
    for key, page in adaptations.items():
        if str(key).startswith("_") or not isinstance(page, dict):
            continue
        if key == "vocabulary":
            wall = page.get("word_wall") or []
            if len(wall) < 4:
                add(HIGH, "thin_vocabulary", f"{key}: fewer than 4 vocabulary cards.", auto_fixable=True)
            continue
        if key == "worksheet":
            dq = page.get("diagram_question") if isinstance(page.get("diagram_question"), dict) else {}
            if not str(dq.get("svg_diagram") or "").startswith("<svg"):
                add(HIGH, "worksheet_diagram_missing", "Worksheet missing SVG diagram.", auto_fixable=True)
            continue

        sections = [s for s in (page.get("sections") or []) if isinstance(s, dict)]
        if len(sections) < 3:
            add(HIGH, "thin_lesson", f"{key}: fewer than 3 sections.", auto_fixable=True)

        bodies = [str(s.get("body") or "") for s in sections]
        # Duplicate paragraphs
        seen: set[str] = set()
        for body in bodies:
            norm = " ".join(body.lower().split())
            if len(norm) > 40 and norm in seen:
                add(HIGH, "duplicate_paragraph", f"{key}: duplicate paragraph detected.", auto_fixable=True)
                break
            seen.add(norm)

        blob = " ".join(bodies).lower()
        for phrase in ("notice how", "students will", "worth mastering", "picture:", "memory tip"):
            if phrase in blob:
                add(CRITICAL, "scaffold_leak", f"{key}: scaffold/AI language “{phrase}”.", auto_fixable=True)

        svg = str(page.get("flowchart_svg") or page.get("svg_diagram") or "")
        if key not in {"parent"} and not svg.startswith("<svg"):
            add(HIGH, "missing_diagram", f"{key}: missing SVG diagram.", auto_fixable=True)
        pkg = page.get("diagram_package") if isinstance(page.get("diagram_package"), dict) else {}
        if svg.startswith("<svg") and not pkg.get("practice_question"):
            add(MEDIUM, "diagram_not_teaching", f"{key}: diagram lacks practice question.", auto_fixable=True)

        # Colour / cream token
        style = page.get("style_guide") if isinstance(page.get("style_guide"), dict) else {}
        if key in {"standard", "visual"} and style and "FFF9EE" not in str(style.get("background") or "").upper():
            add(MEDIUM, "colour_inconsistency", f"{key}: style guide background not cream.", auto_fixable=True)

    # Export smoke — PDF path must exist (module level)
    try:
        from pdf_exporter import export_tab_pdf

        std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
        if std:
            pdf = export_tab_pdf(str(std.get("topic") or topic), std, "standard")
            if not pdf.startswith(b"%PDF"):
                add(CRITICAL, "broken_pdf_export", "PDF export did not return a PDF.", auto_fixable=False)
    except Exception as exc:  # noqa: BLE001
        add(CRITICAL, "pdf_export_exception", f"PDF export failed: {exc}", auto_fixable=False)

    return defects


def auto_resolve_critical_high(
    package: dict[str, Any],
    defects: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Apply existing remediations only — PMES/PEEC polishers, no new systems."""
    resolved: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    board = package.get("intelligence_board") or {}
    adaptations = dict(package.get("adaptations") or {})

    needs_peec = any(
        d.get("auto_fixable") and d.get("severity") in {CRITICAL, HIGH} for d in defects
    )
    if needs_peec and adaptations:
        try:
            from peec import apply_peec

            peec = apply_peec(
                adaptations,
                board=board,
                pmes_report=package.get("publisher_review_report") or package.get("pmes") or {},
                write_reports=False,
                max_passes=2,
            )
            adaptations = peec.get("adaptations") or adaptations
            package = dict(package)
            package["adaptations"] = adaptations
            package["peec"] = {
                "ok": peec.get("ok"),
                "remediation_plan": (peec.get("audit") or {}).get("remediation_plan"),
            }
        except Exception:  # noqa: BLE001
            pass

        try:
            from engines.lesson_composition_engine.pmes import run_pmes

            pmes = run_pmes(adaptations, board=board, max_passes=2)
            adaptations = pmes.get("adaptations") or adaptations
            package["adaptations"] = adaptations
            package["publisher_review_report"] = pmes.get("publisher_review_report")
            package["pmes"] = {
                "approved": bool(pmes.get("publication_ready")),
                "version": pmes.get("pmes_version"),
            }
        except Exception:  # noqa: BLE001
            pass

    # Re-scan
    rescanned = classify_package_defects(package, corpus_id=str(package.get("corpus_id") or ""))
    open_codes = {(d["code"], d.get("topic"), d.get("detail")) for d in rescanned}
    for d in defects:
        key = (d["code"], d.get("topic"), d.get("detail"))
        if d.get("severity") in {CRITICAL, HIGH} and d.get("auto_fixable") and key not in open_codes:
            resolved.append({**d, "status": "resolved"})
        elif d.get("severity") in {CRITICAL, HIGH} and not d.get("auto_fixable"):
            remaining.append({**d, "status": "open"})
        elif key in open_codes:
            remaining.append({**d, "status": "open"})
        else:
            resolved.append({**d, "status": "resolved"})

    # Keep medium/low documented
    for d in rescanned:
        if d.get("severity") in {MEDIUM, LOW}:
            remaining.append({**d, "status": "documented"})

    package["ok"] = not any(
        d.get("severity") == CRITICAL and d.get("status") == "open" for d in remaining
    )
    return package, resolved, remaining
