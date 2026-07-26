# Section C — Future Roadmap Audit (Intentionally Deferred)

**Date:** 2026-07-16  
**Purpose:** Keep the current build production-focused while documenting advanced capabilities that are **out of scope** for Section B completion.

These items should not be started until Section B is stable in classroom pilots.

---

## Deferred capability map

| Area | Capability | Why deferred | Suggested phase |
|------|------------|--------------|-----------------|
| **i18n** | Multilingual UI + bilingual lessons (Hindi/regional) | Requires translation memory, font packs, TTS locales | P4 |
| **Adaptive difficulty / IRT** | Full IRT item response theory + longitudinal learner model | AME mastery + adaptive selection shipped; IRT deferred | P4 |
| **Curriculum ontology (expansion)** | Full multi-board LO corpus beyond Class 8 Science pilot | CIE core shipped; needs curated content scale | P4 |
| **Enterprise admin** | School tenancy, SSO, role RBAC, audit exports | Product/ops, not STEM accuracy | P5 |
| **Licensing** | NCERT/CBSE content rights, DRM for PDFs | Legal + publisher agreements | P5 |
| **xAPI / LTI** | Learning record store, LMS launch | Standards integration after core pedagogy | P5 |
| **Offline desktop sync** | Full GeoGebra local runtime, offline Chroma sync | Packaging complexity | P4 |
| **Computer vision for student diagrams** | Auto-mark labelled diagrams | Research + privacy review | P5 |
| **Speech therapy / AAC profiles** | Beyond current auditory path | Specialist clinical review | P5 |
| **Full CBSE multi-year PYQ corpus** | Thousands of tagged items | Content acquisition at scale | P4 |
| **Multi-grade multi-subject pilots** | Class 6–12 all streams | Seed + engine coverage expansion | P4 |
| **True multi-agent LLM swarm** | Separate model calls per named agent | Cost/latency; current orchestrator facade is enough | P5 |
| **Automated WCAG AA audits** | axe/playwright contrast crawlers | CI infrastructure | P4 |
| **Durable object storage** | S3/GCS for figures & plots | Ops; tempfile + local repo OK for pilot | P4 |

---

## Keep building on (do not replace)

- Subject Tool Router + deterministic engines
- Visualization priority (NCERT → engines → AI last)
- Teacher chapter approval cache
- Hard QA publish gate
- Chroma NCERT + question collections
- Adaptation presentation layer (facts locked)
- **VLIE** (`engines/verified_learning_engine`) — OS orchestration + event-driven Learning Session Orchestrator; see `docs/VLIE_ARCHITECTURE.md` and `docs/EVENT_DRIVEN_VLIE_ARCHITECTURE.md`
- **KIE** (`engines/knowledge_ingestion_engine`) — trusted content entry; see `docs/KNOWLEDGE_INGESTION_ENGINE.md`
- **CIE** (`engines/curriculum_intelligence_engine` + `curriculum_engine`) — academic brain; see `docs/CURRICULUM_INTELLIGENCE_ENGINE.md`
- **AME** (`engines/assessment_mastery_engine` + `assessment_engine`) — evidence & mastery; see `docs/ASSESSMENT_MASTERY_ENGINE.md`
- **AIE** (`engines/accessibility_intelligence_engine` + `accessibility_engine`) — presentation intelligence; see `docs/ACCESSIBILITY_INTELLIGENCE_ENGINE.md`
- **ALE** (`engines/adaptive_learning_engine`) — pathway/pacing decisions; see `docs/ADAPTIVE_LEARNING_ENGINE.md`
- **LAIE** (`engines/learning_analytics_engine`) — insights & alerts; see `docs/LEARNING_ANALYTICS_INSIGHTS_ENGINE.md`
- **ATIE** (`engines/ai_tutor_intelligence_engine` + `ai_tutor_engine`) — grounded tutoring; see `docs/AI_TUTOR_INTELLIGENCE_ENGINE.md`
- **VMLE** (`engines/voice_multimodal_learning`) — voice & multimodal presentation layer; see `docs/VOICE_MULTIMODAL_LEARNING_ARCHITECTURE.md`
- **ALCIS** (`engines/learning_companion_engine`) — motivational companion (never teaches); see `docs/AI_LEARNING_COMPANION_ARCHITECTURE.md`
- **LMAS** (`engines/learning_motivation_engine` + `gamification_engine` facade) — XP/achievements/quests; see `docs/LEARNING_MOTIVATION_ARCHITECTURE.md`
- **UCF** (`engines/universal_curriculum_framework`) — single internal curriculum schema; see `docs/UNIVERSAL_CURRICULUM_FRAMEWORK.md`
- **CEF** (`engines/curriculum_expansion_framework`) — multi-board import → UCF; see `docs/CURRICULUM_EXPANSION_FRAMEWORK.md`
- **CMIF** (`engines/curriculum_migration_framework`) — production migration pipeline → UCF; see `docs/CURRICULUM_MIGRATION_FRAMEWORK.md`
- **LXP** (`engines/learning_experience_platform` + `ui/lxp` + `ui/learning_experience_platform` + `premium/`) — Phases 1–4; see `docs/LEARNING_EXPERIENCE_PLATFORM.md`, `docs/LXP_PHASE3_COLLABORATION_REVISION.md`, `docs/LXP_PHASE4_PREMIUM_EXPERIENCE.md`

### Product refinement next (content acquisition via CMIF)

1. NCERT Classes 1–12 + CBSE competencies (Phase 2 expanded corpus)  
2. ~~ICSE / ISC / Kerala / NIOS~~ — **Phase 3 pilots shipped**  
3. ~~Cambridge / IB~~ — **Phase 4 pilots shipped**  
4. ~~University + professional~~ — **Phase 5 pilots shipped** (`seeds_higher_ed.py`)  
---

## Product refinement next (after LMAS)

1. Intelligent Lesson Reader  
2. Teacher / Special Educator / Parent workspaces  
3. Multi-board curriculum expansion (CBSE, ICSE, Cambridge, IB, NIOS, State Boards)

---

## Success signal to start Section C work

1. One full Class 8 Science chapter validated by a teacher via approve-cache.
2. Zero critical publish-gate false negatives in UAT.
3. Legal clearance for broader NCERT PDF figure reuse.
