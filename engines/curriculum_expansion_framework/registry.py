"""Centralized multi-board curriculum registry (CEF)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.curriculum_expansion_framework.schemas import CURRICULUM_FAMILIES, CurriculumRegistryEntry

CEF_DIR = DATA_DIR / "cef"
REGISTRY_PATH = CEF_DIR / "registry.json"
LOGS_PATH = CEF_DIR / "import_logs.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def ensure_family_catalogue() -> dict[str, Any]:
    """Register all supported curriculum families (stubs until packages imported)."""
    reg = _load(REGISTRY_PATH, {})
    changed = False
    for fid, meta in CURRICULUM_FAMILIES.items():
        if fid in reg:
            continue
        entry = CurriculumRegistryEntry(
            curriculum_id=fid,
            board_name=str(meta.get("programme") or fid),
            programme=str(meta.get("programme") or fid),
            country=str(meta.get("country") or ""),
            region=str(meta.get("region") or ""),
            languages=["en"],
            licensing={"status": "restricted", "note": "Legal clearance required before full ingest"},
            ucf_board_id=str(meta.get("ucf_board") or fid),
            family_id=str(meta.get("family") or ""),
            provenance={"source": "cef_catalogue", "incremental_priority": meta.get("incremental_priority")},
            updated_at=_now(),
        ).to_dict()
        reg[fid] = entry
        changed = True
    if changed:
        _save(REGISTRY_PATH, reg)
    return {"ok": True, "count": len(reg), "families": list(CURRICULUM_FAMILIES.keys())}


def upsert_entry(entry: dict[str, Any]) -> dict[str, Any]:
    ensure_family_catalogue()
    reg = _load(REGISTRY_PATH, {})
    cid = str(entry.get("curriculum_id") or "")
    if not cid:
        return {"ok": False, "error": "missing_curriculum_id"}
    prev = reg.get(cid) or {}
    merged = {**prev, **entry, "updated_at": _now()}
    reg[cid] = merged
    _save(REGISTRY_PATH, reg)
    return {"ok": True, "entry": merged}


def get_entry(curriculum_id: str) -> dict[str, Any] | None:
    ensure_family_catalogue()
    return _load(REGISTRY_PATH, {}).get(curriculum_id)


def list_curricula(
    *,
    family: str = "",
    publication_status: str = "",
    country: str = "",
) -> list[dict[str, Any]]:
    ensure_family_catalogue()
    rows = list(_load(REGISTRY_PATH, {}).values())
    if family:
        rows = [r for r in rows if r.get("family_id") == family]
    if publication_status:
        rows = [r for r in rows if r.get("publication_status") == publication_status]
    if country:
        rows = [r for r in rows if (r.get("country") or "").upper() == country.upper()]
    return sorted(rows, key=lambda r: (r.get("provenance") or {}).get("incremental_priority") or 99)


def list_supported_boards() -> list[dict[str, Any]]:
    ensure_family_catalogue()
    return [
        {
            "curriculum_id": fid,
            "programme": meta.get("programme"),
            "ucf_board": meta.get("ucf_board"),
            "family": meta.get("family"),
            "country": meta.get("country"),
            "incremental_priority": meta.get("incremental_priority"),
        }
        for fid, meta in CURRICULUM_FAMILIES.items()
    ]


def append_import_log(event: dict[str, Any]) -> None:
    logs = _load(LOGS_PATH, [])
    logs.append({**event, "ts": _now()})
    _save(LOGS_PATH, logs[-500:])


def import_logs(limit: int = 50) -> list[dict[str, Any]]:
    return list(_load(LOGS_PATH, []))[-limit:]
