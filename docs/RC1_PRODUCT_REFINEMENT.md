# Phase RC1 — Product Refinement & Release Candidate

**Smoke:** `PRODUCT_REFINEMENT_RC1_SMOKE_OK`  
**Tag:** `ALORA-AI-RC1`  
**Law:** No new engines, frameworks, validators, boards, orchestration layers, or pipelines. Refinement only.

## Product law

Every commit must improve lesson quality, adaptation quality, visual quality, speed, rendering, narration, accessibility, reliability, or usability — without adding architectural complexity.

## Golden lesson library

Permanent quality benchmarks now cover major curriculum areas (13+ exemplars), including:

Mathematics · Physics · Chemistry · Biology · Geography · History · English · Environmental Science

New composed lessons are scored against the closest subject/topic golden via `compare_to_golden`.

## Release candidate loop

```bash
python -m release --smoke          # fast sample
python -m release --target 100     # ≥100 benchmark packages
```

Inspect randomly → fix learner-facing defects → repeat. Do not stop after one pass.

## Success definition

Independent teachers report generated lessons are classroom-ready without further editing.
