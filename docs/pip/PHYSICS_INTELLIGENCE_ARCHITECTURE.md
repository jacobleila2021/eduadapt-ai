# Physics Intelligence Architecture

**Pack:** Physics Intelligence Pack (PIP)  
**Version:** 1.0.0  
**Framework:** Subject Intelligence Framework (SIF) Phase 2  
**Smoke:** `PHYSICS_INTELLIGENCE_SMOKE_OK`

## Role

PIP is the authoritative **physics teaching layer** for Alora AI. It reasons about concepts, experiments, forces, motion, energy, waves, electricity, optics, and scientific modelling — while preserving verified curriculum integrity.

PIP does **not** invent physics, replace Computation Layer solvers/diagrams, mutate `EngineResult`s, or change ULIQE certification thresholds.

## Relationship to MIP

PIP reuses the Mathematics Intelligence Pack patterns:

- Domain markers + prerequisite graph
- Misconception library shape
- Worked-example scaffolds (exam-safe)
- Pedagogy helpers for ATIE / AIE / AME / LXP
- Additive ULIQE `findings_seed` (`ULIQE.PHYS.PIP.*`)

Physics-specific additions: experiment metadata, units/formula inspection, scientific teaching frameworks (POE, CER, inquiry).

## Package layout

```
engines/physics_intelligence/
  pack.py, service.py, engine.py
  domains.py, misconceptions.py, experiments.py
  units_formulas.py, visualizations.py, diagrams.py
  worked_examples.py, pedagogy.py, validators.py
  mechanics.py … measurements.py (domain facets)
```

## Runtime path

ULI → SIF detect `physics` → PIP `analyse_lesson` → `_meta.uli.subject_intelligence` → ULIQE physics stage may append PIP findings.

## Downstream

| Consumer | Fields |
|----------|--------|
| ATIE | tutor_guidance, experimental_reasoning, misconceptions |
| AIE | accessibility_guidance |
| AME | assessment_hints (incl. scientific practices) |
| LXP/VMLE | visuals, experiment hooks, simulations |
| LAIE/LMAS | revision_summary |

## Next

Chemistry Intelligence Pack → Biology Intelligence Pack
