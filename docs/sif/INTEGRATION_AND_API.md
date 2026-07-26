# SIF Integration & API Guide

## API

```python
from engines.subject_intelligence_framework import (
    SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK,
    list_subject_packs,
    enrich_uli_with_subject_intelligence,
    detect_subject_from_uli,
    capability_matrix,
    lxp_hook_catalogue,
    validate_registry,
    get_registry,
)

packs = list_subject_packs()
payload = enrich_uli_with_subject_intelligence(uli)  # detection + placeholder analysis
assert SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK
```

## ULI 2.3 integration

When `ENABLE_ULI_PIPELINE=true`, `build_uli_context` attaches:

`_meta.uli.subject_intelligence` → detection, analysis, ATIE/LXP/AME/AIE adapters.

`LessonBundle.subject_intelligence` mirrors the same payload.

## LXP hooks (descriptions only)

`interactive_diagrams`, `formula_viewers`, `concept_maps`, `simulations`,
`subject_toolbars`, `revision_widgets` — see `lxp_hook_catalogue()`.

## Extension

Register real packs via `get_registry().register(pack, overwrite=True)` without
changing ULI, ULIQE, or prompts.
