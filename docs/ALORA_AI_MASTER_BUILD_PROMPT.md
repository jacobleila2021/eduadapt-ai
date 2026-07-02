# Alora AI (EduAdapt AI) — Master Build Prompt Archive

**Version:** 2.16.1 (matches `version.py` as of June 2026)  
**Creator:** Leila Jacob  
**Repository:** https://github.com/jacobleila2021/eduadapt-ai  
**Live app:** https://eduadapt-ai.streamlit.app  
**Local app folder:** `C:\Users\SPECTRE\Desktop\eduadapt-ai`  
**Safe backup copy:** `C:\Users\SPECTRE\Desktop\EduAdapt Folder\ALORA_AI_MASTER_BUILD_PROMPT.md`

---

## How to use this document

1. **Rebuild from scratch:** Copy **Section A — THE MASTER PROMPT** into Cursor (or any AI coding agent) as one message. Add your OpenAI API key when prompted.
2. **Reference only:** Use Sections B–F for individual AI prompts, design tokens, and file architecture.
3. **Do not commit API keys.** Store keys in `.env` locally and Streamlit Cloud Secrets only.

---

# SECTION A — THE MASTER PROMPT (copy everything below this line)

```
Build a complete production-ready Streamlit application called **Alora AI** (also known as EduAdapt AI).

## PROJECT PURPOSE

Teachers spend 2–5 hours adapting one lesson for students with different learning needs.
Alora AI reduces this to under 2 minutes by generating nine classroom-ready differentiated versions from one PDF/DOCX upload.

## BRAND

- **App name (UI):** Alora AI
- **Tagline:** Built for Learning. Powered by Intelligence.
- **Legacy tagline:** Upload Once. Teach Every Learner.
- **Creator credit:** Leila Jacob (sidebar)
- **Target users:** Teachers, Grades 3–11

## COLOUR PALETTE (do not use Streamlit [theme] override — breaks landing page)

| Token | Hex | Usage |
|-------|-----|--------|
| Deep Navy | #041B4D | Top nav, bottom tabs, hero gradient |
| Teal | #008C95 | Accents, borders, active elements |
| Electric Cyan | #14D9E5 | Highlights, chips |
| Bright Aqua | #22F0FF | Nav accent line |
| Cream (workspace) | #FFF9EE | Dyslexia-friendly lesson background |
| Body text | #333333 | Lesson content |
| Border subtle | #E8E0CF | Cards |

**Landing dashboard:** Navy gradient hero (`.dashboard-hero`), white workspace cards — NOT plain white full-page background.

## CORE WORKFLOW

1. Teacher uploads PDF or DOCX lesson on dashboard.
2. Extract all text (`document_parser.py`).
3. Show analytics: complexity score, reading level, objective count (`analytics_engine.py`).
4. Send lesson to OpenAI GPT-4o-mini with structured JSON prompts.
5. Generate **9 outputs** in parallel (max 4 concurrent):
   - Vocabulary Support
   - Mainstream Support
   - Dyslexia Smart (ld)
   - English Language Support (ELL)
   - Visual Learner Support
   - Auditory Learner Support
   - Teacher Version
   - Parent Version
   - Exam Worksheet
6. Open each version in a dedicated **workspace viewer** (one adaptation at a time).
7. Provide downloads: TXT, Word, HTML, MP3 (TTS), ZIP bundle.

## NINE BOTTOM TABS (fixed navy bar at page bottom)

Exactly these 9 tabs — one spec each, no sub-pills:

1. Vocabulary Support → `vocabulary`
2. Mainstream Support → `standard`
3. Dyslexia Smart → `ld` (renamed from Neurodiversity Support)
4. English Language Support → `ell`
5. Visual Learner Support → `visual`
6. Auditory Learner Support → `auditory`
7. Teacher Version → `teacher`
8. Parent Version → `parent`
9. Exam Worksheet → `worksheet`

## WORKSPACE VIEWER (per adaptation)

Order inside viewer (`viewer_page.py`):

1. **Adaptive Audio Learning** — OpenAI TTS with Play/Pause/Resume/Stop, voice selector, speed control, highlighted transcript.
2. **Auditory Learning Mode toggle** — OFF by default (18px normal text). ON: 28px bold lesson text + 30px bold transcript.
3. **Reading Ruler & Text Size** (`accessibility.py`) — expander titled "📏 Reading Ruler & Text Size" (NOT wheelchair emoji). Ruler colour/width/height/opacity + font slider 16–32px. JS syncs to parent page every 350ms.
4. **Lesson panel** with structured renderers.

## LESSON STRUCTURE (all lesson adaptations)

Each generated lesson JSON object:

```json
{
  "big_idea": "...",
  "mermaid_diagram": "flowchart TD ...",
  "svg_diagram": "<svg ...>",
  "sections": [
    {"title": "Real Concept Name", "body": "80+ words", "box": "teal|blue|green|orange"}
  ],
  "visual_summary": [
    {"icon": "🟦", "color_name": "Topic", "idea": "...", "hex": "#334155"}
  ]
}
```

**Rules:**
- 6–10 sections minimum; validator requires ≥6.
- NEVER use generic titles like "Core Concept 1" — use real concept names (e.g. "Meristematic Tissue").
- Each section body: minimum 80 words, exam-ready content.
- Cover EVERY concept from source lesson; add extra sections if needed.

## ADAPTATION-SPECIFIC FORMATTING

### Dyslexia Smart (`ld`)
- Rich luxe gradient cards with emoji headers (`dyslexia_luxe_section_card_html`).
- Bullet points only: 6–10 substantive bullets per section, **bold** key terms.
- OpenDyslexic / Atkinson Hyperlegible font stack.

### Auditory Learner (`auditory`)
- Full prose paragraphs — NO bullet lists.
- Listen-and-repeat / "Say:" / "Repeat:" call-and-response lines.
- 80+ words per section.

### Visual Learner (`visual`)
- Practice section format:
  ```
  Q1. [question]
  A1. [answer]
  Q2. [question]
  A2. [answer]
  ```
- Render with numbered Q on one line, A on next line (`format_visual_practice_html`).

### Teacher Version (`teacher`)
- Include `answer_key` array (minimum 8 entries), `teacher_notes`, `differentiation_map`.
- Render "Teacher Answer Key & Marking Guide" expander at bottom.

## DIAGRAMS

1. **Concept Diagram** — Mermaid flowchart (colour-coded, 3px bold outlines, OpenDyslexic font, nodeSpacing 65, rankSpacing 85).
2. **Study Diagram** — Vertical section flowchart with real concept titles only (no title+fact cramming).
3. **Vocabulary Picture Words** — Mermaid flowchart (not AI images; `IMAGE_PROVIDER=off` default).
4. Use `flowchart_builder.py`, `study_diagram_builder.py`, `content_renderer.py` (Mermaid 10.6.1, `mermaid.run()`).

## VOCABULARY TAB

Sections: Word Wall → Flashcards → Picture Words (flowchart) → Say·Spell·Use → Self-Test (matching + fill blanks with Show Answer) → Quick Reference → Concept Map.

Fill-blank answers stored in `fill_blank_answers` parallel array — never inline in displayed sentences.

## EXAM WORKSHEET TAB

Parts A–E student-facing; Parts F–G teacher (differentiation map + answer key). Per-question Show Answer buttons. Pale yellow exam answer styling.

## DESIGN SYSTEM

- All CSS via `styles.get_custom_css()` and `lesson_design.get_workspace_css_fragment()` — NO inline `<style>` in `st.markdown`.
- Premium fixed top nav with logo, "Alora AI", version badge, eduadapt-ai.streamlit.app.
- Bottom adaptation tabs: deep navy `#041B4D`, active tab navy highlight (not bright blue).
- Section cards: cream background, 6px coloured accent border (green intro, blue info, orange stories).
- Big Idea appears AFTER Concept + Study diagrams (not before).

