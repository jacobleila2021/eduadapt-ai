"""Premium vocabulary composition — publication-quality educational flashcards."""

from __future__ import annotations

import re
from typing import Any

from engines.lesson_composition_engine.schemas import VocabularyCard
from engines.lesson_composition_engine.vocab_quality import (
    build_student_definition,
    clean_topic,
    is_junk_term,
    is_teacher_facing_text,
    normalize_vocab_items,
    picture_cue_for_term,
    student_safe_definition,
)

CARD_COLORS = (
    "#e6f7f8",  # teal mist
    "#e3f2fd",  # sky
    "#ecfdf5",  # mint
    "#fff7ed",  # warm sand
    "#fdf2f8",  # soft rose
    "#f5f3ff",  # soft violet
    "#fef9c3",  # soft lemon
    "#eef2ff",  # indigo mist
)

def _display_term(term: str) -> str:
    raw = (term or "").strip()
    if not raw:
        return ""
    # Capitalize display form; preserve acronyms
    if raw.isupper() and len(raw) <= 5:
        return raw
    return raw[:1].upper() + raw[1:]


def compose_vocabulary_card(
    term: str,
    *,
    definition: str = "",
    simple_explanation: str = "",
    academic_definition: str = "",
    example_sentence: str = "",
    memory_tip: str = "",
    lesson_context: str = "",
    picture: str = "",
    synonyms: list[str] | None = None,
    antonyms: list[str] | None = None,
    related_concepts: list[str] | None = None,
    difficulty: str = "core",
    reading_level: str = "grade_appropriate",
    color_index: int = 0,
    verified: bool = False,
    emoji: str = "",
    context: dict[str, Any] | None = None,
) -> VocabularyCard:
    """Build one premium vocabulary card. Reuses LXP/UCF/VMLE when available."""
    context = context or {}
    display = _display_term(term)

    # Enrich from LXP vocabulary helper (UCF glossary + VMLE pronunciation)
    try:
        from engines.learning_experience_platform.vocabulary import vocabulary_card as lxp_card

        enrich = lxp_card(display, context=context)
        definition = definition or enrich.get("definition") or ""
        picture = picture or enrich.get("picture") or ""
        related_concepts = related_concepts or list(enrich.get("related_concepts") or [])
        verified = verified or bool(enrich.get("verified"))
        if enrich.get("example_sentence"):
            example_sentence = example_sentence or enrich["example_sentence"]
        if enrich.get("simplified"):
            simple_explanation = simple_explanation or enrich["simplified"]
        reading_level = reading_level or enrich.get("reading_level") or reading_level
    except Exception:  # noqa: BLE001
        pass

    # Never keep LXP "not found" / template filler / teacher objectives
    definition = student_safe_definition(definition)
    academic_definition = student_safe_definition(academic_definition)
    simple_explanation = student_safe_definition(simple_explanation)
    example_sentence = student_safe_definition(example_sentence)
    picture = student_safe_definition(picture) if picture and not is_teacher_facing_text(picture) else ""

    for bad in (
        "not found in verified glossary",
        "core concept in this lesson",
        "a key lesson term",
        "key word connected",
        "ask ai tutor",
        "students will",
    ):
        if bad in (definition or "").lower():
            definition = ""
        if bad in (academic_definition or "").lower():
            academic_definition = ""
        if bad in (simple_explanation or "").lower():
            simple_explanation = ""

    academic = (academic_definition or definition or "").strip()
    student = (simple_explanation or "").strip()
    topic = str((context.get("lesson") or {}).get("topic") or context.get("topic") or "")
    topic = clean_topic(topic, fallback="this topic")
    if not student and academic:
        student = build_student_definition(display, academic, topic=topic)
    if not academic and student:
        academic = student
    if not academic:
        academic = build_student_definition(display, "", topic=topic)
        student = academic
    if not example_sentence and display:
        example_sentence = academic if academic and not is_teacher_facing_text(academic) else (
            f"In the water cycle lesson, {display.lower()} helps explain how water moves."
            if "water" in topic.lower()
            else f"Scientists use the word {display} when they explain {topic} clearly."
        )
    if not memory_tip or is_teacher_facing_text(memory_tip):
        memory_tip = f"Say “{display}” once, then point to it on the lesson diagram."
    if not lesson_context or is_teacher_facing_text(lesson_context):
        lesson_context = f"Use the word {display} when you explain {topic} to a friend."
    if not picture:
        picture = picture_cue_for_term(display, definition=academic)

    return VocabularyCard(
        term=display,
        pronunciation="",
        part_of_speech="",
        definition=student.strip(),
        simple_explanation=student.strip(),
        academic_definition=student.strip(),
        example_sentence=(example_sentence or "").strip(),
        memory_tip=memory_tip.strip(),
        lesson_context=lesson_context.strip(),
        picture=(picture or "").strip(),
        synonyms=[],
        antonyms=[],
        related_concepts=[],
        difficulty="",
        reading_level=reading_level,
        color=CARD_COLORS[color_index % len(CARD_COLORS)],
        emoji=emoji or "📘",
        verified=verified,
    )


