# ULIQE API Documentation

```python
from engines.universal_lesson_validation import (
    validate_uli,
    score_uli,
    certify_uli,
    generate_report,
    compare_versions,
    list_validation_rules,
    gate_for_downstream,
    ULIQE_SMOKE_OK,
)
from engines.universal_lesson_intelligence import build_universal_lesson_intelligence

uli = build_universal_lesson_intelligence(envelope, profile, stem_metadata=stem)
report = validate_uli(uli)           # ULIQEReport
score_uli(uli)                       # dict scores
certify_uli(uli)                     # certification + downstream_allowed
generate_report(uli)                 # report.to_dict()
compare_versions(uli_v1, uli_v2)     # score/certification diff
list_validation_rules()              # pipeline stages
gate = gate_for_downstream(uli)      # {"allowed": bool, "report": ...}
assert ULIQE_SMOKE_OK is True
```

### Input
- `UniversalLessonIntelligence`, or
- `uli.to_dict()` snapshot (`source_envelope` + `universal_profile` [+ optional stem/classifications])

### Output highlights
`certification`, `overall_score`, `confidence`, `findings[]` (each with `rule_id`), gap lists, `downstream_allowed`.