## SIDEBAR

Show:
- Multimodal Learning / Adaptive Learning / AI Powered blocks
- Version: v{APP_VERSION}
- Build ID
- Creator: Leila Jacob
- Time Saved metrics (4 hours manual → 2 minutes = 95%)

## API KEY HANDLING

- `.env` file with `OPENAI_API_KEY=sk-...`
- Sidebar paste + "Save to .env" button
- Streamlit Cloud Secrets for production
- `secrets_helper.py` + `get_effective_api_key()` — never commit keys

## TECH STACK

- Python 3.10+
- Streamlit ≥1.33
- OpenAI GPT-4o-mini (JSON mode)
- pypdf, python-docx, textstat, httpx, lxml

## FILE ARCHITECTURE (modular)

```
app.py                  # Main entry, dashboard + routing
config.py               # Colours, APP_NAME, constants
version.py              # APP_VERSION, BUILD_ID
ai_generator.py         # OpenAI prompts + parallel generation
adaptation_specs.py     # 9 spec definitions + format rules
navigation.py           # PILL_CATEGORIES (9 tabs)
lesson_processor.py     # Lesson analysis context
structured_renderers.py # Vocabulary, lesson, worksheet UI
viewer_page.py          # Workspace viewer
workspace_page.py       # Bottom tabs + workspace wrapper
audio_learning.py       # TTS + transcript player
accessibility.py        # Reading ruler + font size
lesson_design.py        # Dyslexia design tokens + section cards
flowchart_builder.py    # Mermaid generation
study_diagram_builder.py# SVG study diagrams
section_titles.py       # Normalise "Core Concept 1" → real names
content_renderer.py     # Mermaid iframe renderer
styles.py               # Premium CSS
ui_helpers.py           # Top nav, sidebar, dashboard hero
document_parser.py      # PDF/DOCX extraction
analytics_engine.py     # Complexity, reading level
docx_exporter.py        # Word export with answer keys
html_exporter.py        # Print HTML
print_exporter.py       # Combined print pack
session_state.py        # Workspace open/close
run.bat                 # One-click local launcher
requirements.txt
.streamlit/config.toml  # NO [theme] block
samples/sample_lesson.docx
test_ux_fixes.py        # Smoke tests
```

