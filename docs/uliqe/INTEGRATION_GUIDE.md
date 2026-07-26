# ULIQE Integration Guide

## Sequence

```
Teacher upload → universal_ingest → build_universal_lesson_profile
      → build_universal_lesson_intelligence (optional stem passthrough)
      → validate_uli / gate_for_downstream
      → if allowed: teaching engines / AME / AIE / … / export
      → else: surface ULIQE report (Needs Review / Rejected)
```

## Compatibility
- **Do not** require ULIQE inside existing VLIE `process_lesson` until a dedicated wiring milestone.
- Optional: instantiate `UniversalLessonValidationEngine` — **not** registered in `engine_manager` by default.
- Keep `engines.qa` for adaptation publish STEM exactness; ULIQE validates **understanding**, not generated adaptations.

## Subject packs
Future Subject Intelligence should call `validate_uli` after attaching STEM metadata to ULI (Milestone 2.2+), then respect `downstream_allowed`.
