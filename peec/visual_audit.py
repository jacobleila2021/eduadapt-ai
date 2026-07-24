"""Visual learning audit — every visual must teach."""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.publisher_remediation import adaptation_has_generic_diagram
from uevb.visual_audit import audit_visual_quality


def audit_visual_learning(adaptations: Mapping[str, Any]) -> dict[str, Any]:
    base = audit_visual_quality(adaptations)
    issues = list(base.get("issues") or [])

    for key, value in adaptations.items():
        if key.startswith("_") or not isinstance(value, dict) or key in {"vocabulary", "parent"}:
            continue
        svg = str(
            value.get("flowchart_svg")
            or value.get("svg_diagram")
            or value.get("concept_map_svg")
            or ""
        )
        pkg = value.get("diagram_package") if isinstance(value.get("diagram_package"), dict) else {}
        if svg.startswith("<svg"):
            if adaptation_has_generic_diagram(value):
                issues.append(f"{key}: decorative diagram — does not teach the concept.")
            if not pkg.get("explanation") or not pkg.get("practice_question"):
                issues.append(f"{key}: visual lacks explanation/practice — purpose unclear.")
            # Section must reference the diagram somewhere
            blob = " ".join(
                str(s.get("body") or "") + " " + str(s.get("title") or "")
                for s in (value.get("sections") or [])
                if isinstance(s, dict)
            ).lower()
            if "diagram" not in blob and "see" not in blob and "map" not in blob:
                issues.append(f"{key}: diagram not referenced in the teaching flow.")

    # Deduplicate
    issues = list(dict.fromkeys(issues))
    ok = base.get("ok") and not any("decorative" in i or "purpose unclear" in i for i in issues)
    return {
        "schema": "alora.peec.visual_design_audit.v1",
        "ok": bool(ok),
        "visual_quality_score": base.get("visual_quality_score"),
        "issues": issues,
        "design_system": base.get("design_system"),
        "summary": (
            "Every visual teaches."
            if ok
            else "Some visuals are decorative or unexplained."
        ),
    }
