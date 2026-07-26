# SSIP API Documentation

```python
from engines.social_science_intelligence import (
    SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK,
    analyse_social_science_lesson,
    social_science_quality_signals,
    pack_health,
)

assert SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK is True
result = analyse_social_science_lesson(uli)
signals = social_science_quality_signals(uli)  # ULIQE.SOC.SSIP.*
```

SIF detection of `history` / `geography` / `civics` / `economics` / `environmental_science` also resolves to SSIP family packs.
