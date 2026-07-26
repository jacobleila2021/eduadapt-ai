# MIP Integration Guide

## Prerequisites

- Subject Intelligence Framework installed (`engines/subject_intelligence_framework`)
- Universal Lesson Intelligence available for the lesson
- Optional: `ENABLE_ULI_PIPELINE=true` for automatic ULI → SIF → ULIQE wiring

## Registration

MIP auto-registers on import:

```python
import engines.mathematics_intelligence  # registers over mathematics placeholder
```

SIF `__init__` and `get_registry()` / `reset_registry_for_tests()` also ensure the pack is registered.

## ULI pipeline

When the ULI pipeline runs with enrichment:

1. Build / enrich ULI  
2. `enrich_uli_with_subject_intelligence(uli)`  
3. Subject detection → `mathematics` → MIP `analyse_lesson`  
4. Payload on `_meta.uli.subject_intelligence` and `LessonBundle.subject_intelligence`  
5. ULIQE mathematics stage may append `ULIQE.MATH.MIP.*` findings  

## Consumer wiring

| System | How to consume |
|--------|----------------|
| ATIE | `sif["atie"]["tutor_guidance"]` |
| AIE | `sif["aie"]["accessibility_guidance"]` |
| AME | `sif["ame"]["assessment_hints"]` |
| LXP | `sif["lxp"]["visuals"]` / `lxp_hints` — render only; MIP is metadata |
| VMLE | Follow `read_aloud_equations` / visual recommendations |
| LAIE / LMAS | Use `revision_summary` intervals and misconception ids |

## Constraints

- Do not bypass `engines/router.py` for STEM computation  
- Do not feed MIP outputs as official answers  
- Do not change ULIQE `score_findings` / `certify` when extending MIP signals  

## Feature flags

No separate MIP flag. Availability follows SIF + ULI pipeline flags. Computation Layer math remains independent.
