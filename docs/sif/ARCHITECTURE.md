# Subject Intelligence Framework (SIF) — Architecture

**Package:** `engines.subject_intelligence_framework`  
**Smoke:** `SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK`

## Purpose

SIF is **not** a subject engine. It is the plug-in framework that lets Mathematics,
Physics, Chemistry, Biology, English, Social Science, and future packs attach to
the ULI pipeline without changing prompts, VLIE orchestration, or curriculum truth.

## Flow (when `ENABLE_ULI_PIPELINE=true`)

```
Lesson → ULI → Semantic Enrichment → SIF (detect + pack.analyse_lesson)
       → ULIQE → Adaptations → LessonBundle (+ subject_intelligence)
```

When the flag is off, SIF is not invoked from generation (same as today).

## Packages

| Module | Role |
|--------|------|
| `interfaces.py` | `SubjectIntelligencePack` + `PlaceholderSubjectPack` |
| `registry.py` | Register / resolve packs |
| `subject_profile.py` | Detect subject from ULI metadata / STEM kinds |
| `capability_matrix.py` | Declared capabilities + LXP hook catalogue |
| `semantic_hooks.py` | Run pack against ULI |
| `adapters.py` | ATIE / LXP / AME / AIE hint DTOs |
| `validators.py` | Interface compliance |
| `service.py` | Public API |
| `engine.py` | Optional VLIE wrapper (not auto-registered) |

## Rules

1. Packs must not invent verified curriculum or STEM results.  
2. Placeholders return empty structured payloads + warnings.  
3. Adding a subject = implement interface + `registry.register(pack)`.  
4. Curriculum boards (NCERT/CBSE/IB/…) stay in UCF/CIE — SIF is subject pedagogy.

## Next packs (out of scope here)

Mathematics → Physics → Chemistry → Biology → English → Social Science → …
