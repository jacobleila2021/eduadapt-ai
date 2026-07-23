"""Adaptive writing — pedagogically distinct versions, never a recolor of the same lesson."""

from __future__ import annotations

import copy
import re
from typing import Any

from engines.lesson_composition_engine.teaching_rules import ensure_paragraph_quality, scaffold_chunk

# version_id → intentional writing stance
VERSION_PROFILES: dict[str, dict[str, Any]] = {
    "standard": {
        "label": "Mainstream Support",
        "stance": "Full classroom teaching voice with progressive explanation and practice.",
        "chunk": False,
        "sentence_max_words": 28,
        "bold_terms": False,
        "literal": False,
        "glossary_inline": False,
        "listen_cues": False,
        "visual_emphasis": False,
        "audience": "student",
    },
    "ld": {
        "label": "Neurodiversity Support",
        "stance": "Same curriculum depth with chunked steps, bold cues, and calm pacing.",
        "chunk": True,
        "sentence_max_words": 18,
        "bold_terms": True,
        "literal": False,
        "glossary_inline": False,
        "listen_cues": False,
        "visual_emphasis": True,
        "audience": "student",
    },
    "dyslexia": {
        "label": "Dyslexia Support",
        "stance": "Short lines, bold key terms, generous spacing cues, unchanged curriculum depth.",
        "chunk": True,
        "sentence_max_words": 14,
        "bold_terms": True,
        "literal": True,
        "glossary_inline": False,
        "listen_cues": False,
        "visual_emphasis": True,
        "audience": "student",
    },
    "adhd": {
        "label": "ADHD Support",
        "stance": "Two-minute teaching bursts, numbered steps, checkpoints, and movement breaks.",
        "chunk": True,
        "sentence_max_words": 16,
        "bold_terms": True,
        "literal": False,
        "glossary_inline": False,
        "listen_cues": False,
        "visual_emphasis": True,
        "checkpoints": True,
        "audience": "student",
    },
    "autism": {
        "label": "Autism Support",
        "stance": "Predictable structure, explicit transitions, literal language, consistent section labels.",
        "chunk": True,
        "sentence_max_words": 18,
        "bold_terms": False,
        "literal": True,
        "glossary_inline": False,
        "listen_cues": False,
        "visual_emphasis": False,
        "predictable": True,
        "audience": "student",
    },
    "ell": {
        "label": "English Language Support",
        "stance": "Keep board vocabulary; add glossary scaffolds and sentence frames beside dense terms.",
        "chunk": False,
        "sentence_max_words": 20,
        "bold_terms": True,
        "literal": False,
        "glossary_inline": True,
        "listen_cues": False,
        "visual_emphasis": False,
        "audience": "student",
    },
    "visual": {
        "label": "Visual Learner Support",
        "stance": "Colour-coded stages and diagram-first teaching without reducing verbal explanation.",
        "chunk": False,
        "sentence_max_words": 24,
        "bold_terms": False,
        "literal": False,
        "glossary_inline": False,
        "listen_cues": False,
        "visual_emphasis": True,
        "audience": "student",
    },
    "auditory": {
        "label": "Auditory Learner Support",
        "stance": "Listen-and-repeat prose with Say:/Repeat: cues; full paragraphs, not bullets.",
        "chunk": False,
        "sentence_max_words": 26,
        "bold_terms": False,
        "literal": False,
        "glossary_inline": False,
        "listen_cues": True,
        "visual_emphasis": False,
        "audience": "student",
    },
    "teacher": {
        "label": "Teacher Version",
        "stance": "Classroom-teachable lesson plus differentiation map, checks for understanding, answer guidance.",
        "chunk": False,
        "sentence_max_words": 30,
        "bold_terms": False,
        "teacher_notes": True,
        "audience": "teacher",
    },
    "parent": {
        "label": "Parent Version",
        "stance": "Plain-language home summary, conversation starters, and how to help without doing the work.",
        "chunk": False,
        "sentence_max_words": 22,
        "plain_language": True,
        "audience": "parent",
    },
}


