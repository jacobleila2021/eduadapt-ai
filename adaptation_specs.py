"""
AdaptEd AI–aligned adaptation types for EduAdapt AI output tabs.
Product set: nine classroom adaptations (generate=True). Extra Section B
profiles remain registered with generate=False for future opt-in.
"""

# Shared prompt blocks for rich student-facing output
LESSON_VISUAL_FORMAT = """
VISUAL LESSON RULES (for every lesson adaptation in this batch — not vocabulary/worksheet):
Students must SEE the lesson, not only read text. Each lesson version MUST include:
1. Colored HTML "Big Idea" box (teal #008C95 border, light teal background).
2. Color-coded stage labels via HTML (e.g. red=Introduction, blue=Explain, green=Practice, orange=Check).
3. A "Visual Summary" section with a markdown table linking color/icon to each main idea.
The app injects Alora's built coloured Mermaid flowcharts — leave mermaid_diagram and
svg_diagram as empty strings "" unless you can provide a short, Mermaid-10-safe flowchart
with plain text labels only (no HTML in nodes). Do NOT invent complex SVG diagrams.
Use HTML + markdown together. Do NOT use external image URLs.
"""

VOCABULARY_FORMAT = """
VOCABULARY PAGE RULES (key: vocabulary) — separate sections so students can study independently:
Structure EXACTLY with these ## headings in order:

## 1. Word Wall (Study First)
One HTML card per term (10–15 terms). Each card MUST use a different soft background color and include: term (bold), simple definition, emoji icon, and a one-line "Picture in your mind" visual description (like a colorful image caption).

## 2. Flashcards (Term → Meaning)
Numbered list. Format each as:
**Front:** term | **Back:** definition + example from the lesson.

## 3. Picture Words (Visual Flowchart)
One coloured ```mermaid flowchart linking the topic to each key term with short fact labels (no external images).

## 4. Say It · Spell It · Use It
For each term: one numbered fill-in sentence with blank only — no pronunciation or syllable fields.

## 5. Match & Review (Self-Test)
Part A matching (terms numbered, definitions lettered) and at least 6 fill-in-the-blank sentences using ________.
Never put answers in brackets in the displayed sentences — store answers only in fill_blank_answers.

## 6. Quick Reference Chart
Markdown table: Term | Definition | Synonym | Exam Tip.

Include one ```mermaid diagram linking all key terms to the main concept.
"""

WORKSHEET_FORMAT = """
EXAM WORKSHEET RULES (key: worksheet) — student must feel exam-ready:
Structure EXACTLY with these ## headings:

## Exam Paper Header
HTML box: Subject, Topic, Name:____ Date:____ Time Allowed:____ Total Marks:____

## Part A — Short Answer ([2] marks each)
6–8 questions requiring 1–3 sentence answers. After each question add blank answer lines:
_________________________________________________________

## Part B — Long Answer ([5–8] marks each)
3–4 extended-response questions (paragraph/essay). Include mark allocations and lined space indicators.

## Part C — Diagram Question ([4] marks)
One question asking the student to label or sketch a concept (refer to lesson diagram). Include a simple inline SVG outline they can mentally complete.

## Part D — Vocabulary in Context ([1] mark each)
5 questions using vocabulary from the Vocabulary tab in exam-style sentences.

## Part E — Student Exam Ready Checklist
Checkbox list: timing strategy, how many sentences for short vs long answers, words to define first, diagram review tip.

## Part F — Differentiated Assignment Map (Teacher)
Which Part A/B/C/D questions to assign for dyslexia, ADHD, ELL, gifted, executive function — with accommodations.

## Part G — Answer Key & Marking Guide (Teacher)
Model answers, partial credit notes, common mistakes.
"""

