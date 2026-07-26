# Alora AI — Three-Layer Intelligence & Scientific Computing Engine

**Product:** Alora AI (AdaptEd AI / EduAdapt AI)  
**Document:** `THREE_LAYER_SCIENTIFIC_COMPUTING_ARCHITECTURE.md`  
**Status:** Governing architecture — adopt **before** expanding beyond MVP  
**Principle:** Deterministic engines for one correct answer; AI only for teaching  

**Related**

- `VERIFIED_LEARNING_ENGINE_ARCHITECTURE.md` — educational OS / VLE orchestration  
- `SCIENTIFIC_ACCURACY_ENGINE_ARCHITECTURE.md` — STEM validation detail  

---

## 0. Key architectural principle

> **Use deterministic engines for anything that has one correct answer, and use AI only for explanation, teaching, adaptation, personalization, and conversation.**

Alora AI is an **AI Orchestrator**, not a chatbot that invents equations, graphs, or answers.

| Has one correct answer | Owner |
|------------------------|--------|
| Math / algebra / calculus results | Computation Layer (SymPy, NumPy, SciPy) |
| Chemistry balancing / atom counts | Computation Layer (ChemPy / SymPy) |
| Graphs, circuits, molecules | Computation Layer (Matplotlib, Schemdraw, RDKit) |
| Official MCQ / exemplar keys | Knowledge Layer (answer bank) |
| Curriculum facts from NCERT/CBSE | Knowledge Layer (RAG + citations) |

| Pedagogical / soft | Owner |
|--------------------|--------|
| Explain, scaffold, analogies | Teaching Layer |
| Differentiated versions | Teaching Layer |
| Conversational tutor | Teaching Layer |
| Motivation / gamification copy | Teaching Layer |

**The AI never changes a computed or official result.**

---

## 1. Three intelligence layers (mandatory split)

```
┌─────────────────────────────────────────────────────────────┐
│  3. TEACHING LAYER                                          │
│  Multi-agent AI: explain · adapt · personalize · tutor      │
│  Never invents STEM facts or official answers               │
└──────────────────────────▲──────────────────────────────────┘
                           │ consumes Verified Learning Package
┌──────────────────────────┴──────────────────────────────────┐
│  2. COMPUTATION LAYER                                       │
│  SymPy · ChemPy · RDKit · Matplotlib · Schemdraw · GeoGebra │
│  Validators · Subject Tool Router · QA gates                │
│  Guarantees correctness                                     │
└──────────────────────────▲──────────────────────────────────┘
                           │ retrieves truth + assets
┌──────────────────────────┴──────────────────────────────────┐
│  1. KNOWLEDGE LAYER                                         │
│  NCERT · CBSE · Exemplar · question banks · figures         │
│  ChromaDB / vector store · RAG · citations                  │
│  Source of truth                                            │
└─────────────────────────────────────────────────────────────┘
```

### Why this split (enterprise / school / government)

| Concern | Layer |
|---------|--------|
| Certify curriculum fidelity | Knowledge |
| Certify scientific correctness | Computation |
| Scale personalization without re-auditing math | Teaching |
| Unit-test without LLM flakiness | Computation + Knowledge |
| Swap LLM vendor | Teaching only |

---

## 2. Scientific Computing Architecture (SCE)

### 2.1 Components

1. **Subject Tool Router** — never bypass  
2. **Scientific Computing Layer** — engines below  
3. **Visualization Layer** — priority pipeline  
4. **RAG Layer** — Knowledge → Teaching context  
5. **AI Explanation Layer** — Teaching only  
6. **Lesson Adaptation Layer** — presentation only  
7. **Validation / QA Layer** — reject on fail  
8. **Storage** — assets, artifacts, VLP, audit  
9. **Streamlit Integration** — native widgets  
10. **Logging / errors / performance**

### 2.2 Package layout (code)

