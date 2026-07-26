# Alora AI — Critical Regression Investigation Report

**Date:** 23 July 2026  
**Mode:** Investigation first; fixes only after root causes (Section 10)  
**Constraint:** Objective is restore/exceed pre-expansion educational quality — not more architecture

---

## Executive summary

Educational quality degraded primarily because **commit `3652657` (Ship LCE, PQLE, EATS)** replaced claim-grounded / LLM-authored classroom prose with a **deterministic template composer** that emits authoring scaffolding into learner HTML. Most VLIE “intelligence” engines still **run but discard payloads to `summary_keys`**, so they do not compensate. Adaptations are largely **clone + wrapper** of that template. A later “quality” commit (**`4f6bf7e`**) also swapped the premium cream textbook background for cool grey.

**Root cause is not “too few engines.” It is the wrong author (LCE templates) plus unused intelligence buses plus score-optimized gates.**

---

## 1. Template language provenance

| Phrase | Source | Stage | Introduced | Reaches HTML? |
|--------|--------|-------|------------|---------------|
| `We begin with…` | `composer.compose_standard_from_clg` | LCE | `3652657` | Partially remediated in WT |
| `X is a core idea in this lesson` | `composer._concept_explain` | LCE | `3652657` | Partially remediated |
| `worth mastering because…` | composer `big_idea` | LCE | `3652657` | Partially remediated |
| `Students will…` | `clg._student_goal`, source objectives | CLG → vocab | Pre-LCE + LCE | Scrubbed if remediation/vocab hygiene runs |
| `Notice how…` | `writing_excellence.vary_openings` | PQLE polish | `3652657` | **YES — still leaks** |
| `As you read, notice how…` | composer Learning Goal | LCE | `3652657`/WT | **YES** |
| `Worked example: identify where…` | composer / concept_teaching | LCE | `3652657` | Rewritten form still meta |
| `Checkpoint:` / `Key words in this section` | `adaptive_writing._rewrite_section_body` | Adaptations | `3652657` | **YES** |
| `Study the diagram…` / Look first | adaptive_writing / composer | Adaptations | `3652657`→`4f6bf7e` | **YES** |
| `Memory tip` / `Picture` labels | `vocabulary_card_html`, `structured_renderers` | Vocab UI | `3652657` | **YES** (labels + polluted body historically) |
| `Teacher note` spam | adaptive_writing per section | Teacher tab | `3652657` | Consolidated in WT remediation |

**Pipeline path for a polluted sentence:**

```
CLG / claims
  → LCE composer (template sections)
  → adaptive_writing (Checkpoint / Key words / Study the diagram)
  → writing_excellence.vary_openings ("Notice how")
  → publisher_remediation (partial scrub; was untracked until remediation work)
  → structured_renderers / html_exporter
```

No placeholder should reach HTML — **current design intentionally injects scaffold labels into student body text.**

---

## 2. Adaptation matrix (Engine → Output → Consumed → Rendered)

| Adaptation | Engine / author | Output | Consumed by renderer? | Distinct teaching? |
|------------|-----------------|--------|----------------------|--------------------|
| Mainstream (`standard`) | LCE `compose_standard_from_clg` | Template sections + claim facts | Yes | Baseline (template) |
| Vocabulary | LCE `compose_vocabulary_page` | Cards / matching | Yes | Useful if defs clean |
| Worksheet | LCE `compose_worksheet_from_clg` | Exam parts | Yes | Partial |
| ADHD / Autism / ELL / LD / Visual / Auditory | `compose_adaptive_version` deep-copy + wrappers | Same body + cues | Yes | **Mostly cosmetic** |
| Teacher | Same + guidance block | Same body | Yes | **Cosmetic** (was note spam) |
| Parent | Same + home prompts | Same body | Yes | Partial |
| AIE (VLIE) | `analyze_accessibility_context` | Full payload → **summary_keys** | **No** | Does not drive tabs |
| ALE / ATIE / VMLE (VLIE gen) | Planning packages | summary_keys | **No** on gen path | Side APIs only |

`lce.pedagogically_distinct = True` is set even when content is a clone — **false positive for distinctiveness.**

---

## 3. Intelligence utilisation audit

| Engine | Runs? | Output? | Consumed in lesson body? | Changes HTML? | Flag |
|--------|-------|---------|--------------------------|---------------|------|
| KIE | Yes | Envelope | Yes | Yes | Essential |
| STEM / router | Yes | Facts/visuals | Yes | Yes | Essential |
| LCE | Yes | Sections | Yes | Yes | **Essential but currently harmful author** |
| PQLE / EERL | Yes | Scores + polish | Soft | Indirect | Useful if recalibrated |
| EATS | Yes | Gate scores | Gate | Blocks/allows | Misaligned |
| VLIE UCF/AME/AIE/ATIE/VMLE/ALE | Yes (pre) | Payloads | **No** (summary_keys) | No | **No visible value on gen path** |
| ULI + SIF packs | Default OFF | — | No | No | Dormant |
| UVIE | Via STEM | preferred_visuals | Partial | Partial | Useful |
| LXP | Optional UI | Layout | Toggle | Optional | Optional |
| Multi-agent facade | Labels | Roster | No | No | Redundant |

---

## 4. HTML provenance (Force & Pressure / Water Cycle pattern)

For a typical rendered paragraph such as *“Force is a core idea…”* / *“Notice how…”*:

| Field | Value |
|-------|-------|
| Source module | `engines/lesson_composition_engine/composer.py` or `writing_excellence.py` |
| Source function | `_concept_explain` / `vary_openings` / `_rewrite_section_body` |
| Pipeline stage | LCE compose → adaptive → polish |
| Engine responsible | LCE (not AIE/AME/ATIE) |
| Rewrite stage | PQLE writing_excellence / remediation |
| Publisher score | Often ≥95 while teachability ~35–40 (EATS structural) |

Full per-paragraph map for a live generation requires one instrumented run; static provenance above covers >90% of polluted strings.

---

## 5. Golden comparison (educational, not structural)

| Golden | Nature | Generated LCE vs golden |
|--------|--------|-------------------------|
| `biology_water_cycle.json` | Stub hooks | Generated longer but more template; less teacher voice |
| `science_force_pressure.json` | Stub | Same |
| `math_fractions.json` | Stub | Same |
| `samples/sample_lesson.docx` | **Human prose** | Pre-expansion feel; still the quality bar |

Goldens do **not** enforce teachability — only section/SVG/role structure — so gates can “pass” while voice fails.

---

## 6. Voice reader regression

| Hypothesis | Verdict |
|------------|---------|
| TTS provider removed | **No** — still OpenAI neural in `audio_learning.py` |
| `IMAGE_PROVIDER=off` killed audio | **No** — images only |
| Credentials / empty API key | **Likely** — falls back to browser `speechSynthesis` |
| Publication quarantine | **Likely** — viewer returns before audio panel |
| Voice catalog shrink | `6d76e78` — 4 labels → Female/Male (UX regression) |
| Renderer removed panel | **No** — still in `viewer_page.py` |

Premium neural returns when `runtime_api_key` is valid and lesson is not quarantined.

---

## 7. UI background regression

| Item | Premium | Current | Commit |
|------|---------|---------|--------|
| `BG_MAIN` | `#FFF9EE` cream | `#F7FAFC` cool grey | **`4f6bf7e`** |
| Picture-word cards | `#FFF9EE` | `#F7FAFC` | **`4f6bf7e`** |

Docs (`ALORA_AI_MASTER_BUILD_PROMPT`) still specify cream. Restore `BG_MAIN = "#FFF9EE"`.

---

## 8. Multi-subject validation (method note)

No automated 50-lesson corpus exists. Quality pattern is **subject-agnostic**: LCE templates apply to physics, biology, maths alike. Force & Pressure EATS HTML and Water Cycle production screenshots are representative of the regression class across subjects.

---

## 9. Root cause register

| # | Regression | Why | Commit | Engine | Impact | Fix | Pri | Effort |
|---|------------|-----|--------|--------|--------|-----|-----|--------|
| R1 | Authoring templates in student HTML | LCE ships stock phrases as body text | `3652657` | LCE | Sounds like AI instructions | Purge emitters; expand remediation; ban in EATS | P0 | M |
| R2 | “Notice how” spam | `vary_openings` injects prefixes | `3652657` | writing_excellence | Robotic voice | Remove injector | P0 | S |
| R3 | Adaptations identical | Deep-copy + cue wrappers | `3652657` | adaptive_writing | No true a11y redesign | Structural forks or honest labeling | P0 | L |
| R4 | Intelligence unused | VLIE stores summary_keys only | VLIE design / `3652657` era | VLIE buses | Cost without quality | Skip unused on gen path | P1 | M |
| R5 | EATS passes weak lessons | Structural/SVG scoring | `3652657` | EATS | False publisher_ready | Teachability recalibration (started) | P0 | M |
| R6 | Cream UI lost | BG_MAIN changed | `4f6bf7e` | styles/lesson_design | Looks cheaper | Restore `#FFF9EE` | P0 | S |
| R7 | Neural voice “gone” | Key/quarantine/fallback | various + gates | audio_learning | Browser TTS only | Key UX + gate messaging + voice labels | P1 | S |
| R8 | Objective text as definitions | CLG/claims as vocab | Pre + LCE | vocab path | Teacher jargon | Hygiene (partially shipped) | P0 | S |
| R9 | Generic diagrams score 100 | Subject-sequence SVG | LCE diagrams | LCE/EATS | Fake visual quality | Domain nodes (partially shipped) | P0 | S |
| R10 | Soft PQLE reject | `reject_on_fail=False` | LCE attach | PQLE | Weak lessons render | Harden gate after content fixed | P1 | S |

---

## 10. Fix plan (acceptance criterion)

**Acceptance:** Every lesson reads like an exceptional classroom teacher + premium publisher. No template/authoring language in learner HTML. Renderer shows full pipeline intelligence, not generic scaffolds.

**Priority order:**

1. Purge remaining template emitters (`vary_openings`, adaptive cue labels, composer leftovers).  
2. Restore cream textbook UI (`#FFF9EE`).  
3. Harden remediation + EATS so leaks fail closed.  
4. Clarify audio: surface neural vs browser; restore voice choices; quarantine messaging.  
5. Only then deepen adaptation distinctiveness and wire unused engines if they change HTML.

---

## Evidence index

- Commits: `3652657`, `4f6bf7e`, `af4f80f`, `68d5839`, `6d76e78`  
- Code: `composer.py`, `adaptive_writing.py`, `writing_excellence.py`, `orchestrator.py` (`summary_keys`), `audio_learning.py`, `lesson_design.py`  
- Artifacts: `reports/eats/*`, `reports/screenshots/20260723T145916Z/standard.html`, audit `docs/ALORA_COMPLETE_SYSTEM_AUDIT.md`
