# CIP API Documentation

```python
from engines.chemistry_intelligence import (
    CHEMISTRY_INTELLIGENCE_SMOKE_OK,
    analyse_chemistry_lesson,
    chemistry_quality_signals,
    pack_health,
    ChemistryIntelligencePack,
    ChemistryIntelligenceEngine,
)

assert CHEMISTRY_INTELLIGENCE_SMOKE_OK is True
result = analyse_chemistry_lesson(uli, context={"exam_mode": False})
signals = chemistry_quality_signals(uli)  # ULIQE.CHEM.CIP.* seeds
```

## SIF path

```python
from engines.subject_intelligence_framework import enrich_uli_with_subject_intelligence
sif = enrich_uli_with_subject_intelligence(uli)  # subject_key == "chemistry"
```

Metadata includes `equations`, `molecular`, `laboratory`, `worked_examples`.
