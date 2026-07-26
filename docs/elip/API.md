# ELIP API Documentation

```python
from engines.english_language_intelligence import (
    ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK,
    analyse_english_lesson,
    english_quality_signals,
    pack_health,
)

assert ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK is True
result = analyse_english_lesson(uli)
signals = english_quality_signals(uli)  # ULIQE.ENG.ELIP.*
```

SIF path: `enrich_uli_with_subject_intelligence(uli)` → `subject_key == "english"`.
