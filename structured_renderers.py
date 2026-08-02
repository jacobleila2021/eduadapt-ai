"""
Render structured vocabulary, worksheet, and lesson objects with native Streamlit UI.
Guarantees visible sections, colors, and diagrams (not dependent on HTML in markdown).
"""

from __future__ import annotations

import html
import json
import re
from typing import Any

import streamlit as st

from content_renderer import _render_mermaid
from lesson_design import (
    ACCENT_INFO,
    ACCENT_INTRO,
    ACCENT_STORY,
    BG_MAIN,
    BORDER_SUBTLE,
    FONT_STACK,
    TEXT_BODY,
    accent_for_variant,
    classify_section,
    dyslexia_luxe_section_card_html,
    format_visual_practice_html,
    section_card_html,
)
from section_titles import normalize_section_title
_BOX_RENDERERS = {
    "teal": lambda t: st.info(t),
    "blue": lambda t: st.info(t),
    "green": lambda t: st.success(t),
    "orange": lambda t: st.warning(t),
    "intro": lambda t: st.info(f"**Introduction** — {t}"),
    "practice": lambda t: st.success(f"**Practice** — {t}"),
    "check": lambda t: st.warning(f"**Check** — {t}"),
}



def _coerce_dict(content: Any) -> dict | None:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        text = content.strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        if text and not text.startswith("_No content"):
            return {
                "big_idea": "Lesson content",
                "sections": [{"title": "Content", "body": text, "box": "teal"}],
                "mermaid_diagram": "",
                "svg_diagram": "",
                "visual_summary": [],
            }
    return None


def _as_dict(content: Any) -> dict | None:
    return _coerce_dict(content)


def _valid_mermaid(diagram: str) -> bool:
    """True only if the string looks like a real mermaid diagram (avoids blank boxes)."""
    if not diagram or not isinstance(diagram, str):
        return False
    text = diagram.strip().lower()
    if len(text) < 15:
        return False
    keywords = ("flowchart", "graph ", "graph\n", "mindmap", "sequencediagram", "timeline", "classdiagram")
    has_kind = any(k in text for k in keywords)
    has_edges = "-->" in text or "---" in text or "->>" in text
    return has_kind and has_edges


def _valid_svg_diagram(svg: str) -> bool:
    """Reject empty/placeholder SVGs (single circle, no labels, suspicious content)."""
    if not svg or not isinstance(svg, str):
        return False
    text = svg.strip().lower()
    if "<svg" not in text or "</svg>" not in text:
        return False
    if len(text) < 80:
        return False
    # Must contain at least one text label to be educational, not a random shape/flag.
    if "<text" not in text:
        return False
    shape_count = text.count("<rect") + text.count("<circle") + text.count("<path") + text.count("<line") + text.count("<polygon") + text.count("<ellipse")
    return shape_count >= 1


def _fallback_lesson_diagram(lesson: dict) -> str:
    """Deterministic labelled study SVG from lesson sections (never a blank box)."""
    from study_diagram_builder import build_study_diagram_svg

    return build_study_diagram_svg(lesson)


def _word_wall_card_html(word: dict, index: int = 0) -> str:
    """Premium educational flashcard — word dominant, PQLE fields when present."""
    if word.get("pqle_card") or word.get("lce_card") or word.get("memory_tip") or word.get("academic_definition"):
        try:
            from engines.lesson_composition_engine.vocabulary import vocabulary_card_html

            return vocabulary_card_html(word)
        except Exception:
            pass
    term_raw = str(word.get("term") or "Term").strip()
    display = (term_raw[:1].upper() + term_raw[1:]) if term_raw else "Term"
    term = html.escape(display)
    meaning = html.escape(
        word.get("child_friendly")
        or word.get("simple_explanation")
        or word.get("definition")
        or ""
    )
    num = int(word.get("card_number") or (index + 1))
    emoji = html.escape(str(word.get("emoji") or "📘"))

    # Product decision: a word-wall card shows the word and its meaning only.
    body_parts = []
    if meaning:
        body_parts.append(f'<p class="alora-vocab-simple">{meaning}</p>')

    return (
        f'<article class="alora-word-wall-card pqle-vocab-card student-flashcard" data-card="{num}">'
        f'<div class="alora-vocab-number" aria-hidden="true">{num}</div>'
        f'<div class="alora-vocab-icon">{emoji}</div>'
        f'<h3 class="alora-word-wall-term">{term}</h3>'
        f'<div class="alora-word-wall-body">{"".join(body_parts)}</div>'
        f"</article>"
    )


def _lookup_answer(answer_key: list, ref: str) -> str:
    for item in answer_key or []:
        if item.get("question_ref", "").strip().lower() == ref.strip().lower():
            return item.get("model_answer", "")
        if ref.lower() in (item.get("question_ref") or "").lower():
            return item.get("model_answer", "")
    return ""


