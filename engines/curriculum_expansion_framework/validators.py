"""Publication-grade validation before CEF publish → UCF."""

from __future__ import annotations

from typing import Any

from engines.curriculum_expansion_framework.mapping import mapping_completeness


def validate_expansion_package(raw: dict[str, Any], *, ucf_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Reject incomplete packages. Soft warnings for optional assets.
    """
    errors: list[str] = []
    warnings: list[str] = []

    for req in ("board", "subject", "grade"):
        if not raw.get(req) and not (raw.get("structure") or {}).get(req):
            # after mapping, board may be nested
            if req == "board" and raw.get("board"):
                continue
            if not raw.get(req):
                errors.append(f"missing_{req}")

    topics = raw.get("topics") or raw.get("concepts") or []
    if not topics:
        errors.append("missing_topics_or_concepts")

    objs = raw.get("learning_objectives") or raw.get("objectives") or []
    has_topic_objs = any(
        isinstance(t, dict) and (t.get("definition") or t.get("objectives") or t.get("learning_objectives"))
        for t in topics
        if not isinstance(t, str)
    )
    if not objs and not has_topic_objs:
        errors.append("learning_objectives_incomplete")

    comps = raw.get("competencies") or []
    topic_comps = any(isinstance(t, dict) and (t.get("competencies") or t.get("competency_ids")) for t in topics if not isinstance(t, str))
    if not comps and not topic_comps:
        warnings.append("competencies_unmapped")

    if not (raw.get("official_questions") or raw.get("questions") or raw.get("assessment_mappings")):
        warnings.append("assessment_references_missing")

    if not (raw.get("figures") or raw.get("diagrams")):
        warnings.append("diagrams_missing")

    formulae = raw.get("formulae") or raw.get("formulas") or raw.get("equations") or []
    for f in formulae:
        if isinstance(f, dict) and not (f.get("latex") or f.get("formula") or f.get("expression")):
            errors.append("formula_integrity_failed")
            break

    if not (raw.get("glossary") or raw.get("vocabulary")):
        warnings.append("glossary_incomplete")

    if not raw.get("accessibility"):
        warnings.append("accessibility_metadata_missing")

    # Cross-refs: chapter ids mentioned in topics
    chapter_ids = {str(c.get("id") or c) for c in (raw.get("chapters") or []) if c}
    for t in topics:
        if isinstance(t, dict) and t.get("chapter_id") and chapter_ids and str(t["chapter_id"]) not in chapter_ids:
            warnings.append(f"cross_ref_chapter_missing:{t.get('chapter_id')}")

    completeness = mapping_completeness(raw)
    if ucf_validation and not ucf_validation.get("ok"):
        errors.extend(list(ucf_validation.get("errors") or []))
        warnings.extend(list(ucf_validation.get("warnings") or []))

    ok = not errors
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "completeness": completeness,
        "reject": not ok,
        "ready_to_publish": ok and completeness.get("completeness", 0) >= 0.35,
    }
