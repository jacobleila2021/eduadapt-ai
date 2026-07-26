"""Source-linked universal lesson profile; curriculum is optional enrichment."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

_STOPWORDS = {
    "about", "after", "also", "and", "are", "because", "been", "before",
    "being", "between", "can", "could", "each", "for", "from", "have",
    "into", "its", "lesson", "more", "not", "of", "on", "only", "or",
    "other", "should", "students", "such", "than", "that", "the", "their",
    "them", "then", "there", "these", "they", "this", "through", "to",
    "using", "was", "were", "when", "where", "which", "will", "with", "would",
    # Document/worksheet metadata — must never surface as teachable concepts,
    # diagram labels, or vocabulary ("Grade 10", "40 minutes", "5 marks", …).
    "grade", "grades", "class", "classes", "standard", "marks", "mark",
    "minute", "minutes", "hour", "hours", "duration", "period", "periods",
    "page", "pages", "chapter", "chapters", "unit", "units", "section",
    "sections", "exercise", "exercises", "activity", "activities",
    "question", "questions", "answer", "answers", "worksheet", "exam",
    "test", "quiz", "total", "date", "name", "school", "teacher",
    "teachers", "student", "subject", "topic", "syllabus", "curriculum",
    "objectives", "objective", "instructions", "note", "notes", "figure",
    "table", "copyright", "published", "reprint", "edition", "board",
    # Lesson-plan scaffolding words — headings and teacher phrasing that must
    # never become concepts ("Introduction", "Guided Practice", "I want you…").
    "introduction", "understanding", "practice", "guided", "independent",
    "essential", "exploration", "creation", "diagram", "diagrams", "labeled",
    "labelled", "label", "labels", "image", "images", "want", "task", "tasks",
    "moment", "responses", "response", "your", "yours",
}
# Verbs and generic nouns that are never teachable concepts on their own
# ("moves", "changes state", "time") even when frequent in the source.
_GENERIC_CONCEPT_WORDS = {
    "changes", "change", "changing", "changed", "moves", "move", "moving",
    "called", "become", "becomes", "became", "form", "forms", "forming",
    "gives", "give", "given", "makes", "make", "making", "made", "explains",
    "explain", "means", "mean", "stays", "stay", "falls", "fall", "fallen",
    "grows", "grow", "release", "releases", "heats", "heat", "begins",
    "begin", "collects", "collect", "soaks", "soak", "rises", "rise",
    "cools", "cool", "turns", "turn", "keeps", "keep", "shows", "show",
    "time", "times", "state", "states", "stage", "stages", "thing",
    "things", "idea", "ideas", "way", "ways", "kind", "kinds", "part",
    "parts", "example", "examples", "important", "different", "amount",
    "number", "back", "again", "constantly", "continuous", "movement",
    # prepositions / connectives / participles that pass the length filter
    "during", "within", "without", "around", "across", "towards", "toward",
    "under", "over", "above", "below", "along", "among", "while", "until",
    "although", "though", "however", "therefore", "every", "always", "often",
    "usually", "sometimes", "powered", "formed", "heated", "cooled",
    "released", "collected", "known", "seen", "used", "found",
    # number words ("four stages") are counts, not concepts
    "zero", "once", "twice", "three", "four", "five", "seven", "eight",
    "nine", "first", "second", "third", "fourth", "fifth", "many", "several",
}

_SKILL_VERBS = {
    "analyse", "analyze", "apply", "calculate", "classify", "compare",
    "construct", "create", "define", "describe", "design", "discuss",
    "evaluate", "explain", "identify", "interpret", "justify", "observe",
    "predict", "read", "solve", "summarise", "summarize", "write",
}
_CURRICULA: list[tuple[str, tuple[str, ...]]] = [
    ("CBSE", ("cbse", "central board of secondary education")),
    ("ICSE", ("icse", "indian certificate of secondary education")),
    ("Cambridge", ("cambridge international", "cambridge lower secondary")),
    ("IB", ("international baccalaureate", "ib myp", "ib dp", "ib pyp")),
    ("IGCSE", ("igcse",)),
    ("GCSE", ("gcse",)),
    ("US Common Core", ("common core", "ccss")),
    ("Australian Curriculum", ("australian curriculum", "acara")),
    ("Singapore Curriculum", ("singapore curriculum", "moe singapore")),
    ("State Board", ("state board", "scert")),
    ("University", ("university", "undergraduate", "postgraduate", "course code")),
    ("Corporate", ("corporate training", "compliance training", "employee training")),
]


@dataclass(frozen=True)
class SourceClaim:
    claim_id: str
    text: str
    source_block_ids: list[str]
    authority: str = "uploaded_source"


@dataclass
class UniversalLessonProfile:
    schema_version: str
    source_id: str
    title: str
    topic: str
    concepts: list[dict[str, Any]]
    skills: list[dict[str, Any]]
    vocabulary: list[dict[str, Any]]
    learning_objectives: list[dict[str, Any]]
    misconceptions: list[dict[str, Any]]
    examples: list[dict[str, Any]]
    assessment_opportunities: list[dict[str, Any]]
    visual_opportunities: list[dict[str, Any]]
    difficulty: dict[str, Any]
    age_estimate: dict[str, Any]
    language: str
    curriculum_resolution: dict[str, Any]
    claim_ledger: list[SourceClaim] = field(default_factory=list)
    grounding_mode: str = "uploaded_source"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_curriculum(
    text: str, user_metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    metadata = user_metadata or {}
    declared = str(metadata.get("curriculum") or "").strip()
    if declared:
        return {
            "status": "user_declared",
            "curriculum": declared,
            "confidence": 1.0,
            "provenance": "user_metadata",
        }
    sample = str(text or "")[:12000].lower()
    hits = [
        name
        for name, markers in _CURRICULA
        if any(re.search(rf"\b{re.escape(marker)}\b", sample) for marker in markers)
    ]
    if len(hits) == 1:
        return {
            "status": "recognized",
            "curriculum": hits[0],
            "confidence": 0.92,
            "provenance": "source_marker",
        }
    if len(hits) > 1:
        return {
            "status": "ambiguous",
            "curriculum": None,
            "candidates": hits,
            "confidence": 0.45,
            "provenance": "multiple_source_markers",
        }
    return {
        "status": "unknown",
        "curriculum": None,
        "confidence": 0.0,
        "provenance": "no_source_marker",
    }


def _reading_metrics(text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    sentences = max(len(re.findall(r"[.!?]+", text)), 1)
    words = re.findall(r"[A-Za-zÀ-ÿ']+", text)
    word_count = max(len(words), 1)
    average_sentence = word_count / sentences
    average_word = sum(len(word) for word in words) / word_count
    score = average_sentence * 0.45 + average_word * 1.8
    if score < 13:
        band, age = "introductory", "8-11"
    elif score < 18:
        band, age = "intermediate", "11-14"
    elif score < 24:
        band, age = "advanced_secondary", "14-18"
    else:
        band, age = "higher_education_or_professional", "18+"
    return (
        {
            "band": band,
            "score": round(score, 2),
            "average_sentence_words": round(average_sentence, 2),
            "average_word_characters": round(average_word, 2),
        },
        {"band": age, "method": "source_readability_heuristic", "confidence": 0.55},
    )


def _refs(block_id: str) -> list[str]:
    return [block_id] if block_id else []


def build_universal_lesson_profile(
    source_envelope: dict[str, Any],
) -> UniversalLessonProfile:
    blocks = [
        block
        for block in source_envelope.get("blocks") or []
        if isinstance(block, dict) and str(block.get("text") or "").strip()
    ]
    text = str(source_envelope.get("text") or "")
    first_heading = next(
        (
            str(block["text"]).strip()
            for block in blocks
            if block.get("kind") == "heading"
        ),
        "",
    )
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    title = (first_heading or first_line or "Uploaded Lesson")[:160]
    topic = re.split(r"[.:!?]", title, 1)[0][:100].strip() or "Uploaded Lesson"

    # Concepts must be teachable phrases, not raw frequency words. Counting
    # single words split "The Water Cycle" into the junk concepts "water" and
    # "cycle", which then became broken exam questions ("Explain cycle in
    # detail…") and meaningless diagram labels. Prefer repeated two-word
    # phrases ("water cycle"), then single content words not already covered
    # by a chosen phrase.
    def _concept_word(token: str) -> bool:
        return (
            len(token) >= 4
            and token not in _STOPWORDS
            and token not in _GENERIC_CONCEPT_WORDS
        )

    try:
        from engines.lesson_composition_engine.vocab_quality import (
            is_teacher_facing_text as _is_teacher_facing,
        )
    except Exception:  # pragma: no cover - engine always ships together
        def _is_teacher_facing(_: str) -> bool:
            return False

    word_rows: list[tuple[str, str]] = []
    bigram_rows: list[tuple[str, str]] = []
    first_seen: dict[str, int] = {}
    token_pos = 0
    for block in blocks:
        block_id = str(block.get("block_id") or "")
        # Phrases may only pair words that are truly adjacent in the source:
        # split on punctuation first, otherwise the list "evaporation,
        # condensation, precipitation" invents junk phrases like
        # "evaporation condensation". Tokenize EVERY word (including short
        # ones) so "water on Earth" never collapses into "water earth".
        for segment in re.split(r"[.,;:!?()\[\]{}\n\r•|—–]+", str(block["text"])):
            # Classroom-management lines from teacher lesson plans ("I want you
            # to take a moment…", "create your own labeled diagram") must never
            # seed concepts — they produced junk terms like "i want" and
            # "diagram" that became broken questions and vocab cards.
            if _is_teacher_facing(segment):
                continue
            tokens = [
                w.lower()[:-2] if w.lower().endswith("'s") else w.lower()
                for w in re.findall(r"\b[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]*\b", segment)
            ]
            for offset, word in enumerate(tokens):
                if _concept_word(word):
                    word_rows.append((word, block_id))
                    first_seen.setdefault(word, token_pos + offset)
            for offset, (first, second) in enumerate(zip(tokens, tokens[1:])):
                if _concept_word(first) and _concept_word(second):
                    phrase = f"{first} {second}"
                    bigram_rows.append((phrase, block_id))
                    first_seen.setdefault(phrase, token_pos + offset)
            token_pos += len(tokens)
    counts = Counter(word for word, _ in word_rows)
    bigram_counts = Counter(phrase for phrase, _ in bigram_rows)

    phrase_terms: list[str] = []
    covered_words: set[str] = set()
    for phrase, freq in bigram_counts.most_common(20):
        if freq < 2 or len(phrase_terms) >= 6:
            break
        phrase_terms.append(phrase)
        covered_words.update(phrase.split())
    single_terms = [
        word for word, _ in counts.most_common(30) if word not in covered_words
    ]
    # Select by importance (frequency), then present in the order the source
    # teaches them — so diagrams and questions follow the lesson's own flow
    # (evaporation → condensation → precipitation), not raw word counts.
    top_terms = sorted(
        (phrase_terms + single_terms)[:15],
        key=lambda t: first_seen.get(t, 10**9),
    )

    def _term_refs(term: str) -> list[str]:
        rows = bigram_rows if " " in term else word_rows
        return sorted({ref for token, ref in rows if token == term})[:8]

    def _term_freq(term: str) -> int:
        return bigram_counts[term] if " " in term else counts[term]

    concepts = [
        {
            "concept": term,
            "source_refs": _term_refs(term),
            "frequency": _term_freq(term),
        }
        for term in top_terms[:12]
    ]
    vocabulary = [
        {
            "term": term,
            "source_refs": _term_refs(term),
        }
        for term in top_terms[:15]
    ]

    objectives: list[dict[str, Any]] = []
    skills: list[dict[str, Any]] = []
    misconceptions: list[dict[str, Any]] = []
    examples: list[dict[str, Any]] = []
    assessments: list[dict[str, Any]] = []
    visuals: list[dict[str, Any]] = []
    ledger: list[SourceClaim] = []
    claim_index = 0

    for block in blocks:
        # Hard-wrapped source lines (PDF/txt) are NOT sentence boundaries —
        # splitting on single newlines produced mid-sentence claim fragments
        # ("…precipitation and"). Join wrapped lines; only blank lines and
        # end punctuation separate claims.
        block_text = re.sub(r"\n{2,}", "\u2029", str(block["text"]))
        block_text = re.sub(r"[ \t]*\n[ \t]*", " ", block_text)
        block_id = str(block.get("block_id") or "")
        for sentence in re.split(r"(?<=[.!?])\s+|\u2029+", block_text):
            sentence = sentence.strip()
            if len(sentence) < 8:
                continue
            claim_index += 1
            ledger.append(
                SourceClaim(
                    claim_id=f"claim_{claim_index:05d}",
                    text=sentence[:1200],
                    source_block_ids=_refs(block_id),
                )
            )
            low = sentence.lower()
            if re.search(r"\b(?:objective|students? will|learners? will|you will learn)\b", low):
                objectives.append({"objective": sentence, "source_refs": _refs(block_id)})
            verbs = sorted(
                verb
                for verb in _SKILL_VERBS
                if re.search(rf"\b{re.escape(verb)}\w*\b", low)
            )
            for verb in verbs:
                skills.append({"skill": verb, "source_refs": _refs(block_id)})
            if "misconception" in low or "common mistake" in low:
                misconceptions.append(
                    {
                        "misconception": sentence,
                        "source_refs": _refs(block_id),
                        "status": "explicit_in_source",
                    }
                )
            if re.search(r"\b(?:example|for instance|case study)\b", low):
                examples.append({"example": sentence, "source_refs": _refs(block_id)})
            if sentence.endswith("?"):
                assessments.append(
                    {"question": sentence, "source_refs": _refs(block_id)}
                )
            if re.search(
                r"\b(?:cycle|process|sequence|timeline|compare|structure|system|flow|map)\b",
                low,
            ):
                visuals.append(
                    {
                        "opportunity": sentence[:240],
                        "source_refs": _refs(block_id),
                    }
                )

    if not objectives:
        for concept in concepts[:5]:
            objectives.append(
                {
                    "objective": f"Explain {concept['concept']} using evidence from the lesson.",
                    "source_refs": concept["source_refs"],
                    "status": "pedagogically_inferred",
                }
            )

    difficulty, age = _reading_metrics(text)
    curriculum = detect_curriculum(text, source_envelope.get("user_metadata"))
    return UniversalLessonProfile(
        schema_version="3.0.0",
        source_id=str(source_envelope.get("source_id") or ""),
        title=title,
        topic=topic,
        concepts=concepts,
        skills=list({row["skill"]: row for row in skills}.values())[:12],
        vocabulary=vocabulary,
        learning_objectives=objectives[:12],
        misconceptions=misconceptions[:10],
        examples=examples[:12],
        assessment_opportunities=assessments[:20],
        visual_opportunities=visuals[:12],
        difficulty=difficulty,
        age_estimate=age,
        language=str(source_envelope.get("language") or "unknown"),
        curriculum_resolution=curriculum,
        claim_ledger=ledger[:500],
    )


def profile_to_prompt_block(profile: dict[str, Any]) -> str:
    """Compact authoritative prompt representation with source references."""
    lines = [
        "SOURCE_GROUNDING_MODE: uploaded_source",
        "Use only SOURCE_CLAIMS and VERIFIED_ENGINE_ARTIFACTS for factual content.",
        "Do not add uncited general knowledge. Every generated section and answer must include source_refs.",
        f"TOPIC: {profile.get('topic') or 'Uploaded lesson'}",
    ]
    for claim in (profile.get("claim_ledger") or [])[:160]:
        refs = ",".join(claim.get("source_block_ids") or [])
        lines.append(
            f"- {claim.get('claim_id')} [{refs}]: {str(claim.get('text') or '')[:800]}"
        )
    return "\n".join(lines)
