"""Importer — stage 1 entry: parse + security checks."""

from __future__ import annotations

from typing import Any
import uuid

from engines.curriculum_migration_framework.licensing import (
    compute_source_hash,
    detect_duplicate,
    licensing_record,
    verify_checksum,
)
from engines.curriculum_migration_framework.parser import parse_source
from engines.curriculum_migration_framework.provenance import append_audit, build_provenance
from engines.curriculum_migration_framework.schemas import MigrationJob, SUPPORTED_BOARDS


# In-memory known hashes for duplicate detection (persisted lightly via job store in migration)
_KNOWN_HASHES: list[str] = []


def start_import(
    *,
    board: str,
    path: str = "",
    inline: dict[str, Any] | None = None,
    source_type: str = "",
    source_url: str = "",
    expected_checksum: str = "",
    publisher: str = "",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    meta = meta or {}
    board = (board or "cbse").lower()
    job_id = f"cmif_{uuid.uuid4().hex[:10]}"
    job = MigrationJob(
        job_id=job_id,
        board=board,
        source_type=source_type or ("inline_json" if inline is not None else ""),
        status="running",
        stage="import",
        curriculum_id=board,
        resume_token=job_id,
    )

    parsed = parse_source(path=path, inline=inline, source_type=source_type, meta={**meta, "board": board})
    if not parsed.get("ok"):
        job.status = "failed"
        job.errors.append(str(parsed.get("error") or "parse_failed"))
        append_audit(job_id, "import_failed", parsed)
        return {"ok": False, "job": job.to_dict(), "parsed": parsed}

    raw = parsed.get("raw") or {}
    source_hash = compute_source_hash(raw)
    if expected_checksum:
        check = verify_checksum(raw, expected_checksum)
        if not check["ok"]:
            job.status = "failed"
            job.errors.append("checksum_mismatch")
            append_audit(job_id, "checksum_failed", check)
            return {"ok": False, "job": job.to_dict(), "checksum": check}

    if detect_duplicate(source_hash, _KNOWN_HASHES):
        job.warnings.append("duplicate_source_hash")
    else:
        _KNOWN_HASHES.append(source_hash)

    provenance = build_provenance(
        board=board,
        source_type=str(parsed.get("source_type") or source_type or "inline_json"),
        source_url=source_url,
        source_hash=source_hash,
        publisher=publisher,
        job_id=job_id,
    )
    licence = licensing_record(board=board, licence=str(raw.get("licence") or raw.get("license") or ""), source_url=source_url)
    raw = {**raw, "board": raw.get("board") or board, "publisher": publisher, "source_url": source_url, "source_hash": source_hash, "licensing": licence}
    append_audit(job_id, "imported", {"board": board, "source_type": parsed.get("source_type"), "hash": source_hash[:16]})
    return {
        "ok": True,
        "job": job.to_dict(),
        "raw": raw,
        "provenance": provenance,
        "parsed": {k: parsed.get(k) for k in ("ok", "source_type", "parser", "filename")},
        "supported_boards": list(SUPPORTED_BOARDS),
    }
