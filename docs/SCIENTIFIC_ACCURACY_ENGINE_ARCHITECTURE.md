# Alora AI — Scientific Accuracy Engine Architecture

**Product:** Alora AI (EduAdapt AI / AdaptEd AI)  
**Document:** `SCIENTIFIC_ACCURACY_ENGINE_ARCHITECTURE.md`  
**Status:** Governing architecture for STEM accuracy  
**Principle:** **Verified Knowledge First. AI Explanation Second.**  
**Parent system:** [Verified Learning Engine (VLE)](./VERIFIED_LEARNING_ENGINE_ARCHITECTURE.md) — SAE is the STEM truth layer inside the educational OS

**Audience:** Software engineers, curriculum experts, STEM educators, AI architects, QA

---

## 0. Platform rule

### 0.1 Law

The platform must **never invent**:

| Forbidden for LLM invention | Owner |
|-----------------------------|--------|
| Mathematical answers | Mathematics Intelligence Engine |
| Chemical equations / balancing | Chemistry Intelligence Engine |
| Scientific constants | Verified Constants Bank + engines |
| Formula derivations | Math / Physics engines |
| Molecular structures | Chemistry + RDKit / SVG |
| Unit conversions | Physics / Math unit checker |
| Statistical calculations | Mathematics Intelligence Engine |

### 0.2 Separation of duties

```
┌─────────────────────────────────────────────────────────────┐
│                     LESSON PIPELINE                          │
│  Upload → Parse → Detect STEM claims → ENGINES → Validate   │
│       → AI Teaching Layer (explain/adapt only) → Publish     │
└─────────────────────────────────────────────────────────────┘

  Deterministic engines     = truth (numbers, equations, units, structures)
  LLM                       = pedagogy (language, level, analogy, a11y)
  Validation pipeline       = gate (no publish without PASS)
```

### 0.3 Non-goals

- The LLM is **not** a calculator, balancer, or constant lookup.
- “Looking correct” in prose is **not** sufficient for publish.
- AI-generated imagery must not replace verified molecular / biological diagrams when engine or curated assets exist.

---

## 1. Scientific Accuracy Engine (SAE) — system architecture

### 1.1 Components

| Component | Role |
|-----------|------|
| **Claim Extractor** | Finds equations, formulas, constants, units, reactions in source + draft adaptations |
| **Chemistry Intelligence Engine** | Parse, balance, stoichiometry, periodic data |
| **Mathematics Intelligence Engine** | Symbolic solve, verify, steps, graphs |
| **Physics Intelligence Engine** | Formula + unit + dimensional checks, sims |
| **Biology Visualization Engine** | Curated diagrams, pathways, trees |
| **Diagram Generation Engine** | Code-first educational diagrams |
| **Formula Rendering Engine** | LaTeX / KaTeX / mhchem publication render |
| **Scientific Validation Pipeline** | Gate before publish |
| **AI Teaching Layer** | Explain / adapt only; consumes engine artifacts |
| **QA Framework** | Audit logs, regression, teacher review |

### 1.2 Data contract (shared)

Every engine result is an `EngineArtifact`:

```ts
interface EngineArtifact {
  artifactId: string;
  engineId: 'chemistry' | 'mathematics' | 'physics' | 'biology' | 'diagram' | 'formula';
  inputCanonical: string;      // normalized input
  inputHash: string;           // sha256 of canonical input
  outputPayload: unknown;      // structured result (JSON)
  renderHints: {
    latex?: string;
    mhchem?: string;
    svg?: string;
    mermaid?: string;
  };
  validation: {
    status: 'pass' | 'fail' | 'warn' | 'skipped';
    checks: Array<{ code: string; ok: boolean; detail: string }>;
  };
  provenance: {
    libraryVersions: Record<string, string>;
    computedAt: string;        // ISO
    deterministic: true;
  };
}
```

Adaptations reference artifacts by `artifactId` instead of inventing values.

### 1.3 Recommended package layout

