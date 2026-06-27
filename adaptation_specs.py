"""
AdaptEd AI–aligned adaptation types for EduAdapt AI output tabs.
Matches AdaptEd AI schemas (17 versions) — teacher-facing labels.
"""

# Shared prompt blocks for rich student-facing output
LESSON_VISUAL_FORMAT = """
VISUAL LESSON RULES (for every lesson adaptation in this batch — not vocabulary/worksheet):
Students must SEE the lesson, not only read text. Each lesson version MUST include:
1. Colored HTML "Big Idea" box (teal #008C95 border, light teal background).
2. At least ONE valid ```mermaid code block (flowchart, mindmap, or sequenceDiagram).
3. At least ONE inline colored SVG diagram (<svg width="300" height="200" ...>) labeling key parts in navy #0B2E59 and teal #008C95.
4. Color-coded stage labels via HTML (e.g. red=Introduction, blue=Explain, green=Practice, orange=Check).
5. A "Visual Summary" section with a markdown table linking color/icon to each main idea.
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

## 3. Picture Words (Visual Memory)
Table with columns: Term | Color Cue | What to Draw/Imagine | Label on Diagram.
Describe vivid colored scenes students can sketch (e.g. "blue arrow for evaporation rising").

## 4. Say It · Spell It · Use It
For each term: pronunciation guide, syllable breakdown, and a fill-in sentence with blank.

## 5. Match & Review (Self-Test)
Matching exercise (letters → numbers) and 5 fill-in-the-blank sentences. No answer key in this section.

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
        "hint": "UDL sequence with diagrams and colored visual boxes. Hook, context, SVG diagram, mermaid map, guided explanation, practice, mastery check.",
    },
    {
        "id": "ld",
        "tab": "Neurodiversity Support",
        "title": "Neurodiversity Support",
        "generate": True,
        "hint": "Big idea first, reduced load, colored visual cues, simplified language (Grade 3–4), chunked steps, labeled SVG diagram.",
    },
    {
        "id": "dyslexia",
        "tab": "Dyslexia",
        "title": "Dyslexia Version",
        "generate": False,
        "hint": "Bulleted steps, short sentences, bold key terms, spacing cues, mermaid flowchart, one simple colored SVG.",
    },
    {
        "id": "dysgraphia",
        "tab": "Dysgraphia",
        "title": "Dysgraphia Version",
        "generate": False,
        "hint": "Oral options, minimal writing, point-and-label SVG diagram, drag-label style lists, colored boxes.",
    },
    {
        "id": "dyscalculia",
        "tab": "Dyscalculia",
        "title": "Dyscalculia Version",
        "generate": False,
        "hint": "Visual models, number lines in SVG, step-by-step mermaid, no timed drills, concrete before abstract.",
    },
    {
        "id": "adhd",
        "tab": "ADHD",
        "title": "ADHD",
        "generate": False,
        "hint": "2-minute colored chunks, numbered steps, checkpoint boxes, movement breaks, visual mermaid roadmap.",
    },
    {
        "id": "autism",
        "tab": "Autism Support",
        "title": "Autism Support",
        "generate": False,
        "hint": "Predictable structure, explicit transitions, calm tone, consistent color coding, literal language, routine diagram.",
    },
    {
        "id": "executive",
        "tab": "Executive Function",
        "title": "Executive Function Version",
        "generate": False,
        "hint": "START → NEXT → CHECK → DONE checklist with colored HTML boxes and mermaid timeline.",
    },
    {
        "id": "visual",
        "tab": "Visual Learner Support",
        "title": "Visual Learner Support",
        "generate": True,
        "hint": "Heavy diagrams: multiple SVG + mermaid concept map, colour-coded stages, icon markers, minimal dense prose.",
    },
    {
        "id": "auditory",
        "tab": "Auditory Learner Support",
        "title": "Auditory Learner Support",
        "generate": True,
        "hint": "Listen-and-repeat script plus supporting mermaid/SVG visual anchors for each audio chunk.",
    },
    {
        "id": "ell",
        "tab": "English Language Support",
        "title": "English Language Support",
        "generate": True,
        "hint": "Glossary table, sentence frames, cognates, labeled SVG picture dictionary, simplified syntax.",
    },
    {
        "id": "gifted",
        "tab": "Gifted Extension",
        "title": "Gifted Learner Extension Version",
        "generate": False,
        "hint": "Extension questions, deeper analysis, advanced mermaid systems diagram, enrichment tasks.",
    },
    {
        "id": "parent",
        "tab": "Parent Version",
        "title": "Parent Version",
        "generate": True,
        "hint": "Plain-language home summary, how to help, conversation starters, simple visual overview diagram.",
    },
    {
        "id": "teacher",
        "tab": "Teacher Version",
        "title": "Teacher Version",
        "generate": True,
        "hint": "Differentiation map, grouping, accommodations, assessment ideas, which visual aids to print.",
    },
    {
        "id": "tutor",
        "tab": "AI Tutor",
        "title": "AI Tutor Version",
        "generate": False,
        "hint": "Interactive Q&A blocks with hint ladders and small SVG/mermaid for each concept checked.",
    },
    {
        "id": "multisensory",
        "tab": "Multisensory",
        "title": "Multisensory Version",
        "generate": False,
        "hint": "See/Hear/Do/Write with colored activity cards, hands-on diagram labels, mermaid activity flow.",
    },
    {
        "id": "worksheet",
        "tab": "Exam Worksheet",
        "title": "Exam Worksheet",
        "generate": True,
        "hint": (
            "Full mock exam paper. Follow WORKSHEET_FORMAT section structure exactly. "
            "Student-facing Parts A–E; teacher Parts F–G. Must cross-reference vocabulary terms."
        ),
    },
]

LESSON_ADAPTATION_IDS = {
    "standard", "ld", "visual", "auditory", "ell", "teacher", "parent",
}

# Tab labels for st.tabs (derived) — legacy
OUTPUT_TAB_LABELS = [spec["tab"] for spec in ADAPTATION_SPECS]

# Keys sent to / returned from OpenAI
OUTPUT_KEYS = [spec["id"] for spec in ADAPTATION_SPECS if spec["generate"]]