## CODE REQUIREMENTS

- Beginner-friendly, commented functions
- Modular imports — no monolithic single file
- Environment variables for secrets
- `test_ux_fixes.py` smoke tests
- Differentiation validation: adaptations must be ≥80% different from standard (`_adaptation_difference_score`)

## DEPLOYMENT

- GitHub: `jacobleila2021/eduadapt-ai`, branch `main`, entry `app.py`
- Streamlit Cloud: https://eduadapt-ai.streamlit.app
- After push: Reboot app + hard refresh (Ctrl+Shift+R)
- Do NOT add `[theme] base = "light"` to config.toml — it turns landing page white

## DOWNLOADS (every adaptation)

- This version: TXT, Word, HTML, MP3
- All versions: ZIP (HTML + Word per tab) + plain text bundle

Implement the complete application exactly as specified. Comment all major functions. Include `run.bat` and sample lesson for testing.
```

---

# SECTION B — ORIGINAL CREATION PROMPT (June 2026)

This is the exact first prompt used to create EduAdapt AI:

```
Build a complete production-ready Streamlit application called EduAdapt AI.

PROJECT PURPOSE
Teachers spend 2-5 hours adapting one lesson for students with different learning needs.
EduAdapt AI should reduce this to under 2 minutes.

TAGLINE: Upload Once. Teach Every Learner.

TARGET USERS: Teachers from Grades 3-11.

CORE WORKFLOW
1. Teacher uploads a PDF or DOCX lesson.
2. Extract all text.
3. Show original lesson.
4. Send lesson to OpenAI GPT.
5. Generate:
   A. Dyslexia-Friendly Version
   B. ADHD-Friendly Version
   C. Simplified Version
   D. Advanced Learner Version
   E. English Language Learner Version
   F. Three Interactive Classroom Activities
   G. Teacher Differentiation Notes

