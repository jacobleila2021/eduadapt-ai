"""Validation — required fields, prereq integrity, reference checks."""

from __future__ import annotations

from typing import Any


REQUIRED_TOPIC_FIELDS = ("topic_id", "title", "board", "structure")


def validate_package(doc: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not doc.get("package_id"):
        errors.append("missing_package_id")
    if not doc.get("board"):
        errors.append("missing_board")
    topics = doc.get("topics") or []
    if not topics:
        warnings.append("no_topics")

    ids = set()
    for t in topics:
        for f in REQUIRED_TOPIC_FIELDS:
            if f not in t or t.get(f) in (None, ""):
                errors.append(f"topic_missing_{f}:{t.get('topic_id')}")
        tid = t.get("topic_id")
        if tid in ids:
            errors.append(f"duplicate_topic:{tid}")
        ids.add(tid)
        objs = t.get("objectives") or {}
        if not any(objs.get(k) for k in ("knowledge", "skill", "competency", "big_ideas")):
            warnings.append(f"missing_objectives:{tid}")
        for edge in (t.get("prerequisites") or {}).get("edges") or []:
            frm = edge.get("from") or edge.get("from_concept")
            to = edge.get("to") or edge.get("to_concept")
            if frm and frm not in ids and frm not in {x.get("topic_id") for x in topics}:
                # may reference concept ids not yet listed — warn
                warnings.append(f"prereq_from_unresolved:{frm}")
            if to and to not in ids:
                warnings.append(f"prereq_to_unresolved:{to}")

        for ref_field in ("formula_ids", "diagram_ids", "glossary_ids", "question_bank_ids"):
            for ref in t.get(ref_field) or []:
                if not ref:
                    errors.append(f"empty_ref:{ref_field}:{tid}")

    # Collection-level refs
    formula_ids = {f.get("formula_id") for f in (doc.get("formulae") or []) if f.get("formula_id")}
    for t in topics:
        for fid in t.get("formula_ids") or []:
            if formula_ids and fid not in formula_ids:
                warnings.append(f"formula_ref_missing:{fid}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "topics_checked": len(topics),
        "ready_to_import": not errors,
    }
