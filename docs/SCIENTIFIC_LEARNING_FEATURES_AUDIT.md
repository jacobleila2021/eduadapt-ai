# Alora AI — Scientific Learning Features Audit & Gap Analysis

**Date:** 2026-07-16 (updated after Section B completion)  
**Scope:** EduAdapt-ai / Alora AI codebase  
**Rule:** Verify existing → extend partial → implement missing only (no duplicates)

**Companion docs:**
- [`IMPLEMENTATION_CHANGELOG.md`](IMPLEMENTATION_CHANGELOG.md) — files changed in Section B pass
- [`SECTION_C_FUTURE_ROADMAP.md`](SECTION_C_FUTURE_ROADMAP.md) — intentionally deferred capabilities

---

## Gap Analysis Matrix (summary)

| # | Capability | Status | Evidence (primary) |
|---|------------|--------|-------------------|
| 1 | NCERT ingestion (PDF/figures) | **Implemented** | `knowledge/ncert_pipeline.py` + `ncert_figures_ingest.py` (PyMuPDF) |
| 2 | Question bank | **Implemented (pilot corpus)** | JSON seed + `knowledge/question_rag.py` Chroma index |
| 3 | RAG | **Implemented (pilot)** | `knowledge/rag.py` |
| 4 | Subject Tool Router | **Implemented** | `engines/router.py`, `answer_router.py` |
| 5 | Mathematics engine | **Implemented** | Algebra + calculus + limits/matrices/vectors/complex/coord |
| 6 | Graph engine | **Implemented** | Functions + chart types |
| 7 | Geometry / GeoGebra | **Implemented** | Expanded kinds + offline Matplotlib fallback |
| 8 | Physics viz | **Implemented** | Force + diagrams + Schemdraw |
| 9 | Chemistry | **Implemented** | Balance + atom validation + mhchem + RDKit/fallback |
| 10 | Biology diagrams | **Implemented (pilot)** | Curated SVG + PDF figure ingest/merge |
| 11 | Learning adaptations | **Implemented** | Full `generate:True` set including Exam Revision |
| 12 | AI orchestration | **Implemented** | `agents/orchestration.py` named agent facade |
| 13 | Exam question matching | **Implemented** | Bundle + Chroma semantic + lesson section inject |
| 14 | Teacher QA / chapter cache | **Implemented** | `knowledge/chapter_cache.py` |
| 15 | Viz priority | **Implemented** | `engines/visualization/priority.py` |
| 16 | Answer routing | **Implemented** | Full table |
| 17 | Validation / hard QA | **Implemented** | Reading level, NEED_*, Bloom, scorecard |
| 18 | Streamlit | **Implemented** | image/latex/iframe; PNG preferred over pyplot |

---

## Section A — Already Implemented (locked)

Do not rewrite unless defect found.

- Knowledge RAG (`knowledge/rag.py`, `service.py`, seed NCERT + official MCQs)
- Subject Tool Router + Answer Routing + claim → lesson pipeline
- Chemistry balance + atom validation; mhchem; RDKit/fallback
- Graphs (Matplotlib functions + charts)
- Physics force + diagrams + Schemdraw
- Visualization priority + AI diagram suppress
- Teacher chapter cache + hard publish gate (baseline)
- Streamlit STEM / knowledge panels
- Architecture docs + verified-knowledge Cursor rule

---

## Section B — Partially Implemented → **Completed**

| Feature | Was missing | Now implemented |
|---------|-------------|-----------------|
| **NCERT PDF ingest** | Deep PyMuPDF | `ncert_pipeline.py`: chapters, headings, tables, figures, hashes, repository manifest |
| **Question bank** | No Chroma Q index; thin types | `question_rag.py` Chroma collection; HOTS/competency/PYQ/sample in seed; semantic retrieve |
| **Math engine** | No calculus/advanced | Diff/integrate + limits, matrices, vectors, complex, distance/midpoint, tangent/normal |
| **Statistics** | Stub | Quartiles, IQR, regression, 95% CI, intro t-test |
| **GeoGebra** | Few presets | Conics, polygon, locus, coordinate + offline PNG fallback |
| **Biology diagrams** | Curated only | PDF ingest merge via `match_ingested_figures` |
| **Exam matching** | Worksheet only | `inject_exam_practice_into_lessons` + exam_bundle prompts |
| **Adaptations** | Many `generate:False` | Enabled neurodiversity, gifted, tutor, multisensory + `exam_revision` |
| **Exam Revision** | Missing | Dedicated adaptation + Exam & Revision nav group |
| **AI orchestration** | Sequential only | `AloraOrchestrator` named agents wrapping existing pipeline |
| **QA depth** | Soft checks | FK reading level, NEED_* hallucination, Bloom/LO, graph files, alt text, scorecard |
| **Streamlit pyplot** | Optional | Offline geometry uses Matplotlib save → `st.image` (intentional; no rewrite of working image path) |

---

## Section C — Future Roadmap (deferred)

See [`SECTION_C_FUTURE_ROADMAP.md`](SECTION_C_FUTURE_ROADMAP.md): multilingual, adaptive difficulty, curriculum ontology, enterprise admin, licensing, xAPI/LTI, full PYQ corpus, true multi-LLM agent swarm, etc.

---

## Architecture (unchanged)

```
Knowledge Layer ──► RAG + Question Bank (Chroma) + figures + chapter cache
        │
Computation Layer ──► Router → SymPy/ChemPy/Matplotlib/Schemdraw/RDKit/GeoGebra/Physics/Stats
        │
Teaching Layer ──► Orchestrator → ai_generator adaptations (presentation only)
        │
QA Gate ──► validate_lesson_package (+ scorecard) → exam_ready / publish_blocked
```

## Testing

- `tests/test_scientific_learning_gaps.py`
- `tests/test_section_b_completion.py`
- Smoke: `SECTION_B_SMOKE_OK` (19 generated adaptation keys; question Chroma indexed)
