"""Shared educational vocabulary hygiene — reject junk terms, build real definitions."""

from __future__ import annotations

import re
from typing import Any, Iterable

# Words that must never become vocabulary cards / concept-map nodes
VOCAB_STOPWORDS = frozenset(
    {
        "this", "that", "with", "from", "have", "will", "were", "been", "they", "them",
        "their", "about", "which", "while", "where", "when", "what", "into", "also",
        "than", "then", "only", "over", "such", "some", "more", "most", "other", "each",
        "make", "like", "just", "very", "subject", "grade", "level", "objective",
        "objectives", "students", "student", "lesson", "chapter", "learning", "explain",
        "describe", "define", "discuss", "identify", "minutes", "hours", "seconds",
        "earth's", "water's", "using", "used", "uses", "does", "done", "being", "able",
        "should", "could", "would", "must", "need", "needs", "know", "show", "shows",
        "read", "write", "answer", "question", "questions", "example", "examples",
        "diagram", "diagrams", "figure", "figures", "table", "page", "pages", "part",
        "parts", "section", "sections", "unit", "units", "time", "today", "title",
        "introduction", "summary", "revision", "practice", "check", "model", "apply",
        "evidence", "support", "core", "idea", "ideas", "concept", "concepts", "term",
        "terms", "word", "words", "means", "meaning", "called", "name", "named",
        "first", "next", "then", "after", "before", "during", "through", "across",
        "between", "under", "above", "below", "around", "again", "still", "also",
        "because", "however", "therefore", "thus", "hence", "look", "looking",
    }
)

META_TOPICS = frozenset(
    {
        "learning objectives",
        "objectives",
        "learning objective",
        "introduction",
        "instructions",
        "directions",
        "warm up",
        "warmup",
        "do now",
        "exit ticket",
        "this lesson",
        "lesson",
        "untitled",
    }
)

WATER_CYCLE_TERMS = (
    ("Evaporation", "Evaporation is when liquid water turns into water vapour and rises into the air."),
    ("Condensation", "Condensation is when water vapour cools and changes back into tiny liquid droplets."),
    ("Precipitation", "Precipitation is water that falls from clouds as rain, snow, sleet, or hail."),
    ("Collection", "Collection is when water gathers in rivers, lakes, oceans, and groundwater."),
    ("Water vapour", "Water vapour is water in the gas state in the air."),
    ("Water cycle", "The water cycle is the continuous movement of water on, above, and below Earth's surface."),
    ("Transpiration", "Transpiration is when plants release water vapour into the air from their leaves."),
)

WATER_CYCLE_PICTURES = {
    "evaporation": "Draw the sun warming a lake or puddle, with curved arrows of vapour rising upward.",
    "condensation": "Draw a cloud forming high in the sky as tiny droplets gather together.",
    "precipitation": "Draw rain (or snow) falling from a dark cloud toward the ground.",
    "collection": "Draw a river, lake, or ocean where water gathers after rain.",
    "water vapour": "Draw invisible steam/vapour above warm water with a small label 'gas'.",
    "water cycle": "Draw a full loop: sun → rising vapour → cloud → rain → lake → back to sun.",
    "transpiration": "Draw a tree with tiny arrows of vapour leaving the leaves toward the sky.",
}

_TEACHER_TEXT_PATTERNS = (
    r"\bstudents?\s+will\b",
    r"\blearners?\s+will\b",
    r"\bby the end of (this|the) lesson\b",
    r"\blearning\s+objectives?\b",
    r"\bsuccess\s+criteria\b",
    r"\bteacher\s+note\b",
    r"\bdifferentiat",
    r"\bexit\s+ticket\b",
    r"\bwarm[\s-]?up\b",
    r"\binstruct(ion| the class)\b",
    r"\bwrite (it )?on the board\b",
    r"\bcold[\s-]?call\b",
    r"\bmodel cue\b",
    r"\bpractice-from-source\b",
)


def is_teacher_facing_text(text: str) -> bool:
    """True for lesson-plan / objective wording that must never appear as student content."""
    low = (text or "").strip().lower()
    if not low:
        return False
    return any(re.search(p, low) for p in _TEACHER_TEXT_PATTERNS)


def student_safe_definition(text: str) -> str:
    """Return empty string when text is teacher-facing or template filler."""
    raw = (text or "").strip()
    if not raw:
        return ""
    if is_teacher_facing_text(raw):
        return ""
    low = raw.lower()
    for bad in (
        "core concept in this lesson",
        "key lesson term",
        "key word connected",
        "not found in verified glossary",
        "ask ai tutor",
    ):
        if bad in low:
            return ""
    return raw


def canonical_definition(term: str) -> str:
    key = (term or "").strip().lower()
    for name, definition in WATER_CYCLE_TERMS:
        if name.lower() == key:
            return definition
    return ""


def picture_cue_for_term(term: str, *, definition: str = "") -> str:
    key = (term or "").strip().lower()
    if key in WATER_CYCLE_PICTURES:
        return WATER_CYCLE_PICTURES[key]
    if definition and not is_teacher_facing_text(definition):
        return f"Draw a simple labelled sketch that shows: {definition[:120]}"
    display = (term or "this idea").strip()
    return f"Draw a simple classroom sketch that helps you remember what {display} means."


