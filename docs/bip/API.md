# BIP API Documentation

```python
from engines.biology_intelligence import (
    BIOLOGY_INTELLIGENCE_SMOKE_OK,
    analyse_biology_lesson,
    biology_quality_signals,
    pack_health,
    BiologyIntelligencePack,
    BiologyIntelligenceEngine,
)

assert BIOLOGY_INTELLIGENCE_SMOKE_OK is True
result = analyse_biology_lesson(uli, context={"exam_mode": False})
signals = biology_quality_signals(uli)  # ULIQE.BIO.BIP.* seeds
```

## SIF path

```python
from engines.subject_intelligence_framework import enrich_uli_with_subject_intelligence
sif = enrich_uli_with_subject_intelligence(uli)  # subject_key == "biology"
```

Metadata includes `processes`, `laboratory`, `terminology`, `worked_examples`.
