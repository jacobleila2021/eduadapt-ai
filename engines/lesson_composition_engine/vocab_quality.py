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
)


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
    if key in {"earth's", "water's", "sun's"}:
        return True
    # Possessive fragments and bare verbs often scraped from worksheets
    if key.endswith("'s") and len(key) <= 8:
        return True
    if key in {"explain", "describe", "define", "minutes", "diagram"}:
        return True
    return False


def clean_topic(topic: str, *, fallback: str = "Lesson Topic") -> str:
    t = re.sub(r"\s+", " ", (topic or "").strip())
    if not t or t.lower() in META_TOPICS:
        return fallback
    # Strip leading meta labels
    t = re.sub(r"^(learning\s+objectives?|objectives?)\s*[:\-–]?\s*", "", t, flags=re.I).strip()
    if not t or t.lower() in META_TOPICS:
        return fallback
    return t[:120]


def definition_from_claims(term: str, claims: Iterable[str]) -> str:
    """Pick the best claim sentence that actually teaches this term."""
    needle = (term or "").strip().lower()
    if not needle:
        return ""
    best = ""
    for claim in claims:
        text = str(claim or "").strip()
        if not text or needle not in text.lower():
            continue
        # Prefer definitional patterns
        low = text.lower()
        score = 1
        if any(p in low for p in (f"{needle} is ", f"{needle} are ", f"{needle} means", "is when", "is the")):
            score += 5
        if len(text) > 40:
            score += 1
        if score >= 5 or (not best and len(text) > 24):
            if score >= 5 or len(text) > len(best):
                best = text
                if score >= 6:
                    break
    return best[:280]


def enrich_water_cycle_terms(topic: str, existing: list[str]) -> list[tuple[str, str]]:
    """If the lesson is about the water cycle, ensure canonical scientific terms."""
    blob = (topic or "").lower() + " " + " ".join(existing).lower()
    if not any(k in blob for k in ("water cycle", "evaporat", "precipitat", "condens", "water vapour", "water vapor")):
        return []
    have = {e.lower() for e in existing}
    out: list[tuple[str, str]] = []
    for term, definition in WATER_CYCLE_TERMS:
        if term.lower() not in have and not is_junk_term(term):
            out.append((term, definition))
    return out


def build_student_definition(term: str, academic: str, *, topic: str = "") -> str:
    academic = (academic or "").strip()
    display = (term or "").strip()
    if academic and "core concept" not in academic.lower() and "key lesson term" not in academic.lower():
        # Soften long academic lines for students
        if len(academic.split()) > 28:
            first = re.split(r"(?<=[.!?])\s+", academic)[0]
            return first.strip()
        return academic
    topic = clean_topic(topic, fallback="this topic")
    return (
        f"{display} is an important idea in {topic}. "
        f"Use the lesson explanation and examples to say what {display.lower()} means in your own words."
    )


def normalize_vocab_items(
    terms: list[Any],
    *,
    topic: str = "",
    claims: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter junk and attach claim-grounded definitions."""
    claims = claims or []
    topic = clean_topic(topic)
    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    for item in terms:
        if isinstance(item, dict):
            term = str(item.get("term") or item.get("word") or "").strip()
            definition = str(
                item.get("definition")
                or item.get("academic_definition")
                or item.get("simple_explanation")
                or ""
            ).strip()
            example = str(item.get("example") or item.get("example_sentence") or "").strip()
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
        if not definition or "core concept" in definition.lower() or "key lesson term" in definition.lower() or "key word connected" in definition.lower():
            definition = definition_from_claims(term, claims)
        if not definition:
            # water-cycle canonical
            for wt, wd in WATER_CYCLE_TERMS:
                if wt.lower() == key:
                    definition = wd
                    break
        if not definition:
            definition = build_student_definition(term, "", topic=topic)
        if not example:
            example = definition_from_claims(term, claims) or (
                f"In {topic}, we use the word {term} when we explain the main process carefully."
            )
        out.append(
            {
                "term": term[:1].upper() + term[1:] if term else term,
                "definition": definition,
                "academic_definition": definition,
                "simple_explanation": build_student_definition(term, definition, topic=topic),
                "example": example[:220],
                "example_sentence": example[:220],
                "lesson_context": f"{term} helps you explain {topic} accurately.",
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
                "lesson_context": f"{term} is a key stage or idea in {topic}.",
            }
        )

    # Prefer scientific process terms first
    priority = {
        "evaporation": 0,
        "condensation": 1,
        "precipitation": 2,
        "collection": 3,
        "water vapour": 4,
        "water vapor": 4,
        "water cycle": 5,
        "runoff": 6,
        "transpiration": 7,
    }
    out.sort(key=lambda r: priority.get(str(r.get("term") or "").lower(), 50))
    return out[:12]
