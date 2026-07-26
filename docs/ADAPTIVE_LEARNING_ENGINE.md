# Adaptive Learning Engine (ALE) — Architecture & Audit

**Date:** 2026-07-17  
**Product:** Alora AI  
**Rule:** Decision engine only — never generate lessons; never alter curriculum/STEM/official answers.

---

## 1. Audit — before ALE v2

| Area | State |
|------|--------|
| `AdaptiveLearningEngine` | Thin stub: `pathways` = AIE `profiles_generated` |
| Pathway / pacing / SR | Missing |
| Explainability | Missing |
| Teacher override | Missing |

---

## 2. Architecture

```
CIE (prereqs, concepts) + AME (mastery, misconceptions) + AIE (presentation)
                              ↓
                 adaptive_learning_engine/*
                              ↓
        AdaptiveLearningEngine (VLIE v2) → next activity + explainability
                              ↓
                    AI Tutor / Dashboards / Analytics
```

ALE decides **what / when / how (presentation) / when to review** — not content.

---

## 3. Folder structure

```
engines/adaptive_learning_engine/
  engine.py schemas.py learner_model.py learning_path.py
  sequencing.py mastery.py pacing.py spaced_repetition.py
  misconceptions.py intervention.py enrichment.py
  confidence.py predictive.py recommendations.py scheduler.py
  analytics.py dashboards.py indexing.py intelligence.py service.py
docs/ADAPTIVE_LEARNING_ENGINE.md
tests/test_ale.py
data/knowledge/ale/   # models + analytics (gitignored)
```

---

## 4. Teacher Override & Explainability Layer

Every decision returns `ExplainableDecision` with:

- `choice`, `explanation`, `evidence[]`, `confidence`
- `teacher_override_allowed`
- API: `api_teacher_override(...)`

Example explanation:

> This learner is being recommended the 'dyslexia' presentation with difficulty 'guided' on concept 'c8sci.pressure' because confidence is 50%, N concepts are at risk, misconceptions were detected, and accessibility profiles indicate [...].

---

## 5. APIs

`api_get_learner_model`, `api_update_learner_state`, `api_generate_learning_pathway`,  
`api_get_next_activity`, `api_generate_intervention_plan`, `api_generate_enrichment_plan`,  
`api_schedule_review`, `api_predict_learner_outcomes`, `api_retrieve_adaptive_analytics`,  
`api_teacher_override`, `api_dashboards`, `api_rebuild_index`

---

## 6. Integration

| Engine | ALE uses |
|--------|----------|
| CIE | Prerequisites, matched concepts, next concepts |
| AME | Mastery bands, misconceptions, interventions, exam readiness |
| AIE | Presentation mode, readability/cognitive load, profiles |
| AI Tutor | Receives `tutor_brief` + `next_activity` |
| VLIE | `depends_on=["accessibility","curriculum","assessment"]` |

Backward-compatible keys retained: `pathways`, `pacing`, `difference_target`, `next_best_lesson`.

---

## 7. Data model

Structured JSON under `data/knowledge/ale/learner_models/` (primary).  
Chroma only for pathway/difficulty catalogs (`ale_*`).

---

## 8. Testing

`tests/test_ale.py` · smoke `ALE_SMOKE_OK`
