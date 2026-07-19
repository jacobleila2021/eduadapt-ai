"""Source parsers — reuse KIE; support inline JSON / file adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from engines.curriculum_migration_framework.licensing import sanitize_filename
from engines.curriculum_migration_framework.schemas import SUPPORTED_SOURCE_TYPES


def detect_source_type(path: str = "", hint: str = "") -> str:
    if hint and hint in SUPPORTED_SOURCE_TYPES:
        return hint
    ext = Path(path).suffix.lower().lstrip(".") if path else ""
    mapping = {
        "pdf": "pdf",
        "docx": "docx",
        "doc": "docx",
        "epub": "epub",
        "html": "html",
        "htm": "html",
        "md": "markdown",
        "markdown": "markdown",
        "xml": "xml",
        "json": "json",
        "zip": "zip",
    }
    return mapping.get(ext, hint or "inline_json")


def parse_source(
    *,
    path: str = "",
    inline: dict[str, Any] | None = None,
    source_type: str = "",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Parse curriculum source into a raw package dict.
    Reuses KIE for document paths when available; never invents curriculum text.
    """
    meta = meta or {}
    st = detect_source_type(path, source_type)
    if inline is not None:
        return {
            "ok": True,
            "source_type": "inline_json",
            "raw": dict(inline),
            "parser": "cmif_inline",
            "filename": sanitize_filename(str(meta.get("filename") or "inline.json")),
        }

    if not path:
        return {"ok": False, "error": "missing_source", "supported": list(SUPPORTED_SOURCE_TYPES)}

    p = Path(path)
    if not p.is_file():
        return {"ok": False, "error": "file_not_found", "path": path}

    if st == "json":
        raw = json.loads(p.read_text(encoding="utf-8"))
        return {"ok": True, "source_type": st, "raw": raw, "parser": "cmif_json", "filename": sanitize_filename(p.name)}

    # Prefer KIE for binary / rich documents
    try:
        from engines.knowledge_ingestion_engine.service import api_upload_document

        kie = api_upload_document(str(p), **meta)
        pkg = kie.get("package") or kie
        return {
            "ok": bool(kie.get("ok", True)),
            "source_type": st,
            "raw": _kie_to_raw(pkg, meta),
            "parser": "kie",
            "kie": {k: kie.get(k) for k in ("ok", "package_id", "errors") if k in kie or True},
            "filename": sanitize_filename(p.name),
        }
    except Exception as exc:  # noqa: BLE001
        # Markdown / text fallback — extract only, do not invent
        if st in ("markdown", "html", "xml"):
            text = p.read_text(encoding="utf-8", errors="replace")
            return {
                "ok": True,
                "source_type": st,
                "raw": {
                    "board": meta.get("board"),
                    "subject": meta.get("subject"),
                    "grade": meta.get("grade"),
                    "topics": [{"id": "t0", "title": meta.get("title") or p.stem, "definition": text[:2000]}],
                    "learning_objectives": [f"Study {p.stem}"],
                    "body": text[:50000],
                },
                "parser": "cmif_text_fallback",
                "filename": sanitize_filename(p.name),
                "warning": str(exc),
            }
        return {"ok": False, "error": "parse_failed", "detail": str(exc), "source_type": st}


def _kie_to_raw(pkg: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    cur = pkg.get("curriculum") or {}
    return {
        "board": meta.get("board") or cur.get("board") or "cbse",
        "subject": meta.get("subject") or cur.get("subject") or "",
        "grade": meta.get("grade") or cur.get("grade") or "",
        "topics": pkg.get("concepts") or [],
        "learning_objectives": pkg.get("learning_objectives") or [],
        "formulae": pkg.get("equations") or pkg.get("formulae") or [],
        "figures": pkg.get("figures") or [],
        "glossary": pkg.get("vocabulary") or [],
        "official_questions": pkg.get("questions") or [],
        "accessibility": pkg.get("accessibility") or {"alt_text_required": True},
        "package_id": pkg.get("package_id"),
        "text_chunks": pkg.get("text_chunks") or [],
    }