def _show_answer_button(label: str, answer: str, key: str, *, exam_style: bool = False) -> None:
    if not answer:
        return
    reveal_key = f"revealed_{key}"
    if st.button(f"Show Answer — {label}", key=f"btn_{key}", type="secondary"):
        st.session_state[reveal_key] = True
    if st.session_state.get(reveal_key):
        if exam_style:
            st.markdown(
                f'<div class="exam-answer-reveal">{html.escape(answer)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.success(answer)


def _extract_blank_answer(sentence: str) -> tuple[str, str]:
    """Pull the answer out of a fill-in-the-blank sentence's trailing brackets."""
    text = str(sentence)
    match = re.search(r"\(([^)]*)\)\s*([.!?]?)\s*$", text)
    if not match:
        return text, ""
    raw = match.group(1).strip()
    raw = re.sub(r"^(use|answer|ans|hint)\s*[:\-]\s*", "", raw, flags=re.IGNORECASE).strip()
    if not raw:
        return text, ""
    display = (text[: match.start()].rstrip() + match.group(2)).strip()
    return display, raw


def _clean_fill_blank_display(sentence: str) -> str:
    """Student-facing sentence — no bracket hints or stray dash blanks."""
    display, _ = _extract_blank_answer(sentence)
    text = display or str(sentence)
    text = re.sub(r"\s*\([^)]+\)", "", text)
    text = re.sub(r"[_\-]{3,}\s*\.", "________.", text)
    text = re.sub(r"[_\-]{3,}", "________", text)
    text = re.sub(r"________\s*\.\s*________\.?", "________.", text)
    text = re.sub(r"\.\s*\.", ".", text)
    text = re.sub(r"\s+\.", ".", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    if text and not text.endswith((".", "?", "!")):
        text += "."
    return text


def _clean_practice_blank(text: str) -> str:
    """Remove IPA guides and syllable counts from practice sentences."""
    cleaned = str(text or "").strip()
    cleaned = re.sub(r"—?\s*/[^/]+/\s*", " ", cleaned)
    cleaned = re.sub(r"\s*\(\d+\)\s*$", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def _student_safe_wall(word_wall: list[dict], *, topic: str = "") -> list[dict]:
    """Drop teacher-objective text and junk bare terms before matching / cards."""
    try:
        from engines.lesson_composition_engine.vocab_quality import (
            canonical_definition,
            is_junk_term,
            is_teacher_facing_text,
            normalize_vocab_items,
            picture_cue_for_term,
            student_safe_definition,
        )
    except Exception:  # noqa: BLE001
        return list(word_wall or [])

    cleaned: list[dict] = []
    for w in word_wall or []:
        term = str(w.get("term") or "").strip()
        if not term or is_junk_term(term):
            continue
        definition = student_safe_definition(
            str(w.get("definition") or w.get("academic_definition") or "")
        )
        simple = student_safe_definition(
            str(w.get("simple_explanation") or w.get("child_friendly") or "")
        )
        example = student_safe_definition(
            str(w.get("example") or w.get("example_sentence") or "")
        )
        picture = student_safe_definition(str(w.get("picture") or w.get("draw_this") or ""))
        if not definition:
            definition = canonical_definition(term) or simple
        if not definition:
            continue
        if is_teacher_facing_text(definition):
            definition = canonical_definition(term) or ""
        if not definition:
            continue
        row = dict(w)
        row["term"] = term
        row["definition"] = definition
        row["academic_definition"] = definition
        row["simple_explanation"] = simple or definition
        row["child_friendly"] = simple or definition
        row["example"] = example or definition
        row["example_sentence"] = example or definition
        row["picture"] = picture or picture_cue_for_term(term, definition=definition)
        row["draw_this"] = row["picture"]
        cleaned.append(row)

    if len(cleaned) < 4 or (
        topic
        and any(
            k in topic.lower()
            for k in ("water cycle", "evaporat", "precipitat", "condens", "earth's water")
        )
        and len(cleaned) < 6
    ):
        # Rebuild from canonical water-cycle / claim-safe list when wall is polluted
        rebuilt = normalize_vocab_items(
            cleaned or [w.get("term") for w in (word_wall or []) if w.get("term")],
            topic=topic or "Lesson Vocabulary",
        )
        if rebuilt:
            return rebuilt
    return cleaned or list(word_wall or [])


def _build_matching_section(word_wall: list[dict], *, topic: str = "") -> dict:
    """Structured matching items — answers stored separately for Show Answer only."""
    import hashlib
    import random

    safe_wall = _student_safe_wall(word_wall, topic=topic)
    pairs = [
        (w.get("term", ""), w.get("definition", ""))
        for w in safe_wall[:8]
        if w.get("term") and w.get("definition") and len(str(w.get("definition"))) > 12
    ]
    if not pairs:
        return {
            "matching_terms": [],
            "matching_definitions": [],
            "matching_answer_key": [],
        }

    indexed = list(enumerate(pairs, 1))
    shuffled = list(indexed)
    seed_text = "\n".join(f"{term}\t{definition}" for term, definition in pairs)
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
    random.Random(seed).shuffle(shuffled)
    letters = "ABCDEFGH"

    matching_terms = [{"n": n, "term": term} for n, (term, _) in indexed]
    matching_definitions: list[dict] = []
    answer_key: list[dict] = []
    letter_for_number: dict[int, str] = {}

    for slot, (number, (term, definition)) in enumerate(shuffled):
        letter = letters[slot]
        matching_definitions.append({"letter": letter, "text": definition[:160]})
        letter_for_number[number] = letter

    for number, (term, _) in indexed:
        answer_key.append({"n": number, "letter": letter_for_number.get(number, "")})

    return {
        "matching_terms": matching_terms,
        "matching_definitions": matching_definitions,
        "matching_answer_key": answer_key,
    }


def _answer_fits_sentence(answer: str, sentence: str, word_wall: list[dict]) -> bool:
    """True when the answer plausibly completes the blank for this sentence."""
    if not answer:
        return False
    sent = sentence.lower()
    ans = answer.lower()
    if ans in sent.replace("________", ""):
        return True
    clue_words = set(re.findall(r"[a-z]{4,}", sent.replace("________", " ")))
    for word in word_wall:
        term = (word.get("term") or "").lower()
        defin = (word.get("definition") or "").lower()
        if ans == term:
            def_words = set(re.findall(r"[a-z]{4,}", defin))
            return len(clue_words & def_words) >= 2
        if ans in defin:
            def_words = set(re.findall(r"[a-z]{4,}", defin))
            if len(clue_words & def_words) >= 2:
                return True
    return len(ans.split()) <= 3 and any(w in sent for w in ans.split() if len(w) > 3)


def _infer_term_from_clue(sentence: str, word_wall: list[dict]) -> str:
    """Pick the word-wall term best described by the sentence clue."""
    clue = re.sub(r"________", " ", sentence.lower())
    clue_words = set(re.findall(r"[a-z]{4,}", clue))
    best_term = ""
    best_score = 0.0
    for word in word_wall:
        term = (word.get("term") or "").strip()
        if not term:
            continue
        defin = (word.get("definition") or "").lower()
        child = (word.get("child_friendly") or "").lower()
        def_words = set(re.findall(r"[a-z]{4,}", f"{defin} {child}"))
        if not clue_words or not def_words:
            continue
        overlap = len(clue_words & def_words) / max(len(clue_words), 1)
        if term.lower() in clue and "vocabulary word" not in clue:
            overlap += 0.35
        if overlap > best_score:
            best_score = overlap
            best_term = term
    return best_term if best_score >= 0.2 else ""


def _fill_blank_for_word(word: dict) -> tuple[str, str]:
    """Build a fill-in-the-blank sentence and its correct short answer."""
    term = (word.get("term") or "").strip()
    definition = (word.get("definition") or word.get("child_friendly") or "").strip()
    try:
        from engines.lesson_composition_engine.vocab_quality import (
            canonical_definition,
            student_safe_definition,
        )

        definition = student_safe_definition(definition) or canonical_definition(term)
    except Exception:  # noqa: BLE001
        if "students will" in definition.lower():
            definition = ""
    if not term:
        return "This key idea from the lesson is ________.", ""
    if definition:
        lowered = definition.lower()
        if "students will" in lowered or "learning objective" in lowered:
            return (f"This key term from the lesson is ________.", term)
        if "divide" in lowered or "dividing" in lowered:
            return (
                f"{term} is made of cells that can ________.",
                "divide",
            )
        if "water" in lowered and ("transport" in lowered or "carry" in lowered):
            return (
                f"{term} is responsible for transporting water and ________.",
                "minerals",
            )
        return (
            f"{definition.rstrip('.')}. The vocabulary word is ________.",
            term,
        )
    return (f"This key term from the lesson is ________.", term)


def _prepare_self_test(self_test: dict, word_wall: list[dict], *, topic: str = "") -> dict:
    """Ensure self-test has clean structured matching and semantically correct fill-blank answers."""
    data = dict(self_test or {})
    word_wall = _student_safe_wall(word_wall, topic=topic)
    matching = _build_matching_section(word_wall, topic=topic)
    data["matching_terms"] = matching["matching_terms"]
    data["matching_definitions"] = matching["matching_definitions"]
    data["matching_answer_key"] = matching["matching_answer_key"]
    data.pop("matching_prompt", None)
    data.pop("matching", None)

    target_count = min(8, max(6, len(word_wall)))
    blanks = list(data.get("fill_blanks") or [])
    ai_answers = list(data.get("fill_blank_answers") or data.get("answers") or [])
    if not word_wall:
        data["fill_blanks"] = [
            _clean_fill_blank_display(str(sentence))
            for sentence in blanks
            if str(sentence).strip()
        ]
        data["fill_blank_answers"] = [
            str(answer or "").strip() for answer in ai_answers
        ][: len(data["fill_blanks"])]
        return data

    if len(blanks) < target_count:
        for index in range(len(blanks), target_count):
            sentence, answer = _fill_blank_for_word(word_wall[index % len(word_wall)])
            blanks.append(sentence)
            if len(ai_answers) <= index:
                ai_answers.append(answer)

    rebuilt: list[str] = []
    answers: list[str] = []
    for index, sentence in enumerate(blanks[:target_count], 1):
        raw = str(sentence).strip()
        text = _clean_fill_blank_display(raw)
        polluted = "students will" in text.lower() or "learning objective" in text.lower()
        if "________" not in text or polluted:
            word = word_wall[(index - 1) % len(word_wall)]
            text, default_ans = _fill_blank_for_word(word)
            if len(ai_answers) < index:
                ai_answers.append(default_ans)
            elif polluted:
                ai_answers[index - 1] = default_ans
        rebuilt.append(text)

        probe = dict(data)
        probe["fill_blank_answers"] = ai_answers
        _, resolved = _resolve_fill_blank_answer(raw, index, probe, word_wall)
        if not resolved and index - 1 < len(ai_answers):
            candidate = str(ai_answers[index - 1] or "").strip()
            if candidate:
                canonical = _canonical_wall_term(candidate, _wall_term_map(word_wall))
                resolved = canonical or candidate
        if not resolved:
            word = word_wall[(index - 1) % len(word_wall)]
            _, resolved = _fill_blank_for_word(word)
        if not resolved and "vocabulary word" in text.lower():
            resolved = _infer_term_from_clue(text, word_wall)
        if resolved and not _answer_fits_sentence(resolved, text, word_wall):
            word = word_wall[(index - 1) % len(word_wall)]
            text, fallback = _fill_blank_for_word(word)
            rebuilt[-1] = text
            resolved = fallback
        answers.append(resolved or "")

    # Final guard: a fill-blank sentence must never contain its own answer
    # (e.g. "Complete: ________ — The water cycle is…" with answer "water cycle").
    for i, (sentence, answer) in enumerate(zip(rebuilt, answers)):
        if answer and re.search(re.escape(answer), sentence, re.IGNORECASE):
            rebuilt[i] = re.sub(
                re.escape(answer), "________", sentence, flags=re.IGNORECASE
            )

    data["fill_blanks"] = rebuilt
    data["fill_blank_answers"] = answers
    return data


def _prepare_practice(word_wall: list[dict], topic: str = "") -> list[dict]:
    """Numbered say-spell-use items without pronunciation metadata."""
    items: list[dict] = []
    safe = _student_safe_wall(word_wall, topic=topic)
    for word in safe[:8]:
        term = str(word.get("term") or "").strip()
        definition = str(word.get("definition") or "").strip()
        blank = definition
        if term and term.lower() in blank.lower():
            # blank the term once for say-spell-use
            import re as _re

            blank = _re.sub(_re.escape(term), "________", blank, count=1, flags=_re.I)
        elif definition:
            blank = f"{definition.rstrip('.')}. The key word is ________."
        else:
            blank = f"Write one clear sentence that uses ________ correctly."
        items.append(
            {
                "term": term,
                "sentence_blank": blank,
                "sentence": blank,
            }
        )
    return items


def _render_self_test(self_test: dict, word_wall: list[dict], key_prefix: str, *, topic: str = "") -> None:
    """Match & Review — answers revealed only via Show Answer buttons."""
    prepared = _prepare_self_test(self_test, word_wall, topic=topic)
    terms = prepared.get("matching_terms") or []
    definitions = prepared.get("matching_definitions") or []
    match_key = prepared.get("matching_answer_key") or []
    fill_blanks = prepared.get("fill_blanks") or []
    fill_answers = prepared.get("fill_blank_answers") or []

    if terms and definitions:
        st.markdown("**Part A — Matching**")
        st.caption("Match each numbered term to the correct lettered definition.")
        col_terms, col_defs = st.columns(2)
        with col_terms:
            st.markdown("**Terms**")
            for row in terms:
                st.markdown(f"{row['n']}. {row['term']}")
        with col_defs:
            st.markdown("**Definitions**")
            for row in definitions:
                st.markdown(f"{row['letter']}. {row['text']}")
        if match_key:
            compact = ", ".join(
                f"{row['n']} → {row['letter']}"
                for row in sorted(match_key, key=lambda item: item["n"])
                if row.get("letter")
            )
            if compact:
                _show_answer_button("Matching", compact, f"{key_prefix}_matching")

    if fill_blanks:
        st.markdown("**Part B — Fill in the blank**")
        for index, sentence in enumerate(fill_blanks, 1):
            display = _clean_fill_blank_display(sentence)
            st.markdown(f"{index}. {display}")
            ans = fill_answers[index - 1] if index - 1 < len(fill_answers) else ""
            if ans:
                _show_answer_button(f"Q{index}", ans, f"{key_prefix}_ans_{index}")


def _wall_term_map(word_wall: list[dict]) -> dict[str, str]:
    return {
        (w.get("term") or "").strip().lower(): (w.get("term") or "").strip()
        for w in word_wall
        if (w.get("term") or "").strip()
    }


def _canonical_wall_term(candidate: str, term_map: dict[str, str]) -> str:
    key = (candidate or "").strip().lower()
    return term_map.get(key, "") if key else ""


def _best_wall_term_for_sentence(sentence: str, word_wall: list[dict]) -> str:
    """Pick the longest word-wall term mentioned in the sentence."""
    text_lower = sentence.lower()
    term_map = _wall_term_map(word_wall)
    best = ""
    best_len = 0
    for key, term in term_map.items():
        if re.search(rf"\b{re.escape(key)}\b", text_lower):
            if len(term) > best_len:
                best_len = len(term)
                best = term
    return best


def _resolve_fill_blank_answer(
    sentence: str,
    index: int,
    self_test: dict,
    word_wall: list[dict],
) -> tuple[str, str]:
    """Return (display_sentence, correct_answer) for a fill-in-the-blank."""
    display, bracket_ans = _extract_blank_answer(sentence)
    term_map = _wall_term_map(word_wall)

    answers = self_test.get("fill_blank_answers") or self_test.get("answers") or []
    if index - 1 < len(answers):
        entry = answers[index - 1]
        if isinstance(entry, dict):
            explicit = (entry.get("answer") or entry.get("term") or "").strip()
        else:
            explicit = str(entry or "").strip()
        if explicit:
            canonical = _canonical_wall_term(explicit, term_map) if term_map else ""
            return display or sentence, canonical or explicit

    if bracket_ans:
        canonical = _canonical_wall_term(bracket_ans, term_map) if term_map else ""
        if canonical:
            return display, canonical
        if len(bracket_ans.split()) <= 6:
            return display, bracket_ans

    if term_map:
        matched = _best_wall_term_for_sentence(sentence, word_wall)
        if matched:
            return display or sentence, matched

    return display or sentence, ""


def _render_svg(svg: str, height: int = 260) -> None:
    from svg_sanitizer import sanitize_svg

    safe_svg = sanitize_svg(svg)
    if not safe_svg:
        return
    st.markdown(
        f'<div class="alora-study-diagram" style="display:flex;justify-content:center;'
        f'align-items:center;max-width:100%;overflow-x:auto;padding:1rem 0;">'
        f'{safe_svg}</div>',
        unsafe_allow_html=True,
    )


def _render_picture_words(picture_words: list[dict], topic: str, key_prefix: str) -> None:
    """Picture Words retired — no learner value; keep stub for callers."""
    del picture_words, topic, key_prefix
    return


def render_vocabulary(data: Any, key_prefix: str = "vocab") -> None:
    """Word Wall, Flashcards, Practice, Self-Test — always visible."""
    vocab = _coerce_dict(data)
    if not vocab or not vocab.get("word_wall"):
        st.error(
            "Vocabulary sections were not generated correctly. "
            "Click **Clear Session**, then **Generate Adaptations** again (~8–12 min)."
        )
        with st.expander("Technical details"):
            st.write(type(data).__name__, str(data)[:800] if data else "empty")
        return

    topic = vocab.get("topic", "Lesson Vocabulary")
    st.subheader(f"📖 {topic}")

    # --- 1. Word Wall ---
    st.markdown("### 1. Word Wall — Study First")
    word_wall = _student_safe_wall(vocab.get("word_wall") or [], topic=str(topic))
    if not word_wall:
        st.warning("No word wall terms generated.")
    else:
        cards = "".join(
            _word_wall_card_html(word, index=i) for i, word in enumerate(word_wall)
        )
        st.markdown(
            f'<div class="alora-word-wall">{cards}</div>',
            unsafe_allow_html=True,
        )

    # --- 2. Flashcards ---
    st.markdown("### 2. Flashcards — Term → Meaning")
    flashcards = vocab.get("flashcards") or []
    if not flashcards and word_wall:
        flashcards = [
            {"front": w.get("term"), "back": w.get("definition")} for w in word_wall[:8]
        ]
    for index, card in enumerate(flashcards, 1):
        front = card.get("front") or card.get("term", "")
        back = card.get("back") or card.get("definition", "")
        try:
            from engines.lesson_composition_engine.vocab_quality import (
                canonical_definition,
                student_safe_definition,
            )

            back = student_safe_definition(str(back)) or canonical_definition(str(front)) or back
        except Exception:  # noqa: BLE001
            if "students will" in str(back).lower():
                back = str(front)
        with st.expander(f"Card {index}: **{front}** — tap to reveal"):
            st.write(back)

    # Picture Words / Picture Wall removed — no educational value for learners.

    # --- 3. Say · Spell · Use ---
    st.markdown("### 3. Say It · Spell It · Use It")
    practice = _prepare_practice(word_wall, topic) or vocab.get("practice") or []
    for index, item in enumerate(practice, 1):
        term = item.get("term", "")
        blank = _clean_practice_blank(item.get("sentence_blank") or item.get("sentence", ""))
        st.markdown(f"**{index}. {term}**")
        if blank:
            st.markdown(f"_{blank}_")

    # --- 4. Self-Test ---
    st.markdown("### 4. Match & Review (Self-Test)")
    self_test = vocab.get("self_test") or {}
    _render_self_test(self_test, word_wall, key_prefix, topic=str(topic))

    # --- 5. Quick Reference ---
    st.markdown("### 5. Quick Reference Chart")
    chart = vocab.get("reference_chart") or []
    if chart:
        st.table(
            [
                {
                    "Term": row.get("term", ""),
                    "Definition": row.get("definition", ""),
                    "Synonym": row.get("synonym", ""),
                    "Exam tip": row.get("exam_tip", ""),
                }
                for row in chart
            ]
        )

    # --- 6. Concept Map (built from Word Wall — does not need AI mermaid) ---
    st.markdown("---")
    st.markdown("### 6. Concept Map")
    st.caption("Study how all vocabulary terms connect to the main topic.")
    from concept_map_builder import render_concept_map_streamlit

    render_concept_map_streamlit(vocab)


def render_worksheet(data: Any, key_prefix: str = "worksheet") -> None:
    """Exam paper layout with short answer, long answer, checklist."""
    sheet = _coerce_dict(data)
    if not sheet or not sheet.get("short_answer"):
        st.error(
            "Worksheet sections were not generated correctly. "
            "Click **Clear Session**, then **Generate Adaptations** again."
        )
        with st.expander("Technical details"):
            st.write(type(data).__name__, str(data)[:800] if data else "empty")
        return

    header = sheet.get("header") or {}
    st.markdown(
        f"""
        <div class="exam-print-header">
          <p><strong>Subject:</strong> ______________________</p>
          <p><strong>Lesson:</strong> ______________________</p>
          <p><strong>Time:</strong> ______________________</p>
          <p><strong>Marks:</strong> ______________________</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text_input("Name", key=f"{key_prefix}_name", placeholder="Student name")
    st.text_input("Date", key=f"{key_prefix}_date", placeholder="Date")

    # Part A — Short answer
    answer_key = sheet.get("answer_key") or []
    st.markdown("### Part A — Short Answer")
    for index, item in enumerate(sheet.get("short_answer") or [], 1):
        marks = item.get("marks", 2)
        st.markdown(f"**Q{index}. ({marks} marks)** {item.get('question', '')}")
        st.text_area(
            f"Your answer — Q{index}",
            key=f"{key_prefix}_sa_input_{index}",
            height=int(item.get("lines", 3)) * 28,
            label_visibility="collapsed",
            placeholder="Type your answer here…",
        )
        ref = f"Part A Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_sa_{index}", exam_style=True)
        st.markdown("")

    # Part B — Long answer
    st.markdown("### Part B — Long Answer")
    for index, item in enumerate(sheet.get("long_answer") or [], 1):
        marks = item.get("marks", 6)
        st.markdown(f"**Q{index}. ({marks} marks)** {item.get('question', '')}")
        st.text_area(
            f"Your answer — long Q{index}",
            key=f"{key_prefix}_la_input_{index}",
            height=int(item.get("lines", 8)) * 24,
            label_visibility="collapsed",
            placeholder="Type your extended answer here…",
        )
        ref = f"Part B Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_la_{index}", exam_style=True)
        st.markdown("")

    # Part C — Diagram (always show a labelled SVG for chemistry / science pathways)
    diagram = sheet.get("diagram_question") or {}
    if diagram:
        st.markdown("### Part C — Diagram Question")
        st.markdown(
            f"**({diagram.get('marks', 4)} marks)** {diagram.get('question', '')}"
        )
        svg = diagram.get("svg_diagram") or diagram.get("svg", "")
        if not _valid_svg_diagram(svg):
            # Recover a teaching diagram from the worksheet topic rather than
            # asking learners to redraw an empty box.
            try:
                from engines.lesson_composition_engine.diagrams import (
                    build_educational_flowchart_svg,
                )
                from engines.lesson_composition_engine.vocab_quality import (
                    ACIDS_BASES_SALTS_TERMS,
                )

                topic = str((sheet.get("header") or {}).get("topic") or "").strip()
                if not topic or topic.lower() in {"lesson", "lesson topic"}:
                    topic = "Acids, Bases and Salts"
                stages = [t for t, _ in ACIDS_BASES_SALTS_TERMS][:5]
                if any(k in topic.lower() for k in ("acid", "base", "salt")):
                    svg = build_educational_flowchart_svg(
                        topic, stages, subtitle="Label each idea"
                    )
            except Exception:
                svg = ""
        if _valid_svg_diagram(svg):
            _render_svg(svg)
            st.markdown("_Label the diagram above on your answer sheet._")
        else:
            st.caption("Diagram unavailable — answer using the lesson pathway labels.")
        dia_ans = diagram.get("model_answer", "") or _lookup_answer(answer_key, "Part C")
        _show_answer_button("Part C", dia_ans, f"{key_prefix}_dia", exam_style=True)

    # Part D — Vocab in context
    st.markdown("### Part D — Vocabulary in Context")
    for index, item in enumerate(sheet.get("vocab_questions") or [], 1):
        marks = item.get("marks", 1)
        st.markdown(f"**{index}. ({marks} mark)** {item.get('question', '')}")
        st.text_input(
            f"Vocab answer {index}",
            key=f"{key_prefix}_vq_input_{index}",
            label_visibility="collapsed",
            placeholder="Type your answer…",
        )
        ref = f"Part D Q{index}"
        ans = item.get("model_answer", "") or _lookup_answer(answer_key, ref)
        _show_answer_button(ref, ans, f"{key_prefix}_vq_{index}", exam_style=True)

    # Part E — Student checklist
    st.markdown("### Part E — Exam Ready Checklist")
    for index, tip in enumerate(sheet.get("student_checklist") or []):
        st.checkbox(tip, key=f"{key_prefix}_check_{index}")

    # Teacher sections
    with st.expander("Teacher: Differentiation Map (Part F)"):
        st.markdown(sheet.get("teacher_differentiation", "—"))

    with st.expander("Teacher: Answer Key & Marking Guide (Part G)"):
        for item in sheet.get("answer_key") or []:
            ref = item.get("question_ref") or item.get("question", "")
            st.markdown(f"**{ref}**")
            st.write(item.get("model_answer", ""))
            notes = item.get("marks_notes") or item.get("notes", "")
            if notes:
                st.caption(notes)
        from docx_exporter import export_worksheet_docx

        st.download_button(
            "Download Teacher Word (with answer key)",
            data=export_worksheet_docx(sheet, include_teacher_key=True),
            file_name="exam_worksheet_teacher.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"{key_prefix}_teacher_docx",
        )


def _plain_lesson_text(raw: str, *, preserve_lines: bool = False) -> str:
    """Strip HTML/markdown artefacts so lesson text never shows raw tags."""
    if not raw:
        return ""
    text = html.unescape(str(raw))
    text = re.sub(r"<a[^>]*>.*?</a>", " ", text, flags=re.I | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    if preserve_lines:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _lesson_map_items(lesson: dict) -> list[dict]:
    """Build complete concept cards from taught sections (Parent / Visual index)."""
    items: list[dict] = []
    for index, section in enumerate(lesson.get("sections") or []):
        if not isinstance(section, dict):
            continue
        role = str(section.get("role") or "").lower()
        if (
            section.get("presentation_only")
            or role.startswith("presentation_")
            or role in {"practice_question", "exam_question", "hots_question", "assessment"}
        ):
            continue
        # Concept cards: taught theory + summary only (not coaching appendices).
        if role.endswith("_support"):
            continue
        if role not in {"", "concept", "introduction", "worked_example", "summary", "revision"}:
            # Keep unknown teaching roles; skip pure presentation chrome.
            if role.startswith("presentation"):
                continue
        body = _plain_lesson_text(section.get("body") or "", preserve_lines=True)
        raw_title = section.get("title") or f"Section {index + 1}"
        title = normalize_section_title(raw_title, body, index)
        if not body:
            continue
        # Full teaching text — never leave concept boxes halfway cut.
        idea = body.strip()
        if len(idea) > 520:
            idea = idea[:517].rsplit(" ", 1)[0] + "…"
        variant = classify_section(
            title, str(section.get("box") or "none").lower(), index
        )
        items.append(
            {
                "icon": f"{index + 1:02d}",
                "title": title,
                "idea": idea,
                "hex": accent_for_variant(variant),
            }
        )
        if len(items) >= 12:
            break
    return items


def _render_lesson_wall_cards(lesson: dict, *, heading: str = "Lesson wall") -> None:
    """Publisher-quality concept cards (Parent 'Key ideas' wall) for any adaptation."""
    items = _lesson_map_items(lesson)
    if not items:
        return
    st.markdown(f"#### {html.escape(heading)}")
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            hex_colour = html.escape(str(item.get("hex") or ACCENT_INFO))
            title = html.escape(str(item.get("title") or "Idea"))
            idea = html.escape(str(item.get("idea") or "")).replace("\n", "<br/>")
            st.markdown(
                f'<div style="background:#FFF9EE;border:3px solid {hex_colour};'
                f'border-radius:14px;padding:1rem 1.1rem;margin:0.55rem 0;'
                f'min-height:8.5rem;">'
                f'<h4 style="margin:0 0 0.55rem 0;color:{hex_colour};font-size:1.05rem;">'
                f'{title}</h4>'
                f'<div style="color:#111827;font-size:0.95rem;line-height:1.55;">{idea}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )


def _render_parent_concept_cards(lesson: dict) -> None:
    """Parent view: complete concept cards instead of a thin line-chart overview."""
    _render_lesson_wall_cards(lesson, heading="Key ideas for home")


_LESSON_WALL_HEADINGS = {
    "standard": "Lesson wall",
    "ell": "Lesson wall — clear English",
    "visual": "Lesson wall — see each idea",
    "auditory": "Lesson wall — listen to each idea",
    "ld": "Lesson wall — one step at a time",
    "dyslexia": "Lesson wall — calm reading strips",
    "parent": "Key ideas for home",
}


def _is_practice_section(title: str) -> bool:
    return "practice" in (title or "").lower()


def _is_question_section(title: str, role: str = "") -> bool:
    blob = f"{title} {role}".lower()
    return any(
        k in blob
        for k in (
            "practice",
            "exam",
            "hots",
            "mcq",
            "assertion",
            "case study",
            "application",
            "question",
        )
    ) and "answer key" not in blob


def _parse_qa_pairs(body: str) -> list[dict[str, Any]]:
    """Parse 'N. question / Answer: …' blocks even if newlines were collapsed."""
    text = (body or "").strip()
    if not text:
        return []
    # Normalize OCR / broken answer markers: "{ Answer", "( Answer", "- Answer"
    text = re.sub(r"[\{\(\[]\s*(Answer\b\s*:?)", r"\1", text, flags=re.I)
    text = re.sub(r"(Answer\b\s*:?)\s*[\)\}\]]", r"\1 ", text, flags=re.I)
    text = re.sub(r"\s*[-–]\s*[\{\(]?\s*(Answer\b\s*:?)", r"\nAnswer: ", text, flags=re.I)
    # Restore structure when whitespace was flattened into one paragraph.
    text = re.sub(r"\s+(Answer\b\s*:?)\s+", r"\nAnswer: ", text, flags=re.I)
    text = re.sub(r"(?<!\n)\s+(\d+)\.\s+", r"\n\1. ", text)
    text = re.sub(r"(?<!\n)\s+(Question\s+\d+)\.\s*", r"\n\1. ", text, flags=re.I)
    pairs: list[dict[str, Any]] = []
    chunks = re.split(r"(?m)^\s*(?=(?:\d+|Question\s+\d+)\.\s)", text)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        m = re.match(r"^(?:Question\s+)?(\d+)\.\s*(.*)$", chunk, re.S | re.I)
        if not m:
            continue
        num = int(m.group(1))
        rest = m.group(2).strip()
        parts = re.split(r"(?im)^answer\s*:?\s*", rest, maxsplit=1)
        if len(parts) == 1:
            parts = re.split(r"(?i)\bAnswer\s*:?\s*", rest, maxsplit=1)
        question = parts[0].strip(" -–\t")
        answer = parts[1].strip() if len(parts) > 1 else ""
        answer = re.sub(r"^[\{\(\[]+|[\}\)\]]+$", "", answer).strip()
        # Drop glued extra stems after a dash that are separate questions.
        if " - " in question and not question.rstrip().endswith("?"):
            # Keep first clear stem when OCR joined several questions.
            bits = [b.strip() for b in re.split(r"\s+-\s+", question) if b.strip()]
            if len(bits) >= 2 and any("?" in b or len(b.split()) >= 4 for b in bits):
                question = bits[0]
        if not question or question.lower() in {"answer", "{", "("}:
            continue
        marks_m = re.search(r"\((\d+)\s*marks?\)", question, re.I)
        pairs.append(
            {
                "n": num,
                "question": question,
                "answer": answer,
                "marks": int(marks_m.group(1)) if marks_m else None,
            }
        )
    return pairs


def _clean_exam_answer(answer: str) -> str:
    """Strip coaching prefixes so the learner sees exam-ready prose only."""
    text = str(answer or "").strip()
    text = re.sub(r"(?i)^(the\s+answer\s+is|answer\s*:)\s*", "", text).strip()
    text = re.sub(r"(?i)\bthe\s+answer\s+is\s+", "", text).strip()
    text = re.sub(r"^[\{\(\[]+|[\}\)\]]+$", "", text).strip()
    return text


def _render_qa_section(title: str, body: str, *, spec_id: str | None, variant: str) -> None:
    """Show questions; reveal model answers only via Show Answer."""
    del spec_id
    if not (body or "").strip():
        return
    pairs = _parse_qa_pairs(body)
    accent = accent_for_variant(variant)
    if not pairs:
        # Strip inline answers before falling back to a plain card.
        plain = _plain_lesson_text(body, preserve_lines=True)
        plain = re.sub(r"(?is)\bAnswer\s*:.*", "", plain).strip()
        plain = re.sub(r"(?is)[\{\(]\s*Answer\b.*", "", plain).strip()
        if not plain.strip():
            return
        if re.match(r"(?i)^board-style practice\b", plain) and "Answer:" not in plain:
            return
        st.markdown(section_card_html(title, plain, variant), unsafe_allow_html=True)
        return

    st.markdown(
        f'<div class="alora-lesson-section" style="background:{BG_MAIN};border:6px solid {accent};'
        f'border-radius:16px;padding:20px 24px 12px;margin:1.25rem 0;">'
        f'<h3 style="color:{accent};font-weight:700;font-size:1.35rem;margin:0 0 1rem 0;">'
        f"{html.escape(title)}</h3>",
        unsafe_allow_html=True,
    )
    for pair in pairs:
        q = str(pair.get("question") or "").strip()
        a = _clean_exam_answer(str(pair.get("answer") or ""))
        if not q:
            continue
        st.markdown(
            f'<div style="margin:0 0 1.35rem 0;padding:1rem 1.15rem;background:#FFFDF6;'
            f'border-radius:12px;border-left:5px solid {accent};">'
            f'<p style="font-weight:700;margin:0 0 0.65rem 0;line-height:1.7;color:{TEXT_BODY};">'
            f'<span style="color:{accent};">Question {pair["n"]}.</span> {html.escape(q)}</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
        if a:
            _show_answer_button(
                f"{title} Q{pair['n']}",
                a,
                f"lesson_qa_{re.sub(r'[^a-z0-9]+', '_', (title or '').lower())}_{pair['n']}",
                exam_style=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


def _practice_section_card_html(title: str, body: str, variant: str) -> str:
    """Visual learner practice — numbered Q then A on separate lines."""
    accent = accent_for_variant(variant)
    safe_title = html.escape(title)
    body_html = format_visual_practice_html(body)
    return f"""
    <div class="alora-lesson-section alora-practice-section" style="
        background:{BG_MAIN};
        border:6px solid {accent};
        border-radius:16px;
        padding:28px 32px;
        margin:1.25rem 0;
        box-shadow:0 2px 8px rgba(51,51,51,0.06);
        text-align:left;
        font-family:{FONT_STACK};
        color:{TEXT_BODY};">
      <h3 style="color:{accent};font-weight:700;font-size:1.35rem;margin:0 0 1rem 0;
          font-family:{FONT_STACK};">📝 {safe_title}</h3>
      <div class="alora-lesson-body" style="font-size:1.05rem;color:{TEXT_BODY};max-width:52em;">
        {body_html}
      </div>
    </div>
    """


def _render_teacher_answer_key(lesson: dict) -> None:
    """Teacher Version — answer key expander with marking guide."""
    answer_key = lesson.get("answer_key") or []
    if not answer_key:
        return

    st.markdown("---")
    with st.expander("📋 Teacher Answer Key & Marking Guide", expanded=True):
        for index, item in enumerate(answer_key, 1):
            section = item.get("section", "")
            question = item.get("question", item.get("question_ref", ""))
            answer = item.get("model_answer", item.get("answer", ""))
            marks = item.get("marks", "")
            marks_label = f" ({marks} marks)" if marks else ""
            header = f"**{index}. {section}**{marks_label}" if section else f"**{index}.**"
            st.markdown(header)
            if question:
                st.markdown(f"*Q:* {question}")
            st.markdown(f"*Answer:* {answer}")
            notes = item.get("marks_notes", "")
            if notes:
                st.caption(f"Marking: {notes}")
            st.markdown("")

        notes = (lesson.get("teacher_notes") or "").strip()
        if notes:
            st.markdown("**Teacher Notes**")
            st.markdown(notes)

        diff_map = (lesson.get("differentiation_map") or "").strip()
        if diff_map:
            st.markdown("**Differentiation Map**")
            st.markdown(diff_map)


def render_lesson(data: Any, spec_id: str | None = None) -> None:
    """Structured lesson with colored callouts, diagram, and sections."""
    lesson = _coerce_dict(data)
    if not lesson or not (lesson.get("sections") or lesson.get("big_idea")):
        st.error(
            "Lesson sections were not generated correctly. "
            "Use **Clear Session** → **Generate Adaptations** again."
        )
        if data:
            with st.expander("Raw content"):
                st.write(str(data)[:1500])
        return

    sections = lesson.get("sections") or []
    bullet_mode = spec_id == "ld"
    is_visual = spec_id == "visual"
    is_ld = spec_id == "ld"
    is_parent = spec_id == "parent"
    visual_concepts = [
        str(c).strip()
        for c in (
            (lesson.get("lce") or {}).get("concepts")
            or lesson.get("revision_points")
            or []
        )
        if str(c).strip()
    ]
    if not visual_concepts:
        # Recover concept names from section titles / Must Know style lists.
        for sec in sections:
            if not isinstance(sec, dict):
                continue
            if str(sec.get("role") or "") != "concept":
                continue
            title = str(sec.get("title") or "")
            m = re.search(r"(?i)(?:understanding|what are)\s+(.+?)\??$", title.strip())
            if m:
                visual_concepts.append(m.group(1).strip().rstrip("?"))
    visual_concepts = [re.sub(r"(?i)^explain:\s*", "", c).strip() for c in visual_concepts]
    visual_concepts = [c for c in visual_concepts if c][:10]

    wall_heading = _LESSON_WALL_HEADINGS.get(spec_id or "")
    if wall_heading:
        _render_lesson_wall_cards(lesson, heading=wall_heading)

    verified = lesson.get("verified_visuals") or []
    rendered_verified = False
    if verified:
        st.markdown("#### Lesson Visuals")
        from pathlib import Path

        for vis in verified:
            if not isinstance(vis, dict):
                continue
            caption = vis.get("caption") or "Lesson visual"
            st.markdown(f"**{caption}**")
            paths = vis.get("asset_paths") or []
            showed_asset = False
            for path in paths:
                p = Path(path)
                if p.is_file():
                    st.image(str(p), caption=caption)
                    showed_asset = True
                    rendered_verified = True
            if vis.get("iframe_url"):
                try:
                    st.components.v1.iframe(vis["iframe_url"], height=360, scrolling=True)
                    showed_asset = True
                    rendered_verified = True
                except Exception:
                    st.markdown(f"[Open interactive]({vis['iframe_url']})")
                    showed_asset = True
                    rendered_verified = True
            # UVIE organisers often ship svg/mermaid without asset_paths — render them.
            if not showed_asset:
                svg = vis.get("svg") or vis.get("svg_diagram") or ""
                if _valid_svg_diagram(svg):
                    _render_svg(svg)
                    rendered_verified = True
                else:
                    mermaid = (vis.get("mermaid") or vis.get("mermaid_diagram") or "").strip()
                    if mermaid and _valid_mermaid(mermaid):
                        _render_mermaid(mermaid)
                        rendered_verified = True

    # When no subject engine / UVIE visual actually rendered, show Alora's
    # deterministic, content-labelled study diagram (never an AI sketch).
    if not rendered_verified:
        st.markdown("#### Lesson Visual")
        pkg = lesson.get("diagram_package") if isinstance(lesson.get("diagram_package"), dict) else {}
        # Prefer domain concept map (water-cycle figure) over a generic vertical stack.
        try:
            from engines.lesson_composition_engine.publisher_remediation import (
                is_generic_subject_flowchart,
            )
        except Exception:  # noqa: BLE001
            def is_generic_subject_flowchart(_svg: str) -> bool:  # type: ignore
                return False

        candidates = [
            str(pkg.get("svg") or ""),
            str(lesson.get("concept_map_svg") or ""),
            str(lesson.get("svg_diagram") or ""),
            str(lesson.get("flowchart_svg") or ""),
        ]
        svg = next(
            (c for c in candidates if c and not is_generic_subject_flowchart(c)),
            "",
        )
        if not svg:
            svg = next((c for c in candidates if c), "")
        if _valid_svg_diagram(svg):
            title = html.escape(str(pkg.get("title") or lesson.get("topic") or "Lesson diagram"))
            caption = html.escape(str(pkg.get("caption") or "A labelled teaching diagram for this lesson."))
            explain = html.escape(str(pkg.get("explanation") or ""))
            practice = html.escape(str(pkg.get("practice_question") or ""))
            callouts = pkg.get("callouts") or []
            callout_html = "".join(
                f'<li>{html.escape(str(c))}</li>' for c in callouts[:5]
            )
            st.markdown(
                f'<figure class="pmes-diagram-figure">'
                f'<figcaption><strong>{title}</strong></figcaption>'
                f"</figure>",
                unsafe_allow_html=True,
            )
            _render_svg(svg)
            st.markdown(
                f'<div class="pmes-diagram-figure">'
                f'<p class="pmes-diagram-explain"><em>{caption}</em></p>'
                + (f'<p class="pmes-diagram-explain">{explain}</p>' if explain else "")
                + (f'<ul>{callout_html}</ul>' if callout_html else "")
                + (f'<p class="pmes-diagram-practice"><strong>Try this</strong> {practice}</p>' if practice else "")
                + "</div>",
                unsafe_allow_html=True,
            )
        else:
            from study_diagram_builder import resolve_study_diagram_svg

            st.caption("A labelled study diagram built directly from this lesson.")
            _render_svg(resolve_study_diagram_svg(lesson))

    for idx, section in enumerate(sections):
        if not isinstance(section, dict):
            continue
        title_low = str(section.get("title") or "").strip().lower()
        if (
            title_low
            in {
                "step by step",
                "reflect: i can",
                "must-learn ideas",
                "must learn ideas",
                "must know",
                "big idea",
                "using the diagram",
                "see · label · trace",
                "see label trace",
                "what you will learn",
                "key ideas connect",
            }
            or "key ideas connect" in title_low
            or title_low.startswith("reflect")
        ):
            continue
        # Teacher-procedure / presentation chrome is not lesson theory.
        # Student tabs show curriculum sections only; Parent keeps home coaching.
        role = str(section.get("role") or "").lower()
        allow_support = (spec_id == "teacher" and role.endswith("_support")) or (
            is_parent and role == "parent_support"
        )
        if not allow_support and (
            section.get("presentation_only")
            or role.startswith("presentation_")
            or role.endswith("_support")
            or role == "concept_primer"
        ):
            continue
        # Parent / student lesson walls lead with cards — skip repeating the same
        # theory paragraphs underneath (questions & summary still show).
        if wall_heading and role in {"concept", "introduction", "worked_example"}:
            continue
        raw_title = section.get("title", "") or f"Section {idx + 1}"
        body = section.get("body", "")
        title = normalize_section_title(raw_title, body, idx)
        box = (section.get("box") or "none").lower()
        variant = classify_section(title, box, idx)
        st.markdown(f'<span id="sec_{idx}"></span>', unsafe_allow_html=True)
        if body:
            if not str(body).strip():
                continue
            if _is_question_section(title, role):
                _render_qa_section(
                    title,
                    str(body),
                    spec_id=spec_id,
                    variant=variant,
                )
                continue
            keep_lines = (is_visual and _is_practice_section(title)) or is_ld or (
                "Answer:" in str(body)
            ) or (role == "summary")
            plain_body = _plain_lesson_text(body, preserve_lines=keep_lines)
            if not plain_body.strip():
                continue
            if is_visual and _is_practice_section(title):
                card = _practice_section_card_html(title, plain_body, variant)
            elif is_ld:
                card = dyslexia_luxe_section_card_html(
                    title, plain_body, variant, index=idx + 1
                )
            elif is_visual:
                card = section_card_html(
                    title,
                    plain_body,
                    variant,
                    visual_concepts=visual_concepts,
                )
            else:
                card = section_card_html(
                    title,
                    plain_body,
                    variant,
                    bullet_mode=bullet_mode,
                )
            st.markdown(card, unsafe_allow_html=True)

    if spec_id == "teacher":
        _render_teacher_answer_key(lesson)

    return


def vocabulary_to_text(data: Any) -> str:
    vocab = _as_dict(data) or {}
    lines = [f"# Vocabulary — {vocab.get('topic', 'Lesson')}", ""]
    lines.append("## 1. Word Wall")
    for word in vocab.get("word_wall") or []:
        lines.append(f"- **{word.get('term', '')}**: {word.get('definition', '')}")
    lines.append("\n## 2. Flashcards")
    for card in vocab.get("flashcards") or []:
        lines.append(f"- Front: {card.get('front', '')} | Back: {card.get('back', '')}")
    lines.append("\n## 3. Say · Spell · Use")
    practice = _prepare_practice(vocab.get("word_wall") or [], vocab.get("topic", ""))
    for index, item in enumerate(practice, 1):
        blank = _clean_practice_blank(item.get("sentence_blank", ""))
        lines.append(f"{index}. {item.get('term', '')}: {blank}")
    lines.append("\n## 4. Self-Test")
    self_test = _prepare_self_test(vocab.get("self_test") or {}, vocab.get("word_wall") or [])
    if self_test.get("matching_terms"):
        lines.append("Part A — Matching")
        for row in self_test["matching_terms"]:
            lines.append(f"{row['n']}. {row['term']}")
        for row in self_test.get("matching_definitions") or []:
            lines.append(f"{row['letter']}. {row['text']}")
    if self_test.get("fill_blanks"):
        lines.append("Part B — Fill in the blank")
        for index, sentence in enumerate(self_test["fill_blanks"], 1):
            lines.append(f"{index}. {_clean_fill_blank_display(sentence)}")
    lines.append("\n## 5. Quick Reference")
    for row in vocab.get("reference_chart") or []:
        lines.append(
            f"- **{row.get('term', '')}**: {row.get('definition', '')} "
            f"(Exam tip: {row.get('exam_tip', '')})"
        )
    lines.append("\n## 7. Concept Map")
    from concept_map_builder import _topic_and_terms

    topic, terms = _topic_and_terms(vocab)
    lines.append(f"Central topic: **{topic}**")
    lines.append("Linked terms: " + ", ".join(terms))
    lines.append("(Download HTML for the full coloured flowchart.)")
    return "\n".join(lines)


def worksheet_to_text(data: Any) -> str:
    sheet = _as_dict(data) or {}
    lines = ["# Exam Practice Worksheet", ""]
    for index, item in enumerate(sheet.get("short_answer") or [], 1):
        lines.append(f"Q{index}. ({item.get('marks', 2)} marks) {item.get('question', '')}")
    lines.append("\n## Long Answer")
    for index, item in enumerate(sheet.get("long_answer") or [], 1):
        lines.append(f"Q{index}. ({item.get('marks', 6)} marks) {item.get('question', '')}")
    return "\n".join(lines)


def lesson_to_text(data: Any) -> str:
    lesson = _as_dict(data)
    if not lesson:
        return str(data)
    parts = [f"Big Idea: {lesson.get('big_idea', '')}", ""]
    for section in lesson.get("sections") or []:
        parts.append(f"## {section.get('title', '')}")
        parts.append(section.get("body", ""))
    return "\n".join(parts)


def content_to_export(title: str, content: Any, spec_id: str) -> str:
    parsed = _coerce_dict(content) if spec_id != "original" else None
    if spec_id == "vocabulary":
        return f"# {title}\n\n{vocabulary_to_text(parsed or content)}"
    if spec_id == "worksheet":
        return f"# {title}\n\n{worksheet_to_text(parsed or content)}"
    if parsed:
        return f"# {title}\n\n{lesson_to_text(parsed)}"
    from content_renderer import strip_mermaid_for_export

    return f"# {title}\n\n{strip_mermaid_for_export(str(content))}"
