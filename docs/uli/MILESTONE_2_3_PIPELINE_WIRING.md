# ULI Milestone 2.3 — Prompt & Pipeline Wiring

## Architecture

```
Upload / envelope + profile
        ↓
process_lesson_stem (unchanged)
        ↓
[ENABLE_ULI_PIPELINE?]
   no → existing adaptation generation (identical)
   yes → build ULI → enrich → ULIQE (non-blocking) → attach _meta.uli
        ↓
Existing LLM adaptations / prompts (unchanged)
        ↓
[flag on] finalize LessonBundle → _meta.lesson_bundle
        ↓
VLIE package mirrors uli / lesson_bundle when present
        ↓
Exports / LXP / UI (unchanged contracts)
```

## Feature flag

| Env | Default | Effect |
|-----|---------|--------|
| `ENABLE_ULI_PIPELINE` | `false` | Off = current behaviour |

Values treated as on: `1`, `true`, `yes`, `on` (case-insensitive).

## LessonBundle

See `engines/universal_lesson_intelligence/bundle.py`:

`raw_lesson`, `universal_lesson`, `semantic_bundle`, `validation_report`,
`certification`, `quality_score`, `warnings`, `recommendations`,
`adaptation_payloads`, `export_payloads`, …

## Integration map

| Component | Change |
|-----------|--------|
| `config.py` | `ENABLE_ULI_PIPELINE` |
| `ai_generator.generate_adaptations` | Flag-gated attach + finalize |
| `ai_generator.quality_report` | Additive `uli_*` fields |
| VLIE orchestrator | Propagates bundle onto package if present |
| Prompts / STEM / QA gates | **Unchanged** |

## Sequence

1. STEM + profile (as today)  
2. If flag: `attach_uli_pipeline` (reuse stem metadata — no second STEM run for pipeline)  
3. LLM adaptations (identical prompts)  
4. Publish QA (unchanged)  
5. If flag: `finalize_lesson_bundle`  

ULIQE **never rejects** generation (`blocks_generation: false`).

## Smoke

`ULI_MILESTONE_2_3_SMOKE_OK is True`

## Out of scope

Subject packs · prompt rewrites · production gating as default · new UI/exports.
