# MIP API Documentation

## Import

```python
from engines.mathematics_intelligence import (
    MATHEMATICS_INTELLIGENCE_SMOKE_OK,
    analyse_mathematics_lesson,
    math_quality_signals,
    pack_health,
    get_mathematics_pack,
    MathematicsIntelligencePack,
    MathematicsIntelligenceEngine,
)
```

## Smoke

```python
assert MATHEMATICS_INTELLIGENCE_SMOKE_OK is True
```

## Analyse a lesson (preferred)

```python
from engines.universal_lesson_intelligence import build_universal_lesson_intelligence

uli = build_universal_lesson_intelligence(envelope, profile, enrich=True)
result = analyse_mathematics_lesson(uli, context={"exam_mode": False})
payload = result.to_dict()
```

### `SubjectAnalysisResult` fields (MIP)

- `concept_graph` — ULI concepts + domain nodes + prerequisite edges  
- `misconceptions` — detected patterns  
- `visuals` / `interactions` / `lxp_hints`  
- `assessment_hints` / `revision_summary`  
- `accessibility_guidance` / `teaching_strategies` / `tutor_guidance`  
- `metadata.worked_examples`, `metadata.symbolic`, `metadata.domains`  
- `placeholder` — always `False` for MIP  

## SIF enrichment (production path)

```python
from engines.subject_intelligence_framework import enrich_uli_with_subject_intelligence

sif = enrich_uli_with_subject_intelligence(uli)
# sif["analysis"], sif["atie"], sif["aie"], sif["ame"], sif["lxp"]
```

## Quality signals (ULIQE)

```python
signals = math_quality_signals(uli)
# signals["findings_seed"] → ULIQE.MATH.MIP.* INFO/WARNING seeds
```

## Optional engine

```python
from engines.mathematics_intelligence import MathematicsIntelligenceEngine

bundle = MathematicsIntelligenceEngine().process({"universal_lesson_intelligence": uli})
```

Not auto-registered in VLIE.