```
engines/
  __init__.py
  router.py                 # Subject Tool Router
  types.py                  # EngineResult, ValidationStatus
  mathematics/
  graphs/
  geometry/                 # GeoGebra embed helpers
  physics/
  chemistry/
    balancer.py
    validate.py
    render.py
  molecules/                # RDKit
  biology/                  # NCERT figure registry
  qa/
    pipeline.py
knowledge/
  ingest_ncert.py
  question_bank.py
  rag.py
teaching/
  adaptation.py             # wraps existing ai_generator constraints
  tutor.py
```

---

## 3. Subject Tool Router

### 3.1 Routing table

| Subject / task | Engine | Purpose |
|----------------|--------|---------|
| Mathematics | SymPy | Symbolic algebra, solve, simplify, calculus |
| Graphs | Matplotlib | Functions, stats, coordinate geometry |
| Geometry | GeoGebra | Interactive constructions |
| Physics visuals | Matplotlib + Schemdraw | Forces, circuits, rays, vectors |
| Chemistry equations | ChemPy / SymPy | Balancing |
| Chemistry rendering | LaTeX + mhchem | Notation |
| Molecular structures | RDKit | 2D structures from SMILES |
| Biology diagrams | NCERT figure extraction | Original labelled diagrams |
| Tables | Pandas | Data tables |
| Statistics | NumPy + SciPy | Numerical calculations |

### 3.2 Answer routing

| Question type | Engine |
|---------------|--------|
| Balance equation | ChemPy |
| Solve equation | SymPy |
| Calculate force | SymPy (+ unit check) |
| Draw graph | Matplotlib |
| Draw circuit | Schemdraw |
| Molecular structure | RDKit |
| Geometry | GeoGebra |
| MCQ / Assertion-Reason | Official Answer Bank |
| Explain / compare / essay | LLM + RAG (Knowledge only) |

### 3.3 Invariant

```python
# Pseudocode
result = subject_tool_router.route(task)
assert result.layer == "computation" or result.layer == "knowledge"
# Teaching layer may only wrap result.explanation_inputs
```

Never call the LLM for tasks in the computation/official-answer tables.

---

## 4. Mathematics Engine

**Library:** SymPy (+ NumPy/SciPy where numeric)

**Support:** Arithmetic, algebra, simultaneous equations, quadratics, factorisation, fractions, surds, trigonometry, logarithms, calculus, matrices, probability, statistics.

**Outputs (Computation Layer):**

- Exact answer  
- Worked solution / step-by-step derivation (engine-driven)  
- Common-mistakes **catalogue ids** (curated Knowledge), not LLM-invented wrong math  

**Teaching Layer adds:** verbal explanation, learner-profile wording, accessibility adaptations — **without changing the answer**.

---

## 5. Graph Engine

**Library:** Matplotlib  

**Types:** Line, bar, pie, histogram, scatter, coordinate geometry, functions, quadratic, trig, statistical.

**Streamlit:** `st.pyplot(fig)`  

Brand colours: Deep Navy `#041B4D`, Teal `#008C95`, etc.

---

## 6. GeoGebra Integration

**Embed:** `st.components.v1.iframe(...)`  

**Support:** Triangles, circles, angles, constructions, transformations, coordinate geometry, measurement.

Interactive manipulation allowed; geometric **truth** remains GeoGebra/construction params, not LLM.

---

## 7. Physics Visualization Engine

**Libraries:** Matplotlib, Schemdraw  

**Outputs:** Force / free-body diagrams, electric circuits, ray diagrams, motion graphs, vectors, projectile motion, simple machines — **all labelled**.

---

## 8. Chemistry Balancing Engine

```
Unbalanced equation
  → Deterministic balancer (ChemPy or SymPy null-space)
  → Atom-count validation (LHS == RHS per element)
  → Store balanced equation + EngineResult
  → Render (mhchem / st.latex)
```

**Never** allow an LLM to balance equations.

### 8.1 Validation

Before display:

- Atom counts left == right  
- On failure: reject, recompute once, log validation failure, block publish  

---

## 9. Chemical Rendering System

**Stack:** LaTeX + mhchem · `st.latex()`  

