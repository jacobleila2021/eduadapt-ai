# Phase Final — Content Fidelity & Publishing Recovery

**Smoke:** `CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK`  
**Not a new engine** — repairs learner-facing content using existing LCE / PMES / PEEC / EPP polish paths.

## Permanent publishing standard

If the learner cannot see it, it does not exist.

## Repairs included

1. **Prompt leak elimination** — scrub authoring/metadata phrases from learner text; publication fails if residuals remain  
2. **Master-teacher flow** — curiosity → explain → illustrate → real life → diagram → practice → reflection → summary  
3. **Student vocabulary cards** — WORD, Meaning, Real-life example, Picture idea, Remember this, Use this word (no dictionary apparatus)  
4. **True adaptations** — clone paragraphs across learner versions fail fidelity  
5. **Assessment scrub** — questions/answers cannot carry metadata  
6. **Lesson-specific summaries** — generic template summaries rewritten from this lesson’s claims  
7. **Neural voice default** — no silent browser TTS downgrade; show “High-quality narration is temporarily unavailable.”  
8. **Teaching diagrams** — diagram referenced in paragraphs and practice  

## Pipeline

```
… → PMES → PEEC → EPP → Content Fidelity → Publication
```
