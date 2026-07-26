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

# Mandated teaching sequence (absolute curriculum fidelity).
# Extra presentation sections (concept_primer, "Using the Diagram") may be
# interleaved, but these roles must appear in this relative order and none
# may disappear.
CANONICAL_ROLE_SEQUENCE = (
    "objective",            # Learning Objectives (learner title: What You Will Learn)
    "essential_learning",   # Essential Learning — every examinable concept
    "concept",              # Core Lesson — step-by-step theory
    "worked_example",       # Worked Examples
    "visual",               # Diagrams that teach
    "vocabulary",           # Vocabulary
    "real_life_example",    # Real-Life Examples
    "summary",              # Summary
    "practice_question",    # Practice (questions allowed here)
    "revision",             # Revision
    "assessment",           # Assessment
)

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


def build_canonical_lesson(
    board: Mapping[str, Any],
    *,
    flowchart_svg: str = "",
    concept_map_svg: str = "",
) -> dict[str, Any]:
    """Compose the ONE complete Mainstream lesson (Gold Standard).

    Contains the complete curriculum in the mandated sequence:
    objectives → essential learning → core lesson (step-by-step) → worked
    examples → diagram → vocabulary → real-life examples → summary →
    practice → revision → assessment.
    """
    topic = str(board.get("topic") or "Lesson").strip()
    topic_low = topic.lower()
    claims = [c for c in _claims(dict(board)) if not c.strip().endswith("?")]
    names = _textbook_concept_names(board, claims)
    term_names = [n for n in names if n.lower() != topic_low]
    misc = _misc(dict(board))
    goals = [str(g) for g in (board.get("learning_goals") or []) if str(g).strip()]
    examples = [str(e) for e in (board.get("examples") or []) if str(e).strip()]
    assessments = [
        str(a) for a in (board.get("assessment_objectives") or []) if str(a).strip()
    ]

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

    # 1) Learning Objectives — student voice so the scrubbers keep it.
    objective_lines = [_studentize(g, topic) for g in goals[:4]] or [
        f"You will learn what {topic.lower()} means and how each stage works."
    ]
    for name in term_names[:4]:
        line = f"You will be able to explain {name.lower()} in your own words."
        if line not in objective_lines:
            objective_lines.append(line)
    sections.append(
        {
            "title": "What You Will Learn",
            "role": "objective",
            "body": " ".join(objective_lines[:5]),
        }
    )

    # 2) Essential Learning — every examinable concept, locked.
    essential_terms = ", ".join(n[:1].upper() + n[1:] for n in term_names[:8]) or topic
    sections.append(
        {
            "title": "Essential Learning",
            "role": "essential_learning",
            "body": (
                f"Every learner must master these examinable ideas for {topic}: "
                f"{essential_terms}. Each one is taught step by step below, and "
                f"every exam question comes only from these ideas."
            ),
        }
    )

    # 3) Core Lesson — overview then one step per concept (step-by-step).
    overview = _take(lambda c: topic_low in c.lower(), 2) or _take(lambda c: True, 2)
    if overview:
        sections.append(
            {
                "title": f"Understanding {topic}",
                "role": "concept",
                "body": " ".join(s.rstrip(".") + "." for s in overview),
            }
        )
    step = 0
    for name in term_names[:6]:
        low = name.lower()
        body_claims = _take(lambda c: low in c.lower(), 3)
        if not body_claims:
            continue
        step += 1
        sections.append(
            {
                "title": f"Step {step} — {name[:1].upper() + name[1:]}",
                "role": "concept",
                "body": " ".join(s.rstrip(".") + "." for s in body_claims),
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

    # 4) Worked Examples — walk the taught sequence as statements.
    stage_names = [n[:1].upper() + n[1:] for n in term_names[:5]]
    if len(stage_names) >= 2:
        walk = (
            f"Follow one complete example of {topic.lower()} from start to finish. "
            + " ".join(
                f"{'First' if i == 0 else 'Then' if i < len(stage_names) - 1 else 'Finally'}, "
                f"{n.lower()} takes place, exactly as taught in Step {i + 1}."
                for i, n in enumerate(stage_names)
            )
            + " Work through this chain once forwards and once backwards until each step feels natural."
        )
    else:
        walk = (
            f"Take the main idea of {topic.lower()} and apply it to the example in this lesson, "
            f"one sentence at a time, exactly as taught above."
        )
    if examples:
        walk += " Worked example from the lesson: " + examples[0].rstrip(".") + "."
    sections.append({"title": "Worked Examples", "role": "worked_example", "body": walk})

    # 5) Diagram — teaches curriculum, never decorative.
    if flowchart_svg or concept_map_svg:
        flow = " → ".join(stage_names) if len(stage_names) >= 2 else topic
        sections.append(
            {
                "title": "What the diagram shows",
                "role": "visual",
                "body": (
                    f"The diagram shows {topic} as connected stages: {flow}. "
                    f"Read each labelled part in order and match it to the step "
                    f"that teaches it."
                ),
            }
        )

    # 6) Vocabulary — the examinable terms (full cards live on the Vocabulary page).
    if term_names:
        sections.append(
            {
                "title": "Vocabulary",
                "role": "vocabulary",
                "body": (
                    "Key words you must know: "
                    + ", ".join(n[:1].upper() + n[1:] for n in term_names[:8])
                    + ". Study each meaning on the Vocabulary page until you can "
                    "say it without looking."
                ),
            }
        )

    # 7) Real-Life Examples — only from the source; never invented.
    if examples:
        sections.append(
            {
                "title": "Real-Life Examples",
                "role": "real_life_example",
                "body": " ".join(e.rstrip(".") + "." for e in examples[:3]),
            }
        )

    # 8) Common mistake (misconception) — statement + correction.
    for row in misc[:1]:
        label = str(row.get("label") or "").strip()
        correction = str(row.get("correction") or "").strip()
        if label and correction:
            sections.append(
                {
                    "title": "A common mistake to avoid",
                    "role": "common_misconception",
                    "body": f"Some learners think {label.rstrip('.')}. In fact, {correction}",
                }
            )

    # 9) Summary.
    summary_lines = [f"{topic} is the main idea of this lesson."]
    if term_names:
        summary_lines.append(
            "The technical terms to remember are: "
            + ", ".join(n[:1].upper() + n[1:] for n in term_names[:6])
            + "."
        )
    first_claim = next((c for c in claims if topic_low in c.lower()), "")
    if first_claim:
        summary_lines.append(first_claim)
    sections.append(
        {
            "title": "Summary",
            "role": "summary",
            "body": " ".join(s.rstrip(".") + "." for s in summary_lines),
        }
    )

    # 10) Practice → 11) Revision → 12) Assessment (question zone).
    practice = _practice_set(names, claims, topic)
    if practice:
        sections.append(
            {
                "title": "Practice",
                "role": "practice_question",
                "body": "\n".join(
                    f"{i + 1}. {q.get('question')}" for i, q in enumerate(practice[:3])
                ),
            }
        )
    sections.append(
        {
            "title": "Revision",
            "role": "revision",
            "body": (
                "Quick revision checklist — say each one aloud from memory:\n"
                + "\n".join(f"- Explain {n.lower()}." for n in (term_names or [topic])[:6])
            ),
        }
    )
    if len(practice) > 3:
        sections.append(
            {
                "title": "Assessment Check",
                "role": "assessment",
                "body": "\n".join(
                    f"{i + 1}. {q.get('question')} ({q.get('marks')} marks)"
                    for i, q in enumerate(practice[3:5])
                ),
            }
        )

    # 13) Reflection — statement-based self-check ("I can …"), never questions.
    can_lines = [f"I can explain {topic.lower()} in my own words."]
    can_lines += [f"I can state the meaning of {n.lower()}." for n in term_names[:4]]
    sections.append(
        {
            "title": "Reflect: I Can",
            "role": "reflection",
            "body": " ".join(can_lines),
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
        "title": f"{topic} — Canonical Lesson",
        "flowchart_svg": flowchart_svg,
        "concept_map_svg": concept_map_svg,
        "svg_diagram": svg,
        "revision_points": [f"Explain: {n}" for n in names[:6]],
        "practice": practice,
        "lce": {
            "version_id": "standard",
            "schema": CANONICAL_SCHEMA,
            "canonical": True,
            "teacher_composition": True,
            "textbook_theory": True,
            "composed_independently": True,
            "from_intelligence_board": True,
            "pedagogically_distinct": True,
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
    names = _textbook_concept_names(board, claims)
    term_names = [n for n in names if n.lower() != topic.lower()]
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
        "has_diagram": str(canonical.get("svg_diagram") or "").startswith("<svg"),
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

_QUESTION_ZONE_ROLES = {"practice_question", "assessment"}

_LENS_PRESENTATION = {
    "visual": {
        "note": "diagram-anchored reading",
        "css": {"visual_first": True},
    },
    "auditory": {
        "note": "read-aloud rehearsal",
        "css": {"narration": True},
    },
    "ell": {
        "note": "key-word support in plain English",
        "css": {"glossary": True},
    },
    "ld": {
        "note": "single-idea steps, reduced load per block",
        "css": {"bullets": True},
    },
    "dyslexia": {
        "note": "Lexend, larger spacing, one sentence per line, decoding support",
        "css": {
            "font_family": "Lexend, 'OpenDyslexic', sans-serif",
            "line_height": 1.9,
            "letter_spacing": "0.03em",
            "max_paragraph_sentences": 1,
        },
    },
    "adhd": {"note": "short-burst blocks", "css": {"bullets": True}},
    "autism": {"note": "predictable, literal layout", "css": {"literal": True}},
}


def _syllabify(term: str) -> str:
    """Naive decoding support: split a long word at vowel-group boundaries."""
    word = term.strip()
    if len(word) < 8 or " " in word:
        return ""
    parts = re.findall(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy](?=[^aeiouy]))?", word.lower())
    if len(parts) < 3 or "".join(parts) != word.lower():
        return ""
    return "·".join(parts)


def _present_body(body: str, version_id: str, *, role: str) -> str:
    """Transform presentation of one section body — content is untouched."""
    if role in _QUESTION_ZONE_ROLES or not (body or "").strip():
        return body
    if version_id in {"ld", "adhd"}:
        # One idea per block — bullets.
        lines: list[str] = []
        for line in body.split("\n"):
            if line.lstrip().startswith(("-", "•")):
                lines.append(line)
                continue
            for sent in _sentences(line):
                lines.append(f"- {sent}")
        return "\n".join(lines)
    if version_id == "dyslexia":
        # Shorter paragraphs: one sentence per line, calm layout.
        lines = []
        for line in body.split("\n"):
            if line.lstrip().startswith(("-", "•")):
                lines.append(line)
                continue
            lines.extend(_sentences(line))
        return "\n".join(lines)
    return body


def derive_presentation_adaptation(
    frozen: Mapping[str, Any],
    core: Mapping[str, Any],
    version_id: str,
) -> dict[str, Any]:
    """Inherit the frozen canonical lesson; change presentation only.

    Same concepts, same examples, same sequence, same outcomes.
    """
    page = copy.deepcopy(dict(frozen))
    spec = _LENS_PRESENTATION.get(version_id, {})
    topic = str(page.get("topic") or "Lesson")
    sections = [dict(s) for s in (page.get("sections") or []) if isinstance(s, dict)]

    out_sections: list[dict[str, Any]] = []
    for sec in sections:
        row = dict(sec)
        role = str(row.get("role") or "")
        row["body"] = _present_body(str(row.get("body") or ""), version_id, role=role)
        out_sections.append(row)

        # Additive presentation support (never replaces curriculum).
        if role == "concept" and str(row.get("title") or "").lower().startswith("step "):
            name = str(row.get("title") or "").split("—", 1)[-1].strip()
            if version_id == "visual" and page.get("svg_diagram"):
                out_sections.append(
                    {
                        # Support role (not canonical "visual") so the mandated
                        # teaching sequence stays verifiably unchanged.
                        "title": f"See it — {name}",
                        "role": "visual_support",
                        "box": "visual",
                        "body": f"Find {name.lower()} on the diagram and trace its arrow before reading on.",
                        "presentation_only": True,
                    }
                )
            elif version_id == "auditory":
                out_sections.append(
                    {
                        "title": f"Say it aloud — {name}",
                        "role": "auditory_support",
                        "body": f"Read the step above aloud once, slowly. Pause, then say the meaning of {name.lower()} from memory.",
                        "presentation_only": True,
                    }
                )
            elif version_id == "ell":
                out_sections.append(
                    {
                        "title": f"Key word — {name}",
                        "role": "language_support",
                        "body": f"{name} is an important word in this lesson. Say it aloud, then reread the step above slowly.",
                        "presentation_only": True,
                    }
                )
            elif version_id == "dyslexia":
                syl = _syllabify(name)
                if syl:
                    out_sections.append(
                        {
                            "title": f"Decoding support — {name}",
                            "role": "decoding_support",
                            "body": f"Break the word into parts: {syl}. Say each part, then the whole word.",
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
    lce.pop("canonical", None)
    page["lce"] = lce
    return page


def augment_support_version(
    frozen: Mapping[str, Any],
    core: Mapping[str, Any],
    board: Mapping[str, Any],
    version_id: str,
) -> dict[str, Any]:
    """Teacher / Parent versions: the SAME canonical lesson plus additive
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
                "title": "Learning Outcomes (Teacher)",
                "role": "teacher_support",
                "body": " ".join(g.rstrip(".") + "." for g in goals[:4]),
            }
        )
        if misc:
            sections.append(
                {
                    "title": "Misconception Watch",
                    "role": "teacher_support",
                    "body": " ".join(
                        f"Watch for: {str(m.get('label') or '').rstrip('.')}. "
                        f"Correct it with: {str(m.get('correction') or '').rstrip('.')}."
                        for m in misc[:3]
                        if m.get("label")
                    ),
                }
            )
        if concepts:
            blooms = (
                "Bloom's alignment — Remember: state each term. Understand: explain "
                + ", ".join(c.lower() for c in concepts[:4])
                + " in the taught order. Apply: trace the worked example unaided. "
                "Analyse: predict what changes if one stage is disturbed."
            )
            sections.append(
                {"title": "Bloom's Taxonomy Alignment", "role": "teacher_support", "body": blooms}
            )
            sections.append(
                {
                    "title": "Assessment Guidance",
                    "role": "teacher_support",
                    "body": (
                        "Every exam item maps to the Essential Learning list. Award full "
                        "marks only when the answer names the concept, states its meaning, "
                        "and connects it to the next stage. Use the Exam Worksheet for the "
                        "written check."
                    ),
                }
            )
            sections.append(
                {
                    "title": "Teaching Tips and Differentiation",
                    "role": "teacher_support",
                    "body": (
                        "Teach the steps in the printed order — the adaptations keep the same "
                        "sequence, so learners using the Dyslexia, Visual, Auditory or ELL "
                        "presentations can follow along with the class. Extension: ask early "
                        "finishers to run the worked example backwards and explain each link."
                    ),
                }
            )
    elif version_id == "parent":
        if concepts:
            sections.append(
                {
                    "title": "How to Support at Home",
                    "role": "parent_support",
                    "body": (
                        f"Your child is learning {topic.lower()}. The lesson above is exactly "
                        f"what they study in class. Ask them to explain "
                        + ", ".join(c.lower() for c in concepts[:4])
                        + " in their own words — one each evening is enough."
                    ),
                }
            )
            sections.append(
                {
                    "title": "Home Discussion Questions",
                    "role": "parent_support",
                    "body": "\n".join(
                        f"- Ask: can you teach me {c.lower()} the way your lesson taught you?"
                        for c in concepts[:4]
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


def validate_curriculum_fidelity(
    core: Mapping[str, Any],
    adaptations: Mapping[str, Any],
) -> dict[str, Any]:
    """Generation fails if any adaptation removes concepts, claims, diagrams,
    objectives or changes the mandated teaching sequence."""
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
        if has_diagram and not str(
            page.get("svg_diagram") or page.get("flowchart_svg") or ""
        ).startswith("<svg"):
            page_failures.append("diagram removed")
        by_adaptation[key] = {"ok": not page_failures, "failures": page_failures}
        for f in page_failures:
            failures.append(f"{key}: {f}")

    # Exam worksheet: every question maps back to a taught concept.
    ws = adaptations.get("worksheet") if isinstance(adaptations.get("worksheet"), dict) else None
    if ws is not None and concepts:
        qs: list[str] = []
        for zone in ("short_answer", "long_answer", "questions"):
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

    return {
        "schema": "alora.curriculum_fidelity.v1",
        "ok": not failures,
        "failures": failures,
        "by_adaptation": by_adaptation,
        "core_hash": str(core.get("hash") or ""),
        "policy": {
            "one_lesson": True,
            "identical_curriculum": True,
            "presentation_only_adaptations": True,
            "essential_learning_core_locked": True,
        },
    }