```
alora/
  engines/
    chemistry/          # parser, balancer, stoich, periodic, validation
    mathematics/        # sympy facade, solver, steps, verify
    physics/            # units, dimensional, formulas
    biology/            # assets + pathway builders
    diagrams/           # matplotlib, schemdraw, mermaid, geogebra hooks
    formula/            # latex normalize + katex/mhchem
    validation/         # lesson gate
    constants/          # CODATA / curriculum constant bank
  teaching/
    ai_layer/           # prompts that consume EngineArtifacts only
  qa/
    audit/
    regression/
    teacher_review/
```

**Python stack (engines):** SymPy, NumPy, SciPy, ChemPy, RDKit (optional heavy), matplotlib, schemdraw  
**Render (UI):** KaTeX + mhchem (preferred for Streamlit/web); MathJax fallback; SVG from engines

---

## SECTION 1 — Chemistry Intelligence Engine

### 1.1 Capabilities

| Capability | Method | Library |
|------------|--------|---------|
| Molecular formula validation | Parse + atom count | ChemPy / custom parser |
| Equation balancing | Linear algebra over atom matrix | ChemPy / SymPy |
| Ionic / half-equations | Charge + atom balance | ChemPy + rules |
| Oxidation numbers | Deterministic rules engine | Custom + ChemPy |
| Stoichiometry | Mole ratios from balanced eq | ChemPy |
| Gas laws / molar calcs | Formula registry + SymPy | SymPy |
| Periodic table lookup | Static verified dataset | Curated JSON (IUPAC) |
| Solubility rules | Rule table | Curated |
| Reaction classification | Pattern rules | Curated |

### 1.2 Subsystems

#### A. Chemical equation parser

- Input: free text / mhchem / structured tokens  
- Output: AST `{ reactants[], products[], conditions?, charge? }`  
- Normalize: `H2O` ≡ `H₂O`, strip spaces, reject unknown elements  
- Fail closed on parse error → `validation.fail`

#### B. Balancing engine

1. Build atom (and charge) incidence matrix  
2. Solve null-space / integer coefficients (ChemPy / SymPy)  
3. Prefer smallest positive integers  
4. Emit balanced equation + coefficient vector  

#### C. Formula renderer

- Emit `mhchem` / LaTeX: `\ce{2H2 + O2 -> 2H2O}`  
- Formula Rendering Engine owns display  

#### D. Molecular visualization engine

- Prefer RDKit → SVG/PNG for small molecules  
- Fallback: curated SVG library by InChIKey / formula  
- Never ask LLM to invent bond angles or ring systems  

#### E. Validation pipeline (chemistry)

**Mandatory before publication:**

1. Parse success  
2. **Automatic atom-count validation** (LHS atoms == RHS atoms per element)  
3. Charge balance (if ionic / redox)  
4. Coefficient positivity  
5. Species exist in periodic / known ion table  

```
publish_allowed = atom_balance_ok AND charge_ok AND parse_ok
```

### 1.3 API sketch

```python
def balance_equation(raw: str) -> EngineArtifact: ...
def validate_formula(formula: str) -> EngineArtifact: ...
def stoichiometry(eq: str, given: dict) -> EngineArtifact: ...
def lookup_element(symbol: str) -> EngineArtifact: ...
```

---

## SECTION 2 — Mathematics Intelligence Engine

### 2.1 Support domains

Arithmetic · Algebra · Geometry · Trigonometry · Calculus · Statistics · Probability · Matrices · Coordinate geometry

### 2.2 Subsystems

| Subsystem | Responsibility |
|-----------|----------------|
| **Symbolic mathematics engine** | SymPy expressions, simplify, expand, factor |
| **Equation solver** | Exact/numeric solve; systems; inequalities |
| **Formula verification** | Teacher/source claim vs engine result (identity check) |
| **Step-by-step solution generator** | Engine-driven steps (SymPy rewrite rules / custom pedagogic step tree) — **not** LLM arithmetic |
| **Graph generation pipeline** | NumPy sample + matplotlib / SVG; domain/range validated |

### 2.3 Hard rule

