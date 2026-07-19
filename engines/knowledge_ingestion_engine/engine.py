"""Knowledge Ingestion Engine — VLIE-compatible BaseEngine facade."""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle
from engines.knowledge_ingestion_engine.pipeline import KnowledgeIngestionPipeline


class KnowledgeIngestionEngine(BaseEngine):
    """
    Universal source-ingestion facade plus the legacy batch indexing adapter.
    """

    engine_id = "knowledge_ingestion"
    version = "3.0.0"
    layer = "knowledge"
    priority = 5  # before curriculum when enabled for batch jobs

    def __init__(self) -> None:
        super().__init__()
        self.pipeline = KnowledgeIngestionPipeline()

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        envelope = context.get("source_envelope") or {}
        if envelope:
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=bool(envelope.get("ok")) or envelope.get("status") in {"readable", "partial"},
                payload={
                    "source_envelope": envelope,
                    "source_id": envelope.get("source_id"),
                    "readable_content_score": envelope.get("readable_content_score", 0),
                },
                errors=[
                    str(item.get("safe_message") or item.get("reason"))
                    for item in envelope.get("errors") or []
                ],
                warnings=[
                    str(item.get("safe_message") or item.get("reason"))
                    for item in envelope.get("warnings") or []
                ],
                deterministic=True,
            )
        source = context.get("source_path") or context.get("ingest_path")
        if not source:
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=True,
                payload={"skipped": True, "reason": "No source_path — KIE is batch-oriented"},
                warnings=["Provide source_path to ingest"],
            )
        result = self.pipeline.ingest(
            source,
            board=context.get("board"),
            grade=context.get("grade"),
            subject=context.get("subject"),
            curriculum=context.get("curriculum"),
            reindex=bool(context.get("reindex", True)),
            extract_figures=bool(context.get("extract_figures", True)),
        )
        return EngineResultBundle(
            engine_id=self.engine_id,
            ok=bool(result.get("ok")),
            payload=result,
            errors=result.get("package", {}).get("errors") or result.get("errors") or [],
            warnings=result.get("warnings") or [],
            assets=[
                f.get("path")
                for f in (result.get("package") or {}).get("figures") or []
                if f.get("path")
            ],
            deterministic=True,
        )

    def health_check(self) -> EngineHealth:
        deps = {}
        for name, mod in (
            ("pymupdf", "fitz"),
            ("chromadb", "chromadb"),
            ("pypdf", "pypdf"),
            ("docx", "docx"),
            ("pptx", "pptx"),
            ("pillow", "PIL"),
            ("pytesseract", "pytesseract"),
        ):
            try:
                __import__(mod)
                deps[name] = True
            except ImportError:
                deps[name] = False
        deps["tesseract_binary"] = bool(shutil.which("tesseract"))
        return EngineHealth(
            ok=bool(
                deps.get("pypdf")
                and deps.get("docx")
                and deps.get("pptx")
                and deps.get("pillow")
            ),
            engine_id=self.engine_id,
            version=self.version,
            dependencies=deps,
            detail=(
                "Universal PDF/DOCX/PPTX/image ingestion; OCR capability is optional "
                "for text-based sources"
            ),
        )


def ingest_document(path: str | Path, **kwargs: Any) -> dict[str, Any]:
    """Public convenience API."""
    return KnowledgeIngestionPipeline().ingest(path, **kwargs)
