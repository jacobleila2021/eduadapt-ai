# ULIQE Maintenance Guide

1. **Add a rule:** implement `validate_*` returning `ValidationFinding` with stable `rule_id`; append to `PIPELINE_STAGES`; document in `VALIDATION_RULEBOOK.md`.
2. **Never** call LLMs from this package.
3. **Never** write into ULI objects — read via facade accessors only.
4. **Tests:** extend `tests/test_uliqe.py` for each new rule (pass + fail case).
5. **Version:** bump `UniversalLessonValidationEngine.version` and note in Architecture doc when certification thresholds change.
6. **Regression:** run `pytest tests/test_uliqe.py tests/test_universal_lesson_intelligence_facade.py`.
