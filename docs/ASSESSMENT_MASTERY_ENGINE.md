# Assessment & Mastery Engine (AME) — Architecture & Audit

**Date:** 2026-07-17  
**Product:** Alora AI  
**Rule:** Wrap official question bank + CIE — never invent answer keys or replace STEM/RAG.

---

## 1. Audit — before AME

| Area | Existing | Gap |
|------|----------|-----|
| VLIE AssessmentEngine | Thin bank/RAG facade | No mastery / interventions |
| Official bank | `question_bank` + seed JSON + Chroma | Item SSOT — reuse |
| Worksheet path | `ai_generator` + enrich inject | Keep; AME does not duplicate |
| CIE | LOs, competencies, progression | No learner evidence binding |
| Analytics | Lesson text stats | Not learner mastery |
| Misconceptions | STEM `common_mistakes` stubs | No curated detector |
| Adaptive | Presentation pathways only | No mastery-based item selection |

---

## 2. Architecture

```
Official bank / Question RAG / CIE
              ↓
   assessment_mastery_engine/*
              ↓
   AssessmentEngine (VLIE, v2)  → payload: bank + mastery + misconceptions
              ↓
   Adaptive / Tutor / Analytics (consume evidence)
```

AME is the **evidence layer**: what the learner knows, gaps, misconceptions, next steps.

---

## 3. Folder structure

```
engines/assessment_mastery_engine/
  schemas.py store.py mastery.py evidence.py
  misconceptions.py interventions.py assessments.py adaptive.py
  exam_readiness.py revision.py dashboards.py indexing.py
  intelligence.py service.py
  data/misconceptions_class8_science.json
engines/assessment_engine/engine.py   # VLIE facade v2
docs/ASSESSMENT_MASTERY_ENGINE.md
tests/test_ame.py
data/knowledge/ame/learners/          # JSON learner ledgers
```

---

## 4. Frameworks

| Mode | Module | Behavior |
|------|--------|----------|
| Diagnostic | `assessments.py` | Bank items + CIE prerequisite gaps |
| Formative | `assessments.py` | Exit ticket / quick check packaging |
| Summative | `assessments.py` | Exam bundle sections |
| Competency | `assessments.py` | CIE competency bindings |
| Adaptive | `adaptive.py` | Difficulty from mastery + a11y accommodations |
| Mastery | `mastery.py` | Multi-evidence levels (never single score) |
| Misconceptions | `misconceptions.py` | Curated Class 8 Science patterns |
| Interventions | `interventions.py` | Visual / worked / tutor / EF / teacher |
| Revision | `revision.py` | Weak concepts + official practice + spacing |
| Exam readiness | `exam_readiness.py` | Coverage + predicted readiness |
| Dashboards | `dashboards.py` | Student / teacher / parent / school payloads |

### Mastery ladder

`beginning → developing → approaching_proficiency → proficient → advanced → mastered`

Proficient+ requires **≥2 evidence points**.

---

## 5. Chroma collections

| Key | Collection |
|-----|------------|
| assessment_items | `ame_assessment_items` |
| official_answers | `ame_official_answers` |
| misconceptions | `ame_misconceptions` |
| interventions | `ame_interventions` |
| competencies | `ame_competencies` |
| revision_resources | mirrors interventions |
| mastery_records | reserved (JSON store primary) |

Legacy `questions_{pilot}` unchanged.

---

## 6. API (`service.api_*`)

`api_generate_assessment`, `api_submit_answers`, `api_evaluate_response`,  
`api_retrieve_mastery`, `api_retrieve_competencies`, `api_retrieve_interventions`,  
`api_generate_revision_plan`, `api_retrieve_exam_readiness`, `api_retrieve_analytics`,  
`api_detect_misconceptions`, `api_dashboards`, `api_rebuild_index`, `api_analyze_context`

---

## 7. Integration rules

1. Official answers only from bank / SAE — never LLM keys.
2. CIE provides concept/LO/competency IDs and prerequisite gaps.
3. Accessibility accommodations change presentation/time — not item content.
4. Teacher chapter cache and worksheet enrich paths remain authoritative for lessons.
5. Same VLIE `engine_id="assessment"`.

---

## 8. Security / performance

- Learner JSON under `data/knowledge/ame/learners/` (local pilot; encrypt at rest in production).
- Incremental mastery recompute on submit.
- Cached misconception bank (`lru_cache`).
- Role dashboards are data APIs — enforce RBAC at HTTP layer later.

---

## 9. Testing

`tests/test_ame.py` + smoke `AME_SMOKE_OK`.

---

## 10. Migration

1. Callers of AssessmentEngine get richer payload; old keys (`official_mcqs`, `exam_bundle`, `mastery_hooks`) preserved.
2. Pass `learner_id` in VLIE context to enable mastery/revision.
3. Expand misconception JSON per subject without changing APIs.
