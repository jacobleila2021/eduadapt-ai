# Curriculum Intelligence Engine (CIE) — Architecture & Audit

**Date:** 2026-07-17  
**Product:** Alora AI  
**Rule:** Wrap existing curriculum / knowledge modules — do not replace STEM, KIE, or VLIE.

---

## 1. Audit — current curriculum architecture

| Layer | Existing | Status before CIE |
|-------|----------|-------------------|
| VLIE facade | `engines/curriculum_engine/engine.py` | Thin RAG wrapper only |
| Pilot scope | `knowledge/pilot_config.py` | Single CBSE Class 8 Science |
| KIE tags | `CurriculumTag`, `normalize_hierarchy` | Hierarchy stub |
| Question bank | `OfficialMcq` board/grade/chapter/bloom | Assessment tags |
| Chroma | `ncert_class8_science`, `kie_*` | No concept/LO graph |
| Prerequisites / cross-board maps | — | Missing (deferred P4) |

### Reusable components (wrapped)

- `prepare_knowledge_for_lesson` — still the RAG entry
- `normalize_board` / `normalize_hierarchy` — extended via CIE `model.py`
- `ACTIVE_PILOT` — active curriculum binding
- VLIE `engine_id="curriculum"` — same slot, version 2.0.0

---

## 2. Gap analysis → filled

| Gap | CIE module |
|-----|------------|
| Unified curriculum model | `model.py` + `schemas.py` |
| Knowledge graph | `graph.py` + pilot ontology JSON |
| Learning outcomes / Bloom / DOK | `outcomes.py` |
| Prerequisites + gaps | `prerequisites.py` |
| Cross-curriculum mapping | `mapping.py` |
| Concept library | `concepts.py` |
| Learning progression | `progression.py` |
| Adaptation intelligence | `adaptations.py` (presentation only) |
| Search | `search.py` |
| Chroma CIE collections | `indexing.py` |
| API facade | `service.py` |
| Lesson enrichment | `intelligence.py` → `CurriculumEngine` |

---

## 3. Folder structure

```
engines/curriculum_intelligence_engine/
  __init__.py
  schemas.py
  model.py
  ontology.py
  graph.py
  outcomes.py
  prerequisites.py
  mapping.py
  concepts.py
  progression.py
  adaptations.py
  search.py
  indexing.py
  intelligence.py
  service.py
  data/pilot_ontology_class8_science.json
engines/curriculum_engine/engine.py   # VLIE facade (v2) — wraps CIE + knowledge.service
docs/CURRICULUM_INTELLIGENCE_ENGINE.md
tests/test_cie.py
```

---

## 4. Unified curriculum model

```
Curriculum → Programme → Grade → Subject → Unit → Chapter → Topic →
Concept → Learning Objective → Competency → Assessment Outcome →
Resources → Accessibility Supports → Adaptations
```

Original board terminology is preserved in `original_labels` / `original_term`.

---

## 5. Knowledge graph

In-memory directed graph (`CurriculumKnowledgeGraph`):

- Concept nodes with definitions, Bloom, DOK, keywords
- Prerequisite edges (`requires` / spiral-ready)
- Learning outcome nodes linked to concepts
- Cross-curriculum links (CBSE ↔ Cambridge / IB / ICSE)

Pilot seed: Class 8 Science concepts (Force, Pressure, Cell, Combustion, …).

---

## 6. Vector database strategy

| Key | Collection |
|-----|------------|
| curriculum_concepts | `cie_curriculum_concepts` |
| learning_outcomes | `cie_learning_outcomes` |
| competencies | `cie_competencies` |
| prerequisites | `cie_prerequisites` |
| curriculum_maps / cross links | `cie_cross_curriculum_links` |
| concept_resources / assessment_links | reserved |

Call `api_rebuild_index()` or `ensure_indexed(force=True)` to upsert.

Legacy NCERT / KIE collections unchanged.

---

## 7. API specification (Python / future REST)

| Function | Purpose |
|----------|---------|
| `api_list_curricula` | Supported systems + active pilot |
| `api_retrieve_curriculum` | Curriculum metadata |
| `api_retrieve_subject` / `api_retrieve_chapter` | Concept lists |
| `api_retrieve_concept` | Concept + path |
| `api_retrieve_prerequisite_map` | Dependency chain |
| `api_retrieve_competency` | Competency framework |
| `api_retrieve_learning_outcomes` | LO filter |
| `api_compare_curricula` | Bidirectional board compare |
| `api_search_concepts` / `api_search_curriculum_graph` | Search |
| `api_search_competencies` | Competency search |
| `api_analyze_lesson` | Lesson enrichment payload |
| `api_detect_gaps` / `api_progression` | Gaps + mastery levels |
| `api_rebuild_index` | Chroma sync |
| `api_equivalent_topics` | Cross-board equivalents |

---

## 8. Integration with VLIE / KIE

```
KIE (ingest) → verified packages / Chroma
       ↓
CIE (ontology + graph + search)  ← academic brain
       ↓
CurriculumEngine.process (VLIE stage "curriculum")
       ↓  still calls prepare_knowledge_for_lesson
ScientificAccuracy / Assessment / QA (depends_on curriculum)
```

- CIE **does not generate lessons**.
- Adaptations are **presentation recommendations only**.
- KIE remains batch entry; CIE consumes ontology (+ future package hooks).

---

## 9. Performance / security

- `@lru_cache` ontology load; incremental Chroma upsert
- Lazy index (`ensure_indexed`)
- Curriculum ontology treated as read-only seed; version field on packages
- Official source files never exposed via CIE APIs

---

## 10. Testing

`tests/test_cie.py` — graph, prerequisites, mapping, search, CurriculumEngine enrichment, registry health.

Smoke: `CIE_SMOKE_OK`

---

## 11. Migration guide

1. Existing callers of `CurriculumEngine` continue unchanged; payload gains `curriculum_intelligence`.
2. Add ontology JSON files under `data/` for new boards; loader stays the same.
3. Expand cross_maps without changing graph API.
4. Wire FastAPI later to `service.api_*` functions.

---

## 12. Maintenance

- Keep pilot ontology aligned with NCERT seed chapters.
- Prefer extending `normalize_*` helpers over forking.
- Never put LLM-invented LO codes into the graph — curated or KIE-extracted only.
