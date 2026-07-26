# Alora AI — Complete System Audit & Intelligence Validation

**Date:** 23 July 2026  
**Mode:** Independent audit only (no code changes, no new engines, no lesson rewrites)  
**Interactive summary:** [alora-complete-system-audit.canvas.tsx](../../.cursor/projects/c-Users-SPECTRE-Desktop-EduAdapt-ai/canvases/alora-complete-system-audit.canvas.tsx) (open beside chat in Cursor)

---

## Executive Summary

Alora’s architectural expansion is real and large (~50 packages under `engines/`). **Most of that expansion does not improve the student-facing lesson.**

Student HTML is authored by a thin spine:

**Upload → KIE → VLIE orchestrator → `ai_generator` (STEM + LCE + structural gates) → renderer**

Meanwhile, VLIE pre/post “intelligence” engines (AME, AIE, ATIE, VMLE, ALE, LAIE, LMAS, UCF package, LXP, …) typically run, then store **only `summary_keys`** in `_meta.vlie_engine_outputs`. Their rich payloads are **not inputs to LCE or `structured_renderers`**.

**Why lessons feel worse after upgrades**

1. **LCE templates** assemble “X is a core idea…” / empty worked examples instead of claim-grounded teaching narrative.
2. **EATS/PQLE** reward section count, SVG presence, and adaptation keyword hits — a Force & Pressure lesson scored **EATS 95.7** while human teachability is ~**38**.
3. **Source learning objectives** (“Students will…”) polluted student vocab/matching (observed in production Water Cycle).
4. **Adaptations** mostly clone mainstream and wrap scaffolds — not instructional redesign.
5. Pre-upgrade **sample DOCX** was human prose; post-upgrade path optimizes for gate heuristics.

**Engines that genuinely help:** KIE, STEM router + computation packs, selective UVIE/visual injection, `engines.qa`.  
**LCE helps only if rewritten** from template assembler → educational author.  
**Most VLIE buses / ULI+SIF (default OFF) / LXP side platforms:** no measurable default-lesson ROI.

---

## 1. Architecture Diagram (live vs discarded)

```
Upload ──► KIE envelope ──► VLIE
                              ├── Profile (UCF-ish) ──► used (topic/concepts)
                              ├── Pre-engines (UCF/AME/AIE/ATIE/VMLE/…) ──► summary_keys ONLY ──► ✗ discarded for authoring
                              └── AloraOrchestrator ──► ai_generator
                                                         ├── STEM + UVIE (preferred_visuals) ──► ✓
                                                         ├── ULI+SIF+packs [ENABLE_ULI_PIPELINE=false] ──► ✗ default off
                                                         ├── LCE ──► PQLE/EERL ──► ✓ body (often templated)
                                                         ├── QA ──► ✓ gate
                                                         └── EATS ──► ✓ gate (miscalibrated)
                                                              ▼
                                                    publication_gate ──► Streamlit / HTML
```

Evidence: `app.py` → `VerifiedLearningOrchestrator.process_lesson` → `agents/orchestration.py` → `ai_generator.generate_adaptations`; discard pattern in `engines/verified_learning_engine/orchestrator.py` (`vlie_engine_outputs` = `ok` + `summary_keys`).

---

## 2. Pipeline Trace (one uploaded lesson)