> The AI may explain mathematical concepts but must **never calculate independently**.

Teaching layer receives `EngineArtifact.outputPayload.steps` and may only rephrase wording / reading level.

### 2.4 Verification

- Re-substitute solutions into original equation  
- Tolerance policy for floats (document ε)  
- Symbolic exactness preferred for grades 3–11 curriculum  

---

## SECTION 3 — Physics Intelligence Engine

### 3.1 Domains

Mechanics · Electricity · Magnetism · Waves · Light · Modern physics · Thermodynamics

### 3.2 Capabilities

| Capability | Approach |
|------------|----------|
| Formula validation | Named formula registry (curriculum-aligned) + SymPy |
| Unit checking | pint or custom unit graph |
| Dimensional analysis | Base dimensions must match both sides |
| Graph generation | matplotlib / SVG |
| Simulation support | Deterministic ODE / kinematics (NumPy); seedable |

### 3.3 Constants

Pull from **Verified Constants Bank** (CODATA + curriculum subset). LLM must not emit bare “g = 10” without bank id or teacher override.

---

## SECTION 4 — Biology Visualization Engine

### 4.1 Outputs

- Cell diagrams  
- Biological pathways  
- Classification trees  
- Process diagrams  
- DNA structures  
- Flowcharts  

### 4.2 Policy

- Prefer **verified / curated assets** (SVG library keyed by concept id: `cell.animal.grade7`)  
- Parametric diagrams (labelled templates) over generative images  
- Taxonomy trees from curated hierarchy data  
- LLM may choose **which** diagram template to attach, not invent anatomy  

---

## SECTION 5 — Diagram Generation Engine

### 5.1 Types

Flowcharts · Concept maps · Graphs · Geometry · Circuit diagrams · Molecule structures · Timelines · Process maps

### 5.2 Preferred tools

| Tool | Use |
|------|-----|
| Mermaid | Flow / process (sanitized) |
| matplotlib | Plots, stats, physics graphs |
| schemdraw | Circuits |
| GeoGebra | Geometry (embed / export) |
| SVG generation | Brand-aligned study diagrams |
| RDKit | Molecules |

### 5.3 Design system alignment (Alora / AdaptEd)

Tokens (from product design): Deep Navy `#041B4D`, Teal `#008C95`, Electric Cyan `#14D9E5`, Cream `#FFF9EE`, body `#333333`.

All regenerated diagrams must:

- Use token colours  
- Consistent stroke / font sizes for grade band  
- Accessible contrast  
- Label real concept names (no decorative-only art)

---

## SECTION 6 — Formula Rendering Engine

### 6.1 Support

Math equations · Chemical notation · Physics formulae · Matrices · Fractions · Integrals · Greek symbols

### 6.2 Stack

| Layer | Choice |
|-------|--------|
| Authoring | LaTeX / mhchem strings from engines |
| Web render | **KaTeX** (+ mhchem extension) primary |
| Fallback | MathJax |
| Export | HTML with KaTeX CSS; DOCX via OMML or image fallback |

### 6.3 Quality bar

Publication-quality: no plain-text `H2O` in final student HTML when `\ce{H2O}` is available; matrices and integrals via KaTeX.

---

## SECTION 7 — Scientific Validation Pipeline

### 7.1 Gate checklist (every lesson)

| Check | Engine |
|-------|--------|
| Mathematical calculations | Mathematics |
| Chemical balancing + atom count | Chemistry |
| Formula accuracy | Math / Physics / Chemistry |
| Unit consistency | Physics |
| Variable consistency | Math / Physics |
| Scientific constants | Constants Bank |
| Equation formatting | Formula Renderer |

### 7.2 Publish rule

```
IF any check.status == fail → BLOCK publish
IF any check.status == warn → require teacher acknowledge
IF all pass → allow publish + stamp validation_report_id
```

### 7.3 Report artifact

Store `ValidationReport` with lesson version id, artifact ids, timestamps, library versions — for scientific audit.

---

## SECTION 8 — AI Teaching Layer

