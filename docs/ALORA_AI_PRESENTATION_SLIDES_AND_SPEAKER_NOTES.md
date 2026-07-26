# Alora AI — Slide Content & Speaker Notes

**Creator:** Leila Jacob  
**Live app:** https://eduadapt-ai.streamlit.app  
**Version:** 2.16.1  

Use **Part 1** text directly on each slide. Use **Part 2** as your one-page speaker script (print or keep on one screen while presenting).

---

# PART 1 — SLIDE-BY-SLIDE CONTENT (put on slides)

---

## SLIDE 1 — Title

**Alora AI**

Built for Learning. Powered by Intelligence.

Leila Jacob  
eduadapt-ai.streamlit.app

---

## SLIDE 2 — The Problem

**The Teacher Time Crisis**

- Teachers spend **2–5 hours** adapting **one lesson** for different learners
- One class may need: dyslexia support, ELL help, visual layouts, auditory scripts, mainstream, exam prep
- Manual differentiation → burnout, inconsistency, and missed learning opportunities
- Many students never receive materials designed for **how they learn**

**95% time saved** · 4 hours → **2 minutes**

---

## SLIDE 3 — The Solution

**What Is Alora AI?**

- Upload **one** PDF or Word lesson
- AI reads and analyses the **full lesson** (all pages, all concepts)
- Generates **9 classroom-ready adaptations** automatically
- Download, print, listen, or assign — each version in its own workspace

**One upload. Nine learner-ready versions. Under two minutes.**

---

## SLIDE 4 — Who It Is For

**Built for Inclusive Classrooms**

| Teachers | Students | Parents | Schools |
|----------|----------|---------|---------|
| Grades 3–11 lesson planning | Materials matched to learning style | Plain-language home version | UDL-aligned, accessibility-first |

---

## SLIDE 5 — How It Works

**Simple 4-Step Workflow**

**1. Upload** — PDF or DOCX lesson file  

**2. Analyse** — Lesson Complexity, Reading Level, and Objectives appear instantly  

**3. Generate** — AI creates all 9 adaptations in parallel  

**4. Teach & Download** — Open each tab, review, print, assign, or listen  

*[Screenshot: Alora AI dashboard with upload area]*

---

## SLIDE 6 — Lesson Analytics (Overview)

**Three Instant Analytics — Before AI Runs**

| Metric | What it tells you |
|--------|-------------------|
| **Lesson Complexity** | How challenging the text is (0–100) |
| **Reading Level** | Estimated grade level (e.g. Grade 6) |
| **Objectives** | How many learning goals appear in the lesson |

*Calculated locally and instantly from your uploaded text — no AI needed for these three numbers.*

---

## SLIDE 7 — Lesson Complexity Explained

**Lesson Complexity Score (0–100)**

**What it is:**  
A measure of how **structurally difficult** the uploaded lesson text is for typical Grades 3–11 students.

**How it is calculated:**  
The app analyses your lesson text using the `textstat` library and combines:
- Average **word length**
- Average **sentence length**
- **Syllables per word**
- **Flesch-Kincaid grade level**

These are weighted into a single score from **0 (easier)** to **100 (harder)**.

**How to use it:**  
Higher score → plan more scaffolding, pre-teach vocabulary, or assign Dyslexia Smart / ELL versions.

*This is an estimate to guide planning — not a formal assessment.*

---

## SLIDE 8 — Reading Level Explained

**Reading Level**

**What it is:**  
A teacher-friendly label showing the **estimated US school grade** needed to read the lesson comfortably.

**How it is calculated:**  
Uses the **Flesch-Kincaid Grade Level** formula on the full extracted lesson text.

**Examples:**  
- "Grade 4" — suitable for typical Year 4 readers  
- "Grade 8" — upper primary / lower secondary demand  
- "College level" — very advanced text (Grade 13+)

**How to use it:**  
Compare to your class age. If the lesson reads at Grade 9 but you teach Grade 6, use Simplified / Dyslexia Smart / ELL adaptations.

---

## SLIDE 9 — Objectives Explained

**Objectives (Count)**

**What it is:**  
An **estimate** of how many distinct learning objectives or instructional goals appear in the uploaded lesson.

**How it is calculated:**  
The app scans the text for:
- Phrases like *"Students will…"*, *"Learning objective"*, *"SWBAT"*, *"Learning outcome"*
- Numbered goals (*"1. Students will explain…"*)
- Bullet lists with action verbs: *explain, describe, identify, compare, analyze, evaluate, create, demonstrate, apply, summarize, predict*

If none are found, it counts sentences containing strong instructional verbs (capped at 8).

**How to use it:**  
Low count → lesson may need clearer goals. High count → rich lesson; ensure all objectives appear across adaptations after generation.

---

## SLIDE 10 — The 9 Adaptations

**Nine Versions — One Lesson**

1. **Vocabulary Support**  
2. **Mainstream Support**  
3. **Dyslexia Smart**  
4. **English Language Support**  
5. **Visual Learner Support**  
6. **Auditory Learner Support**  
7. **Teacher Version**  
8. **Parent Version**  
9. **Exam Worksheet**

