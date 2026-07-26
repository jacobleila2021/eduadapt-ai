# AI Tutor Intelligence Engine (ATIE) — Architecture

**Date:** 2026-07-17  
**Product:** Alora AI  
**Rule:** Retrieve verified evidence before any tutoring text. Never invent curriculum, STEM, or official answers.

---

## 1. Audit — before ATIE

| Component | State |
|-----------|--------|
| `AITutorEngine` | Thin resource stub (modes list + STEM hooks) |
| Conversational grounding | Missing |
| Hint ladder / Socratic / refusal | Missing |
| Session memory | Missing |

---

## 2. Architecture

```
CIE + AME + AIE + ALE + STEM + RAG/KIE
              ↓
   ai_tutor_intelligence_engine/*  (ATIE)
              ↓
   AITutorEngine (VLIE v2) → grounded turn + controls
              ↓
   LAIE (tutor analytics)
```

If evidence is insufficient → **refuse confidently** and suggest lesson/teacher.

---

## 3. Folder structure

```
engines/ai_tutor_intelligence_engine/
  schemas.py tutor_profile.py retrieval.py personalization.py
  explanations.py hints.py socratic.py worked_examples.py
  misconception_handler.py reasoning.py confidence.py
  executive_function_coach.py reflection.py motivation.py multimodal.py
  session_memory.py conversation_manager.py prompts.py
  analytics.py recommendations.py indexing.py intelligence.py service.py engine.py
engines/ai_tutor_engine/engine.py   # VLIE facade v2
docs/AI_TUTOR_INTELLIGENCE_ENGINE.md
tests/test_atie.py
data/knowledge/atie/  (sessions + analytics, gitignored)
```

---

## 4. Tutoring modes

Socratic, guided discovery, direct instruction, worked examples, step coaching, retrieval practice, spaced review, exam prep, reflection, EF coach, parent/teacher explanation modes.  
Teacher override + require-Socratic + disable-direct-answers supported.

---

## 5. APIs

`api_start_tutoring_session`, `api_end_session`, `api_retrieve_learner_context`,  
`api_generate_explanation`, `api_generate_hint`, `api_retrieve_worked_example`,  
`api_record_reflection`, `api_update_session_memory`, `api_retrieve_tutor_analytics`,  
`api_rebuild_index`

---

## 6. Security

- No medical diagnoses  
- Parents: summaries only (no assessment keys)  
- Session JSON local; configurable retention  
- Audit explainability on every turn  

---

## 7. Testing

`tests/test_atie.py` · smoke `ATIE_SMOKE_OK`
