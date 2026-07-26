"""Master Lesson Architecture (v3.3) — One Canonical Lesson, Many Presentations.

FUNDAMENTAL DESIGN PRINCIPLE
    Alora AI never generates different lessons for different learners.
    There is ONLY ONE lesson: the Canonical Mainstream Lesson (Gold Standard).
    It is generated first, frozen (read-only), and every adaptation inherits
    it unchanged. Adaptation engines change PRESENTATION ONLY — they never
    remove curriculum, omit concepts, invent replacements, reorder the
    teaching sequence, or weaken outcomes.

ESSENTIAL LEARNING CORE
    Before any adaptation is derived, the engine extracts the Essential
    Learning Core: every concept, skill, vocabulary term, diagram, worked
    example and assessment objective each learner must master. The core is
    locked (hashed) and inherited unchanged by every adaptation.

PIPELINE
    Upload → Subject Engine → Curriculum Validation → Canonical Mainstream
    Lesson → Freeze → Derive Adaptations (presentation-only) → Fidelity Gate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Mapping

from engines.lesson_composition_engine.publisher_author import (
    _claims,
    _misc,
    _practice_set,
    _textbook_concept_names,
)

CANONICAL_LESSON_SMOKE_OK = True
CANONICAL_SCHEMA = "alora.canonical_lesson.v1"
CORE_SCHEMA = "alora.essential_learning_core.v1"

# Master Lesson Contract — mandated teaching sequence (absolute curriculum fidelity).
# Extra presentation supports (visual_support, language_support, …) may be
# interleaved, but these roles must appear in this relative order and none
# may disappear from any learner adaptation.
CANONICAL_ROLE_SEQUENCE = (
    "introduction",         # Lesson Introduction
    "objective",            # Learning Objectives — What You Will Learn
    "essential_learning",   # Must Know — every examinable concept
    "concept",              # Key Concepts + Step-by-Step + Concept Explanations
    "worked_example",       # Worked Examples (CRA for mathematics)
    "visual",               # Diagrams that teach
    "vocabulary",           # Vocabulary
    "real_life_example",    # Real-life Applications
    "common_misconception", # Common Misconceptions
    "practice_question",    # Practice Questions (recall / understanding)
    "exam_question",        # Exam Questions
    "hots_question",        # HOTS Questions
    "summary",              # Summary
    "revision",             # Quick Revision
    "exit_ticket",          # Exit Ticket — I Understand This
    "assessment",           # Assessment Check
)

# Roles every student adaptation must keep at Mainstream educational depth.
MASTER_CONTRACT_ROLES = CANONICAL_ROLE_SEQUENCE

# Student presentation lenses derived from the canonical lesson.
PRESENTATION_LENSES = ("visual", "auditory", "ell", "ld", "dyslexia", "adhd", "autism")


# --------------------------------------------------------------------------
# Canonical Mainstream Lesson (Gold Standard)
# --------------------------------------------------------------------------

def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def _studentize(goal: str, topic: str) -> str:
    from engines.lesson_composition_engine.publisher_remediation import studentize_goal

    text = studentize_goal(str(goal or ""), topic=topic).strip()
    if text and not text.endswith((".", "!", "?")):
        text += "."
    return text


def _master_concept_names(board: Mapping[str, Any], claims: list[str]) -> list[str]:
    """Prefer explicit board concepts (string or dict); fall back to claim extraction.

    When the board lists concepts explicitly, keep every listed term — including
    the topic itself when it is an examinable concept (e.g. Force).
    """
    topic = str(board.get("topic") or "").strip()
    names: list[str] = []
    seen: set[str] = set()
    explicit = False
    for item in board.get("concepts") or []:
        if isinstance(item, dict):
            raw = str(item.get("name") or item.get("title") or "").strip()
        else:
            raw = str(item or "").strip()
        low = raw.lower()
        if (
            not raw
            or len(low) < 3
            or low in seen
            or any(ch.isdigit() for ch in low)
            or any(ch in raw for ch in "(|:")
        ):
            continue
        explicit = True
        seen.add(low)
        names.append(raw)
    if explicit and names:
        return names[:8]
    # Claim extraction: avoid duplicating the topic title as a pseudo-concept.
    fallback = _textbook_concept_names(board, claims)
    return [n for n in fallback if n.lower() != topic.lower()][:8] or fallback[:8]


def _concept_explanation(board: Mapping[str, Any], name: str, claims: list[str]) -> str:
    """Best available explanation for a concept — never invent outside the board."""
    low = name.lower()
    for item in board.get("concepts") or []:
        if isinstance(item, dict):
            item_name = str(item.get("name") or "").strip().lower()
            expl = str(item.get("explanation") or item.get("definition") or "").strip()
            if item_name == low and expl:
                return expl.rstrip(".") + "."
    for claim in claims:
        if low in claim.lower():
            return claim.rstrip(".") + "."
    return f"{name[:1].upper() + name[1:]} is a key idea in this lesson that you must be able to explain."


def _body_word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _is_mathematics(board: Mapping[str, Any]) -> bool:
    subject = str(board.get("subject") or board.get("subject_key") or "").lower()
    return any(token in subject for token in ("math", "algebra", "geometry", "arithmetic"))


def _is_science(board: Mapping[str, Any]) -> bool:
    subject = str(board.get("subject") or board.get("subject_key") or "").lower()
    return any(
        token in subject
        for token in ("science", "physics", "chemistry", "biology", "general science")
    )


def build_canonical_lesson(
    board: Mapping[str, Any],
    *,
    flowchart_svg: str = "",
    concept_map_svg: str = "",
) -> dict[str, Any]:
    """Compose the ONE complete Master Lesson (Gold Standard / Mainstream).

    Master Lesson Contract — every educational component below is mandatory.
    Adaptations inherit this lesson and change presentation only.
    """
    topic = str(board.get("topic") or "Lesson").strip()
    topic_low = topic.lower()
    claims = [c for c in _claims(dict(board)) if not c.strip().endswith("?")]
    names = _master_concept_names(board, claims)
    term_names = list(names)
    misc = _misc(dict(board))
    goals = [str(g) for g in (board.get("learning_goals") or []) if str(g).strip()]
    examples = [str(e) for e in (board.get("examples") or []) if str(e).strip()]
    assessments = [
        str(a) for a in (board.get("assessment_objectives") or []) if str(a).strip()
    ]
    experiments = [str(e) for e in (board.get("experiments") or []) if str(e).strip()]
    stage_names = [n[:1].upper() + n[1:] for n in term_names[:6]]

    used: set[str] = set()

    def _take(pred, limit: int) -> list[str]:
        out: list[str] = []
        for c in claims:
            if c in used or not pred(c):
                continue
            used.add(c)
            out.append(c)
            if len(out) >= limit:
                break
        return out

    sections: list[dict[str, Any]] = []

    # 1) Lesson Introduction
    intro_claims = _take(lambda c: topic_low in c.lower(), 2) or _take(lambda c: True, 2)
    intro_body = (
        f"This lesson teaches {topic} completely — every idea you need for class "
        f"and for the examination. "
        + (" ".join(s.rstrip(".") + "." for s in intro_claims) if intro_claims else "")
        + (
            f" You will learn {', '.join(n.lower() for n in term_names[:4])} in order, "
            f"with examples, a diagram, practice and exam questions."
            if term_names
            else f" Follow each section carefully so nothing is missed."
        )
    )
    sections.append(
        {"title": "Lesson Introduction", "role": "introduction", "body": intro_body.strip()}
    )

    # 2) Learning Objectives — What You Will Learn
    objective_lines = [_studentize(g, topic) for g in goals[:4]] or [
        f"You will learn what {topic.lower()} means and how each idea works."
    ]
    for name in term_names[:4]:
        line = f"You will be able to explain {name.lower()} in your own words."
        if line not in objective_lines:
            objective_lines.append(line)
    if assessments:
        objective_lines.append(_studentize(assessments[0], topic))
    sections.append(
        {
            "title": "What You Will Learn",
            "role": "objective",
            "body": " ".join(objective_lines[:6]),
        }
    )

    # 3) Must Know — Essential Learning Core (examinable)
    essential_terms = ", ".join(n[:1].upper() + n[1:] for n in term_names[:8]) or topic
    sections.append(
        {
            "title": "Must Know",
            "role": "essential_learning",
            "body": (
                f"Every learner — whatever support they use — must master these "
                f"examinable ideas for {topic}: {essential_terms}. "
                f"Each idea is taught step by step below. Every exam question comes "
                f"only from this Must Know list. No adaptation may remove any of them."
            ),
        }
    )

    # 4) Key Concepts — overview of every examinable term
    if term_names:
        key_lines = [
            f"{n[:1].upper() + n[1:]}: {_concept_explanation(board, n, claims)}"
            for n in term_names[:8]
        ]
        sections.append(
            {
                "title": "Key Concepts",
                "role": "concept",
                "body": "\n".join(key_lines),
            }
        )

    # 5–6) Step-by-Step Teaching + Concept Explanations
    step = 0
    for name in term_names[:6]:
        low = name.lower()
        body_claims = _take(lambda c, low=low: low in c.lower(), 3)
        explanation = _concept_explanation(board, name, claims)
        if not body_claims:
            body_claims = [explanation]
        # Guarantee teachable depth — never leave a one-line stub step.
        merged_body = " ".join(s.rstrip(".") + "." for s in body_claims)
        if _body_word_count(merged_body) < 40:
            extras = [
                explanation,
                f"In this lesson, {low} belongs in the Must Know sequence for {topic.lower()} and must be explained in your own words.",
                f"Connect {low} to the worked example and the diagram so you can use it in exam answers.",
            ]
            for extra in extras:
                if extra.rstrip(".") not in merged_body:
                    merged_body = (merged_body.rstrip() + " " + extra.rstrip(".") + ".").strip()
                if _body_word_count(merged_body) >= 40:
                    break
        step += 1
        sections.append(
            {
                "title": f"Step {step} — {name[:1].upper() + name[1:]}",
                "role": "concept",
                "body": merged_body,
            }
        )
    leftovers = _take(lambda c: True, 3)
    if leftovers:
        sections.append(
            {
                "title": "More ideas from this lesson",
                "role": "concept",
                "body": " ".join(s.rstrip(".") + "." for s in leftovers),
            }
        )

    # 7) Worked Examples — CRA for mathematics; process walk for science
    if _is_mathematics(board) and stage_names:
        walk = (
            f"Concrete–Representational–Abstract (CRA) worked example for {topic}. "
            f"Concrete: use objects, drawings or a real situation to show "
            f"{stage_names[0].lower()}. "
            f"Representational: draw a diagram or table that shows "
            + ", ".join(n.lower() for n in stage_names[:4])
            + ". "
            f"Abstract: write the formal statement or calculation using the lesson "
            f"symbols and vocabulary. "
        )
        if examples:
            walk += "Lesson example: " + examples[0].rstrip(".") + "."
    elif len(stage_names) >= 2:
        walk = (
            f"Follow one complete example of {topic.lower()} from start to finish. "
            + " ".join(
                f"{'First' if i == 0 else 'Then' if i < len(stage_names) - 1 else 'Finally'}, "
                f"{n.lower()} takes place, exactly as taught in Step {i + 1}."
                for i, n in enumerate(stage_names)
            )
            + " Work through this chain once forwards and once backwards until each step feels natural."
        )
        if examples:
            walk += " Worked example from the lesson: " + examples[0].rstrip(".") + "."
    else:
        walk = (
            f"Take the main idea of {topic.lower()} and apply it to the example in this lesson, "
            f"one sentence at a time, exactly as taught above."
        )
        if examples:
            walk += " " + examples[0].rstrip(".") + "."
    if _is_science(board) and experiments:
        walk += " Classroom / home check: " + experiments[0].rstrip(".") + "."
    sections.append({"title": "Worked Examples", "role": "worked_example", "body": walk})

    # 8) Diagrams
    flow = " → ".join(stage_names) if len(stage_names) >= 2 else topic
    diagram_body = (
        f"The diagram shows {topic} as connected stages: {flow}. "
        f"Point to each labelled part with your finger. Trace every arrow in order. "
        f"Ask yourself: where is each Must Know idea on the diagram, and why does "
        f"that stage come next? Match it to the step that teaches it. "
        f"Say the idea aloud before you move on."
    )
    if not (flowchart_svg or concept_map_svg):
        diagram_body += (
            f" If a drawing is not yet on screen, sketch the sequence {flow} "
            f"in your notebook and label every stage."
        )
    sections.append(
        {"title": "Diagrams", "role": "visual", "body": diagram_body}
    )

    # 9) Vocabulary
    vocab_lines = []
    for n in term_names[:8]:
        vocab_lines.append(
            f"{n[:1].upper() + n[1:]} — {_concept_explanation(board, n, claims)}"
        )
    sections.append(
        {
            "title": "Vocabulary",
            "role": "vocabulary",
            "body": (
                "\n".join(vocab_lines)
                if vocab_lines
                else f"Study the key words for {topic} on the Vocabulary page."
            ),
        }
    )

    # 10) Real-life Applications — source-bound only
    real_parts = [e.rstrip(".") + "." for e in examples[:3]]
    if _is_science(board) and experiments:
        real_parts.append(
            "Try this carefully: " + experiments[0].rstrip(".") + "."
        )
    if not real_parts and claims:
        real_parts = [c.rstrip(".") + "." for c in claims[:2]]
    sections.append(
        {
            "title": "Real-life Applications",
            "role": "real_life_example",
            "body": " ".join(real_parts)
            if real_parts
            else f"Look for {topic.lower()} in everyday life and name one place you see it.",
        }
    )

    # 11) Common Misconceptions
    if misc:
        misc_body = " ".join(
            f"Some learners think {str(m.get('label') or '').rstrip('.')}. "
            f"In fact, {str(m.get('correction') or 'check the Must Know list').rstrip('.')}."
            for m in misc[:3]
            if m.get("label")
        )
    else:
        first = term_names[0] if term_names else topic
        misc_body = (
            f"A common mix-up is to confuse the order of ideas in {topic.lower()}. "
            f"Always start with {first.lower()} and follow the Must Know sequence."
        )
    sections.append(
        {
            "title": "Common Misconceptions",
            "role": "common_misconception",
            "body": misc_body,
        }
    )

    # 12) Practice Questions — recall + understanding
    practice = _practice_set(names, claims, topic)
    practice_lines = [
        f"{i + 1}. {q.get('question')}" for i, q in enumerate(practice[:3])
    ]
    if term_names:
        practice_lines.append(
            f"{len(practice_lines) + 1}. Recall: name each Must Know idea for "
            f"{topic.lower()} in the correct order."
        )
        practice_lines.append(
            f"{len(practice_lines) + 1}. Understanding: explain "
            f"{term_names[0].lower()} using one sentence from this lesson."
        )
    sections.append(
        {
            "title": "Practice Questions",
            "role": "practice_question",
            "body": "\n".join(practice_lines),
        }
    )

    # 13) Exam Questions
    exam_lines: list[str] = []
    for i, name in enumerate(term_names[:3] or [topic]):
        exam_lines.append(
            f"{i + 1}. Explain {name.lower()} clearly. Include its meaning and "
            f"how it connects to {topic.lower()}. (3 marks)"
        )
    if len(term_names) >= 2:
        exam_lines.append(
            f"{len(exam_lines) + 1}. Compare {term_names[0].lower()} and "
            f"{term_names[1].lower()}. State one similarity and one difference. (4 marks)"
        )
    if assessments:
        exam_lines.append(
            f"{len(exam_lines) + 1}. {assessments[0].rstrip('.')} (4 marks)"
        )
    sections.append(
        {"title": "Exam Questions", "role": "exam_question", "body": "\n".join(exam_lines)}
    )

    # 14) HOTS Questions
    hots_anchor = term_names[0] if term_names else topic
    hots_second = term_names[1] if len(term_names) > 1 else topic
    hots_lines = [
        f"1. Predict what would change about {hots_anchor.lower()} if the "
        f"conditions around it were reversed. Give a reason from the lesson. (5 marks)",
        f"2. A classmate confuses {hots_anchor.lower()} with {hots_second.lower()}. "
        f"Write the correction you would teach them, using Must Know language. (5 marks)",
        f"3. Design one everyday situation that shows {topic.lower()} at work, "
        f"and label each Must Know idea inside it. (6 marks)",
    ]
    sections.append(
        {"title": "HOTS Questions", "role": "hots_question", "body": "\n".join(hots_lines)}
    )

    # 15) Summary — concept-complete, never generic filler
    summary_parts = [
        f"{topic} brings together "
        + (", ".join(n.lower() for n in term_names[:6]) if term_names else "the ideas in this lesson")
        + "."
    ]
    for n in term_names[:4]:
        summary_parts.append(_concept_explanation(board, n, claims))
    if claims:
        lead = next((c for c in claims if topic_low in c.lower()), claims[0])
        if lead not in summary_parts:
            summary_parts.append(lead.rstrip(".") + ".")
    sections.append(
        {
            "title": "Summary",
            "role": "summary",
            "body": " ".join(summary_parts),
        }
    )

    # 16) Quick Revision
    sections.append(
        {
            "title": "Quick Revision",
            "role": "revision",
            "body": (
                "Say each Must Know idea aloud from memory:\n"
                + "\n".join(f"- Explain {n.lower()}." for n in (term_names or [topic])[:8])
                + f"\n- Retell the worked example for {topic.lower()} in three sentences."
            ),
        }
    )

    # 17) Exit Ticket — I Understand This
    exit_lines = [
        f"I understand {topic.lower()} well enough to teach it to a friend because "
        f"I can use every Must Know idea."
    ]
    exit_lines += [f"I can explain {n.lower()} without looking." for n in term_names[:5]]
    exit_lines.append("I can answer one practice and one exam question from this lesson.")
    sections.append(
        {
            "title": "I Understand This",
            "role": "exit_ticket",
            "body": "\n".join(f"☐ {line}" for line in exit_lines),
        }
    )

    # 18) Assessment Check (board-style short check)
    assess_body_lines = [
        f"{i + 1}. {q.get('question')} ({q.get('marks')} marks)"
        for i, q in enumerate(practice[3:5] or practice[:2])
    ]
    if not assess_body_lines and term_names:
        assess_body_lines = [
            f"1. Define {term_names[0].lower()}. (2 marks)",
            f"2. Explain how {term_names[0].lower()} fits into {topic.lower()}. (3 marks)",
        ]
    sections.append(
        {
            "title": "Assessment Check",
            "role": "assessment",
            "body": "\n".join(assess_body_lines),
        }
    )

    big = claims[0] if claims else f"Clear ideas help you explain {topic}."
    if len(claims) >= 2 and len(str(big).split()) < 12:
        big = f"{claims[0]} {claims[1]}"

    svg = flowchart_svg or concept_map_svg
    page: dict[str, Any] = {
        "big_idea": str(big)[:400],
        "sections": sections,
        "topic": topic,
        "title": f"{topic} — Master Lesson",
        "flowchart_svg": flowchart_svg,
        "concept_map_svg": concept_map_svg,
        "svg_diagram": svg,
        "revision_points": [f"Explain: {n}" for n in names[:8]],
        "practice": practice,
        "master_contract_roles": list(MASTER_CONTRACT_ROLES),
        "lce": {
            "version_id": "standard",
            "schema": CANONICAL_SCHEMA,
            "canonical": True,
            "master_lesson": True,
            "teacher_composition": True,
            "textbook_theory": True,
            "composed_independently": True,
            "from_intelligence_board": True,
            "pedagogically_distinct": True,
            "science_engine": _is_science(board),
            "mathematics_engine": _is_mathematics(board),
        },
    }
    if str(svg or "").startswith("<svg"):
        from engines.lesson_composition_engine.pmes import _diagram_package

        page["diagram_package"] = _diagram_package(page, topic=topic, concepts=names)
    return page


# --------------------------------------------------------------------------
# Essential Learning Core (locked) + freeze
# --------------------------------------------------------------------------

def extract_essential_learning_core(
    canonical: Mapping[str, Any], board: Mapping[str, Any]
) -> dict[str, Any]:
    """The locked core every adaptation must carry unchanged."""
    topic = str(board.get("topic") or canonical.get("topic") or "Lesson")
    claims = [c for c in _claims(dict(board)) if not c.strip().endswith("?")]
    names = _master_concept_names(board, claims)
    term_names = list(names)
    roles_present = [
        str(s.get("role") or "")
        for s in (canonical.get("sections") or [])
        if isinstance(s, dict)
    ]
    core = {
        "schema": CORE_SCHEMA,
        "topic": topic,
        "concepts": term_names,
        "vocabulary": term_names,
        "claims": claims,
        "objectives": [str(g) for g in (board.get("learning_goals") or [])][:5],
        "assessment_objectives": [
            str(a) for a in (board.get("assessment_objectives") or [])
        ][:8],
        "has_diagram": str(canonical.get("svg_diagram") or "").startswith("<svg")
        or any(str(s.get("role") or "") == "visual" for s in (canonical.get("sections") or []) if isinstance(s, dict)),
        "master_contract_roles": [
            r for r in MASTER_CONTRACT_ROLES if r in roles_present
        ],
        "role_sequence": [r for r in CANONICAL_ROLE_SEQUENCE if r in roles_present],
    }
    core["hash"] = hashlib.sha256(
        json.dumps(
            {k: core[k] for k in ("topic", "concepts", "claims", "role_sequence")},
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()[:16]
    return core


def freeze_canonical(canonical: Mapping[str, Any], core: Mapping[str, Any]) -> dict[str, Any]:
    """Deep-copy the canonical lesson and mark it READ ONLY (frozen)."""
    frozen = copy.deepcopy(dict(canonical))
    lce = dict(frozen.get("lce") or {})
    lce["frozen"] = True
    lce["canonical_hash"] = str(core.get("hash") or "")
    frozen["lce"] = lce
    return frozen


# --------------------------------------------------------------------------
# Presentation-only derivation (adaptations inherit the canonical lesson)
# --------------------------------------------------------------------------

_QUESTION_ZONE_ROLES = {
    "practice_question",
    "exam_question",
    "hots_question",
    "assessment",
}

_LENS_PRESENTATION = {
    "visual": {
        "note": "diagram-anchored reading, colour-coded stages, concept maps",
        "css": {"visual_first": True, "colour_coding": True, "icons": True},
    },
    "auditory": {
        "note": "read-aloud script, listening checkpoints, verbal summaries",
        "css": {"narration": True, "listening_checkpoints": True},
    },
    "ell": {
        "note": "simplified language, sentence stems, inline glossary — same concepts",
        "css": {"glossary": True, "sentence_stems": True},
    },
    "ld": {
        "note": "single-idea steps, chunked blocks, sequential cues",
        "css": {"bullets": True, "chunking": True},
    },
    "dyslexia": {
        "note": "Lexend, large spacing, reading strips, colour emphasis, no walls of text",
        "css": {
            "font_family": "Lexend, 'OpenDyslexic', sans-serif",
            "line_height": 1.9,
            "letter_spacing": "0.03em",
            "max_paragraph_sentences": 1,
            "reading_strips": True,
            "colour_emphasis": True,
        },
    },
    "adhd": {
        "note": "short-burst goals, progress markers, frequent retrieval",
        "css": {"bullets": True, "short_bursts": True},
    },
    "autism": {
        "note": "literal language, predictable order, explicit transitions",
        "css": {"literal": True, "predictable": True},
    },
}

_COLOUR_MARKERS = ("●", "◆", "▲", "■", "★", "✦")


def _syllabify(term: str) -> str:
    """Naive decoding support: split a long word at vowel-group boundaries."""
    word = term.strip()
    if len(word) < 8 or " " in word:
        return ""
    parts = re.findall(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy](?=[^aeiouy]))?", word.lower())
    if len(parts) < 3 or "".join(parts) != word.lower():
        return ""
    return "·".join(parts)


def _emphasise_terms(body: str, concepts: list[str]) -> str:
    """Colour-emphasis markers around examinable terms — content unchanged."""
    text = body
    for i, name in enumerate(concepts):
        if not name or len(name) < 3:
            continue
        marker = _COLOUR_MARKERS[i % len(_COLOUR_MARKERS)]
        pattern = re.compile(rf"\b({re.escape(name)})\b", re.IGNORECASE)
        text = pattern.sub(rf"{marker} \1 {marker}", text, count=1)
    return text


def _ell_present_body(body: str, concepts: list[str]) -> str:
    """Same curriculum in clearer English — add glossary cues, never drop terms."""
    lines: list[str] = []
    for line in body.split("\n"):
        raw = line.strip()
        if not raw:
            continue
        if raw.lstrip().startswith(("-", "•", "☐", "1.", "2.", "3.")):
            lines.append(raw)
            continue
        for sent in _sentences(raw):
            glossed = sent
            for name in concepts:
                low = name.lower()
                if low in sent.lower() and f"({name}" not in sent:
                    # Keep the term; add a short everyday cue beside first hit.
                    glossed = re.sub(
                        rf"\b({re.escape(name)})\b",
                        rf"\1 (key word)",
                        glossed,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                    break
            if len(glossed.split()) > 22:
                # Split long sentences at a mid comma — concepts stay.
                if "," in glossed:
                    left, right = glossed.split(",", 1)
                    lines.append(left.strip().rstrip(".") + ".")
                    lines.append(right.strip()[:1].upper() + right.strip()[1:])
                    continue
            lines.append(glossed)
    return "\n".join(lines)


def _present_body(
    body: str,
    version_id: str,
    *,
    role: str,
    concepts: list[str] | None = None,
) -> str:
    """Transform presentation of one section body — curriculum content is untouched."""
    if not (body or "").strip():
        return body
    concepts = [str(c) for c in (concepts or []) if str(c).strip()]

    # Question zones keep every stem; only layout may change.
    if role in _QUESTION_ZONE_ROLES:
        if version_id in {"ld", "adhd", "dyslexia"}:
            return "\n\n".join(
                line.strip()
                for line in body.split("\n")
                if line.strip()
            )
        return body

    if version_id == "ell":
        return _ell_present_body(body, concepts)

    if version_id in {"ld", "adhd"}:
        lines: list[str] = []
        for line in body.split("\n"):
            if line.lstrip().startswith(("-", "•", "☐")):
                lines.append(line)
                continue
            for sent in _sentences(line):
                lines.append(f"- {sent}")
        return "\n".join(lines)

    if version_id == "dyslexia":
        # Reading strips: numbered one-sentence lines + colour emphasis + airy spacing.
        strips: list[str] = []
        n = 0
        emphasised = _emphasise_terms(body, concepts)
        for line in emphasised.split("\n"):
            if line.lstrip().startswith(("-", "•", "☐")):
                strips.append(line)
                strips.append("")  # breathing space — no walls of text
                continue
            for sent in _sentences(line):
                n += 1
                strips.append(f"{n}. {sent}")
                strips.append("")
        return "\n".join(strips).rstrip()

    if version_id == "visual":
        # Colour-code first examinable term hit; keep every sentence.
        return _emphasise_terms(body, concepts)

    if version_id == "auditory":
        # Read-aloud friendly: keep content; mark listening breaths between paragraphs.
        parts = [p.strip() for p in re.split(r"\n+", body) if p.strip()]
        out: list[str] = []
        for i, part in enumerate(parts):
            out.append(part)
            if i < len(parts) - 1 and role in {"concept", "worked_example", "summary"}:
                out.append("[Pause — listen again]")
        return "\n".join(out)

    if version_id == "autism":
        # Literal, predictable: one sentence per line, no figurative framing.
        lines = []
        for line in body.split("\n"):
            if line.lstrip().startswith(("-", "•", "☐")):
                lines.append(line)
                continue
            lines.extend(_sentences(line))
        return "\n".join(lines)

    return body


_PROFILE_TOOLKITS: dict[str, str] = {
    "visual": (
        "Visual toolkit: icons for each Must Know stage, colour-coded arrows, a concept map "
        "in the margin, and a timeline of the process. Sketch, label, and compare the "
        "flowchart with the concept map. Prefer pictures before paragraphs. Keep tracing "
        "until every stage is automatic."
    ),
    "auditory": (
        "Auditory toolkit: spoken read-aloud script, listening checkpoints after each step, "
        "repeat-after-me drills, call-and-response, partner echo, and a recorded verbal "
        "summary. Prefer hearing and speaking before silent reading. Clap once at each pause."
    ),
    "ell": (
        "Language toolkit: bilingual-friendly glossary, cognate hints where safe, sentence "
        "frames for explain/compare/apply, everyday analogies, and slow paraphrase. Keep "
        "academic Must Know terms exact — simplify the wrapper, never the science."
    ),
    "ld": (
        "Load toolkit: teach step by step with micro-goals, bullet strips, progress ticks, "
        "and one-breath sentences. Hide extra detail until the bullet is mastered. Return "
        "to any missed checklist item before the exam section."
    ),
    "dyslexia": (
        "Reading toolkit: Lexend, wide leading, tinted reading strips, colour emphasis on "
        "target words, syllable decoding, and sequential numbering. Skip dense paragraphs. "
        "Finger-track each strip. Calm and clear beats speed."
    ),
    "adhd": (
        "Focus toolkit: two-minute missions, visible timers, stretch breaks, and a scoreboard "
        "of finished chunks. Start, finish, celebrate, then next mission. Never skip Must Know."
    ),
    "autism": (
        "Routine toolkit: identical section order, literal instructions, finished/not-finished "
        "markers, and no surprise activities. First, next, then done — always the same."
    ),
}

_PROFILE_FRAMES: dict[str, dict[str, str]] = {
    "visual": {
        "title": "How you will learn — Visual path",
        "body": (
            "See it first. This presentation keeps every Must Know idea from the Master Lesson. "
            "Before each step, look at the diagram, trace the arrow, and label the stage. "
            "Colour markers highlight examinable terms. Using the diagram is part of learning — "
            "not decoration."
        ),
    },
    "auditory": {
        "title": "How you will learn — Auditory path",
        "body": (
            "Listen and say it. This presentation keeps every Must Know idea from the Master Lesson. "
            "Use the read-aloud script, pause at listening checkpoints, say each term aloud, "
            "hear your own verbal summary, then discuss one idea with a partner."
        ),
    },
    "ell": {
        "title": "How you will learn — English Language Support",
        "body": (
            "Same concepts, clearer English. Key words are glossed, sentence frames help you answer, "
            "and everyday examples keep meaning clear. Nothing from Must Know is removed — "
            "you still prepare for the same examination."
        ),
    },
    "ld": {
        "title": "How you will learn — Chunked steps",
        "body": (
            "Teach step by step. One idea per bullet. Short bursts. A checklist after each chunk. "
            "Every Must Know idea stays — accessibility reduces load, never curriculum."
        ),
    },
    "dyslexia": {
        "title": "How you will learn — Dyslexia-friendly reading",
        "body": (
            "Calm and clear. Lexend spacing, reading strips, colour emphasis, and decoding support "
            "help you teach step by step through the same Master Lesson. No walls of text. "
            "Every Must Know idea remains for the same examination."
        ),
    },
    "adhd": {
        "title": "How you will learn — Short missions",
        "body": (
            "Two-minute missions. Each chunk is a checklist goal. Take a break after two steps. "
            "Teach step by step — same Must Know ideas, same exam preparation."
        ),
    },
    "autism": {
        "title": "How you will learn — Predictable routine",
        "body": (
            "Same order every time. First read the title, next read the step, then tick finished. "
            "Literal language only. The routine never changes — and neither does the curriculum."
        ),
    },
}


def derive_presentation_adaptation(
    frozen: Mapping[str, Any],
    core: Mapping[str, Any],
    version_id: str,
) -> dict[str, Any]:
    """Inherit the frozen Master Lesson; change presentation only.

    Same concepts, same examples, same sequence, same outcomes.
    Accessibility improves learning — it never reduces curriculum.
    """
    page = copy.deepcopy(dict(frozen))
    spec = _LENS_PRESENTATION.get(version_id, {})
    topic = str(page.get("topic") or "Lesson")
    concepts = [str(c) for c in (core.get("concepts") or [])]
    sections = [dict(s) for s in (page.get("sections") or []) if isinstance(s, dict)]

    out_sections: list[dict[str, Any]] = []
    frame = _PROFILE_FRAMES.get(version_id)
    if frame:
        out_sections.append(
            {
                "title": frame["title"],
                "role": "presentation_frame",
                "body": frame["body"],
                "presentation_only": True,
            }
        )
    toolkit = _PROFILE_TOOLKITS.get(version_id)
    if toolkit:
        out_sections.append(
            {
                "title": "Presentation toolkit",
                "role": "presentation_toolkit",
                "body": toolkit,
                "presentation_only": True,
            }
        )

    for sec in sections:
        row = dict(sec)
        role = str(row.get("role") or "")
        row["body"] = _present_body(
            str(row.get("body") or ""),
            version_id,
            role=role,
            concepts=concepts,
        )
        # Keep learner-facing titles consistent with Mainstream structure.
        title_map = {
            "essential_learning": "Must Know",
            "practice_question": "Practice Questions",
            "exam_question": "Exam Questions",
            "hots_question": "HOTS Questions",
            "revision": "Quick Revision",
            "exit_ticket": "I Understand This",
            "real_life_example": "Real-life Applications",
            "visual": "Diagrams",
            "common_misconception": "Common Misconceptions",
        }
        if role in title_map:
            row["title"] = title_map[role]
        out_sections.append(row)

        # Additive presentation support (never replaces curriculum).
        if role == "concept" and str(row.get("title") or "").lower().startswith("step "):
            name = str(row.get("title") or "").split("—", 1)[-1].strip()
            if version_id == "visual":
                out_sections.append(
                    {
                        "title": f"See it — {name}",
                        "role": "visual_support",
                        "box": "visual",
                        "body": (
                            f"See it first on the diagram. Look for the label {name}. "
                            f"Trace the arrow into and out of {name.lower()}. "
                            f"Using the diagram: point, say the stage, then return to the text. "
                            f"Colour marker beside {name.lower()} must match the flowchart stage."
                        ),
                        "presentation_only": True,
                    }
                )
            elif version_id == "auditory":
                out_sections.append(
                    {
                        "title": f"Say it aloud — {name}",
                        "role": "auditory_support",
                        "body": (
                            f"Listen first. Read-aloud script: read the step above slowly once. "
                            f"Listening checkpoint: pause and hear the key words. "
                            f"Say “{name}” aloud three times, then say its meaning. "
                            f"Verbal summary: retell this step in one spoken sentence."
                        ),
                        "presentation_only": True,
                    }
                )
            elif version_id == "ell":
                out_sections.append(
                    {
                        "title": f"Key words — {name}",
                        "role": "language_support",
                        "body": (
                            f"{name} means the idea taught in the step above. "
                            f"Key words to keep: {name}. "
                            f"Sentence frame: “{name} means ______ and it matters because ______.” "
                            f"Say: fill the sentence frame, then give one everyday example."
                        ),
                        "presentation_only": True,
                    }
                )
            elif version_id == "dyslexia":
                syl = _syllabify(name)
                decode = (
                    f" Decoding support: break the word into parts — {syl}."
                    if syl
                    else f" Decoding support: look carefully at each letter group in {name}."
                )
                out_sections.append(
                    {
                        "title": f"Reading strip — {name}",
                        "role": "decoding_support",
                        "body": (
                            f"Calm and clear. Teach step by step using the numbered reading strips above. "
                            f"{decode} "
                            f"Colour emphasis marks {name.lower()}. "
                            f"Then retell this step in two short sentences — no walls of text."
                        ),
                        "presentation_only": True,
                    }
                )
            elif version_id == "ld":
                out_sections.append(
                    {
                        "title": f"Chunk check — {name}",
                        "role": "chunk_support",
                        "body": (
                            f"Teach step by step. Mission for this chunk: explain {name.lower()} "
                            f"in one bullet. Checklist: read → say → tick. Then move on."
                        ),
                        "presentation_only": True,
                    }
                )
            elif version_id == "adhd":
                out_sections.append(
                    {
                        "title": f"Mission — {name}",
                        "role": "chunk_support",
                        "body": (
                            f"Two-minute mission: explain {name.lower()} in one bullet. "
                            f"Checklist tick when finished. Take a short break after two missions."
                        ),
                        "presentation_only": True,
                    }
                )
            elif version_id == "autism":
                out_sections.append(
                    {
                        "title": f"Routine — {name}",
                        "role": "routine_support",
                        "body": (
                            f"What we will do: first read the step, next say {name.lower()} "
                            f"exactly as written, then mark finished. Same routine every step."
                        ),
                        "presentation_only": True,
                    }
                )

        if version_id == "auditory" and role == "summary":
            out_sections.append(
                {
                    "title": "Verbal summary and discussion",
                    "role": "auditory_support",
                    "body": (
                        f"Listen to your own summary. Say every Must Know idea for {topic.lower()} "
                        f"aloud. Discussion prompt: teach a partner for one minute; partner must "
                        f"hear and repeat one idea back."
                    ),
                    "presentation_only": True,
                }
            )

        if version_id == "ell" and role == "practice_question" and concepts:
            stems = "\n".join(
                f"- Sentence frame: Because of {c.lower()}, ______." for c in concepts[:4]
            )
            out_sections.append(
                {
                    "title": "Sentence frames",
                    "role": "language_support",
                    "body": (
                        "Use these sentence frames to answer the practice questions above. "
                        f"Key words stay the same — do not drop any Must Know idea:\n{stems}"
                    ),
                    "presentation_only": True,
                }
            )

        if version_id == "visual" and role == "visual":
            out_sections.append(
                {
                    "title": "Using the diagram",
                    "role": "visual_support",
                    "body": (
                        f"See it first, then read. Look at each stage of {topic.lower()}, "
                        f"trace every arrow, and explain why the next stage follows. "
                        f"Keep the diagram open while you answer Practice and Exam Questions."
                    ),
                    "presentation_only": True,
                }
            )

        # Mid-lesson presentation bridges — unique teaching moves, same curriculum.
        if role == "essential_learning":
            bridges = {
                "visual": (
                    f"Visual bridge: sketch a tiny icon beside every Must Know idea for "
                    f"{topic.lower()} before you open Step 1."
                ),
                "auditory": (
                    f"Listening bridge: whisper every Must Know idea for {topic.lower()} "
                    f"once, then hear yourself repeat the list."
                ),
                "ell": (
                    f"Language bridge: copy each Must Know key word for {topic.lower()} "
                    f"and write one everyday synonym beside it — keep the academic term too."
                ),
                "ld": (
                    f"Chunk bridge: turn the Must Know list for {topic.lower()} into a "
                    f"personal checklist with empty tick boxes."
                ),
                "dyslexia": (
                    f"Reading bridge: finger-track the Must Know list for {topic.lower()} "
                    f"on a tinted strip, then cover and recall one item."
                ),
                "adhd": (
                    f"Mission bridge: sixty-second sprint — recite Must Know for "
                    f"{topic.lower()}, then stand, stretch, sit."
                ),
                "autism": (
                    f"Routine bridge: first read Must Know, next touch each word, then "
                    f"mark ready for Step 1. Same cue every lesson on {topic.lower()}."
                ),
            }
            if version_id in bridges:
                out_sections.append(
                    {
                        "title": "Presentation bridge",
                        "role": "presentation_bridge",
                        "body": bridges[version_id],
                        "presentation_only": True,
                    }
                )
        if role == "worked_example":
            bridges2 = {
                "visual": (
                    f"Diagram rehearsal: redraw the worked example for {topic.lower()} "
                    f"as arrows only, then restore the labels from memory."
                ),
                "auditory": (
                    f"Story memory: narrate the worked example for {topic.lower()} as a "
                    f"short spoken story with a clear beginning, middle, and end."
                ),
                "ell": (
                    f"Paraphrase drill: retell the worked example for {topic.lower()} using "
                    f"a sentence frame — “First… Next… Finally…” — without dropping terms."
                ),
                "ld": (
                    f"Micro-goal: cover the worked example and restore three bullets about "
                    f"{topic.lower()} from memory, then uncover to check."
                ),
                "dyslexia": (
                    f"Strip rehearsal: rewrite the worked example for {topic.lower()} as "
                    f"four numbered reading strips, then read them aloud slowly."
                ),
                "adhd": (
                    f"Timer mission: ninety seconds to restate the worked example for "
                    f"{topic.lower()}; stop when the timer ends even if mid-sentence."
                ),
                "autism": (
                    f"Same-order practice: replay the worked example for {topic.lower()} "
                    f"using identical wording first, then one careful paraphrase."
                ),
            }
            if version_id in bridges2:
                out_sections.append(
                    {
                        "title": "Worked-example rehearsal",
                        "role": "presentation_bridge",
                        "body": bridges2[version_id],
                        "presentation_only": True,
                    }
                )

    closing = {
        "visual": (
            f"Visual close: redraw the {topic.lower()} flowchart from memory and label "
            f"every Must Know stage before you leave. Compare your sketch with the "
            f"concept map icons one last time."
        ),
        "auditory": (
            f"Auditory close: say a one-minute spoken summary of {topic.lower()} "
            f"without looking, then hear a partner's correction. Clap when finished."
        ),
        "ell": (
            f"Language close: write three sentence frames that use Must Know key words "
            f"from {topic.lower()} correctly. Read each frame aloud once."
        ),
        "ld": (
            f"Chunk close: checklist — tick every Must Know bullet for {topic.lower()} "
            f"you can teach step by step. Any empty box becomes tomorrow's micro-goal."
        ),
        "dyslexia": (
            f"Dyslexia close: calm and clear retell — use reading strips to teach step by step "
            f"through {topic.lower()} one more time. Finger-track, then cover."
        ),
        "adhd": (
            f"Mission close: final two-minute checklist — name every Must Know idea for "
            f"{topic.lower()} without notes. Stand up when the mission ends."
        ),
        "autism": (
            f"Routine close: first review Must Know, next tick finished, then stop. "
            f"Same order for {topic.lower()} next lesson. No surprise extras today."
        ),
    }
    if version_id in closing:
        out_sections.append(
            {
                "title": "Presentation close",
                "role": "presentation_close",
                "body": closing[version_id],
                "presentation_only": True,
            }
        )
        out_sections.append(
            {
                "title": "Specialist teaching move",
                "role": "presentation_signature",
                "body": {
                    "visual": (
                        f"Specialist move for visual learners: convert every Must Know idea "
                        f"in {topic.lower()} into a labelled doodle gallery, then teach from "
                        f"the doodles only."
                    ),
                    "auditory": (
                        f"Specialist move for auditory learners: record a podcast-style mini "
                        f"lesson on {topic.lower()} and play it back once for self-check."
                    ),
                    "ell": (
                        f"Specialist move for English learners: build a personal phrasebook "
                        f"of Must Know sentences for {topic.lower()} and rehearse them daily."
                    ),
                    "ld": (
                        f"Specialist move for reduced-load learners: schedule three tiny "
                        f"reviews of {topic.lower()} instead of one long cram."
                    ),
                    "dyslexia": (
                        f"Specialist move for dyslexia support: print the Must Know list for "
                        f"{topic.lower()} in Lexend on tinted paper and revise strip by strip."
                    ),
                    "adhd": (
                        f"Specialist move for ADHD support: turn {topic.lower()} revision into "
                        f"a scoreboard of five quick wins before leisure time."
                    ),
                    "autism": (
                        f"Specialist move for autism support: laminate a finished/not-finished "
                        f"card for each Must Know idea in {topic.lower()} and reuse it weekly."
                    ),
                }[version_id],
                "presentation_only": True,
            }
        )

    page["sections"] = out_sections
    page["title"] = f"{topic} — {version_id.title()}"
    page["presentation"] = dict(spec.get("css") or {})
    lce = dict(page.get("lce") or {})
    lce["version_id"] = version_id
    lce["derived_from_canonical"] = True
    lce["presentation_only"] = True
    lce["presentation_note"] = str(spec.get("note") or "")
    lce["textbook_theory"] = True
    lce["master_lesson_inherited"] = True
    lce.pop("canonical", None)
    page["lce"] = lce
    return page


def augment_support_version(
    frozen: Mapping[str, Any],
    core: Mapping[str, Any],
    board: Mapping[str, Any],
    version_id: str,
) -> dict[str, Any]:
    """Teacher / Parent versions: the SAME Master Lesson plus additive
    guidance appended after the curriculum. Curriculum is never altered."""
    page = copy.deepcopy(dict(frozen))
    topic = str(page.get("topic") or "Lesson")
    concepts = [str(c) for c in (core.get("concepts") or [])]
    misc = _misc(dict(board))
    sections = [dict(s) for s in (page.get("sections") or []) if isinstance(s, dict)]

    if version_id == "teacher":
        goals = [str(g) for g in (core.get("objectives") or [])] or [
            f"Students can explain {topic.lower()} accurately."
        ]
        sections.append(
            {
                "title": "Teacher Notes — Lesson Objectives",
                "role": "teacher_support",
                "body": " ".join(g.rstrip(".") + "." for g in goals[:4]),
            }
        )
        sections.append(
            {
                "title": "Teacher Notes — Teaching Sequence",
                "role": "teacher_support",
                "body": (
                    "Teach the Master Lesson in print order: Introduction → What You Will Learn → "
                    "Must Know → Key Concepts → Step-by-Step → Worked Examples → Diagrams → "
                    "Vocabulary → Real-life Applications → Misconceptions → Practice → Exam → "
                    "HOTS → Summary → Quick Revision → Exit Ticket. "
                    "Every adaptation keeps this sequence — only presentation changes."
                ),
            }
        )
        if concepts:
            sections.append(
                {
                "title": "Teacher Notes — Differentiation",
                "role": "teacher_support",
                "body": (
                    "Teacher guidance: same curriculum for every learner. Dyslexia / LD: use "
                    "chunked strips and Lexend. Visual: insist on diagram tracing before prose. "
                    "Auditory: use read-aloud scripts and listening checkpoints. ELL: use "
                    "glossary stems without dropping Must Know terms. Differentiation never "
                    "means less content. "
                    + "Must Know ideas: "
                    + ", ".join(c.lower() for c in concepts[:8])
                    + "."
                ),
            }
            )
        if misc:
            sections.append(
                {
                    "title": "Teacher Notes — Misconceptions",
                    "role": "teacher_support",
                    "body": " ".join(
                        f"Watch for: {str(m.get('label') or '').rstrip('.')}. "
                        f"Correct it with: {str(m.get('correction') or '').rstrip('.')}."
                        for m in misc[:3]
                        if m.get("label")
                    ),
                }
            )
        sections.append(
            {
                "title": "Teacher Notes — Question Prompts",
                "role": "teacher_support",
                "body": (
                    "Cold-call after each Step: “Explain this Must Know idea in one sentence.” "
                    "Before Exam Questions: “Which Must Know idea does this item test?” "
                    "Exit Ticket: every learner ticks I Understand This before leaving."
                ),
            }
        )
        if concepts:
            blooms = (
                "Bloom's alignment — Remember: state each Must Know term. Understand: explain "
                + ", ".join(c.lower() for c in concepts[:4])
                + " in the taught order. Apply: trace the worked example unaided. "
                "Analyse: predict what changes if one stage is disturbed. "
                "Evaluate / HOTS: use the HOTS Questions section exactly as printed."
            )
            sections.append(
                {"title": "Teacher Notes — Assessment Guidance", "role": "teacher_support", "body": blooms}
            )
            sections.append(
                {
                    "title": "Teacher Notes — Extension",
                    "role": "teacher_support",
                    "body": (
                        "Extension: early finishers run the worked example backwards and explain "
                        "each link. Never invent replacement concepts — stay inside Must Know."
                    ),
                }
            )
            sections.append(
                {
                    "title": "Teacher Notes — Classroom orchestration",
                    "role": "teacher_support",
                    "body": (
                        f"Orchestrate {topic.lower()} as one Master Lesson with many "
                        f"presentations: open with Must Know for all, then invite learners to "
                        f"use their visual, auditory, ELL or dyslexia toolkit without leaving "
                        f"the shared sequence. Circulate with the same question prompts. "
                        f"Close with the Exit Ticket for every learner."
                    ),
                }
            )
    elif version_id == "parent":
        if concepts:
            sections.append(
                {
                    "title": "Home Explanation",
                    "role": "parent_support",
                    "body": (
                        f"Your child is learning {topic.lower()} with the family tonight. "
                        f"Talk about the lesson the same way the class does. The Master Lesson "
                        f"above is exactly what they study — every Must Know idea is required "
                        f"for the same examination. Ask them to explain "
                        + ", ".join(c.lower() for c in concepts[:4])
                        + " in their own words — one each evening is enough. Praise clear "
                        f"wording and effort, not only the perfect answer."
                    ),
                }
            )
            sections.append(
                {
                    "title": "Conversation Starters",
                    "role": "parent_support",
                    "body": "\n".join(
                        f"- Talk about this at home with your family: can you teach me "
                        f"{c.lower()} the way your lesson taught you?"
                        for c in concepts[:4]
                    )
                    + f"\n- Family challenge: who can retell {topic.lower()} in under one minute?",
                }
            )
            sections.append(
                {
                    "title": "Home Activities",
                    "role": "parent_support",
                    "body": (
                        f"Family activity for homework support: point to one everyday example of "
                        f"{topic.lower()}, match it to a Must Know idea, then check the diagram "
                        f"together. Sit with Practice Questions first, then one Exam Question. "
                        f"Do not skip concepts to make homework shorter — accessibility at home "
                        f"means patience and talk, not less curriculum."
                    ),
                }
            )
            sections.append(
                {
                    "title": "Parent encouragement",
                    "role": "parent_support",
                    "body": (
                        f"If your child feels stuck, talk about one Must Know idea only, then "
                        f"return tomorrow. Keep the family tone calm. The examination is the "
                        f"same for every learner — your support is the bridge, not a shortcut."
                    ),
                }
            )
            sections.append(
                {
                    "title": "Family study plan",
                    "role": "parent_support",
                    "body": (
                        f"Suggested home rhythm for {topic.lower()}: Monday talk about the "
                        f"diagram, Wednesday practise two short questions together, Friday "
                        f"celebrate one clear explanation. Keep sessions short. Invite siblings "
                        f"to listen. Never replace classwork with a lighter version — coach "
                        f"the same Master Lesson with warmth and patience."
                    ),
                }
            )
            sections.append(
                {
                    "title": "What success looks like at home",
                    "role": "parent_support",
                    "body": (
                        f"Success is when your child can teach the family every Must Know idea "
                        f"for {topic.lower()} without fear. Listen more than you correct. "
                        f"Talk about mistakes kindly. Homework support means sitting nearby, "
                        f"not rewriting answers for them."
                    ),
                }
            )
            sections.append(
                {
                    "title": "Parent toolkit",
                    "role": "parent_support",
                    "body": (
                        f"Parent toolkit for {topic.lower()}: sticky-note Must Know wall, "
                        f"kitchen-table diagram redraw, evening teach-back, weekend verbal "
                        f"quiz while walking, and a praise jar for clear explanations. "
                        f"Use the toolkit to coach the Master Lesson — never to replace it "
                        f"with a thinner home version."
                    ),
                }
            )

    page["sections"] = sections
    page["title"] = f"{topic} — {version_id.title()}"
    lce = dict(page.get("lce") or {})
    lce["version_id"] = version_id
    lce["derived_from_canonical"] = True
    lce["presentation_only"] = True
    lce["textbook_theory"] = True
    lce["master_lesson_inherited"] = True
    lce.pop("canonical", None)
    page["lce"] = lce
    return page


# --------------------------------------------------------------------------
# Curriculum Fidelity Validation (hard gate)
# --------------------------------------------------------------------------

def _page_text(page: Mapping[str, Any]) -> str:
    parts = [str(page.get("big_idea") or "")]
    for sec in page.get("sections") or []:
        if isinstance(sec, dict):
            parts.append(str(sec.get("title") or ""))
            parts.append(str(sec.get("body") or ""))
    return re.sub(r"\s+", " ", " ".join(parts)).lower()


def _claim_present(claim: str, blob: str) -> bool:
    c = " ".join(str(claim or "").lower().split())
    if not c:
        return True
    span = c[:60] if len(c) >= 30 else c
    if span in blob:
        return True
    words = [w for w in re.findall(r"[a-z]{4,}", c) if w not in {"that", "this", "with", "from"}]
    if not words:
        return True
    hits = sum(1 for w in words[:6] if w in blob)
    return hits >= max(2, int(0.6 * min(len(words), 6)))


def _curriculum_word_count(page: Mapping[str, Any]) -> int:
    """Count words in Master Contract sections only (ignore additive supports)."""
    total = 0
    for sec in page.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        if str(sec.get("role") or "") not in MASTER_CONTRACT_ROLES:
            continue
        if sec.get("presentation_only"):
            continue
        total += len(re.findall(r"[A-Za-z0-9']+", str(sec.get("body") or "")))
    return total


def validate_educational_parity(
    core: Mapping[str, Any],
    adaptations: Mapping[str, Any],
    *,
    mainstream: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Reject publication when any adaptation falls below Mainstream educational depth.

    Checks Master Lesson Contract completeness and that curriculum body length
    stays within a fair band of Mainstream (presentation supports do not count
    as a substitute for missing curriculum).
    """
    failures: list[str] = []
    by_adaptation: dict[str, Any] = {}
    contract = list(core.get("master_contract_roles") or [])
    # Only enforce the Master Contract when the core was authored with it.
    # Falling back to the full constant against legacy pages falsely fails generation.
    std = mainstream if isinstance(mainstream, dict) else adaptations.get("standard")
    std_words = _curriculum_word_count(std) if isinstance(std, dict) else 0

    required_presence = (
        "objective",
        "essential_learning",
        "concept",
        "worked_example",
        "visual",
        "vocabulary",
        "practice_question",
        "exam_question",
        "hots_question",
        "summary",
        "revision",
        "exit_ticket",
    ) if contract else ()

    for key, page in adaptations.items():
        if str(key).startswith("_") or key in {"vocabulary", "worksheet"}:
            continue
        if not isinstance(page, dict) or not page.get("sections"):
            continue
        roles = {
            str(s.get("role") or "")
            for s in page.get("sections") or []
            if isinstance(s, dict)
        }
        page_failures: list[str] = []
        missing_contract = [r for r in contract if r not in roles]
        if missing_contract:
            page_failures.append(
                f"master contract incomplete: {', '.join(missing_contract[:6])}"
            )
        missing_required = [r for r in required_presence if r not in roles]
        if missing_required:
            page_failures.append(
                f"educational completeness missing: {', '.join(missing_required[:6])}"
            )
        if std_words >= 80 and key != "standard":
            words = _curriculum_word_count(page)
            # Accessibility may reformat, but must not gut curriculum depth.
            if words < int(0.85 * std_words):
                page_failures.append(
                    f"educational depth below Mainstream ({words} < {int(0.85 * std_words)} curriculum words)"
                )
        by_adaptation[key] = {"ok": not page_failures, "failures": page_failures}
        for f in page_failures:
            failures.append(f"{key}: {f}")

    return {
        "schema": "alora.educational_parity.v1",
        "ok": not failures,
        "failures": failures,
        "by_adaptation": by_adaptation,
        "mainstream_curriculum_words": std_words,
        "policy": {
            "equal_to_mainstream": True,
            "accessibility_does_not_reduce_learning": True,
        },
    }


