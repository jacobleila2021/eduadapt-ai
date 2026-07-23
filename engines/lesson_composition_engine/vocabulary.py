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

POS_GUESS = (
    (r"tion$|sion$|ness$|ment$|ity$|ism$", "noun"),
    (r"ise$|ize$|ate$|ify$", "verb"),
    (r"ous$|ful$|less$|ical$|ive$|able$|ible$", "adjective"),
    (r"ly$", "adverb"),
)


def _guess_pos(term: str) -> str:
    t = (term or "").strip().lower()
    for pattern, pos in POS_GUESS:
        if re.search(pattern, t):
            return pos
    return "noun"


def _syllable_guess(term: str) -> str:
    word = re.sub(r"[^A-Za-z]", "", term or "")
    if not word:
        return ""
    vowels = "aeiouy"
    chunks: list[str] = []
    current = ""
    for i, ch in enumerate(word.lower()):
        current += ch
        if ch in vowels and (i + 1 >= len(word) or word.lower()[i + 1] not in vowels):
            if len(current) > 1 or not chunks:
                chunks.append(current)
                current = ""
    if current:
        if chunks:
            chunks[-1] += current
        else:
            chunks.append(current)
    if len(chunks) <= 1:
        return word.lower()
    return "-".join(chunks)


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
    pronunciation: str = "",
    part_of_speech: str = "",
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
        pr = enrich.get("pronunciation")
        if not pronunciation and isinstance(pr, list) and pr:
            pronunciation = "-".join(str(x) for x in pr)
        elif not pronunciation and isinstance(pr, str):
            pronunciation = pr
        if enrich.get("example_sentence"):
            example_sentence = example_sentence or enrich["example_sentence"]
        if enrich.get("simplified"):
            simple_explanation = simple_explanation or enrich["simplified"]
        reading_level = reading_level or enrich.get("reading_level") or reading_level
    except Exception:  # noqa: BLE001
        pass

    if not pronunciation:
        pronunciation = _syllable_guess(display)
    if not part_of_speech:
        part_of_speech = _guess_pos(display)

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
        memory_tip = (
            f"Close your eyes and picture {display} in the lesson diagram, "
            f"then say: “{display} is…” in one sentence."
        )
    if not lesson_context or is_teacher_facing_text(lesson_context):
        lesson_context = f"You need the word {display} to explain {topic} clearly."
    if not picture:
        picture = picture_cue_for_term(display, definition=academic)

    return VocabularyCard(
        term=display,
        pronunciation=pronunciation,
        part_of_speech=part_of_speech,
        definition=student.strip(),
        simple_explanation=student.strip(),
        academic_definition=academic.strip(),
        example_sentence=(example_sentence or "").strip(),
        memory_tip=memory_tip.strip(),
        lesson_context=lesson_context.strip(),
        picture=(picture or "").strip(),
        synonyms=list(synonyms or []),
        antonyms=list(antonyms or []),
        related_concepts=list(related_concepts or []),
        difficulty=difficulty,
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
                pronunciation=str(item.get("pronunciation") or ""),
                part_of_speech=str(item.get("part_of_speech") or ""),
                color_index=i,
                emoji=str(item.get("emoji") or ""),
                verified=bool(item.get("verified")),
                context=context,
            )
        )

    # Do not pad with topic-token junk; quality over quota
    word_wall = [c.to_word_wall_row() for c in cards]
    flashcards = [
        {
            "front": c.term,
            "back": f"{c.definition} | Example: {c.example_sentence}",
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
    practice = [
        {
            "term": c.term,
            "sentence_blank": (
                c.example_sentence.replace(c.term, "________", 1)
                if c.term in c.example_sentence
                else f"Write one sentence that correctly uses ________ ({c.term})."
            ),
        }
        for c in cards
    ]
    fill_blanks = [
        f"Complete: ________ — {c.definition}"
        for c in cards[:8]
    ]
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
        "lce": {"schema": "1.0.0", "premium_cards": True, "pqle": True},
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
    """Premium flashcard HTML — word visually dominant; PQLE fields included."""
    import html as html_lib

    term = html_lib.escape(str(card.get("term") or "Term"))
    pronunciation = html_lib.escape(str(card.get("pronunciation") or ""))
    pos = html_lib.escape(str(card.get("part_of_speech") or ""))
    student = html_lib.escape(
        str(
            card.get("simple_explanation")
            or card.get("child_friendly")
            or card.get("definition")
            or ""
        )
    )
    academic = html_lib.escape(
        str(card.get("academic_definition") or card.get("definition") or "")
    )
    example = html_lib.escape(str(card.get("example_sentence") or card.get("example") or ""))
    memory = html_lib.escape(str(card.get("memory_tip") or ""))
    context = html_lib.escape(str(card.get("lesson_context") or ""))
    picture = html_lib.escape(str(card.get("picture") or card.get("visual_description") or ""))
    related = card.get("related_words") or card.get("synonyms") or []
    opposite = card.get("opposite_words") or card.get("antonyms") or []
    synonyms = ", ".join(html_lib.escape(str(s)) for s in related[:4])
    antonyms = ", ".join(html_lib.escape(str(s)) for s in opposite[:4])
    concepts = ", ".join(
        html_lib.escape(str(s)) for s in (card.get("related_concepts") or [])[:4]
    )
    difficulty = html_lib.escape(str(card.get("difficulty") or "core"))
    reading = html_lib.escape(str(card.get("reading_level") or "grade_appropriate"))
    color = html_lib.escape(str(card.get("color") or "#e6f7f8"))
    emoji = html_lib.escape(str(card.get("emoji") or "📘"))

    rows = [
        f'<p class="lce-vocab-meta"><span>{pos}</span> · <span>/{pronunciation}/</span></p>'
        if pronunciation or pos
        else "",
        f'<p class="lce-vocab-simple"><strong>Student-friendly</strong> {student}</p>' if student else "",
        f'<p class="lce-vocab-def"><strong>Academic</strong> {academic}</p>'
        if academic and academic != student
        else "",
        f'<p class="lce-vocab-ex"><strong>Example</strong> <em>{example}</em></p>' if example else "",
        f'<p class="lce-vocab-tip"><strong>Memory tip</strong> {memory}</p>' if memory else "",
        f'<p class="lce-vocab-ctx"><strong>In this lesson</strong> {context}</p>' if context else "",
        f'<p class="lce-vocab-pic"><strong>Picture</strong> {picture}</p>' if picture else "",
        f'<p class="lce-vocab-syn"><strong>Related words</strong> {synonyms}</p>' if synonyms else "",
        f'<p class="lce-vocab-ant"><strong>Opposite words</strong> {antonyms}</p>' if antonyms else "",
        f'<p class="lce-vocab-rel"><strong>Related concepts</strong> {concepts}</p>' if concepts else "",
        (
            f'<p class="lce-vocab-tags">'
            f'<span class="lce-tag">{difficulty}</span>'
            f'<span class="lce-tag">{reading}</span></p>'
        ),
    ]
    body = "".join(r for r in rows if r)
    return (
        f'<article class="lce-vocab-card alora-word-wall-card pqle-vocab-card" style="background:{color};">'
        f'<div class="alora-vocab-icon" aria-hidden="true">{emoji}</div>'
        f'<h3 class="lce-vocab-term alora-word-wall-term">{term}</h3>'
        f'<div class="lce-vocab-body alora-word-wall-body">{body}</div>'
        f"</article>"
    )