Each opens in its **own workspace** — one adaptation at a time, never stacked.

---

## SLIDE 11 — How AI Adapts Each Version

**From Upload to Adaptation**

1. **Extract** — Full text from PDF or DOCX  
2. **Analyse** — AI curriculum analyst identifies topic, objectives, key concepts, vocabulary, facts, diagram ideas  
3. **Generate** — Separate AI prompt per tab; each version must be **≥80% different** from Mainstream  
4. **Structure** — 6–10 sections, 80+ words each, concept + study flowcharts, real concept names  
5. **Review** — Teacher checks, downloads, assigns  

*AI supports the teacher — final professional judgement stays with you.*

---

## SLIDE 12 — Vocabulary Support

**Tab 1 — Vocabulary Support**

- **Word Wall** — 12–15 terms with definitions, emoji, child-friendly explanations  
- **Flashcards** — Term on front, meaning on back  
- **Picture Words** — Colour-coded flowchart linking terms to the topic  
- **Say · Spell · Use** — Practice sentences with blanks  
- **Self-Test** — Matching + fill-in-the-blank (Show Answer buttons)  
- **Quick Reference Chart** — Term, definition, synonym, exam tip  

**Best use:** Assign **before** the main lesson so students know key terms for the test.

---

## SLIDE 13 — Mainstream Support

**Tab 2 — Mainstream Support**

- Universal Design for Learning (UDL) lesson sequence  
- **Big Idea** summary  
- **Concept Diagram** + **Study Diagram** (colour-coded flowcharts)  
- Section cards: Introduction → Core concepts → Examples → Practice → Exam Focus → Summary  
- Colour borders: **Green** = intro · **Blue** = information · **Orange** = stories/creativity  

**Best use:** Whole-class teaching baseline; print as the main lesson handout.

---

## SLIDE 14 — Dyslexia Smart

**Tab 3 — Dyslexia Smart**

- Simplified language (approximately **Grade 3–4** reading level)  
- **Luxe coloured cards** with emoji section headers  
- **6–10 bullet points** per section — one idea per bullet, concrete facts  
- Cream background **#FFF9EE** — easier on the eyes than pure white  
- Fonts: **OpenDyslexic**, Atkinson Hyperlegible, Lexend  
- **Reading ruler** + **text size slider** (16–32px) in workspace  

**Best use:** Printed handouts, students with dyslexia, reduced cognitive load, chunked learning.

---

## SLIDE 15 — Visual & Auditory Learner Support

**Tab 5 — Visual Learner Support**
- Heavy use of **Concept** and **Study diagrams**  
- Practice in **Q1 / A1** format (question on one line, answer on the next)  
- Colour-coded Visual Summary key  

**Tab 6 — Auditory Learner Support**
- **Full prose paragraphs** — not bullet lists  
- Listen-and-repeat: *"Say:"* and *"Repeat:"* cues  
- **Adaptive Audio Learning** — AI voice narration (Play / Pause / Resume / Stop)  
- **Auditory Learning Mode** — larger, bolder text while listening  

**Best use:** Visual → diagram-first learners. Auditory → listen-first or read-along stations.

---

## SLIDE 16 — ELL, Teacher, Parent & Exam

| Tab | What students / teachers get |
|-----|------------------------------|
| **English Language Support** | Glossary, sentence frames, cognates, simplified syntax, picture dictionary style content |
| **Teacher Version** | Full lesson + **Answer Key & Marking Guide** (expanded by default) + differentiation notes |
| **Parent Version** | Plain-language summary, how to help at home, conversation starters |
| **Exam Worksheet** | Mock exam Parts A–G: short answer, long answer, diagram question, vocabulary, checklist, teacher marking guide |

**Best use:** ELL for language scaffolding · Teacher for marking · Parent for home · Worksheet before assessments.

---

## SLIDE 17 — Inside the Workspace

**Every Adaptation Workspace Includes**

🔊 **Adaptive Audio Learning** — Voice selector, speed control, highlighted transcript  

📏 **Reading Ruler & Text Size** — Overlay ruler (colour, width, opacity) + font slider  

📊 **Concept Diagram** — Main ideas as a colour-coded flowchart  

🎨 **Study Diagram** — Section flowchart with real concept titles  

📚 **Structured lesson sections** — Coloured cards with full exam-ready content  

⬇️ **Downloads** — Text · Word · HTML · MP3 · or ZIP of all 9 versions  

*[Screenshot: Workspace with audio panel and bottom navigation tabs]*

---

## SLIDE 18 — Brand Colours & Fonts

**Alora AI Design System**

**Brand colours**
| Colour | Hex | Used for |
|--------|-----|----------|
| Deep Navy | #041B4D | Top nav, bottom tabs, titles |
| Teal | #008C95 | Accents, buttons, diagram outlines |
| Electric Cyan | #14D9E5 | Highlights, chips |
| Cream | #FFF9EE | Lesson workspace background |
| Body text | #333333 | Lesson reading text |

**Fonts**
- **Dashboard / UI:** Inter  
- **Lesson workspace:** OpenDyslexic → Atkinson Hyperlegible → Lexend → Verdana  

