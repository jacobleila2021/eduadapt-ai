# ULI Milestone 2.2 — Semantic Enrichment & STEM Integration

## Architecture

Milestone 2.2 attaches **verified** outputs from existing Alora pipelines onto the
read-only ULI facade. Extraction logic is **not** duplicated.

```
SourceDocumentEnvelope + UniversalLessonProfile
        │
        ▼
collect_semantic_enrichment()   [enrichment.py]
        │
        ├── content_classifier.classify_source_blocks
        ├── lesson_pipeline.process_lesson_stem
        ├── CIE analyze_lesson_context (optional scope)
        ├── AME detect_from_text
        ├── AIE readability_report
        └── LXP estimate_reading_minutes
        ▼
UniversalLessonIntelligence (enrich=True)
        │
        ├── educational_structure / learning_structure / stem_structure
        ├── diagram / assessment / accessibility / tutor / voice
        ├── companion / lxp / analytics / knowledge_graph
        └── semantic_bundle() (cached, immutable)
```

## API

```python
from engines.universal_lesson_intelligence import (
    build_universal_lesson_intelligence,          # enrich=False default (2.1)
    build_enriched_universal_lesson_intelligence, # enrich=True (2.2)
    ULI_MILESTONE_2_2_SMOKE_OK,
)

uli = build_enriched_universal_lesson_intelligence(envelope, profile)
uli.stem_structure()
uli.knowledge_graph_structure()
uli.semantic_bundle()  # cached
uli.ensure_enriched()  # from a 2.1 instance
```

Accessors return frozen (`MappingProxyType` / tuples) snapshots.

## Knowledge graph

Does **not** rebuild CIE ontology. Emits lesson/concept nodes and prerequisite
edges **referenced** from CIE `analyze_lesson_context` when scope matches.

## STEM

STEM claims/artifacts come only from `process_lesson_stem` / claim extractor /
router. Unsupported STEM is never inferred.

## Accessibility / Assessment / Voice / Analytics

- AIE readability attached when available.
- AME misconception hits attached when patterns match.
- Voice/LXP/analytics expose **anchors** from the claim ledger (ids + text), not
  generated narration or personality.

## ULIQE

Enriched ULI objects are valid ULIQE inputs. **Scoring rules unchanged** — richer
STEM/accessibility fields simply feed existing validators.

## Out of scope

2.3 prompt wiring · Subject packs · VLIE auto-registration · ULIQE score changes ·
automatic downstream gating · LLM prompts.

## Sequence

1. Ingest → profile (unchanged)  
2. `build_enriched_universal_lesson_intelligence`  
3. Optional `validate_uli(uli)`  
4. Downstream engines consume accessors (future)

## Developer guide

- Prefer `build_enriched_*` for new engines.  
- Keep `enrich=False` for unit tests that must not run STEM.  
- Never mutate accessor returns.  
- Smoke: `ULI_MILESTONE_2_2_SMOKE_OK is True`.
