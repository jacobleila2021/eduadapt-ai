"""Teacher chapter validation — approve factual package once, reuse for all learners."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

APPROVED_DIR = DATA_DIR / "approved_chapters"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def factual_fingerprint(
    topic: str,
    artifacts: list[dict],
    citations: list[str] | None = None,
    source_hash: str = "",
) -> str:
    """
    Stable hash of verified facts (not presentation).
    Used as cache key for teacher-approved packages.
    """
    parts: list[str] = [f"topic:{(topic or '').strip().lower()}"]
    if source_hash:
        parts.append(f"source:{source_hash}")
    for art in artifacts or []:
        if not art.get("deterministic", True):
            continue
        payload = art.get("payload") or {}
        parts.append(
            "|".join(
                [
                    str(art.get("task_kind") or ""),
                    str(art.get("engine_id") or ""),
                    str(art.get("latex") or ""),
                    str(payload.get("exact") or ""),
                    str(payload.get("balanced") or ""),
                    str(payload.get("official_answer") or ""),
                    str(payload.get("formula") or ""),
                    str(payload.get("chart_type") or ""),
                    str(payload.get("diagram_type") or ""),
                ]
            )
        )
    for c in citations or []:
        parts.append(f"cite:{c}")
    blob = "\n".join(sorted(parts))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24]


def package_path(fingerprint: str) -> Path:
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    return APPROVED_DIR / f"{fingerprint}.json"


def load_approved_package(fingerprint: str) -> dict | None:
    path = package_path(fingerprint)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def find_approved_for_topic(topic: str) -> dict | None:
    """Best-effort lookup by topic slug when fingerprint unknown."""
    if not APPROVED_DIR.is_dir():
        return None
    topic_l = (topic or "").strip().lower()
    if not topic_l:
        return None
    matches: list[dict] = []
    for path in APPROVED_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (data.get("topic") or "").strip().lower() == topic_l and data.get("approved"):
            matches.append(data)
    if not matches:
        return None
    matches.sort(key=lambda d: d.get("approved_at") or "", reverse=True)
    return matches[0]


def approve_chapter_package(
    *,
    topic: str,
    artifacts: list[dict],
    preferred_visuals: list[dict] | None = None,
    knowledge: dict | None = None,
    biology_figures: list[dict] | None = None,
    stem_prompt_block: str = "",
    approved_by: str = "teacher",
    notes: str = "",
    source_hash: str = "",
) -> dict[str, Any]:
    """
    Persist verified Knowledge + Computation payloads for reuse.
    Teaching layer must only personalize presentation after this.
    """
    knowledge = knowledge or {}
    citations = list(knowledge.get("citations") or [])
    fp = factual_fingerprint(topic, artifacts, citations, source_hash)
    package = {
        "package_id": fp,
        "fingerprint": fp,
        "topic": topic,
        "source_hash": source_hash,
        "approved": True,
        "approved_at": _now(),
        "approved_by": approved_by,
        "notes": notes,
        "engine_artifacts": artifacts,
        "preferred_visuals": preferred_visuals or [],
        "biology_figures": biology_figures or [],
        "knowledge": {
            "pilot_id": knowledge.get("pilot_id"),
            "subject": knowledge.get("subject"),
            "grade": knowledge.get("grade"),
            "citations": citations,
            "rag_hits": knowledge.get("rag_hits") or [],
            "official_mcqs": knowledge.get("official_mcqs") or [],
            "prompt_block": knowledge.get("prompt_block") or "",
        },
        "stem_prompt_block": stem_prompt_block,
        "reuse_policy": "facts_locked_presentation_only",
    }
    path = package_path(fp)
    path.write_text(json.dumps(package, indent=2), encoding="utf-8")
    package["path"] = str(path)
    return package


def list_approved_packages(limit: int = 50) -> list[dict]:
    if not APPROVED_DIR.is_dir():
        return []
    rows: list[dict] = []
    for path in sorted(APPROVED_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rows.append(
            {
                "fingerprint": data.get("fingerprint"),
                "topic": data.get("topic"),
                "approved_at": data.get("approved_at"),
                "approved_by": data.get("approved_by"),
                "artifact_count": len(data.get("engine_artifacts") or []),
                "path": str(path),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def apply_approved_facts_to_meta(meta: dict, package: dict) -> dict:
    """Merge approved facts into generation _meta (presentation still regenerated)."""
    out = dict(meta or {})
    out["engine_artifacts"] = package.get("engine_artifacts") or out.get("engine_artifacts") or []
    out["preferred_visuals"] = package.get("preferred_visuals") or out.get("preferred_visuals") or []
    out["biology_figures"] = package.get("biology_figures") or out.get("biology_figures") or []
    if package.get("knowledge"):
        out["knowledge"] = package["knowledge"]
    out["chapter_approved"] = True
    out["approved_package_id"] = package.get("fingerprint")
    out["approved_at"] = package.get("approved_at")
    return out
