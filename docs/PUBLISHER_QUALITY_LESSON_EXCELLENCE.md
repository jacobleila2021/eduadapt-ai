# Publisher-Quality Lesson Excellence (PQLE)

**Smoke:** `PUBLISHER_QUALITY_LESSON_EXCELLENCE_SMOKE_OK`  
**Threshold:** Publisher Quality Index (PQI) ≥ **95/100**  
**Scope:** Inside LCE · EERL · renderer · presentation — no new intelligence engines.

## What PQLE adds

1. **Writing excellence** — warm teacher voice; strips robotic AI phrasing  
2. **Publisher layout** — premium vocabulary cards, typography, section rhythm  
3. **Vocabulary excellence** — student-friendly + academic definitions, memory tip, lesson context  
4. **Adaptation personalities** — ADHD / Autism / ELL / Visual / Auditory / Teacher / Parent are structurally distinct  
5. **Diagram excellence** — premium SVG required; no placeholder “imagine a diagram”  
6. **Expanded EERL** — rejects robotic language, weak sequencing, missing diagrams, oversized paragraphs  
7. **Publisher Quality Index (PQI)** — 15 dimensions; publish only at ≥ 95  
8. **Golden lesson benchmarks** — `golden_lessons/` exemplars compared before render  
9. **Revise loop** — reject → rewrite → re-evaluate until publication standard  

## Pipeline

```
CLG → Adaptive Lenses → Writing Excellence → Diagram Enrichment
  → Golden Compare → PQI → EERL → Render (only if PQI ≥ 95)
```

## Key modules

| Module | Role |
|--------|------|
| `publisher_quality.py` | PQI scoring |
| `writing_excellence.py` | Prose polish |
| `golden.py` | Exemplar compare + seed |
| `revise.py` | Reject / rewrite / re-evaluate |
| `eerl.py` | Expanded editorial checks |
| `vocabulary.py` | PQLE flashcards |
| `lesson_design.py` / `structured_renderers.py` | Presentation polish |

## Tests

`python -c "import tests.test_pqle as t; t.test_publisher_quality_smoke()"`
