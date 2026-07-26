# ULIQE Validation Rulebook

Rules are deterministic. Severity: `info` | `warning` | `error` | `critical`.

## Schema
| ID | Severity | Meaning |
|----|----------|---------|
| ULIQE.SCHEMA.001 | critical | Cannot coerce ULI |
| ULIQE.SCHEMA.002 | error | Missing source_id |
| ULIQE.SCHEMA.003 | error | Required profile field empty |
| ULIQE.SCHEMA.004 | error | Claim id / type issues |
| ULIQE.SCHEMA.005 | warning | Weak provenance |
| ULIQE.SCHEMA.000 | info | Schema accepted |

## Completeness (COMP.xxx)
Missing title/objectives/concepts/vocab → error; missing definitions/prereqs/misconceptions/examples → warning; empty claim ledger → critical. Summary field absence → warning (ULI gap).

## Curriculum (CUR.xxx)
Unknown curriculum is **info** for `uploaded_source`, **error** for `official_curriculum_publish`. Bloom/DoK/prereq graph absence → warning (not invented).

## Pedagogy / Accessibility / Assessment / Semantic / STEM
See module docstrings (`pedagogy.py`, `accessibility.py`, `assessment.py`, `semantic.py`, `mathematics.py`, `chemistry.py`, `physics.py`, `biology.py`, `diagrams.py`, `readability.py`, `consistency.py`).

STEM packs **skip** with info when not applicable. Failed Computation Layer artifacts → error/critical (chemistry balancer especially).

## Extending rules
Add a function returning `list[ValidationFinding]`, register in `validator.PIPELINE_STAGES`. Keep `rule_id` stable and documented here.
