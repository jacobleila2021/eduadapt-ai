# CIP Integration Guide

## Registration

```python
import engines.chemistry_intelligence  # auto-registers over chemistry placeholder
```

Also ensured by SIF `_ensure_production_packs`.

## Pipeline

ULI enrich → SIF detect `chemistry` → CIP `analyse_lesson` → `_meta.uli.subject_intelligence` → ULIQE may append `ULIQE.CHEM.CIP.*`.

## Constraints

- Atom-count validated balancer outputs remain Computation Layer truth (`engines/chemistry`)  
- CIP never invents equations or lab procedures  
- Do not change ULIQE certify thresholds when extending CIP signals  
- Curriculum boards (NCERT/CBSE/ICSE/Cambridge/IB/…) map via UCF — CIP stays curriculum-agnostic  
