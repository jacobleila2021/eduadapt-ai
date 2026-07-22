# UVIE API

```python
from engines.universal_visual_intelligence import (
    UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK,
    render_visuals_for_uli,
    inject_into_lesson,
    uvie_quality_signals,
    pack_health,
)

assert UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK
result = render_visuals_for_uli(uli, context={"text": lesson_text, "topic": topic})
lesson = inject_into_lesson(lesson, result)
signals = uvie_quality_signals(uli)
health = pack_health()
```

`result["preferred_visuals"]` is backward-compatible with SAE / exporters.
