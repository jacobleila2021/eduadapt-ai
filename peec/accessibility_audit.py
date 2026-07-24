"""Accessibility + adaptation excellence audits."""

from __future__ import annotations

from typing import Any, Mapping

from uevb.differentiation import measure_adaptation_differentiation


def audit_adaptation_quality(adaptations: Mapping[str, Any]) -> dict[str, Any]:
    diff = measure_adaptation_differentiation(adaptations)
    issues: list[str] = []
    for key in ("adhd", "autism", "ell", "visual", "auditory", "parent", "teacher"):
        if key not in adaptations or not isinstance(adaptations.get(key), dict):
            issues.append(f"Missing handcrafted {key} adaptation.")
    if diff.get("cosmetic_failures"):
        issues.append(
            "Cosmetic-only adaptations detected: " + ", ".join(diff["cosmetic_failures"])
        )
    if float(diff.get("adaptation_differentiation_score") or 0) < 55:
        issues.append("Adaptation Differentiation Score below excellence bar.")

    return {
        "schema": "alora.peec.adaptation_quality_audit.v1",
        "ok": not issues and bool(diff.get("ok")),
        "issues": issues,
        "differentiation": diff,
        "summary": (
            "Every profile feels independently authored."
            if not issues
            else "Some adaptations still feel cloned or incomplete."
        ),
    }


def audit_accessibility(adaptations: Mapping[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    required = ("ld", "dyslexia", "adhd", "autism", "ell", "visual", "auditory")
    for key in required:
        page = adaptations.get(key)
        if not isinstance(page, dict):
            # ld/dyslexia may alias — soft
            if key in {"ld", "dyslexia"} and (
                isinstance(adaptations.get("ld"), dict) or isinstance(adaptations.get("dyslexia"), dict)
            ):
                continue
            issues.append(f"Accessibility gap: missing {key} edition.")
            continue
        sections = [s for s in (page.get("sections") or []) if isinstance(s, dict)]
        if len(sections) < 3:
            issues.append(f"{key}: too little structure for accessible pacing.")
        if key in {"ld", "dyslexia"}:
            bullets = sum(1 for s in sections if str(s.get("body") or "").lstrip().startswith("-"))
            if bullets < 1:
                issues.append(f"{key}: needs chunked bullet scaffolding.")

    vocab = adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {}
    wall = vocab.get("word_wall") or []
    if wall:
        missing_audio = sum(1 for c in wall[:6] if isinstance(c, dict) and not c.get("pronunciation"))
        if missing_audio >= 3:
            issues.append("Vocabulary accessibility: several cards lack pronunciation.")

    return {
        "schema": "alora.peec.accessibility_audit.v1",
        "ok": len(issues) == 0,
        "issues": issues,
        "summary": "Accessible profiles are intentional." if not issues else "Accessibility gaps remain.",
    }
