# Chemistry Intelligence Architecture

**Pack:** Chemistry Intelligence Pack (CIP)  
**Version:** 1.0.0  
**Framework:** Subject Intelligence Framework (SIF) Phase 3  
**Smoke:** `CHEMISTRY_INTELLIGENCE_SMOKE_OK`

## Role

CIP is the authoritative **chemistry teaching layer** for Alora AI. It enriches verified lessons with molecular, equation, laboratory, and misconception metadata — without inventing curriculum or replacing Computation Layer balancers (ChemPy / atom-count validation / RDKit).

## STEM family

Mathematics (MIP) → Physics (PIP) → **Chemistry (CIP)** → Biology (next)

CIP reuses MIP/PIP patterns: domain graphs, misconception libraries, exam-safe worked examples, ATIE/AIE/AME/LXP adapters, additive ULIQE `findings_seed`.

## Package

```
engines/chemistry_intelligence/
  pack.py, service.py, engine.py
  domains.py, misconceptions.py, equations.py
  molecular_models.py, laboratory.py, diagrams.py
  worked_examples.py, pedagogy.py, validators.py
  atomic_structure.py … equilibrium.py (domain facets)
```

## Guarantees

- Never invent balanced equations beyond verified STEM artifacts  
- Never mutate `EngineResult` / curriculum  
- Never change ULIQE certification thresholds (`ULIQE.CHEM.CIP.*` are additive INFO/WARNING)  
- Curriculum-agnostic; boards map via UCF  

## Downstream

| Consumer | Fields |
|----------|--------|
| ATIE | tutor_guidance (mole scaffolding, reaction reasoning) |
| AIE | accessibility_guidance |
| AME | assessment_hints (lab skills + scientific practices) |
| LXP/VMLE | visuals, molecular hooks, lab simulations |
| LAIE/LMAS | revision_summary |
