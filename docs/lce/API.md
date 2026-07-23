# LCE API Documentation

## Python API

| Symbol | Purpose |
|--------|---------|
| `compose_lesson_package(uli, sif=, uvie=, topic_hint=)` | Full compose → `{ok, clg, adaptations, eerl, version}` |
| `attach_lce_to_adaptations(adaptations, lesson_text=)` | Final polish / premium vocab |
| `build_canonical_lesson_graph(...)` | CLG only |
| `review_package(adaptations, clg)` | EERL gate |
| `api_compose_lesson(context)` | Service facade |
| `api_compose_vocabulary(terms, topic=)` | Vocabulary page |
| `api_evaluate_quality(lesson, **kw)` | Quality gate |
| `api_narrative_contract(subject, version_id)` | Prompt contracts |
| `pack_health()` | Health + smoke flag |
| `LESSON_COMPOSITION_ENGINE_SMOKE_OK` | Smoke constant |

## VLIE engine

```python
from engines.lesson_composition_engine import LessonCompositionEngine
eng = LessonCompositionEngine()
result = eng.process({"uli": uli, "sif": sif, "uvie": uvie, "topic": "..."})
```

## Response shape

```json
{
  "ok": true,
  "version": "1.0.0",
  "clg": {"topic": "...", "core_concepts": [], "vocabulary": [], "facts": []},
  "adaptations": {
    "standard": {"big_idea": "...", "sections": [], "svg_diagram": "<svg...>"},
    "vocabulary": {"word_wall": [], "lce": {"premium_cards": true}},
    "worksheet": {"short_answer": [], "long_answer": []},
    "adhd": {}, "autism": {}, "dyslexia": {}, "ell": {}, "visual": {}, "auditory": {},
    "teacher": {}, "parent": {}, "ld": {}
  },
  "eerl": {"production_ready": true, "worst_score": 1.0, "by_adaptation": {}}
}
```