Render: subscripts, superscripts, charges, reaction/equilibrium arrows, state symbols `(s)(l)(g)(aq)`.

Example: `\ce{2H2 + O2 -> 2H2O}`

---

## 10. RDKit Molecular Structure Engine

```
SMILES → RDKit 2D → PNG/SVG → st.image()
```

**Coverage:** Hydrocarbons, alcohols, carboxylic acids, esters, functional groups, aromatics, NCERT organic topics.

**Optional dependency:** RDKit may be unavailable on Streamlit Cloud — degrade to curated structure images from Knowledge Layer; never invent structures via LLM.

---

## 11. Biology Diagram Extraction Engine

**Do not** recreate biology diagrams with generative AI when NCERT figures exist.

**Pipeline:** PyMuPDF extract figures from NCERT PDFs → store topic, chapter, figure number, caption, alt text, keywords → `st.image()`.

Respect licensing; only reuse where permitted.

---

## 12. NCERT Content Ingestion (Knowledge Layer)

**Input:** NCERT PDFs  

**Extract:** Text, tables, figures, captions, page numbers, chapter, topic, learning objectives, keywords  

**Store:** Separate collections (text chunks, figures, tables) with stable ids and hashes.

---

## 13. Question Bank Architecture

**Sources:** NCERT Exemplar, CBSE previous years, sample papers, competency questions  

**Store:** ChromaDB (vectors) + structured metadata DB  

**Tags:** Subject, grade, chapter, topic, difficulty, Bloom, learning objective, question type, marks, year, board, **official answer**, explanation  

**Rule:** Never generate official answers with an LLM when an official answer exists.

---

## 14. Answer Routing Engine

Implemented as part of Subject Tool Router (`engines/router.py`) using question-type classifiers (rules + optional light ML). STEM computational types → Computation; keyed items → Knowledge; open explanation → Teaching + RAG.

---

## 15. RAG Integration Workflow

```
User question
  → Retrieve NCERT chunks
  → Retrieve Exemplar / CBSE items
  → Retrieve diagrams
  → Provide cited context to LLM
  → Generate explanation only
  → Cite source chapter / figure ids
```

**The LLM must never answer curriculum content from parametric memory alone.**

---

## 16. Learning Style Adaptation Layer (Teaching)

**Only after** deterministic + knowledge outputs exist.

Versions (presentation only): Standard, LD, Dyslexia, Dysgraphia, Dyscalculia, ADHD, Autism, Executive Function, Visual, Auditory, ELL, Gifted, Parent, Teacher, Exam Revision.

**Never alter scientific facts** — inject `EngineResult` / official answers unchanged into each version.

Maps to existing Alora `adaptation_specs` / nine tracks; extend profiles as listed.

---

## 17. Visualization Pipeline (priority)

1. Original NCERT diagram (Knowledge)  
2. GeoGebra  
3. Matplotlib  
4. Schemdraw  
5. RDKit  
6. AI educational illustration **only if** no deterministic/curated visual exists (flagged `unverified_visual`)

---

## 18. Quality Assurance Pipeline

Validate every lesson before ready/publish:

| Check | Layer |
|-------|--------|
| Mathematical correctness | Computation |
| Chemistry balancing | Computation |
| Formula rendering | Computation |
| Diagram availability | Knowledge / Computation |
| Accessibility / reading level / WCAG | Teaching + Accessibility engine |
| Source citations | Knowledge |

**Reject** if any hard check fails.

---

## 19. Streamlit Integration Plan

| Need | Widget |
|------|--------|
| Graphs | `st.pyplot` |
| Images / molecules / NCERT figs | `st.image` |
| Math / chemistry | `st.latex` |
| GeoGebra | `st.components.v1.iframe` |
| Tables | `st.dataframe` |
| Structure | `st.expander`, `st.tabs`, `st.columns`, `st.progress` |

Preserve Alora design system (navy/teal/cream, fixed tabs, workspace viewer).

---

## 20. Database / storage updates

