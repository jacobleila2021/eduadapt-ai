"""VLIE-level validation before publish — delegates to QA engine output."""

from __future__ import annotations

from typing import Any


class VLIEValidator:
    """
    Ensures the Verified Learning Package meets publish criteria.
    Does not re-implement STEM checks — reads QA engine / package fields.
    """

    def validate_package(self, package: dict[str, Any]) -> dict[str, Any]:
        qa = package.get("qa_report") or {}
        errors: list[str] = []
        if not qa:
            errors.append("Missing QA report at publication boundary")
        if qa.get("publish_blocked"):
            errors.append(qa.get("blocked_reason") or "QA publish blocked")
        if not package.get("lesson_metadata"):
            errors.append("Missing lesson metadata")
        # STEM facts should be present OR explicitly empty with no failures
        stem = package.get("verified_stem_outputs") or []
        failed_stem = [a for a in stem if a.get("validation") == "fail" and not (a.get("payload") or {}).get("optional_dep_missing")]
        if failed_stem:
            errors.append(f"{len(failed_stem)} STEM artifact(s) failed validation")

        return {
            "ok": len(errors) == 0 and not qa.get("publish_blocked", False),
            "publish_blocked": bool(errors) or bool(qa.get("publish_blocked")),
            "errors": errors,
            "scorecard": qa.get("scorecard") or {},
        }
