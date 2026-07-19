"""Multi-format document adapters — wrap existing parsers where possible."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any

MAX_ARCHIVE_EXPANDED_BYTES = 200 * 1024 * 1024


def _parse_with_v3_envelope(path: Path) -> dict[str, Any]:
    from engines.knowledge_ingestion_engine.universal_ingest import (
        ingest_source_bytes,
    )

    envelope = ingest_source_bytes(path.name, path.read_bytes())
    pages = [
        {
            "page": block.page or block.slide or 1,
            "slide": block.slide,
            "text": block.text,
            "block_id": block.block_id,
            "kind": block.kind,
            "extraction_method": block.extraction_method,
            "ocr_confidence": block.ocr_confidence,
            "metadata": block.metadata,
        }
        for block in envelope.blocks
    ]
    return {
        "text": envelope.text,
        "pages": pages,
        "format": envelope.detected_format,
        "source_envelope": envelope.to_dict(),
        "diagnostics": {
            "status": envelope.status,
            "warnings": envelope.warnings,
            "errors": envelope.errors,
            "readable_content_score": envelope.readable_content_score,
        },
        "tables": [page for page in pages if page["kind"] == "table"],
        "headings": [
            page["text"] for page in pages if page["kind"] == "heading"
        ],
        "figures": [
            page
            for page in pages
            if page["kind"] == "image_text"
            or page.get("metadata", {}).get("embedded_asset")
        ],
    }


def parse_txt(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {"text": text, "pages": [{"page": 1, "text": text}], "format": "txt"}


def parse_markdown(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = re.findall(r"^#{1,3}\s+(.+)$", text, flags=re.M)
    return {"text": text, "pages": [{"page": 1, "text": text}], "headings": headings, "format": "md"}


def parse_html(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return {"text": text, "pages": [{"page": 1, "text": text}], "format": "html"}


def parse_docx(path: Path) -> dict[str, Any]:
    return _parse_with_v3_envelope(path)


def parse_pptx(path: Path) -> dict[str, Any]:
    return _parse_with_v3_envelope(path)


def parse_epub(path: Path) -> dict[str, Any]:
    """Lightweight EPUB: unzip HTML/XHTML and strip tags."""
    parts: list[str] = []
    try:
        with zipfile.ZipFile(path, "r") as zf:
            expanded = 0
            names = []
            for info in zf.infolist():
                member = Path(info.filename.replace("\\", "/"))
                if member.is_absolute() or ".." in member.parts:
                    continue
                expanded += max(info.file_size, 0)
                if expanded > MAX_ARCHIVE_EXPANDED_BYTES:
                    break
                if info.filename.lower().endswith((".xhtml", ".html", ".htm", ".xml")):
                    names.append(info.filename)
            for name in names[:80]:
                raw = zf.read(name).decode("utf-8", errors="replace")
                text = re.sub(r"<[^>]+>", " ", raw)
                text = re.sub(r"\s+", " ", text).strip()
                if len(text) > 40:
                    parts.append(text)
    except Exception:
        return {
            "text": "",
            "pages": [],
            "format": "epub",
            "error": "The EPUB archive could not be read safely.",
        }
    text = "\n\n".join(parts)
    return {"text": text, "pages": [{"page": i + 1, "text": p} for i, p in enumerate(parts)], "format": "epub"}


def parse_image_ocr(path: Path) -> dict[str, Any]:
    return _parse_with_v3_envelope(path)


def parse_zip_package(path: Path, work_dir: Path) -> list[Path]:
    """Extract ZIP lesson package; return member files to ingest."""
    work_dir.mkdir(parents=True, exist_ok=True)
    out: list[Path] = []
    with zipfile.ZipFile(path, "r") as zf:
        expanded = 0
        root = work_dir.resolve()
        for info in zf.infolist():
            member = Path(info.filename.replace("\\", "/"))
            if member.is_absolute() or ".." in member.parts:
                raise ValueError("ZIP package contains an unsafe member path")
            expanded += max(info.file_size, 0)
            if expanded > MAX_ARCHIVE_EXPANDED_BYTES:
                raise ValueError("ZIP package expands beyond the allowed size")
            if info.compress_size and info.file_size / info.compress_size > 200:
                raise ValueError("ZIP package has an unsafe compression ratio")
            target = (work_dir / member).resolve()
            if root not in target.parents and target != root:
                raise ValueError("ZIP package member escapes the extraction folder")
            if target.exists() and target.is_symlink():
                raise ValueError("ZIP package cannot overwrite a symbolic link")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, target.open("wb") as destination:
                while chunk := source.read(1024 * 1024):
                    destination.write(chunk)
            if not target.name.startswith("."):
                out.append(target)
    return out


def parse_pdf(path: Path, *, extract_figures: bool = True) -> dict[str, Any]:
    """Use the universal in-memory PDF extractor; curriculum indexing is separate."""
    return _parse_with_v3_envelope(path)
