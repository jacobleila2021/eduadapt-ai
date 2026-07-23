# Educational Acceptance Testing System (EATS)

**Smoke:** `EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK`  
**Role:** Editor-in-chief — the last gate before any lesson reaches a learner  
**Scope:** Sits **above** ULI → SIF → UVIE → LCE → PQLE → Render  
**Rule:** Validates outputs. Does **not** generate lessons. Does **not** modify intelligence engines.

## Pipeline

```
Upload → ULI → Subject Intelligence → UVIE → LCE → PQLE → Render All Adaptations
  → Educational Acceptance Testing → Pass / Revise / Reject
```

## What EATS evaluates (every adaptation independently)

Mainstream · Vocabulary · Visual · Auditory · ADHD · Autism · Dyslexia · ELL · LD · Teacher · Parent · Exam Worksheet

### Score dimensions

Writing · Educational · Visual · Accessibility · Pedagogy · Vocabulary · Layout · Adaptation · Assessment · Diagram  

**Overall Publisher Score** = worst adaptation overall (every learner version must clear the bar).

### Pass bands

| Score | Band |
|------:|------|
| 95+ | Publisher Ready |
| 90–94 | Excellent |
| 85–89 | Good |
| 80–84 | Needs Improvement |
| &lt;80 | Reject |

Publisher-ready requires **≥ 95**. Below that: revise (max 3 attempts via PQLE revise API) → re-evaluate → reject if still short.

## Package layout

| Module | Role |
|--------|------|
| `eats/pipeline.py` | `accept_lesson` orchestrator |
| `eats/evaluator.py` | Per-adaptation evaluation |
| `eats/checks.py` | Writing, pedagogy, vocab, diagrams, accessibility… |
| `eats/revise_gate.py` | Calls existing PQLE revise (read-only consumer) |
| `eats/screenshots.py` | HTML snapshots + optional Playwright PNGs → `reports/screenshots/` |
| `eats/reports.py` | Publisher Quality Report → `reports/eats/` |
| `eats/dashboard.py` | Acceptance dashboard metrics |
| `eats/golden_library.py` | Promote 98+ exemplars; compare to `golden_lessons/` |
| `eats/hooks.py` | `attach_eats_to_adaptations`, gate helper |

## Integration hooks (non-breaking)

1. **`publication_gate.py`** — blocks render/export when `_meta.eats.reject_rendering`
2. **`ai_generator.generate_adaptations`** — attaches `_meta.eats` after QA (engines untouched)

## Reports & screenshots

- `reports/eats/*_publisher_quality_report.json|md`
- `reports/screenshots/<run_id>/` — per-adaptation HTML, mosaic, optional desktop/tablet/mobile PNG
- `reports/eats/dashboard_state.json`

## Tests

```bash
python -m pytest tests/test_eats.py -q -s
```

Smoke must print exactly:

```text
EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK
```