def _shorten_sentences(text: str, max_words: int) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]
    out: list[str] = []
    for s in sentences:
        words = s.split()
        if len(words) <= max_words:
            out.append(s if s.endswith((".", "?", "!")) else s + ".")
            continue
        # Split long sentences at commas/conjunctions when possible
        parts = re.split(r",\s+|\s+and\s+|\s+but\s+", s)
        buf: list[str] = []
        for part in parts:
            cand = (" ".join(buf + [part])).strip()
            if len(cand.split()) > max_words and buf:
                chunk = " ".join(buf).strip().rstrip(",")
                out.append(chunk if chunk.endswith((".", "?", "!")) else chunk + ".")
                buf = [part]
            else:
                buf.append(part)
        if buf:
            chunk = " ".join(buf).strip().rstrip(",")
            out.append(chunk if chunk.endswith((".", "?", "!")) else chunk + ".")
    return " ".join(out)


def _bold_key_terms(text: str, terms: list[str]) -> str:
    out = text
    for term in sorted({t for t in terms if t}, key=len, reverse=True)[:20]:
        if len(term) < 3:
            continue
        pattern = re.compile(rf"\b({re.escape(term)})\b", re.I)
        out = pattern.sub(r"**\1**", out)
    return out


def _rewrite_section_body(
    body: str,
    *,
    profile: dict[str, Any],
    terms: list[str],
    section_title: str,
) -> str:
    text = ensure_paragraph_quality(body, idea=section_title)
    max_words = int(profile.get("sentence_max_words") or 28)
    text = _shorten_sentences(text, max_words)

    if profile.get("chunk"):
        bullets = scaffold_chunk(text, max_bullets=8)
        text = "\n".join(f"- {b}" for b in bullets)
        if profile.get("checkpoints"):
            text += "\n\n**Checkpoint:** Pause. Can you explain the last step in one sentence?"
        if profile.get("predictable"):
            text = f"**Now:** {section_title}\n\n{text}\n\n**Next:** Continue to the following labelled section."

    if profile.get("bold_terms"):
        text = _bold_key_terms(text, terms)

    if profile.get("glossary_inline") and terms:
        gloss = ", ".join(terms[:6])
        text += f"\n\n*Key words in this section:* {gloss}."

    if profile.get("listen_cues"):
        text = f"**Say:** {text}\n\n**Repeat:** Say the main idea aloud in your own words."

    if profile.get("visual_emphasis"):
        # One quiet visual cue — do not spam every section with the same opener
        if "look first" not in text.lower():
            text = f"Study the diagram or colour cues for this idea, then read on.\n\n{text}"

    if profile.get("plain_language"):
        text = (
            "Here is a simple way to talk about this at home.\n\n"
            + text
            + "\n\n**Try asking:** What was the most important idea today?"
        )

    if profile.get("teacher_notes"):
        text += (
            "\n\n**Teacher note:** Check for understanding with a quick cold-call or exit ticket. "
            "Keep verified facts unchanged; differentiate presentation only."
        )

    return text.strip()


