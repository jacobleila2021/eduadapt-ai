# AdaptEd AI / Alora AI — Verified Learning Engine (VLE)

**Product:** Alora AI (AdaptEd AI / EduAdapt AI)  
**Document:** `VERIFIED_LEARNING_ENGINE_ARCHITECTURE.md`  
**Status:** Core platform architecture — competitive foundation  
**Principle:** **Verified Knowledge First. AI Explanation Second.**  
**Positioning:** Not an AI chatbot — a **trusted educational operating system**

**Related**

- `THREE_LAYER_SCIENTIFIC_COMPUTING_ARCHITECTURE.md` — **Knowledge · Computation · Teaching** split + SCE (adopt before post-MVP)
- `SCIENTIFIC_ACCURACY_ENGINE_ARCHITECTURE.md` — STEM validation detail under the VLE

**Audience:** Engineers, curriculum experts, STEM educators, AI architects, school/gov buyers, investors, QA

---

## 1. Why the Verified Learning Engine

Over recent builds, Alora already differentiates lessons, supports accessibility, and uses AI for pedagogy. The next leap is architectural:

> **Do not treat the LLM as the brain of the platform.**  
> Treat it as one agent among many. **Specialized engines** own accuracy, curriculum fit, assessment, accessibility, and mastery. The **Verified Learning Engine (VLE)** orchestrates them.

That is compelling to:

| Stakeholder | Why it matters |
|-------------|----------------|
| **Schools** | Traceable correctness; not “whatever the chatbot said” |
| **Governments** | Curriculum alignment + auditability |
| **Investors** | Defensible OS architecture, not a thin GPT wrapper |
| **Teachers** | Trust + control; engines verify before publish |
| **Learners** | Consistent, accessible, mastery-aware pathways |

---

## 2. Platform law (unchanged)

The VLE **enforces**:

**Verified Knowledge First. AI Explanation Second.**

LLMs must never invent mathematical answers, chemical equations, scientific constants, formula derivations, molecular structures, unit conversions, or statistical calculations. Those belong to computational / verified engines (see SAE doc).

---

## 3. VLE as educational operating system

```
                    ┌──────────────────────────────────┐
                    │     Verified Learning Engine      │
                    │   (orchestrator + policy gate)    │
                    └────────────────┬─────────────────┘
                                     │
     ┌───────────────┬───────────────┼───────────────┬───────────────┐
     ▼               ▼               ▼               ▼               ▼
 Curriculum    Multi-Agent      Scientific      Assessment     Accessibility
 Intelligence  AI Orchestrator  Accuracy (SAE)  & Mastery      Intelligence
     ▼               ▼               ▼               ▼               ▼
 Adaptive          AI Tutor      Analytics &      Gamification
 Learning                        Insights         & Motivation
```

**Kernel responsibilities of the VLE**

1. Route each request to the right engine(s)  
2. Merge results into a single **Verified Learning Package (VLP)**  
3. Run **publish / serve gates** (accuracy, curriculum, a11y, assessment validity)  
4. Attach **provenance** (engine ids, hashes, versions, curriculum codes)  
5. Never let the LLM silently override engine truth  

---

## 4. Engine portfolio

### 4.1 Curriculum Intelligence Engine

**Purpose:** Map content to formal curricula and grade bands.

| Capability | Detail |
|------------|--------|
| Frameworks | NCERT, CBSE, Cambridge, IB, state boards (extensible) |
| Outputs | Objective codes, grade band, topic graph, prerequisite edges |
| Inputs | Lesson text, teacher tags, board selection |
| Non-LLM core | Curated curriculum graphs + deterministic matchers |
| LLM assist | Suggest likely codes; **human or curator confirm** before lock |

**Competitive edge:** “Aligned to CBSE Class 8 — Chemical Reactions” with a code, not a vibe.

---

### 4.2 Multi-Agent AI Orchestrator

**Purpose:** Coordinate specialized AI agents without a single monolithic prompt.

