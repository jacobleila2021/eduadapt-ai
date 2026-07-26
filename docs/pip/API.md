# PIP API Documentation

```python
from engines.physics_intelligence import (
    PHYSICS_INTELLIGENCE_SMOKE_OK,
    analyse_physics_lesson,
    physics_quality_signals,
    pack_health,
    get_physics_pack,
    PhysicsIntelligencePack,
    PhysicsIntelligenceEngine,
)

assert PHYSICS_INTELLIGENCE_SMOKE_OK is True
```

## Analyse

```python
result = analyse_physics_lesson(uli, context={"exam_mode": False})
payload = result.to_dict()
# metadata.experiments, metadata.units_formulas, metadata.worked_examples
```

## SIF path

```python
from engines.subject_intelligence_framework import enrich_uli_with_subject_intelligence
sif = enrich_uli_with_subject_intelligence(uli)  # subject_key == "physics"
```

## Quality signals

```python
signals = physics_quality_signals(uli)
# findings_seed → ULIQE.PHYS.PIP.*
```