OUTPUT DESIGN: Create separate tabs for each version.

SIDEBAR: Time Saved — Manual 4 Hours, EduAdapt 2 Minutes, 95% saved.

ANALYTICS: Lesson Complexity Score, Reading Level, Learning Objectives count.

DESIGN: Modern EdTech. Colors: Dark Blue #0B2E59, Teal #008C95, Silver #C0C0C0, White.
Use cards and clean typography. Download buttons for every output.

CODE: Beginner friendly, comment functions, modular, .env for API key, requirements.txt.
```

---

# SECTION C — EVOLUTION PROMPTS (feature requests that shaped v2.16.1)

Apply these **in order** when rebuilding or extending the app.

### C1 — Rebrand to Alora AI + premium UI
- Rename display to **Alora AI**, tagline **Built for Learning. Powered by Intelligence.**
- Premium fixed top nav (navy gradient, ~135px height, logo left, centred brand, version + URL right).
- Dashboard hero navy gradient — not flat white page.
- Bottom fixed adaptation tab bar (3 rows of pills on mobile, navy background).

### C2 — Nine generated adaptations (not seven)
Replace original 7 outputs with 9 workspace tabs listed in Section A.

### C3 — Dedicated workspace viewer
- One adaptation opens full-screen workspace (not stacked on dashboard).
- Audio panel at top, lesson body below, tabs at bottom.
- Back to Dashboard button.

### C4 — Dyslexia-friendly lesson design
- Cream `#FFF9EE` workspace background.
- OpenDyslexic + Atkinson Hyperlegible font stack.
- Coloured section cards: introduction (green), information (blue), stories (orange).
- Reading ruler + text size toolbar.

### C5 — Adaptive Audio Learning
- OpenAI TTS (multiple voices), browser fallback.
- Sticky audio toolbar, sentence highlighting, resume from last position.
- Auditory Learning Mode toggle with visible text size change.

### C6 — Structured JSON rendering (not raw HTML in markdown)
- `structured_renderers.py` for vocabulary, lessons, worksheets.
- Native Streamlit UI for word wall, flashcards, self-test with Show Answer.

### C7 — Flowcharts replace AI images
- Mermaid 10.6.1 via CDN, `mermaid.run()` not startOnLoad.
- Bold 3px coloured node outlines, dyslexia-friendly fonts, dynamic iframe height.
- Title-only nodes — no cramming title + fact in one box.
- `IMAGE_PROVIDER=off` default for Picture Words.

### C8 — Rename Neurodiversity → Dyslexia Smart
- Tab label and spec title: **Dyslexia Smart** (spec id stays `ld`).

### C9 — Content depth + inspection readiness (v2.14–v2.16)
- Minimum 6 sections per lesson; complete exam-ready content.
- Real concept names in section titles and study diagrams.
- Dyslexia Smart: luxe bullet cards, 6–10 bullets per section.
- Auditory: revert bullets → full prose paragraphs.
- Visual: Q1/A1 practice layout.
- Teacher: answer_key expander with marking guide.
- Fill-blank semantic answers (not index-based).
- Exam worksheet blank header fields for student name/date.

### C10 — Deploy + version display
- `version.py` with `APP_VERSION` and `BUILD_ID`.
- Show version in top nav and sidebar.
- Push to GitHub → Streamlit Cloud auto-deploy → manual Reboot if stale.
- Never add Streamlit `[theme]` to config.toml.

---

# SECTION D — OPENAI PROMPT CONSTANTS (from `ai_generator.py`)

## DEPTH_RULES
```
- Cover EVERY learning objective and key concept from the lesson analysis.
- Do NOT compress a long lesson into one page. Each lesson adaptation needs 6–10 sections.
- Each section body: minimum 80 words with concrete facts, examples, and steps.
- Students must be able to pass an exam using ONLY this material.
- Include worked examples where the subject requires them.
- DIAGRAM-FIRST: every adaptation MUST include mermaid_diagram AND svg_diagram.
- MERMAID: flowchart/mindmap of the whole lesson process (4+ labelled nodes).
- SVG STUDY DIAGRAM: valid inline SVG, width 720+, height 400+, 6+ <text> labels naming REAL lesson parts. Navy #0B2E59 and teal #008C95.
- SECTION TITLES in sections[] MUST match svg_diagram labels.
- ACCURACY: all facts scientifically and historically correct.
- Each learner version must be MEASURABLY DIFFERENT (≥80% unique from standard).
```

