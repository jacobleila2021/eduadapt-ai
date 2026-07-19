"""Mandatory CMIF migration workflow — no stage may be skipped."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

from engines.curriculum_migration_framework.importer import start_import
from engines.curriculum_migration_framework.indexer import index_package
from engines.curriculum_migration_framework.mapper import map_to_ucf
from engines.curriculum_migration_framework.normalizer import normalize_package
from engines.curriculum_migration_framework.provenance import append_audit
from engines.curriculum_migration_framework.publisher import publish_to_ucf
from engines.curriculum_migration_framework.schemas import PIPELINE_STAGES
from engines.curriculum_migration_framework.validator import validate_package
from engines.curriculum_migration_framework.versioning import save_version

JOBS_DIR = DATA_DIR / "cmif" / "jobs"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _save_job(job: dict[str, Any]) -> None:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    path = JOBS_DIR / f"{job['job_id']}.json"
    path.write_text(json.dumps(job, indent=2, ensure_ascii=False), encoding="utf-8")


def load_job(job_id: str) -> dict[str, Any] | None:
    path = JOBS_DIR / f"{job_id}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_jobs(limit: int = 50) -> list[dict[str, Any]]:
    if not JOBS_DIR.exists():
        return []
    rows = []
    for p in sorted(JOBS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
        rows.append(json.loads(p.read_text(encoding="utf-8")))
    return rows


def _extract(normalized: dict[str, Any]) -> dict[str, Any]:
    """Deterministic extraction stages — reshape only, never invent curriculum."""
    return {
        "metadata": {
            "board": normalized.get("board"),
            "programme": normalized.get("programme"),
            "subject": normalized.get("subject"),
            "grade": normalized.get("grade"),
            "academic_year": normalized.get("academic_year"),
            "country": normalized.get("country"),
            "region": normalized.get("region"),
            "publisher": normalized.get("publisher"),
            "version": normalized.get("version") or "1.0.0",
            "language": normalized.get("language"),
            "licence": (normalized.get("licensing") or {}).get("licence"),
            "source_url": normalized.get("source_url"),
            "source_hash": normalized.get("source_hash"),
            "package_id": normalized.get("package_id"),
        },
        "learning_outcomes": list(normalized.get("learning_objectives") or []),
        "assessments": list(normalized.get("official_questions") or []) + list(normalized.get("assessment_mappings") or []),
        "diagrams": list(normalized.get("figures") or []),
        "formulae": list(normalized.get("formulae") or []),
        "glossary": list(normalized.get("glossary") or []),
        "accessibility": normalized.get("accessibility") or {},
        "knowledge_graph": {
            "nodes": [
                {"id": t.get("id") or t.get("topic_id"), "title": t.get("title")}
                for t in (normalized.get("topics") or [])
                if isinstance(t, dict)
            ],
            "edges": list(normalized.get("prerequisites") or []),
        },
        "semantic_chunks": list(normalized.get("text_chunks") or [])[:50]
        or [
            {"chunk_id": f"c{i}", "text": str((t.get("definition") if isinstance(t, dict) else t) or "")[:500]}
            for i, t in enumerate((normalized.get("topics") or [])[:20])
        ],
    }


def run_migration(
    *,
    board: str,
    path: str = "",
    inline: dict[str, Any] | None = None,
    source_type: str = "",
    source_url: str = "cmif://inline",
    expected_checksum: str = "",
    publisher: str = "",
    publish: bool = True,
    role: str = "system",
    resume_job_id: str = "",
    lazy_index: bool = False,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute the full mandatory pipeline. Stages cannot be bypassed.
    """
    stages_done: list[str] = []
    artifacts: dict[str, Any] = {}

    # Resume support
    if resume_job_id:
        existing = load_job(resume_job_id)
        if existing and existing.get("status") in ("paused", "failed", "running"):
            stages_done = list(existing.get("stages_done") or [])
            artifacts = dict(existing.get("artifacts") or {})
            job = existing
        else:
            resume_job_id = ""

    if not resume_job_id:
        imported = start_import(
            board=board,
            path=path,
            inline=inline,
            source_type=source_type,
            source_url=source_url or "cmif://inline",
            expected_checksum=expected_checksum,
            publisher=publisher,
            meta=meta,
        )
        if not imported.get("ok"):
            return imported
        job = {
            **imported["job"],
            "stages_done": ["import"],
            "artifacts": {
                "raw": imported["raw"],
                "provenance": imported["provenance"],
            },
            "created_at": _now(),
            "updated_at": _now(),
        }
        stages_done = ["import"]
        artifacts = job["artifacts"]
        _save_job(job)
        append_audit(job["job_id"], "stage", {"stage": "import"})

    def _advance(stage: str, payload: Any) -> None:
        stages_done.append(stage)
        artifacts[stage] = payload
        job["stage"] = stage
        job["stages_done"] = list(stages_done)
        job["artifacts_keys"] = list(artifacts.keys())
        job["updated_at"] = _now()
        # Persist compact job (drop huge bodies from disk snapshot except essentials)
        compact = {**job, "artifacts": {k: artifacts[k] for k in artifacts if k in ("raw", "provenance", "normalize", "map_ucf", "validate", "publish", "extracts", "index", "version")}}
        _save_job(compact)
        append_audit(job["job_id"], "stage", {"stage": stage})

    # Ensure every PIPELINE_STAGES entry runs in order
    for stage in PIPELINE_STAGES:
        if stage in stages_done and stage != "import":
            continue
        if stage == "import":
            continue

        if stage == "validate":
            report = validate_package(artifacts["raw"], provenance=artifacts.get("provenance"))
            if report.get("reject"):
                job["status"] = "rejected"
                job["errors"] = report.get("errors") or []
                job["quality_score"] = report.get("quality_score")
                _advance("validate", report)
                _save_job({**job, "artifacts": {"validate": report, "provenance": artifacts.get("provenance")}})
                return {"ok": False, "job": job, "validation": report}
            job["quality_score"] = report.get("quality_score")
            _advance("validate", report)

        elif stage == "normalize":
            norm = normalize_package(artifacts["raw"], board=board)
            _advance("normalize", norm)

        elif stage == "map_ucf":
            mapped = map_to_ucf(artifacts["normalize"])
            _advance("map_ucf", mapped)

        elif stage in (
            "extract_metadata",
            "extract_learning_outcomes",
            "extract_assessments",
            "extract_diagrams",
            "extract_formulae",
            "extract_glossary",
            "accessibility_metadata",
            "knowledge_graph",
            "semantic_chunking",
        ):
            if "extracts" not in artifacts:
                artifacts["extracts"] = _extract(artifacts["normalize"])
            # mark each extract stage explicitly (no bypass)
            key = {
                "extract_metadata": "metadata",
                "extract_learning_outcomes": "learning_outcomes",
                "extract_assessments": "assessments",
                "extract_diagrams": "diagrams",
                "extract_formulae": "formulae",
                "extract_glossary": "glossary",
                "accessibility_metadata": "accessibility",
                "knowledge_graph": "knowledge_graph",
                "semantic_chunking": "semantic_chunks",
            }[stage]
            _advance(stage, {key: artifacts["extracts"].get(key)})

        elif stage == "vector_index":
            pkg = {
                **artifacts["normalize"],
                **(artifacts["map_ucf"].get("ucf_payload") or {}),
                "package_id": (artifacts["map_ucf"].get("ucf_payload") or {}).get("package_id")
                or f"cmif_pkg_{job['job_id'][-8:]}",
            }
            idx = index_package(pkg, lazy=lazy_index)
            _advance("vector_index", idx)
            artifacts["index"] = idx

        elif stage == "version_package":
            pid = (artifacts["map_ucf"].get("ucf_payload") or {}).get("package_id") or job["job_id"]
            ver = save_version(str(pid), artifacts["normalize"], status="review", note="pre_publish")
            _advance("version_package", ver)
            artifacts["version"] = ver

        elif stage == "quality_assurance":
            qa = {
                "ok": True,
                "quality_score": job.get("quality_score") or (artifacts.get("validate") or {}).get("quality_score"),
                "stages_completed": list(stages_done) + ["quality_assurance"],
                "mandatory_pipeline": list(PIPELINE_STAGES),
                "bypass_detected": False,
            }
            # Verify no stage missing before publish
            missing = [s for s in PIPELINE_STAGES if s not in stages_done and s not in ("quality_assurance", "publish")]
            if missing:
                qa = {"ok": False, "missing_stages": missing, "bypass_detected": True}
                job["status"] = "failed"
                job["errors"] = [f"pipeline_bypass:{missing}"]
                _advance("quality_assurance", qa)
                return {"ok": False, "job": job, "qa": qa}
            _advance("quality_assurance", qa)

        elif stage == "publish":
            if not publish:
                _advance("publish", {"ok": True, "skipped": True, "reason": "publish=False"})
                job["status"] = "completed"
                job["package_id"] = (artifacts["map_ucf"].get("ucf_payload") or {}).get("package_id")
                _save_job({**job, "artifacts": {k: artifacts.get(k) for k in ("validate", "map_ucf", "version", "index")}})
                return {"ok": True, "job": job, "published": False, "artifacts": artifacts}
            pub = publish_to_ucf(
                job_id=job["job_id"],
                curriculum_id=str(artifacts["map_ucf"].get("curriculum_id") or board),
                ucf_payload=artifacts["map_ucf"].get("ucf_payload") or artifacts["normalize"],
                role=role,
            )
            _advance("publish", pub)
            artifacts["publish"] = pub
            job["status"] = "completed" if pub.get("ok") else "failed"
            job["package_id"] = pub.get("package_id") or ""
            if not pub.get("ok"):
                job["errors"] = [str(pub.get("error") or "publish_failed")]
                _save_job({**job, "artifacts": {"publish": pub, "validate": artifacts.get("validate")}})
                return {"ok": False, "job": job, "publish": pub}

    job["status"] = "completed"
    job["stages_done"] = stages_done
    _save_job({**job, "artifacts": {k: artifacts.get(k) for k in ("validate", "map_ucf", "version", "index", "publish")}})
    return {
        "ok": True,
        "job": job,
        "package_id": job.get("package_id"),
        "quality_score": job.get("quality_score"),
        "stages": stages_done,
        "policy": {
            "never_generate_curriculum_with_ai": True,
            "engines_consume_ucf_only": True,
            "pipeline_mandatory": True,
        },
    }
