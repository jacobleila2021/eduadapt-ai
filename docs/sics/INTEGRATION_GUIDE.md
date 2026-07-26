# SICS Integration Guide

## Import

```python
from engines.subject_intelligence_core import (
    SUBJECT_INTELLIGENCE_CORE_SMOKE_OK,
    core_health,
    SHARED_STRATEGY_CATALOGUE,
)
```

## Building a new subject pack

1. Keep pack-specific catalogues (domains, misconceptions, visuals).  
2. Call SICS builders for detection, strategies, graphs, visuals, assessment metadata.  
3. Register via SIF `get_registry().register(pack, overwrite=True)`.  
4. Emit additive ULIQE seeds only — never change certify rules.  
5. Expose ATIE/AIE/AME/LXP metadata through existing SIF adapters.

## What not to do

- Do not call LLMs for factual curriculum content  
- Do not mutate `EngineResult` payloads  
- Do not fork SICS copies inside packs  
