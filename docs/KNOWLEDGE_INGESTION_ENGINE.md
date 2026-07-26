# Knowledge Ingestion Engine (KIE) — Architecture & Audit

**Date:** 2026-07-17  
**Product:** Alora AI  
**Rule:** Wrap existing `knowledge/*` — do not replace STEM/RAG/VLIE.

---

## 1. Audit — existing modules (reused)

| Capability | Existing | KIE role |
|------------|----------|----------|
| PDF text + structure | `knowledge/ncert_pipeline.py`, `ncert_ingest.py` | `adapters/parsers.parse_pdf` |
| Figures | `ncert_figures_ingest.py`, biology pack | PDF path + package.figures |
| Tables | `extract_tables_from_page` in ncert_pipeline | Carried in manifest/pages |
| Chroma chunks | `knowledge/rag.py` | Also `kie_curriculum_chunks` |
| Question Chroma | `question_rag.py` | Also `kie_question_bank` |
| Official bank | `question_bank.py` + seed JSON | Refreshed on index |
| DOCX (lesson) | `document_parser.py` | `parse_docx` adapter |
| VLIE curriculum | `curriculum_engine` | Consumes indexed knowledge |

## 2. Gap analysis → filled

| Gap | Implementation |
|-----|----------------|
| Unified ingest API | `KnowledgeIngestionPipeline` + `service.py` REST-shaped API |
| Multi-format | PDF, DOCX, PPTX, EPUB, TXT, HTML, MD, images (OCR stub), ZIP |
| Validation + hashing | `stages/validate.py` |
| Equation / question / LO extract | `stages/extract.py` |
| Semantic chunking | Concept/heading-aware (not page-only) |
| Separate Chroma collections | `stages/indexing.py` |
| Verified Knowledge Package | JSON under `data/knowledge/ingested/kie_packages/` |
| Curriculum normalization | `normalization.py` |
| CLI | `scripts/kie_ingest.py` (legacy `ingest_ncert_pilot.py` kept) |

## 3. Pipeline stages

```
Validate → Parse → Figures/Tables → Equations → Objectives →
Questions → Metadata → Semantic Chunk → Vector Index → Knowledge Package
```

## 4. Folder structure

```
engines/knowledge_ingestion_engine/
  __init__.py
  engine.py              # BaseEngine (batch; disabled on default lesson runs)
  pipeline.py
  service.py             # api_* functions
  schemas.py
  normalization.py
  adapters/parsers.py
  stages/validate.py
  stages/extract.py
  stages/indexing.py
scripts/kie_ingest.py
docs/KNOWLEDGE_INGESTION_ENGINE.md
tests/test_kie.py
```

## 5. Chroma collections

| Key | Collection name |
|-----|-----------------|
| curriculum_chunks | `kie_curriculum_chunks` |
| question_bank | `kie_question_bank` |
| figures / diagrams | `kie_figures` |
| formulas | `kie_formulas` |
| vocabulary | `kie_vocabulary` |
| worked_examples / misconceptions | reserved |

Legacy `ncert_class8_science` + `questions_{pilot}` still refreshed for backward compatibility.

## 6. Knowledge Package schema (v1.0.0)

`package_id`, `source_path`, `source_hash`, `curriculum` (+ hierarchy), `text_chunks`, `figures`, `tables`, `equations`, `questions`, `vocabulary`, `learning_objectives`, `concepts`, `accessibility`, `citations`, `index_status`, `version`, errors/warnings.

## 7. API specification (Python / future REST)

| Function | Intent |
|----------|--------|
| `api_upload_document` | POST /kie/documents |
| `api_reprocess_document` | POST /kie/documents/{id}/reprocess |
| `api_retrieve_package` | GET /kie/packages/{id} |
| `api_list_packages` | GET /kie/packages |
| `api_search_concepts` | GET /kie/search/concepts |
| `api_search_figures` | GET /kie/search/figures |
| `api_search_formulae` | GET /kie/search/formulae |
| `api_search_questions` | GET /kie/search/questions |
| `api_rebuild_index` | POST /kie/packages/{id}/reindex |

## 8. Security & performance

- SHA-256 duplicate index under `ingested/hashes/`
- 200MB cap; PDF magic-byte warning
- Sandbox note: never expose raw copyrighted PDFs in public UI
- Incremental upsert into Chroma; lazy OCR/PPTX deps
- KIE **disabled** in default VLIE lesson runs (enable for batch)

## 9. Migration

1. New content → `python scripts/kie_ingest.py <file>`
2. Old pilot script still works
3. Downstream engines unchanged — read same RAG/question paths

## 10. Testing

See `tests/test_kie.py` — validate, txt/md ingest, package fields, registry presence.
