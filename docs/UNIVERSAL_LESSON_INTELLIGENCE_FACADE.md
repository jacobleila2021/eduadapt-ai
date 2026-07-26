# Universal Lesson Intelligence (ULI) Facade — Milestones 2.1 & 2.2

**Status:** 2.1 Facade + 2.2 Semantic Enrichment  
**Schema:** `3.2.0-semantic`  
**Package:** `engines.universal_lesson_intelligence`

## Purpose

Single educational contract for future Alora engines. Read-only. Curriculum-agnostic.

## Factories

| Factory | Behaviour |
|---------|-----------|
| `build_universal_lesson_intelligence(..., enrich=False)` | 2.1 wrap only |
| `build_enriched_universal_lesson_intelligence(...)` | 2.2 attach STEM/CIE/AME/AIE/LXP |
| `uli.ensure_enriched()` | Lazy upgrade from 2.1 instance |

## Semantic accessors

`educational_structure` · `learning_structure` · `stem_structure` · `diagram_structure` ·
`learning_resources` · `assessment_structure` · `accessibility_structure` ·
`tutor_structure` · `voice_structure` · `companion_structure` · `lxp_structure` ·
`analytics_structure` · `knowledge_graph_structure` · `semantic_bundle` ·
`enriched_profile_view`

See `docs/uli/MILESTONE_2_2_SEMANTIC_ENRICHMENT.md` for data flow and integration notes.

## Consumer rule

Future engines **must** import from `engines.universal_lesson_intelligence`.
Live generation (`ai_generator`, VLIE) may keep current imports until a wiring milestone.

## Out of scope

Prompt integration (2.3), Subject Intelligence packs, ULIQE scoring changes, VLIE auto-gate.
