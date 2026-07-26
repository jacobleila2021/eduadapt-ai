# CEIP API

```python
from engines.commerce_economics_intelligence import (
    COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK,
    analyse_commerce_economics_lesson,
    commerce_economics_quality_signals,
    pack_health,
    register_commerce_economics_pack,
)

assert COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK
register_commerce_economics_pack(overwrite=True)
result = analyse_commerce_economics_lesson(uli)
signals = commerce_economics_quality_signals(uli)
health = pack_health()
```

Enrichment attaches under ULI subject intelligence via SIF; never mutates curriculum.
