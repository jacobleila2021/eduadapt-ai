"""Phase 4 — One-Generate confidence gate (hard publish checks).

Phase 1 freeze: Lesson Wall is the one true lesson; vocab / exam / voice must
reuse its science. Blocks classroom open when wall or surface parity fails.
Does not add engines — only gates what already exists.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

CONFIDENCE_GATE_VERSION = "1.1.0"


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
        if re.search(r"(?i)\b(balanced equation|exact result|solutions?:)\b", a):
            continue
        if re.search(r"(?i)\b(balance|solve|calculate)\b", q) and a and src != "engine_result":
            if re.search(r"\d|→|->|=", a) and "is when" not in a.lower() and "is the" not in a.lower()[:40]:
                issues.append(f"Unverified computation answer for: {q[:80]}")
    return issues[:5]


def _adaptation_wall_sync_issues(adaptations: Mapping[str, Any], wall: list[dict]) -> list[str]:
    """Every student lens must carry the same Lesson Wall titles."""
    if not wall:
        return []
    titles = [str(c.get("title") or "").strip().lower() for c in wall if str(c.get("title") or "").strip()]
    if not titles:
        return []
    issues: list[str] = []
    for vid in ("standard", "ell", "parent", "visual", "auditory", "ld", "dyslexia"):
        page = adaptations.get(vid)
        if not isinstance(page, dict):
            continue
        page_wall = page.get("lesson_wall") if isinstance(page.get("lesson_wall"), list) else []
        if not page_wall:
            issues.append(f"{vid} adaptation is missing the shared Lesson Wall.")
            continue
        page_titles = [
            str(c.get("title") or "").strip().lower()
            for c in page_wall
            if isinstance(c, dict) and str(c.get("title") or "").strip()
        ]
        if titles[:3] != page_titles[:3]:
            issues.append(f"{vid} Lesson Wall does not match the Master wall.")
    return issues[:4]


def confidence_gate_issues(adaptations: Mapping[str, Any] | None) -> list[str]:
    """Return human-readable issues that should block confident classroom open."""
    if not adaptations:
        return ["No lesson package to validate."]
    issues: list[str] = []
    wall = _wall_items(adaptations)

    vocab = adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {}
    worksheet = adaptations.get("worksheet") if isinstance(adaptations.get("worksheet"), dict) else {}
    narration = ""
    try:
        from audio_learning import build_narration

        std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
        if std:
            narration = build_narration(std, "standard")
    except Exception:
        narration = ""

    try:
        from engines.lesson_composition_engine.lesson_wall import wall_surface_parity_issues

        issues.extend(
            wall_surface_parity_issues(
                wall,
                vocabulary=vocab,
                worksheet=worksheet if worksheet.get("long_answer") else None,
                narration=narration,
                min_cards=3,
            )
        )
    except Exception:
        if len(wall) < 3:
            issues.append("Lesson Wall is too thin (need at least 3 teachable cards).")

    issues.extend(_adaptation_wall_sync_issues(adaptations, wall))

    # Authoring chrome must never reach learners.
    wall_text = " ".join(f"{row.get('title') or ''} {row.get('idea') or ''}" for row in wall)
    vocab_text = " ".join(
        f"{row.get('term') or ''} {row.get('definition') or ''}"
        for row in (vocab.get("word_wall") or [])
        if isinstance(row, dict)
    )
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
        if wall:
            issues.append("Teaching diagram missing from adaptations (Lesson Visual).")

    issues.extend(_invented_stem_answers(adaptations))
    return issues


def confidence_block_reason(adaptations: Mapping[str, Any] | None) -> str:
    """Hard block reason for publication_gate, or empty string if OK."""
    issues = confidence_gate_issues(adaptations)
    # Diagram-only issues soft-pass for text-first STEM problem sheets with artifacts.
    hard = [i for i in issues if "Teaching diagram missing" not in i]
    arts = []
    if adaptations:
        arts = list(adaptations.get("_stem_artifacts") or [])
        meta = adaptations.get("_meta") if isinstance(adaptations.get("_meta"), dict) else {}
        arts = arts or list(meta.get("engine_artifacts") or [])
    ok_arts = [a for a in arts if isinstance(a, dict) and a.get("ok")]
    if ok_arts and any("Lesson Wall is too thin" in i for i in hard):
        hard = [i for i in hard if "Lesson Wall is too thin" not in i]
        if any("Vocabulary does not reuse" in i for i in hard) and not (
            isinstance(adaptations.get("vocabulary"), dict)
            and (adaptations.get("vocabulary") or {}).get("word_wall")
        ):
            hard = [i for i in hard if "Vocabulary does not reuse" not in i]
        # Thin STEM sheets may omit exam long answers / full lens stamps.
        hard = [
            i
            for i in hard
            if "Exam long answers" not in i and "adaptation is missing the shared" not in i
            and "does not match the Master wall" not in i
            and "Reading narration" not in i
        ]
    if not hard:
        return ""
    return "Confidence gate failed: " + "; ".join(hard[:3])
