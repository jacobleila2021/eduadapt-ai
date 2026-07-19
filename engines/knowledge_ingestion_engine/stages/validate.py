"""Stage 1 — Document validation, hashing, duplicate detection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from engines.knowledge_ingestion_engine.schemas import SUPPORTED_EXTENSIONS
from knowledge.paths import INGEST_DIR


HASH_INDEX = INGEST_DIR / "hashes" / "index.json"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _load_hash_index() -> dict[str, str]:
    if HASH_INDEX.is_file():
        try:
            return json.loads(HASH_INDEX.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def _save_hash_index(index: dict[str, str]) -> None:
    HASH_INDEX.parent.mkdir(parents=True, exist_ok=True)
    HASH_INDEX.write_text(json.dumps(index, indent=2), encoding="utf-8")


def validate_document(path: Path) -> dict[str, Any]:
    """
    Validate integrity, format, and duplicates.
    Virus scanning is a policy hook (sandbox note) — not a full AV engine.
    """
    path = Path(path)
    result: dict[str, Any] = {
        "ok": False,
        "path": str(path),
        "errors": [],
        "warnings": [],
        "content_hash": "",
        "duplicate": False,
        "extension": "",
    }
    if not path.is_file():
        result["errors"].append("File not found")
        return result
    if path.stat().st_size <= 0:
        result["errors"].append("Empty file")
        return result
    if path.stat().st_size > 200 * 1024 * 1024:
        result["errors"].append("File exceeds 200MB limit")
        return result

    ext = path.suffix.lower()
    result["extension"] = ext
    if ext not in SUPPORTED_EXTENSIONS:
        result["errors"].append(f"Unsupported format: {ext}")
        return result

    # Basic extension/content mismatch soft check
    if ext == ".pdf":
        head = path.read_bytes()[:5]
        if head != b"%PDF-":
            result["warnings"].append("Extension is .pdf but magic bytes are not %PDF-")

    digest = file_sha256(path)
    result["content_hash"] = digest
    index = _load_hash_index()
    if digest in index and Path(index[digest]).resolve() != path.resolve():
        result["duplicate"] = True
        result["warnings"].append(f"Duplicate of {index[digest]}")
    else:
        index[digest] = str(path)
        _save_hash_index(index)

    result["ok"] = len(result["errors"]) == 0
    result["sandbox_note"] = "Process in isolated worker; never serve raw copyrighted PDFs publicly"
    return result
