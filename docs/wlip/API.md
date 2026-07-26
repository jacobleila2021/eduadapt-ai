# WLIP API

```python
from engines.world_languages_intelligence import (
    WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK,
    analyse_world_languages_lesson,
    world_languages_quality_signals,
    pack_health,
    register_world_languages_pack,
    list_language_plugins,
)

assert WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK
register_world_languages_pack(overwrite=True)
result = analyse_world_languages_lesson(uli)
signals = world_languages_quality_signals(uli)
health = pack_health()
plugins = list_language_plugins()
```