def validate_curriculum_fidelity(
    core: Mapping[str, Any],
    adaptations: Mapping[str, Any],
) -> dict[str, Any]:
    """Generation fails if any adaptation removes concepts, claims, diagrams,
    objectives or changes the mandated teaching sequence. Also fails when
    educational depth falls below the Mainstream Master Lesson."""
    failures: list[str] = []
    by_adaptation: dict[str, Any] = {}
    concepts = [str(c).lower() for c in (core.get("concepts") or [])]
    claims = [str(c) for c in (core.get("claims") or [])]
    sequence = [str(r) for r in (core.get("role_sequence") or [])]
    has_diagram = bool(core.get("has_diagram"))

    for key, page in adaptations.items():
        if str(key).startswith("_") or key in {"vocabulary", "worksheet"}:
            continue
        if not isinstance(page, dict) or not page.get("sections"):
            continue
        blob = _page_text(page)
        page_failures: list[str] = []
        missing_concepts = [c for c in concepts if c not in blob]
        if missing_concepts:
            page_failures.append(f"concepts removed: {', '.join(missing_concepts[:4])}")
        missing_claims = [c for c in claims if not _claim_present(c, blob)]
        if missing_claims:
            page_failures.append(f"curriculum claims missing: {len(missing_claims)}")
        # Sequence check: canonical roles must appear in the same relative order.
        roles = [
            str(s.get("role") or "")
            for s in page.get("sections") or []
            if isinstance(s, dict)
        ]
        core_roles_in_page = [r for r in roles if r in sequence]
        expected = [r for r in sequence if r in core_roles_in_page]
        deduped: list[str] = []
        for r in core_roles_in_page:
            if not deduped or deduped[-1] != r:
                deduped.append(r)
        # Collapse repeats of the same stage (e.g. several concept steps).
        collapsed: list[str] = []
        for r in deduped:
            if not collapsed or collapsed[-1] != r:
                collapsed.append(r)
        if [r for r in collapsed if r in expected] != [
            r for r in expected if r in collapsed
        ] and collapsed != expected:
            page_failures.append(f"teaching sequence changed: {collapsed}")
        missing_roles = [r for r in sequence if r not in roles]
        if missing_roles:
            page_failures.append(f"mandatory sections missing: {', '.join(missing_roles)}")
        if has_diagram and not (
            str(page.get("svg_diagram") or page.get("flowchart_svg") or "").startswith("<svg")
            or "visual" in roles
        ):
            page_failures.append("diagram removed")
        by_adaptation[key] = {"ok": not page_failures, "failures": page_failures}
        for f in page_failures:
            failures.append(f"{key}: {f}")

    # Exam worksheet: every question maps back to a taught concept.
    ws = adaptations.get("worksheet") if isinstance(adaptations.get("worksheet"), dict) else None
    if ws is not None and concepts:
        qs: list[str] = []
        for zone in ("short_answer", "long_answer", "questions", "hots"):
            for q in ws.get(zone) or []:
                if isinstance(q, dict):
                    qs.append(str(q.get("question") or ""))
                elif isinstance(q, str):
                    qs.append(q)
        core_tokens = set()
        for c in concepts + [str(core.get("topic") or "").lower()]:
            core_tokens.update(re.findall(r"[a-z]{4,}", c))
        for c in claims:
            core_tokens.update(re.findall(r"[a-z]{4,}", c.lower()))
        unmapped = [
            q
            for q in qs
            if q.strip()
            and not (set(re.findall(r"[a-z]{4,}", q.lower())) & core_tokens)
        ]
        if unmapped:
            failures.append(f"worksheet: {len(unmapped)} question(s) outside the taught lesson")
        by_adaptation["worksheet"] = {"ok": not unmapped, "failures": unmapped[:3]}

    parity = validate_educational_parity(core, adaptations)
    if not parity.get("ok", True):
        failures.extend(list(parity.get("failures") or []))
        for key, row in (parity.get("by_adaptation") or {}).items():
            prior = by_adaptation.get(key) or {"ok": True, "failures": []}
            merged_fail = list(prior.get("failures") or []) + list(row.get("failures") or [])
            by_adaptation[key] = {"ok": not merged_fail, "failures": merged_fail}

    return {
        "schema": "alora.curriculum_fidelity.v1",
        "ok": not failures,
        "failures": failures,
        "by_adaptation": by_adaptation,
        "core_hash": str(core.get("hash") or ""),
        "educational_parity": parity,
        "policy": {
            "one_lesson": True,
            "identical_curriculum": True,
            "presentation_only_adaptations": True,
            "essential_learning_core_locked": True,
            "equal_educational_standard": True,
        },
    }
