# Language Plugin Guide

```python
from engines.world_languages_intelligence import (
    list_language_plugins,
    register_language_plugin,
)

register_language_plugin(
    "swahili",
    {
        "code": "sw",
        "name": "Swahili",
        "scripts": ["Latin"],
        "direction": "ltr",
        "pronunciation_notes": ["syllable_timed"],
        "grammar_highlights": ["noun_classes"],
    },
    overwrite=True,
)

assert any(p["id"] == "swahili" for p in list_language_plugins())
```

Required fields: `code`, `name`, `scripts`, `direction`. Optional: pronunciation/grammar notes, `integration_only`.