def compose_vocabulary_page(
    terms: list[Any],
    *,
    topic: str = "",
    context: dict[str, Any] | None = None,
    misconceptions: list[str] | None = None,
    claims: list[str] | None = None,
) -> dict[str, Any]:
    """Full vocabulary study page with premium cards + practice scaffolds."""
    context = context or {}
    topic = clean_topic(topic, fallback=str(context.get("topic") or "Lesson Vocabulary"))
    context = {**context, "topic": topic, "lesson": {**(context.get("lesson") or {}), "topic": topic}}

    claim_pool = list(claims or [])
    for c in context.get("claims") or []:
        if c:
            claim_pool.append(str(c))

    normalized = normalize_vocab_items(terms, topic=topic, claims=claim_pool)
    cards: list[VocabularyCard] = []
    seen: set[str] = set()

    for i, item in enumerate(normalized):
        term = str(item.get("term") or "").strip()
        if not term or term.lower() in seen or is_junk_term(term):
            continue
        seen.add(term.lower())
        cards.append(
            compose_vocabulary_card(
                term,
                definition=str(item.get("definition") or ""),
                simple_explanation=str(item.get("simple_explanation") or ""),
                academic_definition=str(item.get("academic_definition") or item.get("definition") or ""),
                example_sentence=str(item.get("example_sentence") or item.get("example") or ""),
                memory_tip=str(item.get("memory_tip") or ""),
                lesson_context=str(item.get("lesson_context") or ""),
                picture=str(item.get("picture") or ""),
                synonyms=_as_list(item.get("synonyms") or item.get("related_words")),
                antonyms=_as_list(item.get("antonyms") or item.get("opposite_words")),
                related_concepts=_as_list(item.get("related_concepts")),
                difficulty=str(item.get("difficulty") or "core"),
                reading_level=str(item.get("reading_level") or "grade_appropriate"),
                color_index=i,
                emoji=str(item.get("emoji") or ""),
                verified=bool(item.get("verified")),
                context=context,
            )
        )

    # Do not pad with topic-token junk; quality over quota.
    # A card whose meaning is a placeholder ("EARTH is an important idea in…")
    # teaches nothing and poisons flashcards, matching, and fill-blanks —
    # drop it rather than show a wrong meaning.
    def _real_meaning(definition: str) -> bool:
        low = (definition or "").lower()
        return bool(low.strip()) and not any(
            p in low
            for p in (
                "is an important idea in",
                "is a key idea in",
                "find where the lesson explains",
            )
        )

    solid = [c for c in cards if _real_meaning(c.definition)]
    if len(solid) >= 3:
        cards = solid

    # Everyday words ("cloud", "rain") do not belong on a word wall when the
    # lesson offers enough real technical terms — learners study the terms
    # they will actually be assessed on.
    _everyday = {
        "cloud", "clouds", "rain", "sun", "water", "air", "soil",
        "plant", "plants", "earth", "sky", "sea", "land",
    }
    technical = [c for c in cards if c.term.strip().lower() not in _everyday]
    if len(technical) >= 5:
        cards = technical

    word_wall = [c.to_word_wall_row() for c in cards]
    flashcards = [
        {
            "front": c.term,
            "back": (
                f"{c.definition} | Example: {c.example_sentence}"
                if c.example_sentence
                and c.example_sentence.strip().lower() != c.definition.strip().lower()
                else c.definition
            ),
        }
        for c in cards
    ]
    picture_words = [
        {
            "term": c.term,
            "color_cue": c.color,
            "draw_this": c.picture or c.simple_explanation,
            "label": c.term,
        }
        for c in cards
    ]
    def _blank_out(text: str, term: str) -> str:
        """Case-insensitively hide every occurrence of the answer term —
        a fill-blank question must never contain its own answer."""
        if not term:
            return text
        return re.sub(re.escape(term), "________", text, flags=re.IGNORECASE)

    practice = [
        {
            "term": c.term,
            "sentence_blank": (
                _blank_out(c.example_sentence, c.term)
                if re.search(re.escape(c.term), c.example_sentence, re.IGNORECASE)
                else f"Write one sentence that correctly uses ________ ({c.term})."
            ),
        }
        for c in cards
    ]
    def _fill_line(c: VocabularyCard) -> str:
        # Exactly ONE blank per question. When the term appears inside its own
        # definition, blank it there; otherwise put a single blank up front.
        if re.search(re.escape(c.term), c.definition, re.IGNORECASE):
            return f"Complete: {_blank_out(c.definition, c.term)}"
        return f"Complete: ________ — {c.definition}"

    fill_blanks = [_fill_line(c) for c in cards[:8]]
    fill_answers = [c.term for c in cards[:8]]
    reference_chart = [
        {
            "term": c.term,
            "definition": c.definition,
            "synonym": (c.synonyms[0] if c.synonyms else ""),
            "exam_tip": f"Define {c.term} and give one example from the lesson.",
        }
        for c in cards
    ]

    from engines.lesson_composition_engine.diagrams import build_vocabulary_concept_map_svg

    map_terms = [c.term for c in cards if not is_junk_term(c.term)][:8]
    concept_map_svg = build_vocabulary_concept_map_svg(topic, map_terms)
    flowchart_svg = build_vocabulary_concept_map_svg(topic, map_terms, mode="flowchart")

    return {
        "topic": topic,
        "pre_teach": [
            {
                "term": c.term,
                "meaning": c.definition,
                "pronunciation": c.pronunciation or f"Say: {c.term}",
                "picture": c.picture,
                "context_usage": c.lesson_context or c.example_sentence,
            }
            for c in cards
        ],
        "word_wall": word_wall,
        "flashcards": flashcards,
        "picture_words": picture_words,
        "practice": practice,
        "self_test": {
            "fill_blanks": fill_blanks,
            "fill_blank_answers": fill_answers,
        },
        "reference_chart": reference_chart,
        "vocabulary_cards": [c.to_dict() for c in cards],
        "mermaid_diagram": "",
        "svg_diagram": concept_map_svg,
        "concept_map_svg": concept_map_svg,
        "flowchart_svg": flowchart_svg,
        "misconceptions_addressed": list(misconceptions or [])[:6],
        "lce": {
            "schema": "1.0.0",
            "premium_cards": True,
            "pqle": True,
            "pre_teach": True,
            "from_master_lesson": True,
        },
    }


