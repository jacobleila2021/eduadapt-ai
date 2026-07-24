"""Visual design audit against Alora publisher design system."""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.publisher_remediation import adaptation_has_generic_diagram
from engines.lesson_composition_engine.publisher_style_guide import CREAM, NAVY, STYLE_GUIDE
from uevb.constants import VISUAL_MIN


def audit_visual_quality(
    adaptations: Mapping[str, Any],
    *,
    style_tokens: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    style_tokens = style_tokens or STYLE_GUIDE.get("visual") or {}
    issues: list[str] = []
    page_scores: dict[str, float] = {}

    cream = str(style_tokens.get("background") or CREAM).lower()
    for key, value in adaptations.items():
        if key.startswith("_") or not isinstance(value, dict):
            continue
        score = 100.0
        local: list[str] = []

        style = value.get("style_guide") if isinstance(value.get("style_guide"), dict) else {}
        bg = str(style.get("background") or "").lower()
        if bg and bg != cream and "fff9ee" not in bg:
            score -= 15
            local.append(f"{key}: background diverges from cream textbook canvas.")

        if key == "vocabulary":
            wall = value.get("word_wall") or value.get("vocabulary_cards") or []
            if len(wall) < 4:
                score -= 20
                local.append(f"{key}: vocabulary cards insufficient.")
            weak = sum(
                1
                for c in wall[:6]
                if isinstance(c, dict)
                and (not c.get("memory_tip") or not c.get("example_sentence"))
            )
            if weak:
                score -= 10
                local.append(f"{key}: flashcards lack memorability fields.")
            if not any(isinstance(c, dict) and (c.get("pmes_flashcard") or c.get("lce_card")) for c in wall):
                score -= 8
                local.append(f"{key}: cards missing premium flashcard markers.")
        elif key == "worksheet":
            dq = value.get("diagram_question") if isinstance(value.get("diagram_question"), dict) else {}
            svg = str(dq.get("svg_diagram") or value.get("svg_diagram") or "")
            if not svg.startswith("<svg"):
                score -= 25
                local.append(f"{key}: missing exam diagram SVG.")
        elif key == "parent":
            blob = " ".join(
                str(s.get("body") or "")
                for s in (value.get("sections") or [])
                if isinstance(s, dict)
            ).lower()
            if "home" not in blob and "child" not in blob:
                score -= 15
                local.append(f"{key}: parent page lacks home coaching cues.")
        else:
            svg = str(
                value.get("flowchart_svg")
                or value.get("svg_diagram")
                or value.get("concept_map_svg")
                or ""
            )
            if not svg.startswith("<svg"):
                score -= 25
                local.append(f"{key}: missing professional SVG.")
            elif adaptation_has_generic_diagram(value):
                score -= 18
                local.append(f"{key}: generic/decorative diagram.")
            pkg = value.get("diagram_package") if isinstance(value.get("diagram_package"), dict) else {}
            if svg.startswith("<svg") and (
                not pkg.get("caption") or not pkg.get("practice_question")
            ):
                score -= 12
                local.append(f"{key}: diagram package incomplete (caption/practice).")
            if "fff9ee" not in svg.lower() and key in {"standard", "visual"}:
                # Prefer cream canvas inside SVG; soft penalty only
                score -= 4

        # Typography / spacing proxies via style CSS attachment
        if not value.get("publisher_style_css") and key in {"standard", "visual"}:
            score -= 5
            local.append(f"{key}: publisher style CSS not attached.")

        score = max(0.0, min(100.0, score))
        page_scores[key] = round(score, 2)
        issues.extend(local)

    overall = round(sum(page_scores.values()) / len(page_scores), 2) if page_scores else 0.0
    return {
        "schema": "alora.uevb.visual_design_audit.v1",
        "visual_quality_score": overall,
        "threshold": VISUAL_MIN,
        "ok": overall >= VISUAL_MIN and not any("missing professional SVG" in i for i in issues),
        "by_page": page_scores,
        "issues": issues,
        "design_system": {
            "cream": CREAM,
            "navy": NAVY,
            "no_dashboard_chrome": True,
        },
    }
