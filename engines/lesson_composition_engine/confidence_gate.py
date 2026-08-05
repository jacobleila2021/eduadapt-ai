"""Phase 4 — One-Generate confidence gate (hard publish checks).

Blocks classroom open when Lesson Wall / vocab / STEM answers are not trustworthy.
Does not add engines — only gates what already exists.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

CONFIDENCE_GATE_VERSION = "1.0.0"


def _wall_items(adaptations: Mapping[str, Any]) -> list[dict]:
    wall = adaptations.get("_lesson_wall")
    if isinstance(wall, list) and wall:
        return [w for w in wall if isinstance(w, dict)]
    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    attached = std.get("lesson_wall") if isinstance(std.get("lesson_wall"), list) else []
    if attached:
        return [w for w in attached if isinstance(w, dict)]
    try:
        from engines.lesson_composition_engine.lesson_wall import extract_lesson_wall

        return extract_lesson_wall(std)
    except Exception:
        return []


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z]{4,}", (text or "").lower())}


def _wall_blob(wall: list[dict]) -> str:
    return " ".join(
        f"{row.get('title') or ''} {row.get('idea') or ''}" for row in wall
    )


def _vocab_blob(adaptations: Mapping[str, Any]) -> str:
    vocab = adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {}
    parts: list[str] = []
    for row in vocab.get("word_wall") or []:
        if isinstance(row, dict):
            parts.append(str(row.get("term") or ""))
            parts.append(str(row.get("definition") or ""))
            parts.append(str(row.get("lesson_context") or ""))
    return " ".join(parts)


def _has_domain_diagram(adaptations: Mapping[str, Any]) -> bool:
    try:
        from engines.lesson_composition_engine.publisher_remediation import (
            is_generic_subject_flowchart,
        )
    except Exception:

        def is_generic_subject_flowchart(_svg: str) -> bool:  # type: ignore
            return False

    for key in ("standard", "ell", "parent", "visual", "worksheet", "vocabulary"):
        page = adaptations.get(key)
        if not isinstance(page, dict):
            continue
        pkg = page.get("diagram_package") if isinstance(page.get("diagram_package"), dict) else {}
        for svg in (
            pkg.get("svg"),
            page.get("svg_diagram"),
            page.get("concept_map_svg"),
            page.get("flowchart_svg"),
            (page.get("diagram_question") or {}).get("svg_diagram")
            if isinstance(page.get("diagram_question"), dict)
            else "",
        ):
            text = str(svg or "")
            if text.startswith("<svg") and not is_generic_subject_flowchart(text):
                return True
    return False


def _invented_stem_answers(adaptations: Mapping[str, Any]) -> list[str]:
    """Detect numerical/balance answers that are not engine-backed when artifacts exist."""
    from engines.lesson_pipeline import looks_like_computable_stem

    artifacts = list(adaptations.get("_stem_artifacts") or [])
    meta = adaptations.get("_meta") if isinstance(adaptations.get("_meta"), dict) else {}
    if not artifacts:
        artifacts = list(meta.get("engine_artifacts") or [])
    ok_arts = [a for a in artifacts if isinstance(a, dict) and a.get("ok")]
    if not ok_arts:
        return []

    issues: list[str] = []
    worksheet = adaptations.get("worksheet") if isinstance(adaptations.get("worksheet"), dict) else {}
    for row in worksheet.get("short_answer") or []:
        if not isinstance(row, dict):
            continue
        q = str(row.get("question") or "")
        a = str(row.get("model_answer") or "")
        src = str(row.get("source") or "")
        if not looks_like_computable_stem(q):
            continue
        if src == "engine_result":
            continue
        # Computable stem with a numeric/balance-looking answer not marked engine_result.
        if re.search(r"(?i)\b(balanced equation|exact result|solutions?:)\b", a):
            continue
        if re.search(r"(?i)\b(balance|solve|calculate)\b", q) and a and src != "engine_result":
            # Allow pure prose definitions (Ohm's law wording) without digits/arrows.
            if re.search(r"\d|→|->|=", a) and "is when" not in a.lower() and "is the" not in a.lower()[:40]:
                issues.append(f"Unverified computation answer for: {q[:80]}")
    return issues[:5]


def confidence_gate_issues(adaptations: Mapping[str, Any] | None) -> list[str]:
    """Return human-readable issues that should block confident classroom open."""
    if not adaptations:
        return ["No lesson package to validate."]
    issues: list[str] = []
    wall = _wall_items(adaptations)
    if len(wall) < 2:
        issues.append("Lesson Wall is too thin (need at least two teachable cards).")

    wall_text = _wall_blob(wall)
    vocab_text = _vocab_blob(adaptations)
    if wall and vocab_text:
        overlap = _tokens(wall_text) & _tokens(vocab_text)
        if len(overlap) < 2:
            issues.append("Vocabulary does not reuse Lesson Wall teaching language.")

    # Authoring chrome must never reach learners.
    blob = wall_text + " " + vocab_text
    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    for sec in std.get("sections") or []:
        if isinstance(sec, dict):
            blob += " " + str(sec.get("body") or "")
    low = blob.lower()
    if "(key word)" in low or "important words:" in low:
        issues.append("Authoring chrome still present (key word / Important words).")
    if re.search(r"(?m)^\s*model\s*:", low) or "model answer:" in low:
        issues.append("Authoring chrome still present (Model labels).")

    if not _has_domain_diagram(adaptations):
        # Soft for non-visual lessons; only warn when wall exists (contentful lesson).
        if wall:
            issues.append("Teaching diagram missing from adaptations (Lesson Visual).")

    issues.extend(_invented_stem_answers(adaptations))
    return issues


def confidence_block_reason(adaptations: Mapping[str, Any] | None) -> str:
    """Hard block reason for publication_gate, or empty string if OK."""
    issues = confidence_gate_issues(adaptations)
    # Diagram-only issues soft-pass for text-first STEM problem sheets with artifacts.
    hard = [
        i
        for i in issues
        if "Teaching diagram missing" not in i
    ]
    # Problem-sheet soft path: if STEM artifacts exist and wall is thin, allow when
    # engine answers are present and chrome is clean.
    arts = []
    if adaptations:
        arts = list(adaptations.get("_stem_artifacts") or [])
        meta = adaptations.get("_meta") if isinstance(adaptations.get("_meta"), dict) else {}
        arts = arts or list(meta.get("engine_artifacts") or [])
    ok_arts = [a for a in arts if isinstance(a, dict) and a.get("ok")]
    if ok_arts and any("Lesson Wall is too thin" in i for i in hard):
        hard = [i for i in hard if "Lesson Wall is too thin" not in i]
        if any("Vocabulary does not reuse" in i for i in hard) and not _vocab_blob(adaptations or {}):
            hard = [i for i in hard if "Vocabulary does not reuse" not in i]
    if not hard:
        return ""
    return "Confidence gate failed: " + "; ".join(hard[:3])