| Stage | Input | Output | Educational contribution | Downstream consumes? | Waste |
|-------|-------|--------|--------------------------|----------------------|-------|
| Upload | File bytes | `source_envelope`, `lesson_text` | Source of truth | Yes | — |
| KIE | Bytes / envelope | Envelope + blocks | Trusted extract | Yes | Batch index not on Streamlit path |
| UCF profile | Text | Topic, concepts, objectives, claims | Grounding for prompts | Partial | Deep package unused |
| VLIE pre-engines | Context | Full payloads → **summary_keys** | Intended planning | **No** for LCE/renderer | High |
| ULI enrichment | ULI flag | Semantic bundle | Subject depth | Default **off** | Dormant |
| SIF + subject packs | ULI | `subject_intelligence` | Pedagogy packs | Default off; LCE looks for `sif` key | Wiring bug |
| STEM / router | Claims | Exact values + visuals | Correctness | Yes | Duplicate STEM run |
| UVIE | STEM | Visuals + metadata | Diagrams | `preferred_visuals` only | Metadata dropped |
| AME/AIE/ATIE/VMLE | VLIE | Assessment/a11y/tutor/voice plans | Side features | Not in gen body | High |
| LXP | Post | Layout/phases | Workspace | Toggle off by default | High on gen path |
| LCE | Profile + visuals | Adaptation HTML bodies | **Should** author | Yes | Template pollution |
| PQLE / EERL | LCE package | PQI ≥95 polish | Publisher polish | Meta + soft reject | Structural bias |
| EATS | Adaptations | Verdict ≥95 | Acceptance | Gate | Score ≠ teachability |
| Renderer | Adaptation dict | Streamlit/HTML | Learner surface | Yes | Ignores most `_meta` |

**Processing notes:** OpenAI timeout 90s; parallel LLM workers 4; EATS ≤3 revise attempts; STEM effectively twice (VLIE scientific accuracy + generator).

---

## 3. Engine Value Matrix (abbreviated)

| Classification | Engines |
|----------------|---------|
| **Essential** | KIE, STEM router + domain computation packs, answer_router, VLIE as thin orchestrator, `engines.qa`, multi-agent wrapper only as gen entry |
| **Essential* (needs rewrite)** | LCE (currently template author) |
| **Useful** | UVIE/viz priority, CIE/knowledge when curriculum hit, PQLE/EERL/EATS *after recalibration*, UCF thin profile |
| **Optional / side** | LXP, ATIE, VMLE, ALE, LAIE, LMAS, ALCIS, AME dashboards, CEF/CMIF |
| **Redundant** | Facade duplicates (`accessibility_engine`↔AIE, `assessment_engine`↔AME, gamification↔LMAS, scientific_accuracy facade, multi-agent static roster) |
| **No visible value (default path)** | ULI+ULIQE+SIF subject packs (flag off), VLIE AIE/AME/ATIE payloads for lesson tabs |

Full pair analysis: facade packages intentionally wrap `*_intelligence_engine`; educational waste is **payload non-consumption**, not accidental dual implementations.

---

## 4. Lesson Quality Audit — Corpus Honesty

### What exists (not 50 lessons)

| Asset | Count | Coverage |
|-------|-------|----------|
| Golden JSON stubs | 3 | Water Cycle, Force & Pressure, Fractions |
| Sample DOCX | 1 | Water cycle (human prose) |
| EATS runs | 10 | **All** “Force and Pressure” (physics) |
| Automated 50-lesson suite | **None** | Finding in itself |

**Part 3 requirement (50 lessons × subjects × boards × adaptations) was not executed** because this audit forbids modifying the system and no batch generator exists. Conclusions triangulate code + existing corpus + human review of rendered HTML (including production Water Cycle screenshots).

### Human scores — Force & Pressure EATS pass (`20260723T145916Z`)

| Dimension | EATS | Human (auditor) |
|-----------|------|-----------------|
| Overall / teachability | 95.7 | ~38 |
| Educational quality | 98.8 | ~35 |
| Visual / diagram | 96.8 / **100** | ~30 (generic Concept→Practice boxes; flowchart duplicated) |
| Pedagogy | 97.7 | ~40 |
| Accessibility differentiation | 99 | ~45 (tabs exist; shallow clones) |
| Publishing quality | “publisher_ready” | Fail — not textbook-publishable |

**Evidence quotes from `reports/screenshots/20260723T145916Z/standard.html`:**

- Big idea: *“Force and Pressure is worth mastering because it helps you explain Force, Pressure…”*
- Sections: *“Force is a core idea in this lesson.”* / *“Worked example: identify where force appears in the lesson evidence.”*
- Misconception: *“Force and pressure are the same Pressure depends on area.”*
- Diagram nodes: Concept, Phenomenon, Experiment, Diagram, Formula, Example, Practice

