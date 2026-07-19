"""Knowledge Ingestion Engine (KIE) — trusted entry for educational content."""

from engines.knowledge_ingestion_engine.engine import KnowledgeIngestionEngine, ingest_document
from engines.knowledge_ingestion_engine.pipeline import KnowledgeIngestionPipeline
from engines.knowledge_ingestion_engine import service as kie_api

__all__ = [
    "KnowledgeIngestionEngine",
    "KnowledgeIngestionPipeline",
    "ingest_document",
    "kie_api",
]