| Agent (examples) | Allowed to do | Must not do |
|------------------|---------------|-------------|
| Explainer | Simplify, analogies | Invent STEM facts |
| Differentiator | Reading level, structure | Change verified equations |
| Storyteller | Narrative hooks | Alter numbers / science |
| A11y rewriter | Captions, plain language | Drop required STEM artifacts |
| Planner | Lesson sequence | Skip validation gates |

Orchestrator policy: agents consume **EngineArtifacts** and **CurriculumBindings**; they emit pedagogy only.

---

### 4.3 Scientific Accuracy Engine (SAE)

**Purpose:** Deterministic STEM truth.

Fully specified in `SCIENTIFIC_ACCURACY_ENGINE_ARCHITECTURE.md`:

- Chemistry / Mathematics / Physics engines  
- Biology visualization (curated-first)  
- Diagram + Formula rendering  
- Scientific Validation Pipeline  

**VLE rule:** No STEM-bearing lesson is served or published unless SAE validation is `pass` (or audited teacher override).

---

### 4.4 Assessment & Mastery Engine

**Purpose:** Measure learning; never invent “correct” keys for STEM items without engines.

| Capability | Approach |
|------------|----------|
| Item generation | Templates + engine-verified answers |
| Rubrics | Curriculum-aligned criteria |
| Mastery model | Deterministic scores / spaced evidence (e.g. Elo-like or mastery thresholds) |
| Misconception tags | Curated bank + response patterns |

LLM may write stem wording at a reading level; **answer keys and numeric/chemical correctness** come from SAE + item bank.

---

### 4.5 Accessibility Intelligence Engine

**Purpose:** Enforce inclusion as a system property, not an afterthought.

| Capability | Detail |
|------------|--------|
| Profiles | Dyslexia, ADHD, autism support, ELL, visual/auditory, motor |
| Checks | Contrast, reading level, chunking, caption presence, diagram alt-text |
| Outputs | A11y scorecard + required remediations before publish |
| Assets | Prefer verified diagrams + TTS from approved pipelines |

Maps to Alora’s nine adaptation tracks; becomes **measurable** gate, not only prompt instructions.

---

### 4.6 Adaptive Learning Engine

**Purpose:** Decide *what next* for each learner.

| Signal | Source |
|--------|--------|
| Mastery | Assessment & Mastery Engine |
| Preferences / profile | Accessibility + teacher roster |
| Curriculum path | Curriculum Intelligence |
| Difficulty | Verified items only |

Adaptation = pathway + representation. Truth content stays engine-backed.

---

### 4.7 Analytics & Learning Insights Engine

**Purpose:** Privacy-respecting insights for teachers and schools.

| Insight | Example |
|---------|---------|
| Class heatmaps | Objectives with low mastery |
| Time-on-task | Engagement without dark patterns |
| Adaptation efficacy | Which version improved outcomes |
| Integrity | Validation fail rates, override rates |

Local-first / school-tenant friendly; no ad-tech telemetry.

---

### 4.8 Gamification & Motivation Engine

**Purpose:** Motivation without compromising academic integrity.

| Allowed | Forbidden |
|---------|-----------|
| Streaks, badges for *effort* / *completion of verified practice* | Rewarding guessed wrong STEM as “creative” |
| Progress toward curriculum objectives | Leaderboards that expose sensitive learner data by default |

All game events reference **verified** practice items when STEM is involved.

---

### 4.9 AI Tutor Engine

**Purpose:** Conversational coaching **on top of** verified packages.

| May | Must not |
|-----|----------|
| Explain using SAE artifacts | Recalculate / rebalance unaided |
| Socratic questions from item bank | Invent exam answers |
| Scaffold per Adaptive Learning plan | Bypass Accessibility or Validation gates |

Tutor sessions log `artifactIds` cited in each reply for audit.

---

## 5. Verified Learning Package (VLP)

Canonical object the VLE produces and stores:

```ts
interface VerifiedLearningPackage {
  packageId: string;
  sourceDocumentHash: string;
  curriculumBindings: Array<{ board: string; grade: string; code: string; confidence: number; locked: boolean }>;
  engineArtifacts: string[];          // SAE + diagram + formula ids
  assessmentBundleId?: string;
  accessibilityProfile: string[];
  adaptationVariant: string;          // e.g. dyslexia_smart, ell
  validation: {
    scientific: 'pass' | 'fail' | 'warn';
    curriculum: 'pass' | 'fail' | 'warn';
    accessibility: 'pass' | 'fail' | 'warn';
    assessment: 'pass' | 'fail' | 'warn' | 'n/a';
  };
  pedagogy: {
    sections: unknown;                // LLM-adapted language only
    stories?: unknown;
    scaffolds?: unknown;
  };
  provenance: {
    vleVersion: string;
    engineVersions: Record<string, string>;
    createdAt: string;
  };
}
```

**Serve / publish only if required gates pass.**

---

## 6. Request lifecycle (orchestration)

```
Teacher upload / learner query
        │
        ▼
VLE Router
        │
        ├─► Curriculum Intelligence ── bindings
        ├─► Claim Extractor ── STEM claims
        ├─► SAE (chem/math/physics/…) ── EngineArtifacts
        ├─► Diagram / Formula engines ── renders
        ├─► Assessment engine (if quiz path)
        ├─► Accessibility engine ── scorecard + constraints
        │
        ▼
Multi-Agent Orchestrator (teaching agents only)
        │
        ▼
Assemble VLP
        │
        ▼
Gate: scientific ∩ curriculum ∩ a11y ∩ assessment
        │
        ├─ FAIL → block + teacher review queue
        └─ PASS → Adapt / Tutor / Analytics / Gamification consumers
```

---

## 7. Competitive narrative (one paragraph)

AdaptEd AI is not a chatbot that writes lessons. It is a **Verified Learning Engine**: curriculum-aware, scientifically gated, accessibility-enforced, mastery-measured, and audit-ready. AI agents personalize language and support; specialized engines guarantee correctness and pedagogical quality. That architecture is what schools, governments, and investors can trust at scale.

---

## 8. Implementation roadmap (phased)

### Phase 0 — Constitution (now)

- [x] Platform rule + SAE architecture  
- [x] VLE architecture (this document)  
- [ ] Cursor / product docs cross-link; naming: Alora AI product, AdaptEd AI platform brand as needed  

### Phase 1 — Kernel

1. VLE router stub in app pipeline (before/after `generate_adaptations`)  
2. SAE gate for chem/math claims  
3. VLP schema + store validation reports  
4. Accessibility scorecard (checklist v1)  

### Phase 2 — Trust for schools

5. Curriculum Intelligence (CBSE/NCERT first)  
6. Assessment items with engine-backed keys  
7. Teacher review + override audit  
8. Analytics dashboard (class mastery)  

### Phase 3 — OS depth

9. Adaptive pathways  
10. AI Tutor bound to VLP artifacts  
11. Gamification (integrity-safe)  
12. Multi-board curriculum packs + government pilot tooling  

---

## 9. Mapping to current Alora codebase

| Today | VLE home |
|-------|----------|
| `ai_generator.py` / OpenAI | Teaching agents under Multi-Agent Orchestrator — **not** truth source |
| `adaptation_specs.py` | Adaptive + Accessibility profiles |
| Analytics / complexity | Seed of Analytics & Curriculum signals |
| Mermaid / SVG in prompts | Migrate to Diagram Engine + SAE |
| Streamlit publish | Add VLP validation gate before “ready” |

---

## 10. FINAL DELIVERABLES (this document)

| Deliverable | Section |
|-------------|---------|
| Verified Learning Engine (core) | §1–§3, §5–§6 |
| Curriculum Intelligence Engine | §4.1 |
| Multi-Agent AI Orchestrator | §4.2 |
| Scientific Accuracy Engine | §4.3 + SAE doc |
| Assessment & Mastery Engine | §4.4 |
| Accessibility Intelligence Engine | §4.5 |
| Adaptive Learning Engine | §4.6 |
| Analytics & Learning Insights Engine | §4.7 |
| Gamification & Motivation Engine | §4.8 |
| AI Tutor Engine | §4.9 |
| Competitive / buyer narrative | §7 |
| Deployment / roadmap | §8–§9 |

---

*AdaptEd AI: AI enhances learning; specialized engines ensure accuracy, consistency, accessibility, and pedagogical quality.*
