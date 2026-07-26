# Alora AI — Implementation Changelog (Section B completion)

**Date:** 2026-07-16  
**Scope:** Complete partially implemented features from `docs/SCIENTIFIC_LEARNING_FEATURES_AUDIT.md` Section B without rewriting Section A.

## Philosophy

- Extend existing modules; do not duplicate routers, engines, or RAG.
- Deterministic STEM remains authoritative; AI only explains/adapts presentation.
- Backward compatible: pypdf path retained; GeoGebra iframe retained; existing seeds still load.

---

## New modules

| Module | Purpose |
|--------|---------|
| `knowledge/ncert_pipeline.py` | Production PyMuPDF ingest: chapters, headings, tables, figures, content hashes, repository manifest |
| `knowledge/question_rag.py` | Chroma-backed semantic question bank + metadata filters |
| `engines/mathematics/advanced.py` | Limits, matrices, vectors, complex numbers, coord geometry, tangent/normal |
| `agents/orchestration.py` | Named multi-agent facade over existing `generate_adaptations` |
| `agents/__init__.py` | Package export |
| `docs/SECTION_C_FUTURE_ROADMAP.md` | Intentionally deferred capabilities |
| `docs/IMPLEMENTATION_CHANGELOG.md` | This file |

## Extended modules

| Module | Change |
|--------|--------|
| `engines/mathematics/solver.py` | Calls advanced math after calculus |
| `engines/statistics/engine.py` | Quartiles, IQR, regression, 95% CI, intro t-test |
| `engines/geometry/geogebra.py` | Conics, polygon, locus, coordinate; offline Matplotlib fallback PNG |
| `engines/qa/pipeline.py` | Reading level (FK), hallucination NEED_* scan, Bloom/LO, graph correctness, WCAG alt, scorecard |
| `knowledge/service.py` | Semantic question merge; `inject_exam_practice_into_lessons` |
| `knowledge/question_bank.py` / seed | (prior) HOTS/competency/PYQ/sample fields |
| `adaptation_specs.py` | Enabled remaining adaptations + `exam_revision` |
| `navigation.py` | Grouped neurodiversity / extension / exam pills |
| `ai_generator.py` | Exam practice inject + QA scorecard |
| `app.py` | Uses `AloraOrchestrator` |
| `test_ux_fixes.py` | Updated navigation/OUTPUT_KEYS assertions |
| `tests/test_section_b_completion.py` | New regression tests |

## Migration notes

1. **Generation cost:** More `generate:True` adaptations → longer OpenAI runs. Orchestrator still parallelizes lesson keys.
2. **Chroma:** Question collection `questions_{pilot_id}` created beside existing NCERT chunk collection under `data/knowledge/chroma/`.
3. **PDF ingest:** Prefer `knowledge.ncert_pipeline.ingest_pdf_pipeline(path)` for production; `ingest_pdf_to_chunks` remains for simple text.
4. **GeoGebra:** Offline PNG appears in `asset_paths` when Matplotlib available; iframe still primary.
5. **QA:** Critical failures still block publish; reading-level extremes >18 block; softer checks recorded in scorecard without always blocking.

## Testing performed

```
python -c "...Section B smoke..."
# calculus, advanced limit/matrix, stats regression, geogebra offline,
# question chroma ensure_index, orchestrator roster, adaptations generate flags,
# inject_exam_practice, reading-level QA
```

See `tests/test_section_b_completion.py`.
