# ULIQE Architecture

**Engine:** Universal Lesson Intelligence Validation & Quality Engine  
**Package:** `engines.universal_lesson_validation`  
**Consumes:** `UniversalLessonIntelligence` (Milestone 2.1 facade) only  
**Does not:** generate lessons, invent content, or modify VLIE / ULI / AME / AIE / …

## Position in Alora

```
Ingest → ULI Facade → ULIQE → (optional gate) → Teaching / AME / AIE / … / Export
```

ULIQE is a **QA layer for understanding**, distinct from `engines.qa` (publish STEM exactness on adaptations).

## Pipeline

Receive ULI → Schema → Semantic → Curriculum → Pedagogy → Accessibility (+ readability) → STEM (math/chem/physics/bio + diagrams) → Assessment → Completeness → Consistency → Score → Certify

## Modules

| Module | Role |
|--------|------|
| `schemas.py` | Findings, scores, certification enum |
| `schema_check.py` | Malformed ULI rejection |
| `validator.py` | Pipeline + public validate/score/certify |
| `service.py` | API + `gate_for_downstream` |
| `engine.py` | Optional `BaseEngine` (not auto-registered) |
| Subject/a11y/assess modules | Deterministic rule packs |

## Design principles

1. Report deficiencies — never fill gaps with AI or invented facts.  
2. Reuse ULI semantic accessors; do not re-parse source text.  
3. Every finding includes `rule_id`.  
4. Curriculum is optional under `uploaded_source`.  
5. Only **Production Ready** sets `downstream_allowed=True`.

See also: Validation Rulebook, Scoring Methodology, Certification Workflow, API Documentation, Integration Guide, Maintenance Guide.
