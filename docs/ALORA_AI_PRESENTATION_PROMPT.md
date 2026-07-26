# Alora AI — PowerPoint Presentation Prompt

**Use this entire document as a single prompt** in Gamma, Canva Magic Design, Microsoft Copilot (PowerPoint), or Google Slides + Gemini.

**Live demo:** https://eduadapt-ai.streamlit.app  
**Creator:** Leila Jacob  
**Version:** 2.16.1

---

## COPY FROM HERE ↓ (paste into your presentation AI tool)

```
Create a professional 18–20 slide presentation for **Alora AI** — an AI-powered inclusive learning platform for teachers (Grades 3–11).

**Audience:** Teachers, judges, school leaders, parents, investors  
**Tone:** Warm, confident, educational, premium EdTech — not salesy  
**Duration:** 8–12 minutes when presented  

---

## BRAND & VISUAL STYLE (apply to every slide)

**App name:** Alora AI  
**Tagline:** Built for Learning. Powered by Intelligence.  
**Secondary tagline (optional):** Upload Once. Teach Every Learner.  
**Creator credit on title/closing slide:** Leila Jacob  

**Colour palette (use consistently):**
| Role | Hex | Use on slides |
|------|-----|----------------|
| Deep Navy | #041B4D | Headers, title backgrounds, footer bars |
| Teal | #008C95 | Buttons, accents, icons, key callouts |
| Electric Cyan | #14D9E5 | Highlights, dividers, stat numbers |
| Bright Aqua | #22F0FF | Thin accent lines only |
| Silver | #C0C0C0 | Subtitles, secondary text |
| White | #FFFFFF | Text on dark backgrounds |
| Cream | #FFF9EE | Light content panels (lesson workspace feel) |
| Body text on light | #333333 | Paragraphs on cream/white |

**Fonts:**
- **Slide titles & app name:** Inter or Plus Jakarta Sans (bold, modern)
- **Body text:** Inter (regular)
- **Accessibility / dyslexia mention slides:** note that lesson workspace uses OpenDyslexic, Atkinson Hyperlegible, Lexend

**Layout rules:**
- Dark navy title slides; cream or white content slides
- Teal accent bar under every title
- One main idea per slide — minimal bullet text
- Include simple icons (book, ear, eye, brain, download, clock)
- Leave space for screenshots on slides marked [SCREENSHOT]

---

## SLIDE-BY-SLIDE CONTENT

### SLIDE 1 — Title
**Title:** Alora AI  
**Subtitle:** Built for Learning. Powered by Intelligence.  
**Footer:** Leila Jacob · eduadapt-ai.streamlit.app  
**Visual:** Navy gradient background, teal accent line, optional logo placeholder

---

### SLIDE 2 — The Problem
**Title:** The Teacher Time Crisis  
**Bullets:**
- Teachers spend **2–5 hours** adapting ONE lesson for different learners
- Dyslexia, ADHD, ELL, visual, auditory, and mainstream needs = multiple versions
- Time pressure → many students never get truly differentiated materials
- Result: burnout, inequality, missed learning opportunities  
**Stat callout:** "95% time saved — 4 hours → 2 minutes"

---

### SLIDE 3 — The Solution
**Title:** What Is Alora AI?  
**Bullets:**
- Upload **one** PDF or Word lesson
- AI analyses the full lesson (all pages, all concepts)
- Generates **9 classroom-ready adaptations** automatically
- Each version is downloadable (Word, HTML, MP3, ZIP)  
**One-liner:** One upload. Nine learner-ready versions. Under two minutes.

---

### SLIDE 4 — Who It Is For
**Title:** Built for Inclusive Classrooms  
**Four columns or icons:**
- **Teachers** Grades 3–11 — lesson planning & differentiation
- **Students** — materials matched to how they learn
- **Parents** — plain-language home support version
- **Schools** — UDL-aligned, accessibility-first design

---

### SLIDE 5 — How It Works (Workflow)
**Title:** Simple 4-Step Workflow  
**Numbered steps (large icons):**
1. **Upload** — PDF or DOCX lesson file
2. **Analyse** — instant lesson analytics appear
3. **Generate** — AI creates 9 adaptations in parallel
4. **Teach & Download** — open each tab, listen, print, assign  
[SCREENSHOT: Dashboard with upload area]

---

### SLIDE 6 — Lesson Analytics Explained
**Title:** What Do the Three Analytics Mean?  
**Three cards:**

**Lesson Complexity (0–100)**
- Measures how challenging the uploaded lesson text is
- Based on: average word length, sentence length, syllables per word, and Flesch-Kincaid grade level
- **Higher score = harder lesson** for typical Grades 3–11
- Helps teachers decide how much scaffolding students may need

**Reading Level**
- Shows estimated US grade level (e.g. "Grade 6") or "College level"
- Calculated using the **Flesch-Kincaid Grade Level** formula on the full lesson text
- Tells teachers the reading demand before adaptations are made

**Objectives (count)**
- Estimates how many learning objectives appear in the lesson
- Scans for phrases like "Students will…", "Learning objective", "SWBAT", numbered goals, and instructional verbs (explain, describe, analyze, compare…)
- Minimum count of 1 if lesson text exists
- Helps teachers see if the lesson is goal-rich or needs clearer objectives

**Footer note:** Analytics run **locally and instantly** on your device — before AI generation — using the `textstat` library. They are estimates, not official curriculum standards.

---

### SLIDE 7 — The 9 Adaptations Overview
**Title:** Nine Versions — One Lesson  
**Grid (3×3):**
1. Vocabulary Support
2. Mainstream Support
3. Dyslexia Smart
4. English Language Support
5. Visual Learner Support
6. Auditory Learner Support
7. Teacher Version
8. Parent Version
9. Exam Worksheet  
**Note:** Each opens in its own workspace — one at a time, never stacked.

---

### SLIDE 8 — How AI Adapts (Behind the Scenes)
**Title:** How Each Adaptation Is Created  
**Flow diagram text:**
1. Full lesson text extracted (PDF/DOCX)
2. AI curriculum analyst breaks lesson into: topic, objectives, key concepts, vocabulary, facts, diagram ideas
3. Separate AI prompt per adaptation type (each must be ≥80% different from mainstream)
4. Each lesson version: 6–10 sections, 80+ words per section, concept diagrams, study flowcharts
5. Teacher reviews, downloads, assigns  
**Important:** Adaptations use **real concept names** — never generic "Core Concept 1" labels.

---

### SLIDE 9 — Vocabulary Support
**Title:** Tab 1 — Vocabulary Support  
**Bullets:**
- Word Wall with definitions, emoji, child-friendly explanations
- Flashcards (term → meaning)
- Picture Words → colour-coded **Mermaid flowchart** (not external images)
- Say · Spell · Use practice sentences
- Self-test: matching + fill-in-the-blank with Show Answer
- Quick reference chart for exam revision  
**Best for:** Pre-teaching terms before the main lesson

---

### SLIDE 10 — Mainstream Support
**Title:** Tab 2 — Mainstream Support  
**Bullets:**
- Universal Design for Learning (UDL) sequence
- Big Idea → Concept Diagram → Study Diagram → section cards
- Full exam-ready content: introduction, concepts, examples, practice, exam focus, summary
- Colour-coded section borders (green intro, blue information, orange stories)  
**Best for:** Whole-class baseline instruction

---

### SLIDE 11 — Dyslexia Smart
**Title:** Tab 3 — Dyslexia Smart  
**Bullets:**
- Simplified language (Grade 3–4 reading level)
- **Luxe coloured cards** with emoji headers
- 6–10 bullet points per section — one idea per bullet
- Cream background (#FFF9EE), OpenDyslexic-friendly fonts
- Reading ruler + text size slider available in workspace  
**Best for:** Dyslexic readers, reduced cognitive load, chunked learning

---

### SLIDE 12 — Visual & Auditory Learners
**Title:** Tabs 5 & 6 — Visual and Auditory Support  

**Visual Learner Support:**
- Heavy diagrams: Concept + Study flowcharts
- Practice in **Q1 / A1 format** (question line, answer line)
- Colour-coded visual summary key

**Auditory Learner Support:**
- Full prose paragraphs (not bullet lists)
- Listen-and-repeat and "Say / Repeat" cues
- **Adaptive Audio Learning** panel — OpenAI voice narration
- Auditory Learning Mode toggle → larger bold text while listening  
**Best for:** Students who learn by seeing diagrams or hearing content

---

### SLIDE 13 — ELL, Teacher, Parent, Exam
**Title:** Tabs 4, 7, 8 & 9 — Support for Everyone  

| Tab | Purpose |
|-----|---------|
| English Language Support | Glossary, sentence frames, cognates, simplified syntax |
| Teacher Version | Full lesson + **Answer Key & Marking Guide** expander |
| Parent Version | Plain-language summary, home conversation starters |
| Exam Worksheet | Mock exam Parts A–G, student checklist, teacher marking guide |

---

### SLIDE 14 — Workspace Features
**Title:** Inside Each Adaptation Workspace  
**Bullets:**
- 🔊 Adaptive Audio Learning (Play / Pause / Resume / Stop, voice + speed)
- 📏 Reading Ruler & Text Size (overlay ruler, font 16–32px)
- 📊 Concept Diagram + Study Diagram (colour-coded flowcharts)
- 📚 Structured lesson sections with coloured cards
- ⬇️ Downloads: Text, Word, HTML, MP3 — or ZIP of all versions  
[SCREENSHOT: Workspace with audio panel and bottom tabs]

---

### SLIDE 15 — Best Way to Use Alora AI
**Title:** Teacher Best Practice Guide  
**Numbered tips:**
1. Upload a **complete** lesson (not just one page) for best results
2. Check **analytics** first — complexity and reading level guide your expectations
3. Start with **Vocabulary Support** — students learn terms before content
4. Use **Mainstream** for whole class, then assign specific tabs to groups
5. Turn on **Auditory Mode** for listen-first students
6. Use **Dyslexia Smart** for printed handouts with bullets and cream background
7. Give **Exam Worksheet** before tests; use **Teacher Version** for marking
8. Send **Parent Version** home for family conversations
9. After updates on Streamlit Cloud: **Reboot app + hard refresh** if version looks old
10. **Regenerate** (Clear Session → Generate) after major app updates for new formatting

---

### SLIDE 16 — Accessibility & Design Philosophy
**Title:** Accessibility First  
**Bullets:**
- Dyslexia-friendly font stack: OpenDyslexic, Atkinson Hyperlegible, Lexend
- Cream workspace reduces visual stress vs pure white
- Reading ruler follows mouse for line-by-line tracking
- Adjustable text size without breaking layout
- Bold coloured flowchart outlines — readable for children with dyslexia
- WCAG-oriented contrast on navy/teal brand palette

---

### SLIDE 17 — Technology Stack
**Title:** How It Is Built  
**Two columns:**

**Platform:**
- Python + Streamlit (web app)
- OpenAI GPT-4o-mini (JSON structured generation)
- Deployed: Streamlit Cloud + GitHub

**Processing:**
- PDF/DOCX text extraction (pypdf, python-docx)
- Local analytics (textstat)
- Mermaid flowcharts for diagrams
- OpenAI TTS for audio narration

**Links:**
- Live: eduadapt-ai.streamlit.app
- Code: github.com/jacobleila2021/eduadapt-ai

---

### SLIDE 18 — FAQ (Questions Users Always Ask)
**Title:** Frequently Asked Questions  

**Q: Do I need an OpenAI API key?**  
A: Yes. Add it in the sidebar or `.env` file locally; use Streamlit Secrets on Cloud.

**Q: How long does generation take?**  
A: About 1–2 minutes for all 9 versions (depends on lesson length and API speed).

**Q: Is student data stored?**  
A: Lesson content is processed for generation; check your school's data policy for uploads.

**Q: Can I edit the generated lessons?**  
A: Yes — download Word or HTML and edit before printing.

**Q: Why do I see an old version number?**  
A: Reboot the Streamlit Cloud app and hard-refresh your browser (Ctrl+Shift+R).

**Q: Are the analytics the same as official reading levels?**  
A: No — they are **estimates** from readability formulas to guide teachers, not formal assessments.

**Q: What file types can I upload?**  
A: PDF and DOCX (Word).

**Q: Does it work on phone?**  
A: Yes in browser, but desktop is best for uploading and reviewing all tabs.

---

### SLIDE 19 — Impact
**Title:** Why Alora AI Matters  
**Three stats (large teal numbers):**
- **95%** time saved vs manual differentiation
- **9** learner-ready versions from 1 upload
- **2 min** typical generation time  
**Quote:** "Every learner deserves a learning experience designed for them."

---

### SLIDE 20 — Thank You / Call to Action
**Title:** Alora AI  
**Subtitle:** Built for Learning. Powered by Intelligence.  
**Bullets:**
- Try it live: eduadapt-ai.streamlit.app
- View source: github.com/jacobleila2021/eduadapt-ai
- Created by Leila Jacob  
**Visual:** Navy background, teal CTA button graphic "Upload Once. Teach Every Learner."

---

## SPEAKER NOTES (add to presenter notes in PowerPoint)

- Emphasise **inclusion** — this is not just summarisation, it is measurable differentiation
- Demo live if possible: upload sample lesson → show analytics → open Dyslexia Smart + Audio
- Mention **Teacher Answer Key** — important for judges assessing educational rigour
- If asked about accuracy: AI content should always be teacher-reviewed before class
- Complexity/reading level/objectives are **pre-generation estimates** — explain formulas briefly if asked

---

Generate the full slide deck now. Use the exact hex colours listed. Keep text large and readable. Add [SCREENSHOT] placeholders where indicated. Export as PowerPoint (.pptx) if possible.
```

---

## END OF PROMPT ↑

---

## Best tool to create this presentation

| Tool | Best if you… | How to use |
|------|----------------|------------|
| **Gamma.app** (Recommended) | Want fastest prompt → beautiful deck | Paste prompt at gamma.app → Generate → Export PPT or PDF |
| **Canva** (Magic Design) | Want easy editing + brand colours | Canva → Presentation → Magic Design → paste prompt |
| **PowerPoint + Copilot** | Already have Microsoft 365 | New presentation → Copilot → "Create from prompt" → paste |
| **Google Slides + Gemini** | Want free + cloud save | Slides → Gemini sidebar → paste prompt |

**Recommendation for you:** Start with **Gamma.app** or **Canva** — paste the prompt above, then tweak colours to `#041B4D` and `#008C95`. Export to PowerPoint if judges need `.pptx`.

**For judge submission:** Export PDF + keep `.pptx` editable copy.