# Each spec: id (JSON key), tab (short UI label), title (download header), generate (AI or upload)
# Decided product set (generate=True): vocabulary, standard, ld, ell, visual, auditory, teacher, parent, worksheet
ADAPTATION_SPECS = [
    {
        "id": "original",
        "tab": "Original",
        "title": "Original Lesson Archive",
        "generate": False,
        "hint": "Preserve uploaded lesson verbatim for audit trail.",
    },
    {
        "id": "vocabulary",
        "tab": "Vocabulary Support",
        "title": "Vocabulary Support",
        "generate": True,
        "hint": (
            "Dedicated vocabulary-only page — NOT mixed into the lesson. "
            "Follow VOCABULARY_FORMAT section structure exactly. "
            "Students use this tab alone to familiarise themselves before the exam."
        ),
    },
    {
        "id": "standard",
        "tab": "Mainstream Support",
        "title": "Mainstream Support",
        "generate": True,
        "hint": "UDL sequence with diagrams and colored visual boxes. Hook, context, guided explanation, practice, mastery check. Leave mermaid/svg empty for Alora built flowcharts.",
    },
    {
        "id": "ld",
        "tab": "Dyslexia Smart",
        "title": "Dyslexia Smart",
        "generate": True,
        "hint": "Big idea first, rich coloured layout, simplified language (Grade 3–4), 6–10 bullet points per section with concrete facts. Complete lesson — every concept from source material.",
    },
    {
        "id": "dyslexia",
        "tab": "Dyslexia",
        "title": "Dyslexia Version",
        "generate": False,
        "hint": "Bulleted steps, short sentences, bold key terms, spacing cues. Presentation only — keep ENGINE_ARTIFACTS facts unchanged.",
    },
    {
        "id": "dysgraphia",
        "tab": "Dysgraphia",
        "title": "Dysgraphia Version",
        "generate": False,
        "hint": "Oral options, minimal writing, point-and-label lists, colored boxes. Do not change verified STEM facts.",
    },
    {
        "id": "dyscalculia",
        "tab": "Dyscalculia",
        "title": "Dyscalculia Version",
        "generate": False,
        "hint": "Visual models, step-by-step structure, no timed drills, concrete before abstract. Use ENGINE math steps verbatim.",
    },
    {
        "id": "adhd",
        "tab": "ADHD",
        "title": "ADHD",
        "generate": False,
        "hint": "2-minute colored chunks, numbered steps, checkpoint boxes, movement breaks. Facts unchanged.",
    },
    {
        "id": "autism",
        "tab": "Autism Support",
        "title": "Autism Support",
        "generate": False,
        "hint": "Predictable structure, explicit transitions, calm tone, consistent color coding, literal language. Facts unchanged.",
    },
    {
        "id": "executive",
        "tab": "Executive Function",
        "title": "Executive Function Version",
        "generate": False,
        "hint": "START → NEXT → CHECK → DONE checklist with colored HTML boxes. Facts unchanged.",
    },
    {
        "id": "visual",
        "tab": "Visual Learner Support",
        "title": "Visual Learner Support",
        "generate": True,
        "hint": "Heavy visual layout: colour-coded stages, icon markers. Practice section: Q1/A1 format with each question and answer on separate numbered lines. Leave mermaid/svg empty for built flowcharts.",
    },
    {
        "id": "auditory",
        "tab": "Auditory Learner Support",
        "title": "Auditory Learner Support",
        "generate": True,
        "hint": "Listen-and-repeat script with full prose paragraphs (80+ words per section), call-and-response cues, audio chunk headers. Complete lesson coverage — NOT bullet lists.",
    },
    {
        "id": "ell",
        "tab": "English Language Support",
        "title": "English Language Support",
        "generate": True,
        "hint": "Glossary table, sentence frames, cognates, simplified syntax.",
    },
    {
        "id": "gifted",
        "tab": "Gifted Extension",
        "title": "Gifted Learner Extension Version",
        "generate": False,
        "hint": "Extension questions, deeper analysis, enrichment tasks. Do not invent STEM answers — cite ENGINE_ARTIFACTS / official bank.",
    },
    {
        "id": "parent",
        "tab": "Parent Version",
        "title": "Parent Version",
        "generate": True,
        "hint": "Plain-language home summary, how to help, conversation starters, simple visual overview.",
    },
    {
        "id": "teacher",
        "tab": "Teacher Version",
        "title": "Teacher Version",
        "generate": True,
        "hint": "Full lesson plus teacher answer_key for every practice question, differentiation map, grouping, accommodations, assessment ideas, and marking guide.",
    },
    {
        "id": "tutor",
        "tab": "AI Tutor",
        "title": "AI Tutor Version",
        "generate": False,
        "hint": "Interactive Q&A blocks with hint ladders. Verified facts only.",
    },
    {
        "id": "multisensory",
        "tab": "Multisensory",
        "title": "Multisensory Version",
        "generate": False,
        "hint": "See/Hear/Do/Write with colored activity cards. Facts unchanged.",
    },
    {
        "id": "exam_revision",
        "tab": "Exam Revision",
        "title": "Exam Revision Version",
        "generate": False,
        "hint": (
            "Dedicated exam revision pack: revision summary, key vocabulary, formula sheet from ENGINE_ARTIFACTS, "
            "concept map, flashcards, retrieval practice, timed quiz tips, exam tips, common mistakes, "
            "and official-style questions from EXAM_QUESTION_BANK only (never invent keys)."
        ),
    },
    {
        "id": "worksheet",
        "tab": "Exam Worksheet",
        "title": "Exam Worksheet",
        "generate": True,
        "hint": (
            "Full mock exam paper. Follow WORKSHEET_FORMAT section structure exactly. "
            "Student-facing Parts A–E (Short / Long / Diagram / Vocab / Checklist); "
            "teacher Parts F–G. Must cross-reference vocabulary terms. "
            "Do NOT use vocabulary fill-in-the-blank self-test format for this tab."
        ),
    },
]

# Lesson adaptations among the nine generated product set
LESSON_ADAPTATION_IDS = {
    "standard",
    "ld",
    "visual",
    "auditory",
    "ell",
    "teacher",
    "parent",
}

# Tab labels for st.tabs (derived) — legacy
OUTPUT_TAB_LABELS = [spec["tab"] for spec in ADAPTATION_SPECS]

# Keys sent to / returned from OpenAI
OUTPUT_KEYS = [spec["id"] for spec in ADAPTATION_SPECS if spec["generate"]]
