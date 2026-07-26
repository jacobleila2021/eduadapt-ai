# Accessibility Intelligence Engine (AIE) — Architecture & Audit

**Date:** 2026-07-17  
**Product:** Alora AI  
**Rule:** Presentation personalization only — curriculum, STEM, and official answers stay locked.

---

## 1. Audit — before AIE

| Area | Existing | Gap |
|------|----------|-----|
| VLIE AccessibilityEngine | Thin presets stub | No learner profile / rules engine |
| `adaptation_specs.py` | Canonical tab catalog | Engine did not select by learner |
| `accessibility.py` / `lesson_design` / TTS | Real UI chrome | Presets unused by engine |
| CIE adaptations | Concept presentation tips | Not wired to learner roster |
| AME accommodations | Per-call profile list | No persistent a11y profile |

---

## 2. Architecture

```
adaptation_specs + CIE hints + lesson text
              ↓
   accessibility_intelligence_engine/*
              ↓
   AccessibilityEngine (VLIE v2) → profiles_generated + interface + tutor_brief
              ↓
   AdaptiveLearning / AI Tutor / AME (consume accommodations)
```

AIE decides **how** the learner experiences content — never **what** the verified facts are.

---

## 3. Folder structure

```
engines/accessibility_intelligence_engine/
  schemas.py learner_profile.py sensory_profiles.py
  adaptation_rules.py accommodations.py recommendations.py
  presentation.py interface.py assistive.py
  readability.py language_support.py analytics.py
  dashboards.py indexing.py intelligence.py service.py engine.py
engines/accessibility_engine/engine.py   # VLIE facade v2
docs/ACCESSIBILITY_INTELLIGENCE_ENGINE.md
tests/test_aie.py
data/knowledge/aie/   # profiles + analytics (gitignored)
```

---

## 4. Processing workflow

1. Build/load learner accessibility profile (functional preferences only — **no medical diagnoses**).
2. Apply deterministic rules → recommendations (reason, evidence, priority, confidence).
3. Select presentation mode + interface config (WCAG 2.2 AA / UDL 3.0 oriented).
4. Emit AT compatibility, language/EF scaffolds, readability report.
5. Produce `tutor_brief` for AI Tutor; `assessment_accommodations` for AME.
6. Preserve backward keys: `profiles_generated`, `presets`, `facts_immutable`.

---

## 5. API (`service.api_*`)

| Endpoint-shaped API | Purpose |
|---------------------|---------|
| `api_get_learner_profile` | GET profile |
| `api_update_accessibility_preferences` | Update prefs |
| `api_generate_recommendations` | Deterministic supports |
| `api_apply_accommodations` | Full accommodation package |
| `api_get_readability_report` | Readability / cognitive load |
| `api_retrieve_accessibility_analytics` | Usage analytics |
| `api_dashboards` | student / teacher / parent / class |
| `api_rebuild_index` | Chroma catalog sync |

---

## 6. Security

- Store functional supports only (explicit `stores_medical_diagnoses=False`).
- Learner a11y data under `data/knowledge/aie/` (gitignored).
- RBAC for dashboards at HTTP layer later.

---

## 7. Integration map

| Consumer | Receives |
|----------|----------|
| AdaptiveLearningEngine | `profiles_generated` |
| AITutorEngine | `tutor_brief` / `accessibility_profile` |
| AME | `accessibility_profiles_for_ame` + assessment accommodations |
| Streamlit UI | `interface_css_hints` (wire when ready) |
| CIE | optional concept adaptation hints merged in |

---

## 8. Testing

`tests/test_aie.py` · smoke `AIE_SMOKE_OK`
