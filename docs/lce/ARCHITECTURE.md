# Lesson Composition Engine (LCE) 1.0 — Architecture

**Product:** Alora AI  
**Status:** Production composition layer  
**Smoke:** `LESSON_COMPOSITION_ENGINE_SMOKE_OK`  
**Principle:** Compose verified knowledge. Never invent curriculum.

---

## 1. Why LCE exists

Alora already has world-class intelligence (VLIE, ULI, SIF, UVIE, Subject Packs, AIE, AME, ALE…).  
It lacked a **final educational author** that turns fragmented intelligence into premium classroom lessons.

LCE is that author. It **composes**. It does not invent.

---

## 2. Pipeline position

```
Uploaded Lesson
  → Knowledge Extraction / KIE
  → ULI
  → SIF + Subject Packs
  → UVIE
  → Assessment / Accessibility
  → Lesson Composition Engine (NEW)
  → ULIQE / EERL
  → Rendering Engine / LXP
```

---

## 3. Internal architecture

```
ULI + SIF + UVIE
        ↓
Canonical Lesson Graph (CLG)     — single educational truth
        ↓
Adaptive Lenses                  — pedagogically distinct versions
        ↓
Premium Vocabulary + SVG diagrams
        ↓
Educational Editorial Review (EERL) + Quality Gate
        ↓
Adaptations package for rendering
```

Optional LLM role: **Educational Editor only** (`LCE_LLM_POLISH=true`).  
Default path is deterministic composition from the CLG.

---

## 4. Package layout

```
engines/lesson_composition_engine/
  clg.py                 Canonical Lesson Graph builder
  lenses.py              Adaptive writing lenses
  editor.py              Optional LLM editor contracts
  eerl.py                Educational Editorial Review Layer
  composer.py            Orchestrator / public compose API
  vocabulary.py          Premium flashcards
  diagrams.py            Publication SVG flowcharts & concept maps
  concept_teaching.py    Eight-step concept sequence
  visual_placement.py    UVIE placement rules
  subject_adapters.py    MIP/PIP/CIP/BIP/… flow reuse
  adaptive_writing.py    Distinct adaptive rewrites
  teaching_rules.py      Paragraph / flow rules
  contracts.py           Narrative contracts
  quality_gate.py        Publication scoring
  schemas.py             Contracts & dataclasses
  engine.py              VLIE BaseEngine facade
  service.py             REST-shaped API + smoke constant
docs/lce/                Architecture + guides
tests/test_lce.py        Composition / flow / vocab / smoke
```

---

## 5. What LCE reuses (never duplicates)

| Engine | LCE use |
|--------|---------|
| ULI | Topic, claims, concepts, accessibility structure |
| SIF + Subject Packs | Subject pedagogy, misconceptions, assessment hints |
| UVIE | Verified visuals only — placement, never invention |
| AIE | Accessibility presentation intent |
| MIP/PIP/CIP/BIP/ELIP/SSIP/CSIP/CEIP/WLIP | Subject teaching arcs |
| VLIE | Registers `lesson_composition` in workflow |
| ULIQE / QA | Downstream certification / hard publish |

---

## 6. Adaptive versions authored

Standard · Vocabulary Support · Mainstream (`standard`) · Neurodiversity (`ld`) · ELL · Visual · Auditory · Teacher · Parent · Exam Worksheet · ADHD · Autism · Dyslexia

Each version is rewritten under a lens contract — never a recolor of the same text.

---

## 7. Feature flags

| Flag | Default | Meaning |
|------|---------|---------|
| `ENABLE_LCE_PIPELINE` | `true` | Wire LCE into `generate_adaptations` |
| `LCE_LLM_POLISH` | `false` | Optional Educational Editor LLM |

---

## 8. Success criteria

- Lessons read like expert teachers / NCERT-quality publishers — not ChatGPT metadata.
- Adaptive versions are pedagogically distinct.
- Vocabulary cards, SVG flowcharts, and concept maps meet publication standards.
- Existing engines remain unchanged; LCE orchestrates them.
- Smoke: `pytest tests/test_lce.py -k smoke -s` → `LESSON_COMPOSITION_ENGINE_SMOKE_OK`
