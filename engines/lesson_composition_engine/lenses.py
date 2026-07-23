"""Adaptive composition lenses — pedagogically distinct, never recolored clones."""

from __future__ import annotations

from typing import Any

LENS_CONTRACTS: dict[str, dict[str, Any]] = {
    "standard": {
        "title": "Mainstream Support",
        "voice": "expert classroom teacher; natural textbook prose",
        "structure": [
            "Learning Goal",
            "Lesson Introduction",
            "Core Ideas",
            "Guided Explanation",
            "Examples",
            "Misconceptions",
            "Visual Study",
            "Practice",
            "Summary and Reflection",
        ],
        "rules": (
            "Write cohesive paragraphs (2+ sentences, ≤120 words). "
            "Progressive teaching with smooth transitions. Never teach metadata."
        ),
    },
    "ld": {
        "title": "Dyslexia Support",
        "voice": "clear specialist teacher; short sentences; one idea per paragraph",
        "structure": [
            "Learning Goal",
            "Big Idea",
            "Teach Step by Step",
            "Examples",
            "Check Understanding",
            "Exam Practice",
            "Summary",
        ],
        "rules": (
            "Short sentences. One idea per paragraph. Bold **key terms**. "
            "Extra spacing cues via bullets. Keep full exam terminology and depth."
        ),
        "format": "bullets",
    },
    "adhd": {
        "title": "ADHD Support",
        "voice": "energetic coach; chunked goals",
        "structure": [
            "Mission Goal",
            "2-Minute Chunk 1",
            "Quick Check",
            "2-Minute Chunk 2",
            "Movement Break",
            "Practice Sprint",
            "Done Checklist",
        ],
        "rules": (
            "Chunked learning with mini goals, timers, quick checks, and movement prompts. "
            "Keep full concept coverage; do not dilute curriculum."
        ),
    },
    "autism": {
        "title": "Autism Support",
        "voice": "calm, literal, predictable",
        "structure": [
            "What We Will Learn",
            "Today's Routine",
            "Concept A",
            "Concept B",
            "Examples",
            "What To Do Next",
            "Practice",
            "Finished Summary",
        ],
        "rules": (
            "Predictable structure, literal language, explicit transitions, visual supports. "
            "No idioms or sarcasm. Same colour pattern cues in headings."
        ),
    },
    "ell": {
        "title": "English Language Support",
        "voice": "supportive language teacher",
        "structure": [
            "Learning Goal",
            "Key Words First",
            "Guided Explanation",
            "Sentence Frames",
            "Examples",
            "Practice",
            "Summary",
        ],
        "rules": (
            "Keep board vocabulary; add glossary scaffolds and sentence frames. "
            "Do not replace exam terms with baby words."
        ),
    },
    "visual": {
        "title": "Visual Learner Support",
        "voice": "visual designer-teacher",
        "structure": [
            "Learning Goal",
            "See the Big Picture",
            "Colour-Coded Stages",
            "Diagram Study",
            "Worked Visual Example",
            "Practice Q/A",
            "Summary Map",
        ],
        "rules": (
            "Diagram-rich, colour-coded stages, minimal long paragraphs. "
            "Refer to UVIE visuals by caption. Practice as Q1/A1 pairs."
        ),
    },
    "auditory": {
        "title": "Auditory Learner Support",
        "voice": "spoken classroom conversation",
        "structure": [
            "Listen Goal",
            "Talk Through the Idea",
            "Say and Repeat",
            "Worked Explanation",
            "Discussion Practice",
            "Reflection",
            "Summary Aloud",
        ],
        "rules": (
            "Natural spoken explanations, conversation style, Say:/Repeat: cues, pause prompts. "
            "Full prose paragraphs — not bullet lists."
        ),
        "format": "prose",
    },
    "teacher": {
        "title": "Teacher Version",
        "voice": "colleague instructional coach",
        "structure": [
            "Lesson Intent",
            "Teaching Notes",
            "Misconception Alerts",
            "Timing Guide",
            "Differentiation",
            "Extensions",
            "Assessment and Answer Key",
        ],
        "rules": (
            "Teacher-facing notes, misconceptions, timing, extensions, differentiation. "
            "Avoid long student-facing repetition."
        ),
    },
    "parent": {
        "title": "Parent Version",
        "voice": "warm home guide",
        "structure": [
            "What Your Child Is Learning",
            "Simple Explanation",
            "Home Activity",
            "Discussion Prompts",
            "How To Help",
            "Encourage Next Steps",
        ],
        "rules": "Plain-language home summary, activities, real-life discussion prompts.",
    },
    "vocabulary": {
        "title": "Vocabulary Support",
        "voice": "vocabulary coach",
        "structure": ["Word Study Goal", "Word Wall", "Concept Connections", "Practice", "Self Check"],
        "rules": "Compose from CLG vocabulary only — never frequency word lists.",
    },
    "worksheet": {
        "title": "Exam Worksheet",
        "voice": "board examiner",
        "structure": ["Header", "Short Answer", "Long Answer", "Diagram Question", "Answer Key"],
        "rules": "Questions from CLG assessment outcomes and facts only — never metadata.",
    },
    "dyslexia": {
        "title": "Dyslexia Support",
        "voice": "clear specialist teacher; short sentences; one idea per paragraph",
        "structure": [
            "Learning Goal",
            "Big Idea",
            "Teach Step by Step",
            "Examples",
            "Check Understanding",
            "Exam Practice",
            "Summary",
        ],
        "rules": (
            "Short sentences. One idea per paragraph. Bold **key terms**. "
            "Extra spacing cues via bullets. Keep full exam terminology and depth."
        ),
        "format": "bullets",
    },
}


def lens_for(adaptation_id: str) -> dict[str, Any]:
    return dict(LENS_CONTRACTS.get(adaptation_id) or LENS_CONTRACTS["standard"])


SUBJECT_TEACHING_ARCS: dict[str, list[str]] = {
    "mathematics": ["Concrete", "Visual", "Representation", "Symbols", "Worked Example", "Practice", "Application"],
    "physics": ["Concept", "Phenomenon", "Experiment", "Diagram", "Formula", "Example", "Practice"],
    "chemistry": ["Concept", "Particle view", "Reaction", "Equation", "Diagram", "Safety", "Application"],
    "biology": ["Concept", "Process", "Diagram", "Labels", "Analogy", "Application"],
    "english": ["Reading", "Vocabulary", "Grammar", "Writing", "Speaking", "Listening", "Literature"],
    "social_science": ["Timeline", "Map", "Cause-effect", "Primary source", "Citizenship", "Inquiry"],
    "computer_science": ["Algorithm", "Flowchart", "Code", "Memory", "Execution trace"],
    "commerce": ["Scenario", "Table", "Graph", "Case study", "Decision"],
    "economics": ["Scenario", "Graph", "Case study", "Decision"],
    "world_languages": ["Pronunciation", "Sentence building", "Culture", "Listening", "Speaking"],
}


def subject_arc(subject_key: str) -> list[str]:
    key = (subject_key or "general").lower()
    for family, arc in SUBJECT_TEACHING_ARCS.items():
        if family in key or key in family:
            return list(arc)
    return ["Concept", "Explanation", "Example", "Practice", "Application"]
