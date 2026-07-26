# Biology Intelligence Architecture

**Pack:** Biology Intelligence Pack (BIP)  
**Version:** 1.0.0  
**Framework:** Subject Intelligence Framework (SIF) Phase 4  
**Smoke:** `BIOLOGY_INTELLIGENCE_SMOKE_OK`

## Role

BIP is the authoritative **biology / life sciences teaching layer** for Alora AI. It enriches verified lessons with living systems, anatomical diagrams, physiological processes, genetics, ecology, taxonomy, and laboratory metadata — without inventing curriculum.

## STEM quartet (complete)

Mathematics (MIP) → Physics (PIP) → Chemistry (CIP) → **Biology (BIP)**

BIP reuses MIP/PIP/CIP patterns: domain graphs, misconception libraries, exam-safe worked examples, ATIE/AIE/AME/LXP adapters, additive ULIQE `findings_seed`.

## Package

```
engines/biology_intelligence/
  pack.py, service.py, engine.py
  domains.py, misconceptions.py, processes.py
  diagrams.py, laboratory.py, terminology.py
  worked_examples.py, pedagogy.py, validators.py
  cell_biology.py … taxonomy.py (domain facets)
```

## Guarantees

- Never invent biology facts, diagrams, or lab procedures  
- Never mutate `EngineResult` / curriculum  
- Never change ULIQE certification thresholds (`ULIQE.BIO.BIP.*` additive INFO/WARNING)  
- Curriculum-agnostic; boards map via UCF  

## Downstream

| Consumer | Fields |
|----------|--------|
| ATIE | tutor_guidance (inquiry, structure–function) |
| AIE | accessibility_guidance (diagram descriptions, TTS) |
| AME | assessment_hints (practical biology skills) |
| LXP/VMLE | anatomy viewers, life cycles, food webs, labs |
| LAIE/LMAS | revision_summary |