def compose_adaptive_version(
    standard_lesson: dict[str, Any],
    version_id: str,
    *,
    vocabulary_terms: list[str] | None = None,
) -> dict[str, Any]:
    """
    Produce a pedagogically distinct adaptation from the LCE standard lesson.
    Never merely recolors; rewrites structure and scaffolds intentionally.
    """
    profile = VERSION_PROFILES.get(version_id) or VERSION_PROFILES["standard"]
    lesson = copy.deepcopy(standard_lesson)
    terms = vocabulary_terms or []
    if not terms:
        for section in lesson.get("sections") or []:
            # harvest bold-ish words later; leave empty ok
            pass

    new_sections: list[dict[str, Any]] = []
    for section in lesson.get("sections") or []:
        if not isinstance(section, dict):
            continue
        sec = dict(section)
        title = str(sec.get("title") or "")
        body = str(sec.get("body") or "")
        if version_id == "parent" and sec.get("role") in {
            "worked_example",
            "practice_question",
            "common_misconception",
        }:
            # Parents get lighter technical sections → home coaching angle
            body = (
                f"At home, you can support this part by asking your child to explain "
                f"'{title}' in their own words. Listen for the key idea; you do not need "
                f"to teach the full classroom explanation."
            )
        sec["body"] = _rewrite_section_body(
            body, profile=profile, terms=terms, section_title=title
        )
        if version_id == "adhd":
            sec["box"] = "checkpoint"
        elif version_id == "autism":
            sec["box"] = "predictable"
        elif version_id in {"dyslexia", "ld"}:
            sec["box"] = "accessible"
        elif version_id == "visual":
            sec["box"] = "visual"
        new_sections.append(sec)

    # Intentional structural differences
    if version_id == "adhd":
        new_sections.insert(
            0,
            {
                "title": "Energy Plan (2-minute bursts)",
                "body": (
                    "We will learn in short bursts. After each numbered chunk, take a 20-second stretch. "
                    "Then continue. This keeps attention fresh without reducing what you need to learn."
                ),
                "box": "checkpoint",
                "role": "hook",
            },
        )
    if version_id == "autism":
        new_sections.insert(
            0,
            {
                "title": "Lesson Map (What Happens Next)",
                "body": (
                    "First we open the idea. Next we explain it. Then we look at an example. "
                    "After that we practise. Finally we summarise. The order stays the same every time."
                ),
                "box": "predictable",
                "role": "hook",
            },
        )
    if version_id == "ell":
        new_sections.insert(
            0,
            {
                "title": "Key Words First",
                "body": (
                    "Before the full explanation, learn these lesson words: "
                    + (", ".join(terms[:8]) if terms else "the main lesson terms")
                    + ". "
                    "Sentence frame: “______ means ______, and an example is ______.”"
                ),
                "box": "glossary",
                "role": "vocabulary",
            },
        )
    if version_id == "visual":
        new_sections.insert(
            0,
            {
                "title": "See the Big Picture",
                "body": (
                    "Start with the diagram. Trace each labelled part with your finger, "
                    "then read the matching explanation. Colour cues mark stages of learning."
                ),
                "box": "visual",
                "role": "visual",
            },
        )
    if version_id == "auditory":
        new_sections.insert(
            0,
            {
                "title": "Listen Goal",
                "body": (
                    "You will hear the idea, say it, and check it. "
                    "Use Say / Repeat cues in every section. Pause when you see a listening checkpoint."
                ),
                "box": "listen",
                "role": "hook",
            },
        )
        new_sections.append(
            {
                "title": "Listening Checkpoint",
                "body": (
                    "**Say:** the big idea in one sentence. "
                    "**Repeat:** one example aloud. "
                    "**Discuss:** tell a partner what still feels unclear."
                ),
                "box": "listen",
                "role": "reflection",
            },
        )
    if version_id == "teacher":
        new_sections.append(
            {
                "title": "Differentiation Map",
                "body": (
                    "Dyslexia/ADHD/Autism: use chunked tabs. ELL: keep board terms with glossary frames. "
                    "Visual/Auditory: prefer those adaptive versions. Do not change verified STEM facts."
                ),
                "box": "teacher",
                "role": "application",
            }
        )
        new_sections.append(
            {
                "title": "Misconception Alerts",
                "body": (
                    "Listen for mix-ups between related terms. Ask students to contrast the correct idea "
                    "with the common mistake using evidence from the lesson."
                ),
                "box": "teacher",
                "role": "common_misconception",
            }
        )
    if version_id == "parent":
        lesson["big_idea"] = (
            "Today's home focus: "
            + str(lesson.get("big_idea") or "the main lesson idea")
        )
        new_sections.append(
            {
                "title": "Home Activity",
                "body": (
                    "Ask your child to teach you one idea from today's lesson in two minutes. "
                    "Then try one real-life example together. Praise effort, not just correct wording."
                ),
                "box": "home",
                "role": "application",
            }
        )

    lesson["sections"] = new_sections
    lesson.setdefault("lce", {})
    lesson["lce"] = {
        **(lesson.get("lce") if isinstance(lesson.get("lce"), dict) else {}),
        "version_id": version_id,
        "adaptive_profile": profile.get("label"),
        "stance": profile.get("stance"),
        "pedagogically_distinct": True,
    }
    lesson["pedagogy_notes"] = [profile.get("stance")]
    return lesson


def compose_all_adaptive_versions(
    standard_lesson: dict[str, Any],
    *,
    vocabulary_terms: list[str] | None = None,
    version_ids: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    ids = version_ids or list(VERSION_PROFILES.keys())
    out: dict[str, dict[str, Any]] = {}
    for vid in ids:
        if vid == "standard":
            std = copy.deepcopy(standard_lesson)
            std.setdefault("lce", {})
            if isinstance(std["lce"], dict):
                std["lce"]["version_id"] = "standard"
            out["standard"] = std
        else:
            out[vid] = compose_adaptive_version(
                standard_lesson, vid, vocabulary_terms=vocabulary_terms
            )
    return out
