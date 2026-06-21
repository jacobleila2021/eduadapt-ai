"""
Build a rich lesson context from long uploads (multi-chunk extraction).
Ensures 20-page lessons are not collapsed into a one-page summary.
"""

from openai import OpenAI

from config import MAX_CHUNK_CHARS, MAX_LESSON_CHARS

EXTRACT_SYSTEM = """You are a curriculum analyst. Extract content faithfully — do NOT summarize away detail.

Return JSON:
{
  "topic": "...",
  "grade_level": "...",
  "learning_objectives": ["objective 1", "..."],
  "key_concepts": [{"name": "...", "explanation": "2-4 sentences with facts students need for exams"}],
  "vocabulary_terms": ["term1", "..."],
  "facts_and_processes": ["Every important fact, step, date, formula, or process from this chunk"],
  "diagram_ideas": ["Describe diagram 1 students need to study", "..."]
}

Include ALL exam-relevant facts from the chunk. Minimum 5 key_concepts and 8 facts_and_processes when content allows."""


def _split_chunks(text: str, size: int) -> list:
    paragraphs = text.split("\n\n")
    chunks = []
    current = []
    length = 0
    for para in paragraphs:
        para_len = len(para) + 2
        if length + para_len > size and current:
            chunks.append("\n\n".join(current))
            current = [para]
            length = para_len
        else:
            current.append(para)
            length += para_len
    if current:
        chunks.append("\n\n".join(current))
    return chunks or [text[:size]]


def build_lesson_context(client: OpenAI, lesson_text: str, model: str) -> dict:
    """
    Analyze full lesson text (all pages). Uses chunking for long documents.
    Returns structured context used by all generators.
    """
    import json

    text = lesson_text.strip()
    if len(text) <= MAX_LESSON_CHARS:
        chunks = [text]
    else:
        chunks = _split_chunks(text, MAX_CHUNK_CHARS)

    merged = {
        "topic": "",
        "grade_level": "",
        "learning_objectives": [],
        "key_concepts": [],
        "vocabulary_terms": [],
        "facts_and_processes": [],
        "diagram_ideas": [],
        "source_char_count": len(text),
        "chunks_processed": len(chunks),
        "was_truncated": len(text) > MAX_LESSON_CHARS,
    }

    for index, chunk in enumerate(chunks, 1):
        user = f"Chunk {index} of {len(chunks)}:\n\n{chunk}"
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=4000,
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)

        if not merged["topic"] and data.get("topic"):
            merged["topic"] = data["topic"]
        if not merged["grade_level"] and data.get("grade_level"):
            merged["grade_level"] = data["grade_level"]

        for key in (
            "learning_objectives",
            "vocabulary_terms",
            "facts_and_processes",
            "diagram_ideas",
        ):
            merged[key].extend(data.get(key) or [])

        for concept in data.get("key_concepts") or []:
            if isinstance(concept, dict):
                merged["key_concepts"].append(concept)

    # Deduplicate while preserving order
    merged["learning_objectives"] = list(dict.fromkeys(merged["learning_objectives"]))
    merged["vocabulary_terms"] = list(dict.fromkeys(merged["vocabulary_terms"]))
    merged["facts_and_processes"] = list(dict.fromkeys(merged["facts_and_processes"]))
    return merged


def context_to_prompt(context: dict, excerpt: str) -> str:
    """Format extracted context + source excerpt for adaptation prompts."""
    import json

    lines = [
        f"TOPIC: {context.get('topic', 'Lesson')}",
        f"GRADE: {context.get('grade_level', 'Unknown')}",
        f"SOURCE LENGTH: {context.get('source_char_count', 0):,} characters"
        f" ({context.get('chunks_processed', 1)} sections analyzed)",
        "",
        "LEARNING OBJECTIVES:",
        *[f"- {o}" for o in context.get("learning_objectives") or []],
        "",
        "KEY CONCEPTS (must all appear in adaptations):",
    ]
    for concept in context.get("key_concepts") or []:
        if isinstance(concept, dict):
            lines.append(f"- **{concept.get('name', '')}**: {concept.get('explanation', '')}")

    lines.extend([
        "",
        "EXAM FACTS & PROCESSES (students must know these):",
        *[f"- {f}" for f in (context.get("facts_and_processes") or [])[:40]],
        "",
        "DIAGRAM IDEAS:",
        *[f"- {d}" for d in (context.get("diagram_ideas") or [])[:8]],
        "",
        "LESSON SOURCE EXCERPT:",
        excerpt[:12000],
    ])
    if context.get("was_truncated"):
        lines.append(
            "\n[Note: Full document was analyzed in sections above — "
            "include ALL listed objectives, concepts, and facts in output.]"
        )
    return "\n".join(lines)