### 8.1 Allowed

- Explain concepts  
- Simplify language  
- Generate analogies  
- Adapt reading levels  
- Personalize learning  
- Scaffold instruction  
- Create stories  
- Generate accessibility supports  

### 8.2 Forbidden

- Replacing engines for factual verification  
- Inventing numbers, equations, structures, constants, unit conversions  
- “Fixing” a failed balance by rewriting coefficients without re-running the balancer  

### 8.3 Integration pattern

```
1. Extract STEM claims from source lesson
2. Resolve each claim via engines → EngineArtifacts
3. Prompt LLM with: lesson text + artifacts (as ground truth) + adaptation profile
4. LLM output may reference artifact ids; post-processor injects rendered LaTeX/SVG
5. Re-run Validation Pipeline on final adaptation
```

Prompt invariant (must appear in `ai_generator` system rules):

> Use only the provided ENGINE_ARTIFACTS for numbers, equations, and diagrams. If a needed fact is missing, output NEED_ENGINE:{type}:{request} instead of inventing.

---

## SECTION 9 — Quality Assurance Framework

### 9.1 Pipeline

1. **Automated validation** — SAE gate on every generate / edit  
2. **Teacher review** — UI queue for warns / overrides  
3. **Version control** — lesson content + artifacts + validation report (immutable versions)  
4. **Error reporting** — teacher “flag inaccuracy” → audit ticket  
5. **Regression testing** — golden STEM fixtures (known equations, solves, units)  
6. **Scientific audit logs** — who published, which engine versions, override reason  

### 9.2 Traceability

```
Source document hash
  → Claim set
    → EngineArtifact[] (inputHash, libraryVersions)
      → Adaptation version
        → ValidationReport
          → Publish event
```

Every adapted lesson must be traceable back to verified source + engine provenance.

---

## 10. Deployment recommendations

### Phase A — Foundation (must ship first)

1. Codify rule in product + Cursor rule (done)  
2. Constants Bank (curriculum subset)  
3. Math verify + Chemistry balance + atom-count gate  
4. KaTeX + mhchem in adaptation viewer  
5. Validation report on generate; block “bad” chem/math claims  

### Phase B — Coverage

6. Physics units / dimensional analysis  
7. Diagram engine (matplotlib / schemdraw / Mermaid sanitize)  
8. Biology curated SVG pack (grades 3–11 priority topics)  

### Phase C — Hardening

9. RDKit optional wheel for desktop/local; graceful degrade on Streamlit Cloud  
10. Teacher review UI + audit logs  
11. Golden regression suite in CI  

### Runtime notes

- **Streamlit Cloud:** prefer pure Python (SymPy, ChemPy, NumPy); treat RDKit as optional extra  
- **Local / school server:** full stack including RDKit + schemdraw  
- Cache artifacts by `inputHash` to avoid recompute  
- Pin library versions in `requirements-engines.txt` for reproducibility  

---

## 11. FINAL DELIVERABLES map

| Deliverable | This document section |
|-------------|----------------------|
| Scientific Accuracy Engine Architecture | §0–§1 |
| Chemistry Intelligence Engine | §1 (Section 1) |
| Mathematics Intelligence Engine | §2 |
| Physics Intelligence Engine | §3 |
| Biology Visualization Engine | §4 |
| Diagram Generation Engine | §5 |
| Formula Rendering Engine | §6 |
| Validation Pipeline | §7 |
| AI Teaching Layer Integration | §8 |
| Quality Assurance Framework | §9 |
| Deployment Recommendations | §10 |

---

## 12. Parent platform

This SAE sits under the **Verified Learning Engine (VLE)** — see `VERIFIED_LEARNING_ENGINE_ARCHITECTURE.md`. Curriculum, assessment, accessibility, adaptive pathways, analytics, gamification, and the AI tutor are sibling engines; SAE owns STEM correctness only.

**Curriculum Standards Bank** (board/grade codes) lives primarily in the Curriculum Intelligence Engine and is referenced by SAE for formula/constant/diagram tagging.