def upgrade_vocabulary_dict(vocab: dict[str, Any], *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Upgrade an existing vocabulary adaptation to premium LCE cards."""
    if not isinstance(vocab, dict):
        return compose_vocabulary_page([], topic="", context=context)
    terms = vocab.get("word_wall") or vocab.get("vocabulary_cards") or []
    topic = str(vocab.get("topic") or "")
    upgraded = compose_vocabulary_page(terms, topic=topic, context=context)
    # Preserve any extra practice already validated
    for key in ("practice", "self_test", "reference_chart"):
        if vocab.get(key) and not upgraded.get(key):
            upgraded[key] = vocab[key]
    return upgraded


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [p.strip() for p in re.split(r"[,;/|]", text) if p.strip()]


def vocabulary_card_html(card: dict[str, Any]) -> str:
    """Student flashcard — WORD and its meaning only (product decision:
    no example / picture idea / memory tip / usage apparatus on the card)."""
    import html as html_lib

    raw_term = str(card.get("term") or "Term").strip()
    display_term = raw_term.upper() if len(raw_term) <= 28 else raw_term
    term = html_lib.escape(display_term)
    meaning = html_lib.escape(
        str(
            card.get("simple_explanation")
            or card.get("child_friendly")
            or card.get("definition")
            or ""
        )
    )
    color = html_lib.escape(str(card.get("color") or "#FFFDF6"))
    emoji = html_lib.escape(str(card.get("emoji") or "📘"))

    body = (
        f'<p class="lce-vocab-simple">{meaning}</p>'
        if meaning
        else f'<p class="lce-vocab-simple">An important word in this lesson.</p>'
    )
    return (
        f'<article class="lce-vocab-card alora-word-wall-card pqle-vocab-card pmes-flashcard student-flashcard" '
        f'style="background:{color};border-top:6px solid #008C95;">'
        f'<div class="alora-vocab-icon pmes-flash-icon" aria-hidden="true">{emoji}</div>'
        f'<h3 class="lce-vocab-term alora-word-wall-term">{term}</h3>'
        f'<div class="lce-vocab-body alora-word-wall-body">{body}</div>'
        f"</article>"
    )
