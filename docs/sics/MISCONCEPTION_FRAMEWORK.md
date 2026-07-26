# Misconception Framework

`engines.subject_intelligence_core.misconceptions.detect_from_catalogue`

## Shared model fields

- `misconception_id`, `label`, `domain`
- `matched_patterns`, `correction_strategy`, `related_concepts`
- `confidence`, `provenance`
- Optional: `severity`, `remediation`, `intervention`, `evidence_links`

## Pack responsibilities

Each pack owns its catalogue (regex patterns + corrections). SICS owns detection mechanics and output shape.

```python
from engines.subject_intelligence_core.misconceptions import detect_from_catalogue
hits = detect_from_catalogue(MY_CATALOGUE, text, provenance="my_pack.misconceptions")
```
