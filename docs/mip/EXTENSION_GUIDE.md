# MIP Extension Guide (template for future Subject Packs)

MIP is the **reference implementation** for Physics, Chemistry, Biology, English, and other Subject Intelligence Packs.

## Checklist for a new pack

1. Create `engines/<subject>_intelligence/` mirroring MIP modules.  
2. Subclass `SubjectIntelligencePack`; set `placeholder=False` in analysis.  
3. Implement `capabilities()` + `analyse_lesson()`.  
4. Keep Knowledge / Computation / Teaching separation.  
5. Register via `get_registry().register(pack, overwrite=True)` and ensure from SIF registry `_ensure_production_packs`.  
6. Add additive ULIQE subject findings **without** changing certification rules.  
7. Document architecture, teaching strategies, misconception catalogue, API, integration.  
8. Smoke constant: `<SUBJECT>_INTELLIGENCE_SMOKE_OK`.  
9. Tests: unit, misconceptions, accessibility metadata, SIF integration, regression.  

## Recommended order after Mathematics

1. Physics  
2. Chemistry  
3. Biology  
4. English Language  
5. Social Science  
6. Computer Science  
7. Commerce & Economics  
8. World Languages  

## What to reuse from MIP

- Domain marker + prerequisite graph pattern  
- Misconception library shape  
- Worked-example scaffold schema (exam-safe)  
- Pedagogy helpers for ATIE / AIE / AME / LXP  
- Additive ULIQE `findings_seed` pattern  

## What not to copy

- Mathematics-specific visual catalogue without review  
- Direct SymPy calls for non-math subjects  
- Any LLM factual generation for verified curriculum  
