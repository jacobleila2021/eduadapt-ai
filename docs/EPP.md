# Educational Product Perfection (EPP)

**Smoke:** `ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK`  
**Phase:** Omega Ultimate  
**Not an intelligence engine** — final learner-visible polish over permanently frozen architecture.

## Mission

Every change must improve educational quality, writing, engagement, adaptations, visuals, accessibility, rendering, UX, performance, or reliability. If it does not improve the learner experience, it must not ship.

## Golden rule

Every intelligence contribution must visibly improve the lesson (explanations, examples, activities, questioning, visuals, assessments, accessibility, engagement).  
**Metadata that never reaches the learner is a defect.**

## Pipeline

```
… → PMES → PEEC → EPP (surface + polish) → UEVB → Production
```

EPP does **not** replace UEVB/PMES/PEEC gates. It perfects what the learner reads.

## What EPP does

1. **Surface** board examples, misconceptions, claims, vocabulary, visuals, and goals into learner pages when missing  
2. **Persona intent** — ADHD / autism / ELL / visual / auditory / LD / dyslexia / teacher / parent pages get intentional structure  
3. **Writing polish** — scrub scaffold/robotic language; master-teacher pass; cream style tokens  
4. **Vocabulary** — retention tips use “Draw this” language, not “Picture / Memory tip” scaffold leaks  

## CLI

```bash
python -m epp
```

## Stop condition

Lessons that would confidently stand beside Pearson, Oxford, Cambridge, National Geographic Learning, or Scholastic.  
Future work = maintenance, feature requests, and user-driven educational improvements only.

## Regression rule

No future commit may reduce lesson quality, adaptation quality, publisher quality, accessibility, visual quality, or performance.