### Water Cycle (production observation)

Teacher objectives used as student definitions; matching/fill-blanks repeated “Students will identify…”; visual was box flowchart (pictorial hotfix later). Confirms **quality loss at composition + claim selection**, not missing engine count.

---

## 5. Adaptation Differentiation Audit

| Adaptation | Instructional difference | Semantic / a11y difference | Verdict |
|------------|--------------------------|----------------------------|---------|
| Mainstream | Template LCE | Baseline | Weak author |
| Vocabulary | Cards/practice | Higher if defs clean | Useful when hygienic |
| ELL / ADHD / Autism / Dyslexia(LD) | Clone + Say/Checkpoint/Look-first | Cosmetic load change | **Mostly cosmetic** |
| Visual / Auditory | Keyword wrappers | Cosmetic | Reject as redesign |
| Teacher | Same body + identical “Teacher note” on every section | Near-zero | **Cosmetic** |
| Parent / Worksheet | Prompts / Q list | Partial | Partial value |

Code: `engines/lesson_composition_engine/adaptive_writing.py` (`compose_adaptive_version` deep-copies standard; sets `pedagogically_distinct = True`). EATS personality = keyword hits in `eats/constants.py`, not redesign proof.

---

## 6. Visual Quality Audit

| Visual type | Publisher-ready? | Finding |
|-------------|------------------|---------|
| Subject-sequence flowchart | No | Generic pedagogy stages; still diagram_score 100 |
| Concept map hub | Weak | Thin nodes (Force/Pressure/Area) |
| Water cycle (pre-pictorial) | No | Boxes only |
| Vocab cards | Mixed | Good structure; content pollution risk |
| UVIE generative images | Off | `IMAGE_PROVIDER=off` |
| Duplicate SVG in one HTML | Fail | Force & Pressure pass export |

Prior doc: `docs/production-readiness/VISUAL_DIAGRAM_FLOWCHART_AUDIT.md` (64/100) — no visual goldens.

---

## 7. LCE Audit

**Behaves as:** metadata-driven template assembler with stock transitions.  
**Does not behave as:** exceptional classroom teacher.

Signals:

- Per-concept section explosion (core / understanding / everyday / worked / practice / reflect)
- Stock openers (“Today we study…”, “We begin with… so … feels clear”)
- Worked examples that do not work any example
- Adaptive clones rather than re-authored arcs
- `ENABLE_LCE_PIPELINE` in config is **not checked** at call sites (LCE always attempted when import succeeds)

---

## 8. PQLE Audit

- Threshold 95; golden compare is structural (sections/SVG/roles).
- Soft attach: `reject_on_fail=False` in generator path.
- Can raise polish scores while leaving template teaching intact.
- Vocabulary/worksheet pages can receive hard-coded high dimension scores when cards/SVG exist.

**Barely-pass / fail behaviour:** EATS trend shows reject 64.6 → pass 95.7 on the **same topic** while human teachability stays ~32–38 — gates moved, teaching did not.

---

## 9. EATS Audit — Calibration Failure

| Metric | Value |
|--------|-------|
| Pass rate (dashboard) | 30% |
| Average educational_quality | **98.49** |
| Average diagram | **99.38** |
| Human teachability on pass HTML | **~38** |
| Gap | **~50–60 points** |

EATS checks structure, AI-phrase lists, SVG `<svg`, vocab field density, adaptation keyword signatures — **not** scientific correctness of diagrams, **not** absence of teacher-objective leakage (until later hygiene), **not** worked-example substance.

**Recommendation:** recalibrate with human teachability goldens; fail on template phrase density; require domain-labelled diagrams; do not award diagram 100 for subject-sequence boxes.

---

## 10. Performance & Waste

