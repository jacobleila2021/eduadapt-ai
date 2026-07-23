# LCE Developer Documentation

## Quick start

```python
from engines.lesson_composition_engine import compose_lesson_package

pkg = compose_lesson_package(
    uli,                 # ULI object or dict with universal_profile + claim_ledger
    sif=sif_payload,     # enrich_uli_with_subject_intelligence(...)
    uvie=uvie_payload,   # render_visuals_for_uli(...)
    topic_hint="Force and Pressure",
)
adaptations = pkg["adaptations"]
clg = pkg["clg"]
eerl = pkg["eerl"]
```

## VLIE registration

`LessonCompositionEngine` is registered in `engines/verified_learning_engine/engine_manager.py`  
with `depends_on=["accessibility", "assessment", "adaptive_learning"]`.  
Workflow stage: `lesson_composition` (before `ai_tutor` / LXP packaging).

## Generation hook

`ai_generator.generate_adaptations`:

1. Builds ULI + SIF + UVIE  
2. Calls `compose_lesson_package` (primary educational author)  
3. Prefers LCE adaptations; LLM fills gaps only  
4. Merges ADHD/Autism/Dyslexia LCE versions  
5. `attach_lce_to_adaptations` upgrades premium vocabulary  

## Do not

- Invent curriculum or STEM answers  
- Bypass `engines/router.py` for equations/graphs  
- Emit Mermaid unless explicitly requested  
- Recolor one lesson into “adaptive” clones  
