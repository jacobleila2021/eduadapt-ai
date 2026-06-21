"""
AdaptEd AI–aligned adaptation types for EduAdapt AI output tabs.
Matches AdaptEd AI schemas (17 versions) — teacher-facing labels.
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
        "tab": "Vocabulary",
        "title": "Vocabulary Builder",
        "generate": True,
        "hint": (
            "Post-lesson vocabulary page: 10–15 key terms with student-friendly definitions, "
            "example sentences from the lesson, word bank table, 'Use in a sentence' prompts, "
            "and ELL cognates where helpful. Include a quick matching or fill-in review section."
        ),
    },
    {
        "id": "standard",
        "tab": "Standard Enhanced",
        "title": "Standard Enhanced Version",
        "generate": True,
        "hint": "UDL sequence: hook, real-life context, visual, guided explanation, practice, mastery check. Clear headings, same objectives as source.",
    },
    {
        "id": "ld",
        "tab": "Learning Disability",
        "title": "Learning Disability Version",
        "generate": True,
        "hint": "Big idea first, reduced cognitive load, visual cues, simplified language (Grade 3–4), chunked steps.",
    },
    {
        "id": "dyslexia",
        "tab": "Dyslexia",
        "title": "Dyslexia Version",
        "generate": True,
        "hint": "Bulleted steps, short sentences, bold key terms, wide spacing cues, avoid dense blocks, sans-serif-friendly layout.",
    },
    {
        "id": "dysgraphia",
        "tab": "Dysgraphia",
        "title": "Dysgraphia Version",
        "generate": True,
        "hint": "Oral response options, minimal writing demands, drag-label or point-to tasks, diagram labelling instead of long prose.",
    },
    {
        "id": "dyscalculia",
        "tab": "Dyscalculia",
        "title": "Dyscalculia Version",
        "generate": True,
        "hint": "Visual models, number lines, step-by-step, no timed drills, concrete before abstract.",
    },
    {
        "id": "adhd",
        "tab": "ADHD",
        "title": "ADHD Version",
        "generate": True,
        "hint": "2-minute chunks, numbered steps, checkpoint questions, movement break prompts, clear headings, visual breaks.",
    },
    {
        "id": "autism",
        "tab": "Autism",
        "title": "Autism Version",
        "generate": True,
        "hint": "Predictable structure, explicit transitions, calm tone, sensory-friendly layout, literal language, routine cues.",
    },
    {
        "id": "executive",
        "tab": "Executive Function",
        "title": "Executive Function Version",
        "generate": True,
        "hint": "START HERE → NEXT STEP → CHECKPOINT → FINISHED checklist format, task initiation scaffolds, working memory supports.",
    },
    {
        "id": "visual",
        "tab": "Visual Learner",
        "title": "Visual Learner Version",
        "generate": True,
        "hint": "Diagrams described in text, colour-coded stages, concept maps, flowcharts, icon-style section markers.",
    },
    {
        "id": "auditory",
        "tab": "Auditory Learner",
        "title": "Auditory Learner Version",
        "generate": True,
        "hint": "Listen-and-repeat script, discussion prompts, rhythm/mnemonic hooks, read-aloud friendly phrasing.",
    },
    {
        "id": "ell",
        "tab": "English Language Learner",
        "title": "English Language Learner Version",
        "generate": True,
        "hint": "Glossary, sentence frames, cognates, visuals described in text, simplified syntax, key vocabulary highlighted.",
    },
    {
        "id": "gifted",
        "tab": "Gifted Extension",
        "title": "Gifted Learner Extension Version",
        "generate": True,
        "hint": "Extension questions, deeper analysis, enrichment tasks, research prompts, higher-order thinking.",
    },
    {
        "id": "parent",
        "tab": "Parent Support",
        "title": "Parent Support Version",
        "generate": True,
        "hint": "Plain-language home summary, how to help, conversation starters, no jargon, reassuring tone.",
    },
    {
        "id": "teacher",
        "tab": "Teacher Support",
        "title": "Teacher Support Version",
        "generate": True,
        "hint": "Differentiation map, grouping suggestions, accommodation tips, assessment ideas, pairing recommendations.",
    },
    {
        "id": "tutor",
        "tab": "AI Tutor",
        "title": "AI Tutor Version",
        "generate": True,
        "hint": "Interactive Q&A tutoring blocks, hints, vocabulary checks, Socratic questions, scaffolded dialogue.",
    },
    {
        "id": "multisensory",
        "tab": "Multisensory",
        "title": "Multisensory Version",
        "generate": True,
        "hint": "See / Hear / Do / Write activities integrated, hands-on options, multi-modal reinforcement.",
    },
    {
        "id": "worksheet",
        "tab": "Worksheet",
        "title": "Exam Practice Worksheet",
        "generate": True,
        "hint": (
            "Exam-style worksheet with learner-specific guidance. Include: "
            "Part A — 6–8 short-answer questions (1–3 sentences, exam-ready); "
            "Part B — 3–4 long-answer / extended-response questions (paragraph or essay style); "
            "Part C — Differentiated Assignment Map (which Part A/B questions to assign for dyslexia, "
            "ADHD, ELL, gifted, and executive function learners, with accommodations such as oral response, "
            "sentence frames, or extended time); "
            "Part D — Teacher Answer Key with marking rubric hints. "
            "Questions must align with lesson objectives and suit formal assessments."
        ),
    },
]

# Tab labels for st.tabs (derived)
OUTPUT_TAB_LABELS = [spec["tab"] for spec in ADAPTATION_SPECS]

# Keys sent to / returned from OpenAI
OUTPUT_KEYS = [spec["id"] for spec in ADAPTATION_SPECS if spec["generate"]]