## DIFFERENTIATION_RULES
```
- Visual Learner: 2+ diagrams, minimal prose, icon labels, color-coded stages.
- Auditory Learner: full prose paragraphs (80+ words), listen-and-repeat — NOT bullet lists.
- Dyslexia Smart: simplified vocabulary (Grade 3-4), rich coloured bullet sections, 6-10 substantive points per section.
```

## SECTION_TITLE_RULES
```
- NEVER use "Core Concept 1", "Core Concept 2", "Section 3", "Topic 1".
- Every title MUST be the REAL concept name from the lesson.
- Short (2-6 words), complete phrases.
```

## Per-adaptation extras
- **ld:** BULLET_SECTION_RULES (6-10 bullets, 80+ words total, **bold** terms)
- **auditory:** AUDITORY_SECTION_RULES (prose only, Say/Repeat cues)
- **visual:** VISUAL_PRACTICE_RULES (Q1/A1 format, 5+ pairs)
- **teacher:** TEACHER_ANSWER_RULES (answer_key, teacher_notes, differentiation_map, 8+ entries)

---

# SECTION E — ADAPTATION SPEC HINTS (from `adaptation_specs.py`)

| ID | Tab | AI Hint Summary |
|----|-----|-----------------|
| vocabulary | Vocabulary Support | Dedicated vocab page, word wall 12-15 terms, self-test |
| standard | Mainstream Support | UDL sequence, diagrams, coloured boxes, practice, mastery |
| ld | Dyslexia Smart | Rich coloured bullets, Grade 3-4 language, complete lesson |
| ell | English Language Support | Glossary, sentence frames, cognates, picture dictionary |
| visual | Visual Learner Support | Heavy diagrams, Q1/A1 practice format |
| auditory | Auditory Learner Support | Full prose, listen-and-repeat, NOT bullets |
| teacher | Teacher Version | Full lesson + answer_key + differentiation map |
| parent | Parent Version | Plain-language home summary, conversation starters |
| worksheet | Exam Worksheet | Mock exam Parts A-G, teacher answer key |

---

# SECTION F — QUICK START (local + cloud)

## Local
```bat
cd C:\Users\SPECTRE\Desktop\eduadapt-ai
run.bat
```
Or double-click `EduAdapt Folder\EduAdapt START HERE.bat`

## API key
Create `.env`:
```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
IMAGE_PROVIDER=off
```

## Streamlit Cloud secrets
```
OPENAI_API_KEY = sk-...
```

## Judge / demo links
- Live: https://eduadapt-ai.streamlit.app
- Repo: https://github.com/jacobleila2021/eduadapt-ai

---

# SECTION G — WHAT NOT TO DO (lessons learned)

1. Do **not** add `[theme] base = "light"` to `.streamlit/config.toml` — breaks navy landing page.
2. Do **not** commit `.env` or API keys to GitHub.
3. Do **not** use wheelchair emoji ♿ for accessibility toolbar — use 📏.
4. Do **not** use generic section titles in AI prompts — causes unreadable study diagrams.
5. Do **not** put bullet lists in Auditory adaptation — use full prose.
6. Do **not** use `components.html` height=0 for accessibility sync — use height≥64.
7. Do **not** inject inline `<style>` via `st.markdown` — use `styles.py` only.
8. Do **not** use invalid Mermaid syntax `(["text"])` or HTML in labels — causes bomb icon error.

---

*Document generated for Leila Jacob / Alora AI (EduAdapt AI).  
Stored alongside application source at `eduadapt-ai/docs/` for safekeeping.*