**Design principle:** Calm, premium, accessibility-first — not cluttered.

---

## SLIDE 19 — Best Way to Use Alora AI

**Teacher Best Practice — 10 Steps**

1. Upload a **complete** lesson (all pages), not a single excerpt  
2. Read **Complexity, Reading Level, Objectives** before generating  
3. Start class with **Vocabulary Support** — pre-teach terms  
4. Teach from **Mainstream Support** for the whole class  
5. Assign **Dyslexia Smart** to students who need chunked bullets + cream layout  
6. Use **Visual** for diagram-first learners; **Auditory** + audio panel for listen-first  
7. Send **Parent Version** home the night before a test  
8. Use **Exam Worksheet** as mock practice; mark with **Teacher Version** answer key  
9. Download **Word or HTML** to edit before printing if needed  
10. After app updates: **Reboot Streamlit Cloud app** + hard refresh browser (Ctrl+Shift+R)

---

## SLIDE 20 — FAQ

**Questions Users Ask**

**Do I need an OpenAI API key?**  
Yes — sidebar or `.env` locally; Streamlit Secrets on Cloud.

**How long does generation take?**  
About 1–2 minutes for all 9 versions.

**Can I edit the output?**  
Yes — download Word or HTML and edit freely.

**Are analytics official reading tests?**  
No — they are **estimates** from readability formulas to guide you.

**What files can I upload?**  
PDF and DOCX (Word).

**Why is my version number old on the website?**  
Reboot the app on Streamlit Cloud and hard-refresh your browser.

**Is the content always accurate?**  
AI-generated — **always review** before teaching, especially science and history facts.

---

## SLIDE 21 — Impact & Close

**Why Alora AI Matters**

**95%** time saved  
**9** learner-ready versions  
**~2 min** to generate  

*"Every learner deserves a learning experience designed for them."*

**Try it:** eduadapt-ai.streamlit.app  
**Code:** github.com/jacobleila2021/eduadapt-ai  

**Thank you — Leila Jacob**

---

---

# PART 2 — ONE-PAGE SPEAKER NOTES

*Print this page. Aim for 8–10 minutes total. Demo live on eduadapt-ai.streamlit.app if possible.*

---

**OPEN (Slides 1–3, ~1 min)**  
Introduce yourself and Alora AI. Core message: teachers spend hours differentiating one lesson; Alora AI does it in about two minutes from a single upload. Tagline: *Built for Learning. Powered by Intelligence.* Mention live URL for judges.

**PROBLEM & AUDIENCE (Slides 2–4, ~1 min)**  
Stress pain point: 2–5 hours per lesson manually. Name learner types — dyslexia, ELL, visual, auditory, mainstream, exam prep. Audience: Grades 3–11 teachers, students, parents, inclusive schools.

**WORKFLOW (Slide 5, ~30 sec)**  
Walk through four steps: Upload → Analyse → Generate → Teach/Download. Point to dashboard screenshot if shown.

**ANALYTICS — KEY SLIDE (Slides 6–9, ~2 min)**  
*Expect questions here.* Explain all three are **instant local estimates** before AI runs — not formal tests.

- **Complexity (0–100):** Blend of word length, sentence length, syllables, Flesch-Kincaid. Higher = harder text. Use to decide scaffolding.
- **Reading Level:** Flesch-Kincaid grade label (e.g. Grade 6). Compare to your class age.
- **Objectives:** Counts "Students will…", SWBAT, numbered goals, instructional verbs. Shows if lesson is goal-rich.

**NINE ADAPTATIONS (Slides 10–16, ~3 min)**  
Briefly name all nine. Highlight differences: **Vocabulary** = pre-teach terms. **Mainstream** = UDL whole class. **Dyslexia Smart** = bullets, cream, OpenDyslexic, reading ruler. **Visual** = diagrams + Q1/A1 practice. **Auditory** = prose + AI narration + larger text toggle. **Teacher** = answer key. **Parent** = home summary. **Exam Worksheet** = mock paper Parts A–G. Mention each adaptation is ≥80% unique from mainstream and uses **real concept names**, not "Core Concept 1."

**WORKSPACE & DESIGN (Slides 17–18, ~1 min)**  
Show audio panel, reading ruler, flowcharts, downloads. Colours: Navy #041B4D, Teal #008C95, Cream #FFF9EE. Fonts chosen for dyslexia accessibility.

**BEST PRACTICE & FAQ (Slides 19–20, ~1 min)**  
Top tips: complete upload, vocabulary first, teacher reviews AI output, download Word to edit. FAQ: needs API key, 1–2 min generation, PDF/DOCX only, reboot if version stale.

**CLOSE (Slide 21, ~30 sec)**  
95% time saved, 9 versions, 2 minutes. *"Every learner deserves a learning experience designed for them."* Thank judges. Offer to demo live.

**IF ASKED:** Tech = Python, Streamlit, OpenAI GPT-4o-mini, GitHub + Streamlit Cloud. Data = lesson processed for generation; follow school policy. Accuracy = teacher must review AI content. Not a replacement for professional judgement — a time-saving differentiation assistant.

---

*End of speaker notes — one page*
