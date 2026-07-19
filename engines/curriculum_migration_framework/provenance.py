"""Provenance + immutable audit trail for CMIF jobs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

AUDIT_DIR = DATA_DIR / "cmif" / "audit"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_provenance(
    *,
    board: str,
    source_type: str,
    source_url: str = "",
    source_hash: str = "",
    publisher: str = "",
    package_id: str = "",
    job_id: str = "",
) -> dict[str, Any]:
    return {
        "board": board,
        "source_type": source_type,
        "source_url": source_url,
        "source_hash": source_hash,
        "publisher": publisher,
        "package_id": package_id,
        "job_id": job_id,
        "imported_at": _now(),
        "chain": ["source", "cmif", "kie_optional", "cef", "ucf", "engines"],
        "policy": {
            "never_generate_curriculum_with_ai": True,
            "engines_consume_ucf_only": True,
            "immutable_when_published": True,
        },
    }


def append_audit(job_id: str, event: str, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    path = AUDIT_DIR / f"{job_id}.jsonl"
    row = {"ts": _now(), "job_id": job_id, "event": event, "detail": detail or {}}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_audit(job_id: str, limit: int = 200) -> list[dict[str, Any]]:
    path = AUDIT_DIR / f"{job_id}.jsonl"
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows[-limit:]
