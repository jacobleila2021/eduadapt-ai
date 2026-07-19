"""Licensing & security checks — checksum, sanitize, RBAC publish gate."""

from __future__ import annotations

import hashlib
import re
from typing import Any

PUBLISH_ROLES = frozenset({"administrator", "curriculum_publisher", "content_admin"})


def compute_source_hash(payload: bytes | str | dict[str, Any]) -> str:
    if isinstance(payload, dict):
        import json

        data = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    elif isinstance(payload, str):
        data = payload.encode("utf-8")
    else:
        data = payload
    return hashlib.sha256(data).hexdigest()


def sanitize_filename(name: str) -> str:
    name = (name or "package").replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^\w.\-]+", "_", name)
    return name[:120] or "package"


def verify_checksum(payload: bytes | str | dict[str, Any], expected: str) -> dict[str, Any]:
    actual = compute_source_hash(payload)
    ok = bool(expected) and actual.lower() == expected.lower()
    return {"ok": ok, "expected": expected, "actual": actual, "mismatch": not ok and bool(expected)}


def can_publish(role: str) -> bool:
    return (role or "").strip().lower().replace(" ", "_") in PUBLISH_ROLES or role == "administrator"


def licensing_record(*, board: str, licence: str = "", source_url: str = "", status: str = "restricted") -> dict[str, Any]:
    return {
        "board": board,
        "licence": licence or "restricted",
        "status": status,
        "source_url": source_url,
        "policy": {
            "never_ingest_without_clearance": True,
            "ncert_cbse_require_legal_review": board in ("ncert", "cbse"),
        },
    }


def detect_duplicate(source_hash: str, known_hashes: list[str]) -> bool:
    return bool(source_hash) and source_hash in set(known_hashes or [])
