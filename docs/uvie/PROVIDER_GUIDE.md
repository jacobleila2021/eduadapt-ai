# UVIE Provider Guide

| Provider | Module | Notes |
|----------|--------|-------|
| Knowledge | `providers/knowledge.py` | NCERT / curated paths, UCF diagram resolve |
| Computation | `providers/computation.py` | Reuses router artifacts / TaskKinds |
| Pedagogy | `providers/pedagogy.py` | Flowchart, concept map, study SVG from lesson text |
| Timeline | `providers/timeline.py` | Scaffold from dated lesson text only |
| Geography | `providers/geography.py` | Place labels from lesson; no invented borders |

Add providers by implementing `provide_*_visuals(intents, **ctx) -> list[VisualSpec]` and registering in `registry.run_providers`.
