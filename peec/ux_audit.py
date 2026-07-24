"""UX + first-impression + journey audits."""

from __future__ import annotations

from typing import Any, Mapping

from peec.constants import PERSONAS


def audit_ux(adaptations: Mapping[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    sections = [s for s in (std.get("sections") or []) if isinstance(s, dict)]

    if not std.get("big_idea"):
        issues.append("First impression weak — missing opening claim.")
    if len(sections) < 6:
        issues.append("Visual hierarchy thin — too few teaching beats.")
    if not any(str(s.get("role") or "") == "visual" for s in sections) and not str(
        std.get("flowchart_svg") or ""
    ).startswith("<svg"):
        issues.append("No clear visual anchor on first scroll.")
    if not any(str(s.get("role") or "") in {"practice_question", "application"} for s in sections):
        issues.append("Journey lacks a confident practice beat.")
    if not any(str(s.get("role") or "") == "summary" for s in sections):
        issues.append("Missing calm closing summary for confidence building.")

    # Emotional / confidence close
    last_bodies = " ".join(str(s.get("body") or "") for s in sections[-2:]).lower()
    if sections and not any(w in last_bodies for w in ("you can", "proud", "ready", "check", "remember", "next")):
        issues.append("Ending does not build learner confidence.")

    return {
        "schema": "alora.peec.ux_audit.v1",
        "ok": len(issues) == 0,
        "issues": issues,
        "checks": {
            "first_impression": bool(std.get("big_idea")),
            "visual_hierarchy": len(sections) >= 6,
            "practice_beat": any(str(s.get("role") or "") in {"practice_question", "application"} for s in sections),
            "confidence_close": not any("confidence" in i for i in issues),
        },
    }


def walk_student_journeys(adaptations: Mapping[str, Any]) -> dict[str, Any]:
    """Simulate persona walkthroughs; flag confusion points."""
    findings: dict[str, list[str]] = {}

    for persona in PERSONAS:
        notes: list[str] = []
        key = {
            "age_12": "standard",
            "adhd": "adhd",
            "autism": "autism",
            "ell": "ell",
            "visual": "visual",
            "parent": "parent",
            "teacher": "teacher",
        }[persona]
        page = adaptations.get(key) if isinstance(adaptations.get(key), dict) else None
        if not page:
            notes.append(f"Missing {key} experience for {persona} journey.")
            findings[persona] = notes
            continue

        titles = " ".join(
            str(s.get("title") or "") for s in (page.get("sections") or []) if isinstance(s, dict)
        ).lower()
        blob = " ".join(
            str(s.get("body") or "") for s in (page.get("sections") or []) if isinstance(s, dict)
        ).lower()

        if persona == "adhd" and not any(w in titles for w in ("chunk", "mission", "minute", "checklist")):
            notes.append("ADHD learner may lose pacing — needs visible chunks.")
        if persona == "autism" and not any(w in titles for w in ("routine", "finished", "what we will")):
            notes.append("Autistic learner needs predictable routine language.")
        if persona == "ell" and "key words" not in titles and "word" not in titles:
            notes.append("ELL learner needs key words before dense explanation.")
        if persona == "visual" and "diagram" not in blob and "see" not in titles:
            notes.append("Visual learner lacks an early diagram-led moment.")
        if persona == "parent" and "home" not in blob and "child" not in blob:
            notes.append("Parent journey lacks home coaching voice.")
        if persona == "teacher" and "differentiat" not in blob and "misconception" not in blob:
            notes.append("Teacher journey lacks differentiation guidance.")
        if persona == "age_12":
            long_sents = sum(1 for s in blob.split(".") if len(s.split()) > 28)
            if long_sents >= 4:
                notes.append("12-year-old may hit cognitive overload — shorten sentences.")

        findings[persona] = notes

    confusion = {k: v for k, v in findings.items() if v}
    return {
        "schema": "alora.peec.student_journey.v1",
        "ok": not confusion,
        "by_persona": findings,
        "confusion_points": confusion,
    }