| Store | Contents |
|-------|----------|
| SQLite / files (MVP) | Lesson versions, EngineResult JSON, validation reports |
| Figure asset store | NCERT extracts, RDKit PNGs, matplotlib exports |
| ChromaDB | Chunk + question embeddings |
| Audit log | Validation failures, teacher overrides, engine versions |

Suggested tables (logical):

- `engine_artifact(id, engine, input_hash, payload_json, validation_json, created_at)`  
- `ncert_figure(id, book, chapter, figure_no, path, caption, alt_text, keywords)`  
- `question_item(id, metadata…, official_answer, source)`  
- `vlp_package(id, lesson_id, validation, pedagogy_ref, created_at)`  

---

## 21. API specifications (internal Python)

```python
# engines/router.py
def route(task: ToolTask) -> EngineResult: ...

# engines/chemistry/balancer.py
def balance_equation(raw: str) -> EngineResult: ...

# engines/mathematics/solver.py
def solve(expression: str, domain: str | None = None) -> EngineResult: ...

# engines/graphs/plotter.py
def plot_function(expr: str, x_range: tuple[float, float]) -> EngineResult: ...

# knowledge/rag.py
def retrieve(query: str, k: int = 8) -> list[CitedChunk]: ...

# teaching/adaptation.py
def adapt_presentation(vlp: VerifiedLearningPackage, profile: str) -> AdaptationDoc: ...
```

`EngineResult` must include: `exact_payload`, `latex`, `asset_paths`, `validation`, `provenance`, `deterministic=True`.

---

## 22. Deployment strategy

| Phase | Scope |
|-------|--------|
| **MVP+** | Router + SymPy solve + ChemPy/SymPy balance + atom validation + `st.latex` + QA gate hooks in generate path |
| **School pilot** | NCERT ingest subset + Chroma RAG + answer bank for one grade/subject + Matplotlib graphs |
| **Full SCE** | Schemdraw, GeoGebra embeds, RDKit (local/desktop), biology figures, full QA + audit |
| **Cloud** | Optional RDKit; pin `requirements-engines.txt`; cache by `input_hash` |

**Error handling:** Fail closed on STEM validation; surface teacher-friendly errors; log engine + library versions.

**Performance:** Cache artifacts; limit parallel SymPy/ChemPy; lazy-import heavy libs (RDKit).

---

## 23. FINAL DELIVERABLES map

| # | Deliverable | Section |
|---|-------------|---------|
| 1 | Scientific Computing Architecture | §2 |
| 2 | Subject Tool Router | §3 |
| 3 | Mathematics Engine | §4 |
| 4 | Graph Engine | §5 |
| 5 | GeoGebra Integration | §6 |
| 6 | Physics Visualization Engine | §7 |
| 7 | Chemistry Balancing Engine | §8 |
| 8 | Chemical Rendering System | §9 |
| 9 | RDKit Molecular Structure Engine | §10 |
| 10 | Biology Diagram Extraction Engine | §11 |
| 11 | NCERT Ingestion Pipeline | §12 |
| 12 | Question Bank Architecture | §13 |
| 13 | Answer Routing Engine | §14 |
| 14 | RAG Integration Workflow | §15 |
| 15 | Learning Style Adaptation Layer | §16 |
| 16 | Quality Assurance Pipeline | §18 |
| 17 | Streamlit Integration Plan | §19 |
| 18 | Database Updates | §20 |
| 19 | API Specifications | §21 |
| 20 | Deployment Strategy | §22 |
| — | **Three-layer split** | §1 |

---

## 24. Code entry points (scaffold)

| Module | Role |
|--------|------|
| `engines/router.py` | Subject Tool Router |
| `engines/types.py` | Shared result types |
| `engines/chemistry/balancer.py` | Balance + atom check |
| `engines/mathematics/solver.py` | SymPy facade |
| `engines/qa/pipeline.py` | Lesson validation gate |

Wire into `ai_generator.py` only after engines return; prompts must forbid inventing equations when `ENGINE_ARTIFACTS` are present.

---

*Alora AI: Knowledge holds truth · Computation guarantees correctness · Teaching personalizes learning.*