def is_junk_term(term: str) -> bool:
    raw = (term or "").strip()
    if len(raw) < 3:
        return True
    key = raw.lower().strip(" .,;:!?\"'`")
    if not key or key in VOCAB_STOPWORDS:
        return True
    if key.endswith("'s") and key[:-2] in VOCAB_STOPWORDS:
        return True
    if re.fullmatch(r"\d+", key):
        return True
    if key in {"earth's", "water's", "sun's", "water", "cycle"}:
        # Bare fragments from titles — prefer "Water cycle" as one term
        return True
    if key.endswith("'s") and len(key) <= 8:
        return True
    if key in {"explain", "describe", "define", "minutes", "diagram"}:
        return True
    return False


def clean_topic(topic: str, *, fallback: str = "Lesson Topic") -> str:
    t = re.sub(r"\s+", " ", (topic or "").strip())
    if not t or t.lower() in META_TOPICS:
        return fallback
    t = re.sub(r"^(learning\s+objectives?|objectives?)\s*[:\-–]?\s*", "", t, flags=re.I).strip()
    if not t or t.lower() in META_TOPICS:
        return fallback
    return t[:120]


def definition_from_claims(term: str, claims: Iterable[str]) -> str:
    """Pick the best claim sentence that actually teaches this term (never objectives)."""
    needle = (term or "").strip().lower()
    if not needle:
        return ""
    best = ""
    best_score = 0
    for claim in claims:
        text = student_safe_definition(str(claim or ""))
        if not text or needle not in text.lower():
            continue
        low = text.lower()
        score = 1
        if any(
            p in low
            for p in (f"{needle} is ", f"{needle} are ", f"{needle} means", "is when", "is the")
        ):
            score += 6
        if "students will" in low or "learning objective" in low:
            continue
        if len(text) > 40:
            score += 1
        if score > best_score:
            best_score = score
            best = text
    return best[:280] if best_score >= 5 else (best[:280] if best_score >= 2 else "")


def enrich_water_cycle_terms(topic: str, existing: list[str]) -> list[tuple[str, str]]:
    """If the lesson is about the water cycle, ensure canonical scientific terms."""
    blob = (topic or "").lower() + " " + " ".join(existing).lower()
    if not any(
        k in blob
        for k in ("water cycle", "evaporat", "precipitat", "condens", "water vapour", "water vapor")
    ):
        return []
    have = {e.lower() for e in existing}
    out: list[tuple[str, str]] = []
    for term, definition in WATER_CYCLE_TERMS:
        if term.lower() not in have and not is_junk_term(term):
            out.append((term, definition))
    return out


def build_student_definition(term: str, academic: str, *, topic: str = "") -> str:
    academic = student_safe_definition(academic)
    display = (term or "").strip()
    canonical = canonical_definition(display)
    if canonical:
        return canonical
    if academic:
        if len(academic.split()) > 28:
            first = re.split(r"(?<=[.!?])\s+", academic)[0]
            return first.strip()
        return academic
    topic = clean_topic(topic, fallback="this topic")
    return (
        f"{display} is an important idea in {topic}. "
        f"Say what {display.lower()} means in one clear sentence using the lesson diagram."
    )


def normalize_vocab_items(
    terms: list[Any],
    *,
    topic: str = "",
    claims: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter junk and attach student-safe, claim-grounded definitions."""
    claims = [c for c in (claims or []) if student_safe_definition(str(c))]
    topic = clean_topic(topic)
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    waterish = any(
        k in topic.lower()
        for k in ("water cycle", "evaporat", "precipitat", "condens")
    )

    for item in terms:
        if isinstance(item, dict):
            term = str(item.get("term") or item.get("word") or "").strip()
            definition = student_safe_definition(
                str(
                    item.get("definition")
                    or item.get("academic_definition")
                    or item.get("simple_explanation")
                    or ""
                )
            )
            example = student_safe_definition(
                str(item.get("example") or item.get("example_sentence") or "")
            )
        else:
            term = str(item or "").strip()
            definition = ""
            example = ""
        if not term or is_junk_term(term):
            continue
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)

        # Water-cycle lessons: always prefer scientific canonical wording
        if waterish and canonical_definition(term):
            definition = canonical_definition(term)
        elif not definition:
            definition = definition_from_claims(term, claims) or canonical_definition(term)
        if not definition:
            definition = build_student_definition(term, "", topic=topic)

        if not example or is_teacher_facing_text(example):
            example = definition_from_claims(term, claims) or definition

        picture = picture_cue_for_term(term, definition=definition)
        out.append(
            {
                "term": term[:1].upper() + term[1:] if term else term,
                "definition": definition,
                "academic_definition": definition,
                "simple_explanation": build_student_definition(term, definition, topic=topic),
                "example": example[:220],
                "example_sentence": example[:220],
                "picture": picture,
                "lesson_context": f"You need the word {term} to explain {topic} clearly.",
            }
        )

    for term, definition in enrich_water_cycle_terms(topic, list(seen)):
        if term.lower() in seen:
            continue
        seen.add(term.lower())
        out.append(
            {
                "term": term,
                "definition": definition,
                "academic_definition": definition,
                "simple_explanation": definition,
                "example": definition,
                "example_sentence": definition,
                "picture": picture_cue_for_term(term, definition=definition),
                "lesson_context": f"{term} is a key stage in {topic}.",
            }
        )

    priority = {
        "evaporation": 0,
        "condensation": 1,
        "precipitation": 2,
        "collection": 3,
        "transpiration": 4,
        "water vapour": 5,
        "water vapor": 5,
        "water cycle": 6,
        "runoff": 7,
    }
    out.sort(key=lambda r: priority.get(str(r.get("term") or "").lower(), 50))
    return out[:12]