| Issue | Evidence |
|-------|----------|
| Unused engine execution | VLIE pre-engines → summary_keys |
| Duplicate STEM | VLIE scientific_accuracy + `process_lesson_stem` |
| Overlapping quality stacks | EERL + PQI + EATS + qa |
| Dead / dormant hot path | ULI/SIF default off; LXP toggle off |
| Config dead letter | `ENABLE_LCE_PIPELINE` unused at callers |
| Memory/latency | Not re-profiled this audit; prior production-readiness noted Chroma cold start ~21s |

---

## Top 20 Issues

1. LCE template teaching (“core idea” loops)  
2. EATS/PQLE miscalibration (95+ ≠ teachable)  
3. Learning-objective text as student content  
4. VLIE payloads discarded after compute  
5. Cosmetic adaptations flagged as distinct  
6. Generic flowcharts scoring diagram=100  
7. Duplicate STEM execution  
8. ULI/SIF off + `sif` vs `subject_intelligence` mismatch  
9. `ENABLE_LCE_PIPELINE` not enforced  
10. UVIE metadata dropped  
11. Teacher note spam adaptation  
12. Stub golden library (3)  
13. No multi-board 50-lesson suite  
14. Soft PQLE reject  
15. Four quality layers, same blind spots  
16. Side engines on gen path without UI ROI  
17. Duplicated SVG in export  
18. `IMAGE_PROVIDER=off`  
19. Multi-agent facade = labels  
20. Score chasing vs human sample prose quality  

---

## Prioritized Remediation Plan

### Quick wins (do not remove architecture)

1. Student-safe filters for objectives/teacher text (partially shipped).  
2. Recalibrate EATS/PQLE against human teachability panels.  
3. Fail generic subject-sequence diagrams as publisher visuals.  
4. Skip unused VLIE pre-engines on the generation hot path (keep APIs).  
5. Deduplicate STEM.

### Priority (restore > pre-upgrade quality)

6. Rewrite LCE composer: claim-grounded paragraphs, real examples, misconception sentences that parse.  
7. True adaptation forks (structure + cognitive load), not clone+wrapper.  
8. Feed CIE/knowledge claims into section bodies.  
9. Replace stub goldens with 30+ scored publisher exemplars across subjects.  
10. One hard quality gate with teachability criteria.

### Long-term

11. Enable ULI/SIF only after LCE consumption proven.  
12. Park LXP/ATIE/ALE/LMAS off default gen until measured ROI.  
13. Build the missing 50-lesson multi-board acceptance suite.  
14. Domain pictorial library.  
15. Collapse facade engines; document one OS spine.

---

## Success Criteria — Answers

| Question | Answer |
|----------|--------|
| Which engines improve lesson quality? | KIE, STEM/router/packs, selective visuals, qa; LCE only after rewrite |
| Which do not contribute to final output? | Most VLIE pre/post payloads; ULI/SIF by default; AME/AIE/ATIE/VMLE/ALE on gen path |
| Where is quality lost? | LCE templating, unused intelligence, miscalibrated gates, cosmetic adaptations |
| Why pre-upgrade looked better? | Human source prose + less score-optimized scaffolding |
| Top 20 blockers? | Listed above |
| Plan without discarding strengths? | Slim hot path; keep computation layer; recalibrate gates; rewrite LCE; park dormant buses |

---

## Appendix — Evidence Index

- Pipeline: `app.py`, `engines/verified_learning_engine/orchestrator.py`, `ai_generator.py`, `agents/orchestration.py`, `publication_gate.py`, `structured_renderers.py`  
- LCE/PQLE: `engines/lesson_composition_engine/{composer,adaptive_writing,publisher_quality,eerl}.py`  
- EATS: `eats/`, `reports/eats/dashboard_state.json`, `reports/eats/20260723T145916Z_*`, `reports/screenshots/20260723T145916Z/standard.html`  
- Config: `config.py` (`ENABLE_ULI_PIPELINE=false`)  
- Prior audits: `docs/production-readiness/*` (AI quality 38, integration 42, visual 64)

**Constraint honored:** no fixes, no refactors, no new engines during this audit.
