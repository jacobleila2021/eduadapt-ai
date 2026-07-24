# Universal Educational Validation & Benchmarking (UEVB)

**Status:** Final production authority for learner experience  
**Smoke:** `UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK`  
**Not an intelligence engine** — validation, benchmarking, and release gating only.

## Mission

Validate the complete learner experience before production: educational quality, adaptation distinctness, engine contribution, visual design, curriculum consistency, and golden benchmarks.

## Pipeline position

```
Intelligence Board → LCE authorship → PQLE → Editorial Board → PMES → UEVB → Production
```

## Suite

- Subjects: Mathematics … World Languages
- Curricula: NCERT, CBSE, ICSE, ISC, Kerala SCERT, NIOS, Cambridge, IB, University, Professional
- Adaptations: Mainstream, Vocabulary, ADHD, Autism, Dyslexia, ELL, Visual, Auditory, Teacher, Parent, Worksheet

## Reports

Written under `reports/uevb/`:

- Universal Educational Validation Report
- Engine Contribution Report
- Adaptation Differentiation Report
- Publisher Benchmark Report
- Curriculum Consistency Report
- Visual Design Audit
- Regression Summary
- `dashboard_state.json`

## CLI

```bash
python -m uevb --smoke
python -m uevb --subjects physics biology --curricula cbse ncert --max-lessons 8
```

## Release gate

A release is permitted only when every lesson passes PMES, adaptations are pedagogically distinct, core engines show learner-visible value, pages meet the design system, publisher standards hold, and no regressions are detected.
