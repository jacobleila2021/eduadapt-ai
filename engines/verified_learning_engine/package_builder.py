"""Build the Verified Learning Package — single source of truth artifact."""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

PACKAGE_DIR = DATA_DIR / "verified_packages"


class PackageBuilder:
    """
    Standardized Verified Learning Package (VLP).

    Consumed by teacher dashboard, student UI, offline mode, AI tutor.
    """

    SCHEMA_VERSION = "3.0.0"

    def build(
        self,
        *,
        run_id: str,
        lesson_text: str,
        adaptations: dict[str, Any] | None,
        merged: dict[str, Any],
        qa_report: dict[str, Any] | None = None,
        audit: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        meta = (adaptations or {}).get("_meta") or {}
        knowledge = meta.get("knowledge") or {}
        source = meta.get("source_envelope") or {}
        profile = meta.get("universal_profile") or {}
        curriculum_resolution = meta.get("curriculum_resolution") or profile.get(
            "curriculum_resolution"
        ) or {}
        qa = qa_report or meta.get("publish_qa") or {}
        package = {
            "schema_version": self.SCHEMA_VERSION,
            "package_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "lesson_metadata": {
                "topic": (meta.get("lesson_context") or {}).get("topic"),
                "source_chars": len(lesson_text or ""),
                "source_id": source.get("source_id"),
                "curriculum_status": curriculum_resolution.get("status", "unknown"),
                "board": curriculum_resolution.get("curriculum"),
                "grade": None,
                "subject": None,
            },
            "source": source,
            "universal_profile": profile,
            "curriculum": {
                "resolution": curriculum_resolution,
                "enrichment": knowledge.get("external_enrichment")
                or {"status": "no_hits", "required": False},
                "citations": knowledge.get("citations") or [],
                "rag_hits": knowledge.get("rag_hits") or [],
                "exam_bundle": knowledge.get("exam_bundle") or {},
            },
            "verified_concepts": meta.get("engine_artifacts") or [],
            "verified_stem_outputs": meta.get("engine_artifacts") or [],
            "verified_visuals": meta.get("preferred_visuals") or [],
            "biology_figures": meta.get("biology_figures") or [],
            "accessibility_adaptations": {
                k: True
                for k in (adaptations or {})
                if k not in ("_meta", "vocabulary", "worksheet") and isinstance((adaptations or {}).get(k), dict)
            },
            "assessment_assets": {
                "vocabulary": (adaptations or {}).get("vocabulary"),
                "worksheet": (adaptations or {}).get("worksheet"),
                "official_mcqs": knowledge.get("official_mcqs") or [],
            },
            "ai_tutor_resources": (adaptations or {}).get("tutor"),
            "visual_assets": meta.get("preferred_visuals") or [],
            "analytics_metadata": merged.get("engines", {}).get("learning_analytics", {}),
            "gamification": merged.get("engines", {}).get("gamification", {}),
            "qa_report": qa,
            "grounding_mode": meta.get("grounding_mode") or "uploaded_source",
            "grounding_coverage": (qa.get("scorecard") or {}).get(
                "source_grounding_coverage"
            ),
            "lifecycle_state": (
                "quarantined" if qa.get("publish_blocked") else "review_draft"
            ),
            "orchestration_trace": meta.get("orchestration_trace") or [],
            "chapter_approved": meta.get("chapter_approved", False),
            "version_history": [
                {
                    "version": 1,
                    "at": datetime.now(timezone.utc).isoformat(),
                    "note": "VLIE package build",
                }
            ],
            "adaptations_keys": [k for k in (adaptations or {}) if not str(k).startswith("_")],
            "merged_engine_summary": {
                "ok": merged.get("ok"),
                "errors": merged.get("errors") or [],
                "warnings": merged.get("warnings") or [],
            },
            "audit_trail": audit or [],
        }
        return package

    def persist(self, package: dict[str, Any]) -> Path:
        PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
        path = PACKAGE_DIR / f"{package.get('package_id', 'pkg')}.json"
        # Store without full adaptation bodies to keep size manageable
        slim = dict(package)
        slim["assessment_assets"] = {
            "has_vocabulary": bool((package.get("assessment_assets") or {}).get("vocabulary")),
            "has_worksheet": bool((package.get("assessment_assets") or {}).get("worksheet")),
            "official_mcqs": (package.get("assessment_assets") or {}).get("official_mcqs") or [],
        }
        slim.pop("ai_tutor_resources", None)
        handle, temporary = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(slim, stream, indent=2, default=str)
                stream.flush()
                os.fsync(stream.fileno())
            last_error: PermissionError | None = None
            for attempt in range(8):
                try:
                    os.replace(temporary, path)
                    last_error = None
                    break
                except PermissionError as exc:
                    last_error = exc
                    time.sleep(0.05 * (attempt + 1))
            if last_error is not None:
                path.write_text(
                    json.dumps(slim, indent=2, default=str),
                    encoding="utf-8",
                )
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return path
