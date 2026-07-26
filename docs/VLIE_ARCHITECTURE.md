# VLIE — Engine Audit Report & Architecture

**Date:** 2026-07-16  
**Product:** Alora AI / EduAdapt  
**Objective:** Map existing code into Verified Learning Intelligence Engine (VLIE) without redesigning STEM/RAG.

---

## 1. Engine Audit Report

| VLIE Engine | Existing modules (reused) | Status |
|-------------|---------------------------|--------|
| **Curriculum Intelligence** | `knowledge/*`, `ncert_pipeline`, `pilot_config`, RAG | Facade `engines/curriculum_engine` |
| **Scientific Accuracy** | `engines/router`, `lesson_pipeline`, math/chem/physics/graphs/geometry/circuits/molecules/statistics/visualization | Facade `engines/scientific_accuracy_engine` |
| **Assessment & Mastery** | `question_bank`, `question_rag`, worksheet enrich, exam inject | Facade `engines/assessment_engine` |
| **Accessibility Intelligence** | `adaptation_specs`, `accessibility.py`, `lesson_design` | Facade `engines/accessibility_engine` |
| **Adaptive Learning** | `ai_generator` difference scoring / pathways | Facade `engines/adaptive_learning_engine` |
| **AI Tutor** | `tutor` adaptation, `audio_learning.py` | Facade `engines/ai_tutor_engine` |
| **Analytics & Insights** | `analytics_engine.py` | Facade `engines/learning_analytics_engine` |
| **Gamification** | *(none)* | New stub `engines/gamification_engine` |
| **Multi-Agent Orchestrator** | `agents/orchestration.py` | Facade `engines/multi_agent_engine` + teaching via agents |
| **Quality Assurance** | `engines/qa/pipeline.py`, `chapter_cache.py` | Facade `engines/quality_assurance_engine` |
| **VLIE (coordinator)** | *(new)* | `engines/verified_learning_engine/*` |

**Duplicates avoided:** No second ChemPy/SymPy/RAG. Facades call existing APIs.

**Overlaps noted:** Teaching generation still owns STEM/RAG inside `ai_generator` when `generate_adaptations=True` (intentional — prevents double engine cost). VLIE package mirrors those outputs.

---

## 2. Module Structure

```
engines/
  base.py                          # BaseEngine interface
  verified_learning_engine/        # VLIE core
    orchestrator.py
    workflow.py
    validator.py
    package_builder.py
    engine_registry.py
    engine_manager.py
    execution_context.py
    result_merger.py
    audit_logger.py
  curriculum_engine/
  scientific_accuracy_engine/
  assessment_engine/
  accessibility_engine/
  adaptive_learning_engine/
  ai_tutor_engine/
  learning_analytics_engine/
  gamification_engine/
  multi_agent_engine/
  quality_assurance_engine/
  # Existing STEM modules unchanged:
  mathematics/, chemistry/, physics/, graphs/, ...
```

---

## 3. Data Flow

```
Lesson text
    │
    ▼
VLIE Orchestrator
    ├─ (light) accessibility / adaptive / tutor / analytics / gamification / multi-agent plan
    ├─ Multi-Agent teaching → ai_generator (STEM + RAG + adaptations + QA)
    ├─ ResultMerger
    ├─ PackageBuilder → Verified Learning Package (JSON)
    └─ VLIEValidator → publish gate mirror
```

Engines **do not** call each other. Only VLIE invokes engines.

---

## 4. Verified Learning Package (VLP)

Fields: lesson metadata, curriculum citations, verified STEM artifacts, visuals, accessibility flags, assessment assets, tutor resources, analytics, gamification, QA report, version history, audit trail.

Persisted under: `data/knowledge/verified_packages/{run_id}.json`

---

## 5. Engine Interface

Every facade implements `BaseEngine`:

- `initialize()`, `process()`, `validate()`, `enrich()`, `export()`, `health_check()`

---

## 6. Migration Plan

| Step | Action | Risk |
|------|--------|------|
| 1 | Ship VLIE + facades alongside existing modules | Low |
| 2 | `app.py` entry → `VerifiedLearningOrchestrator.process_lesson` | Low |
| 3 | Keep `AloraOrchestrator` / `generate_adaptations` as teaching backend | None |
| 4 | Gradually pass VLIE precomputed stem into ai_generator (optional later) | Medium |
| 5 | Persist gamification / mastery when Section C starts | Low |

**Rollback:** Point `app.py` back to `AloraOrchestrator` / `generate_adaptations` directly.

---

## 7. Testing Strategy

- Registry lists 10 engines; health_check all
- `process_lesson(..., generate_adaptations=False)` runs enrichment engines without OpenAI
- Package builder produces schema_version 1.0.0
- Regression: existing STEM/router/QA tests unchanged

---

## 8. Configuration / Feature Flags

`ExecutionContext.feature_flags` e.g. `{"gamification": true}`  
Registry `enable` / `disable` per engine_id.

---

## 9. Learning Session Orchestrator (LSO) extension

VLIE now also orchestrates the **learner journey** (sessions, events, workflows, decisions). See:

- **`docs/EVENT_DRIVEN_VLIE_ARCHITECTURE.md`** — event catalogue, state machine, APIs, migration notes
- Package modules: `session_manager`, `event_bus`, `workflow_manager`, `decision_engine`, `service.py`, …
- Smoke: `pytest tests/test_vlie_orchestration.py` → `VLIE_ORCHESTRATION_SMOKE_OK` (`requirements-dev.txt` + `pytest.ini`)

`process_lesson` / `run_engines` remain the Verified Learning Package path (unchanged contracts).
