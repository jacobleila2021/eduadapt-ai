# PIP Integration Guide

## Registration

Auto-registers on import / SIF `_ensure_production_packs`:

```python
import engines.physics_intelligence
```

## ULI pipeline

With `ENABLE_ULI_PIPELINE` + enrichment: detect physics → PIP analysis → `_meta.uli.subject_intelligence` → ULIQE may append `ULIQE.PHYS.PIP.*`.

## Consumers

| System | Consume |
|--------|---------|
| ATIE | `sif["atie"]["tutor_guidance"]` |
| AIE | `sif["aie"]["accessibility_guidance"]` |
| AME | `sif["ame"]["assessment_hints"]` |
| LXP | visuals / experiment hooks — render only |
| VMLE | diagram descriptions, TTS units |

## Constraints

- Do not invent physics beyond verified ULI  
- Do not bypass Subject Tool Router for STEM computation  
- Do not change ULIQE certify thresholds when extending PIP signals  
