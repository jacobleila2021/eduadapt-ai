# Mathematics Intelligence Architecture

**Pack:** Mathematics Intelligence Pack (MIP)  
**Version:** 1.0.0  
**Framework:** Subject Intelligence Framework (SIF)  
**Smoke:** `MATHEMATICS_INTELLIGENCE_SMOKE_OK`

## Role

MIP is the authoritative **mathematics teaching layer** for Alora AI. It understands how mathematics should be taught — concept graphs, misconceptions, CRA representations, worked-example scaffolds, tutor/assessment/accessibility metadata — while preserving verified curriculum integrity.

MIP does **not**:

- Invent curriculum beyond the verified lesson / ULI
- Replace SymPy / `engines.mathematics` / Subject Tool Router
- Generate protected exam answers
- Mutate `EngineResult` payloads
- Change ULIQE certification thresholds

## Three-layer placement

| Layer | Owner | MIP role |
|-------|--------|----------|
| Knowledge | NCERT/CIE/RAG | Read concepts/objectives from ULI |
| Computation | SymPy, safe_math, STEM pipeline | Inspect existing artifacts for symbol consistency |
| Teaching | MIP + ATIE + LXP | Pedagogy metadata and tutoring guidance |

## Package layout

```
engines/mathematics_intelligence/
  pack.py              # SubjectIntelligencePack implementation
  service.py           # Public API + registration
  engine.py            # Optional VLIE-compatible wrapper (not auto-registered)
  domains.py           # Domain markers + prerequisite edges
  algebra.py …         # Domain facets
  misconceptions.py    # Pattern library
  worked_examples.py   # Scaffold structure (exam-safe)
  symbolic.py          # Consistency over STEM outputs
  visualizations.py    # Visual type recommendations
  representations.py   # CRA / multi-rep plans
  pedagogy.py          # Teaching / AME / AIE / ATIE / LXP helpers
  assessment.py
  revision.py
  accessibility.py
  validators.py        # Additive ULIQE quality signals
```

## Runtime path

1. ULI pipeline (`ENABLE_ULI_PIPELINE`) builds/enriches ULI
2. SIF `enrich_uli_with_subject_intelligence` detects subject
3. Registry returns `MathematicsIntelligencePack` for `mathematics`
4. Analysis attached as `_meta.uli.subject_intelligence`
5. ULIQE `validate_mathematics` may emit additive `ULIQE.MATH.MIP.*` INFO/WARNING findings

## Downstream consumers

| Consumer | Payload fields |
|----------|----------------|
| ATIE | `tutor_guidance`, misconceptions |
| AIE | `accessibility_guidance` |
| AME | `assessment_hints`, `revision_summary` |
| LXP / VMLE | `lxp_hints`, `visuals`, interactions |
| LAIE / LMAS | revision spaced intervals, misconception ids |
| ULIQE | `collect_math_quality_signals` → findings seeds |

## Roadmap (subsequent packs)

Mathematics → Physics → Chemistry → Biology → English → Social Science → Computer Science → Commerce/Economics → World Languages
