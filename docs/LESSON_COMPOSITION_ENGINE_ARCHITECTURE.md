# Lesson Composition Architecture (LCE 1.0)

## Role

The Lesson Composition Engine is the **final educational author** before ULIQE / rendering.
It composes premium lessons from verified ULI · SIF · UVIE · Subject Pack knowledge.
It does **not** invent curriculum or alter EngineResult payloads.

## Pipeline

```
Uploaded Lesson → Knowledge Extraction → ULI → SIF / Subject Packs → UVIE
  → Assessment / Accessibility → Lesson Composition Engine → ULIQE → Rendering
```

## Public API

```python
from engines.lesson_composition_engine import (
    LESSON_COMPOSITION_ENGINE_SMOKE_OK,
    compose_lesson_package,
    attach_lce_to_adaptations,
    pack_health,
)

assert LESSON_COMPOSITION_ENGINE_SMOKE_OK
assert pack_health()["ok"]
package = compose_lesson_package(lesson_text=..., universal_profile=..., meta=...)
adaptations = attach_lce_to_adaptations(adaptations, lesson_text=...)
print("LESSON_COMPOSITION_ENGINE_SMOKE_OK")
```

## Key modules

| Concern | Module |
|---------|--------|
| Engine facade | `engine.py` |
| Composition | `composer.py` |
| Adaptive lenses | `adaptive_writing.py` |
| Vocabulary cards | `vocabulary.py` |
| Concept teaching | `concept_teaching.py` |
| Diagrams / maps | `diagrams.py` |
| Visual placement | `visual_placement.py` |
| Quality gate | `quality_gate.py` |
| Subject arcs | `subject_adapters.py`, `schemas.SUBJECT_TEACHING_SEQUENCES` |

## Adaptive versions

standard, vocabulary, ld, ell, visual, auditory, teacher, parent, worksheet, adhd, autism, dyslexia

## Quality

Ten publication categories in `QUALITY_CATEGORIES`. Failed gates can block rendering via `gate_for_rendering`.

## Non-goals

Does not replace VLIE, ULI, ULIQE, SIF, SICS, UVIE, UCF, CIE, AME, ALE, ATIE, VMLE, LAIE, ALCIS, LXP, or Subject Packs.
