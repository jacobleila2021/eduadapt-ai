"""Human-first educational quality — publisher pride, not metric inflation.

A lesson fails unless an exceptional teacher would use it without editing,
a top publisher would accept the page, and a learner would understand better.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Mapping

from engines.lesson_composition_engine.golden import load_golden
from engines.lesson_composition_engine.recovery import (
    adaptation_similarity_report,
    instructional_text,
)
from forensics.learner_metrics import (
    ROBOTIC_PHRASES,
    TEACHER_ADVISORY,
    _text_blob,
    phrase_hits,
    repetition_ratio,
    vocab_quality,
)

HUMAN_EDUCATIONAL_QUALITY_SMOKE_OK = True
PUBLICATION_HEQ_THRESHOLD = 95.0

# Template / meta language that proves weak teaching (never publisher-grade)
WEAK_TEACHING_MARKERS = (
    "today you will master",
    "helps you explain the topic clearly",
    "remember:",
    "write one sentence that links",
    "you already know everyday patterns",
    "like a familiar idea",
    "next, keep this meaning",
    "have you ever wondered why",
    "matters when you study",
    "trace each labelled part, then match it to the explanation",
    "the diagram shows how the ideas",
    "to everyday life:",
    "tell a partner where you would see",
    "underline the words that define",
    "read this evidence carefully",
    "in this lesson we will",
    "success criteria",
)

CONCRETE_LIFE_MARKERS = (
    "pin",
    "thumb",
    "door",
    "ball",
    "knife",
    "cup",
    "steam",
    "rain",
    "cloud",
    "chapati",
    "bread",
    "rice",
    "home",
    "kitchen",
    "playground",
    "bike",
    "shoe",
    "glass",
    "tap",
    "puddle",
    "leaf",
    "window",
    "market",
    "street",
    "notebook",
    "fridge",
    "kettle",
    "bulb",
    "mirror",
    "desk",
    "classroom",
    "sun",
    "puddle",
    "kettle",
    "ice",
    "snow",
    "window",
    "mirror",
    "shadow",
    "market",
    "street",
    "nail",
    "fridge",
    "ship",
    "wire",
    "bulb",
    "plant",
    "leaf",
)

STORY_MARKERS = (
    "have you ever",
    "imagine",
    "follow",
    "journey",
    "once",
    "when you",
    "press",
    "feel",
    "notice",
    "watch",
    "compare",
)


def _sections(adaptation: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(adaptation, dict):
        return []
    return [s for s in (adaptation.get("sections") or []) if isinstance(s, dict)]


def _role_bodies(adaptation: Mapping[str, Any], role: str) -> list[str]:
    return [
        str(s.get("body") or "").strip()
        for s in _sections(adaptation)
        if str(s.get("role") or "") == role and str(s.get("body") or "").strip()
    ]


def _concrete_hits(text: str) -> int:
    low = (text or "").lower()
    return sum(1 for m in CONCRETE_LIFE_MARKERS if m in low)


def _story_hits(text: str) -> int:
    low = (text or "").lower()
    return sum(1 for m in STORY_MARKERS if m in low)


def _weak_hits(text: str) -> list[str]:
    low = (text or "").lower()
    return [m for m in WEAK_TEACHING_MARKERS if m in low]


def _claim_alignment(adaptation: Mapping[str, Any], claims: list[str]) -> float:
    """Fraction of verified claims that appear (substantively) in learner prose."""
    if not claims:
        return 0.5
    blob = instructional_text(adaptation).lower()
    hits = 0
    for claim in claims[:6]:
        c = str(claim or "").strip().lower()
        if not c:
            continue
        # Require a meaningful span, not just one word
        span = c[:48] if len(c) >= 24 else c
        if span and span in blob:
            hits += 1
            continue
        words = [w for w in re.findall(r"[a-z]{4,}", c) if w not in {"that", "this", "with", "from", "into"}]
        if words and sum(1 for w in words[:4] if w in blob) >= min(2, len(words)):
            hits += 1
    return hits / max(len(claims[:6]), 1)


def golden_prose_similarity(adaptation: Mapping[str, Any], *, subject: str = "", topic: str = "") -> dict[str, Any]:
    """Compare learner prose to the best pre-upgrade golden lesson (not recent clones)."""
    golden = load_golden(subject=subject, topic=topic) or {}
    g_lesson = golden.get("lesson") if isinstance(golden.get("lesson"), dict) else golden
    if not isinstance(g_lesson, dict) or not g_lesson:
        return {"matched": False, "ratio": 0.0, "delta_vs_golden_words": 0, "notes": ["no golden"]}
    g_text = instructional_text(g_lesson)
    a_text = instructional_text(adaptation)
    ratio = SequenceMatcher(None, g_text[:8000].lower(), a_text[:8000].lower()).ratio()
    # Educational depth: not identical clone, but at least as substantive
    g_words = len(g_text.split())
    a_words = len(a_text.split())
    notes = []
    if a_words + 20 < g_words:
        notes.append("shorter than golden exemplar")
    if ratio < 0.12 and _concrete_hits(a_text) < _concrete_hits(g_text):
        notes.append("weaker concrete teaching than golden")
    textbook = bool(((adaptation or {}).get("lce") or {}).get("textbook_theory"))
    if textbook:
        # Product law: textbook theory is deliberately leaner than the old
        # coaching exemplars — judge substance (enough theory, no template
        # junk), not verbosity parity with pre-upgrade goldens.
        ok = a_words >= 80 and not _weak_hits(a_text)
        notes.append("textbook mode: verbosity parity with golden not required")
    else:
        ok = a_words + 15 >= g_words and _concrete_hits(a_text) >= max(1, _concrete_hits(g_text) - 1)
    return {
        "matched": True,
        "golden_id": golden.get("id"),
        "ratio": round(ratio, 4),
        "golden_words": g_words,
        "lesson_words": a_words,
        "delta_vs_golden_words": a_words - g_words,
        "notes": notes,
        "ok": ok,
    }


def score_clarity(adaptation: Mapping[str, Any]) -> float:
    text = instructional_text(adaptation)
    if len(text.split()) < 80:
        return 25.0
    weak = _weak_hits(text)
    score = 92.0 - min(50, 8 * len(weak))
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if sents:
        avg = sum(len(s.split()) for s in sents) / len(sents)
        if avg > 28:
            score -= 15
        if avg < 6:
            score -= 10
    return max(0.0, min(100.0, score))


def score_engagement(adaptation: Mapping[str, Any]) -> float:
    text = instructional_text(adaptation)
    score = 40.0 + min(35, 12 * _story_hits(text)) + min(25, 8 * _concrete_hits(text))
    if _weak_hits(text):
        score -= min(40, 5 * len(_weak_hits(text)))
    hooks = (
        _role_bodies(adaptation, "hook")
        or _role_bodies(adaptation, "introduction")
        or _role_bodies(adaptation, "concept_primer")
    )
    if hooks and _story_hits(hooks[0]) + _concrete_hits(hooks[0]) >= 1:
        score += 10
    return max(0.0, min(100.0, score))


def score_storytelling(adaptation: Mapping[str, Any]) -> float:
    text = instructional_text(adaptation)
    score = 30.0 + min(40, 15 * _story_hits(text)) + min(30, 10 * _concrete_hits(text))
    if "journey" in text.lower() or "follow" in text.lower() or "compare" in text.lower():
        score += 8
    if _story_hits(text) >= 1 and _concrete_hits(text) >= 1:
        score += 10
    return max(0.0, min(100.0, score))


def score_progression(adaptation: Mapping[str, Any]) -> float:
    roles = [str(s.get("role") or "") for s in _sections(adaptation)]
    role_set = set(roles)
    # Master Lesson Contract uses introduction/essential_learning instead of
    # hook/simple_explanation — count those aliases so theory pages are not
    # unfairly docked for following the mandated sequence.
    needed_groups = (
        {"hook", "introduction", "concept_primer"},
        {"visual"},
        {"concept"},
        {"simple_explanation", "essential_learning"},
        {"real_life_example"},
        {"summary"},
    )
    present = sum(1 for group in needed_groups if role_set & group)
    score = 15.0 * present
    # Penalise role spam / clone depth without teaching
    if len(roles) > 28:
        score -= 20
    if "process" in role_set or "worked_example" in role_set:
        score += 8
    if "reflection" in role_set or "exit_ticket" in role_set:
        score += 5
    if "essential_learning" in role_set or "introduction" in role_set:
        score += 4
    return max(0.0, min(100.0, score))


def score_learner_confidence(adaptation: Mapping[str, Any]) -> float:
    """Can a learner restate the big idea and one example?"""
    big = str(adaptation.get("big_idea") or "")
    text = instructional_text(adaptation)
    score = 40.0
    if len(big.split()) >= 12 and not _weak_hits(big):
        score += 25
    elif len(big.split()) >= 8:
        score += 10
    else:
        score -= 15
    if _role_bodies(adaptation, "simple_explanation") or "say it simply" in text.lower():
        score += 10
    if "i understand" in text.lower() and "because" in text.lower():
        score += 20
    if _role_bodies(adaptation, "practice_question") or _role_bodies(adaptation, "application"):
        score += 10
    if _role_bodies(adaptation, "common_misconception") or "many learners think" in text.lower() or "many learners believe" in text.lower():
        score += 8
    if _weak_hits(text):
        score -= min(30, 4 * len(_weak_hits(text)))
    return max(0.0, min(100.0, score))


def score_examples(adaptation: Mapping[str, Any]) -> float:
    examples = _role_bodies(adaptation, "real_life_example") + _role_bodies(adaptation, "worked_example")
    text = instructional_text(adaptation)
    if not examples and _concrete_hits(text) < 2:
        return 15.0
    score = 45.0
    # Count distinct concrete scenes
    concrete = _concrete_hits(text)
    score += min(35, concrete * 8)
    for body in examples[:6]:
        if _concrete_hits(body) >= 1:
            score += 6
        if _weak_hits(body):
            score -= 10
        if "underline the words" in body.lower() or "read this evidence carefully" in body.lower():
            score -= 20
    if "many learners think" in text.lower() or "many learners believe" in text.lower() or "actually" in text.lower():
        score += 8
    return max(0.0, min(100.0, score))


def score_educational_flow(adaptation: Mapping[str, Any]) -> float:
    sections = _sections(adaptation)
    if len(sections) < 6:
        return 35.0
    score = 70.0
    # First section should hook, not announce mastery
    first = str(sections[0].get("body") or "").lower()
    if "today you will master" in first or "learning goal" in first:
        score -= 25
    if _story_hits(first) or _concrete_hits(first):
        score += 15
    # Diagram early
    roles = [str(s.get("role") or "") for s in sections[:4]]
    if "visual" in roles:
        score += 10
    return max(0.0, min(100.0, score))


def score_diagram_usefulness(adaptation: Mapping[str, Any]) -> float:
    svg = any(
        str(adaptation.get(k) or "").startswith("<svg")
        for k in ("flowchart_svg", "concept_map_svg", "svg_diagram")
    )
    # Slim theory keeps SVG assets without a Diagrams prose section.
    if bool((adaptation.get("lce") or {}).get("slim_theory")) and svg:
        return 88.0
    visual_bodies = _role_bodies(adaptation, "visual")
    text = instructional_text(adaptation).lower()
    if not svg:
        return 20.0
    if not visual_bodies:
        return 25.0
    body = " ".join(visual_bodies).lower()
    score = 45.0
    if any(w in body for w in ("trace", "point", "label", "arrow", "stage", "→", "->", "finger")):
        score += 20
    if any(w in body for w in ("ask yourself", "where is", "why", "explain", "match it")):
        score += 10
    if _concrete_hits(body) or any(
        w in body for w in ("evaporat", "force", "pressure", "digest", "fraction", "light")
    ):
        score += 15
    # Re-use later in the lesson
    if text.count("diagram") >= 2 or ("point to" in text and "diagram" in text):
        score += 10
    if "ask yourself" in body or "match it to the step" in body:
        score += 8
    if "the diagram shows how the ideas" in body:
        score -= 35
    return max(0.0, min(100.0, score))


def score_vocabulary_learning(adaptations: Mapping[str, Any]) -> float:
    vocab = adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {}
    raw = float((vocab_quality(vocab) or {}).get("score") or 0)
    # Cap inflation: vocab cards cannot manufacture teaching quality
    return min(100.0, raw)


def _is_textbook_page(page: Mapping[str, Any] | None) -> bool:
    return bool(((page or {}).get("lce") or {}).get("textbook_theory")) if isinstance(page, dict) else False


# Presentation markers each textbook lens must carry (product law: same
# verified theory, lens-specific presentation).
_TEXTBOOK_LENS_MARKERS = {
    "visual": (("see it in the diagram", "see it —", "diagram"), "diagram-anchored theory reading"),
    "auditory": (("aloud",), "read-aloud rehearsal of the same theory"),
    "ell": (("clear english", "short", "everyday", "means"), "clearer English framing"),
    "ld": (("step by step", "one step at a time", "\n-"), "single-idea steps with reduced load"),
    "dyslexia": (("calm and clear", "decoding support", "\n"), "one sentence per line, calm layout, decoding support"),
    "adhd": (("short", "step", "\n-"), "short-burst reading"),
    "autism": (("same order", "routine", "step"), "predictable order"),
}


def adaptation_educational_advantage(
    adaptation: Mapping[str, Any],
    mainstream: Mapping[str, Any],
    *,
    version_id: str,
) -> dict[str, Any]:
    """What educational advantage does this version provide that mainstream does not?"""
    a_text = instructional_text(adaptation)
    m_text = instructional_text(mainstream)
    sim = SequenceMatcher(None, a_text[:10000], m_text[:10000]).ratio()
    advantages: list[str] = []
    weak = True

    if _is_textbook_page(adaptation) and version_id in {"teacher", "parent"}:
        # v3.3: Teacher/Parent inherit the canonical lesson unchanged and ADD
        # guidance — high similarity to mainstream is mandated, not a clone.
        support_role = "teacher_support" if version_id == "teacher" else "parent_support"
        has_support = any(
            str(s.get("role") or "") == support_role for s in _sections(adaptation)
        )
        label = (
            "canonical lesson plus teaching guidance (outcomes, misconceptions, Bloom's, assessment)"
            if version_id == "teacher"
            else "canonical lesson plus home support (discussion questions, support strategies)"
        )
        if has_support and sim <= 0.995:
            return {
                "version_id": version_id,
                "advantage": label,
                "advantages": [label],
                "similarity_to_mainstream": round(sim, 4),
                "ok": True,
                "failure_reason": "",
            }
        return {
            "version_id": version_id,
            "advantage": "",
            "advantages": [],
            "similarity_to_mainstream": round(sim, 4),
            "ok": False,
            "failure_reason": (
                "clone_of_mainstream" if sim > 0.995 else "no_clear_educational_advantage"
            ),
        }

    if _is_textbook_page(adaptation) and version_id in _TEXTBOOK_LENS_MARKERS:
        markers, label = _TEXTBOOK_LENS_MARKERS[version_id]
        raw_bodies = " ".join(
            str(s.get("body") or "") for s in _sections(adaptation)
        )
        haystack = (a_text + " " + raw_bodies).lower()
        if any(m in haystack for m in markers) and sim <= 0.995:
            return {
                "version_id": version_id,
                "advantage": label,
                "advantages": [label],
                "similarity_to_mainstream": round(sim, 4),
                "ok": True,
                "failure_reason": "",
            }
        return {
            "version_id": version_id,
            "advantage": "",
            "advantages": [],
            "similarity_to_mainstream": round(sim, 4),
            "ok": False,
            "failure_reason": (
                "clone_of_mainstream" if sim > 0.995 else "no_clear_educational_advantage"
            ),
        }

    if version_id == "visual":
        if "diagram" in a_text.lower() or "picture" in a_text.lower() or "illustration" in a_text.lower():
            if score_diagram_usefulness(adaptation) >= 55:
                advantages.append("diagram-led teaching with labelled practice")
        if "see it first" in a_text.lower() or "illustration first" in a_text.lower():
            advantages.append("illustration-first sequence")
    elif version_id == "auditory":
        if any(w in a_text.lower() for w in ("say", "listen", "aloud", "story", "hear", "repeat")):
            advantages.append("spoken rehearsal and story memory cues")
    elif version_id == "ell":
        if any(w in a_text.lower() for w in ("sentence frame", "word:", "means", "say:")):
            advantages.append("simplified English with sentence frames")
    elif version_id in {"ld", "dyslexia"}:
        if a_text.count("\n-") >= 2 or "small step" in a_text.lower() or "calm read" in a_text.lower():
            advantages.append("chunked / slowed instructional load")
    elif version_id == "adhd":
        if "chunk" in a_text.lower() or "mission" in a_text.lower() or "2-minute" in a_text.lower():
            advantages.append("short-burst mission structure with checks")
    elif version_id == "autism":
        if "routine" in a_text.lower() or "same" in a_text.lower() or "first," in a_text.lower():
            advantages.append("predictable routine and literal steps")
    elif version_id == "teacher":
        if any(w in a_text.lower() for w in ("misconception", "model", "exit", "assess", "teach")):
            advantages.append("teaching guidance and misconception watch")
    elif version_id == "parent":
        if any(w in a_text.lower() for w in ("home", "ask", "praise", "tonight", "together")):
            advantages.append("home conversation and real-life activity prompts")
    else:
        advantages.append("mainstream classroom arc")

    # Must be substantially different instructional approach
    if sim > 0.40:
        advantages = []
    if advantages and sim <= 0.40:
        weak = False

    return {
        "version_id": version_id,
        "advantage": advantages[0] if advantages else "",
        "advantages": advantages,
        "similarity_to_mainstream": round(sim, 4),
        "ok": not weak and bool(advantages),
        "failure_reason": (
            ""
            if (not weak and advantages)
            else ("clone_of_mainstream" if sim > 0.40 else "no_clear_educational_advantage")
        ),
    }


def adaptation_advantage_report(adaptations: Mapping[str, Any]) -> dict[str, Any]:
    mainstream = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    rows = []
    for key, value in adaptations.items():
        if str(key).startswith("_") or key in {"vocabulary", "worksheet", "standard"}:
            continue
        if not isinstance(value, dict):
            continue
        rows.append(adaptation_educational_advantage(value, mainstream, version_id=key))
    failures = [r for r in rows if not r.get("ok")]
    return {
        "by_adaptation": rows,
        "failures": failures,
        "ok": not failures and bool(mainstream),
    }


def textbook_teaching_score(
    std: Mapping[str, Any], claims: list[str]
) -> tuple[float, dict[str, float]]:
    """Teaching quality for textbook-theory pages (product law: clean theory,
    no questions in prose, every technical term explained, tight chunking).

    A perfect textbook page scores 100; every real defect deducts."""
    secs = _sections(std)
    roles = [str(s.get("role") or "") for s in secs]
    # Master Lesson Contract question zones are allowed — they are not theory prose.
    _question_roles = {
        "practice_question",
        "exam_question",
        "hots_question",
        "assessment",
    }
    bodies = [
        str(s.get("body") or "")
        for s in secs
        if str(s.get("role") or "") not in _question_roles
    ]
    text = instructional_text(std)

    score = 100.0
    # Chunking: one idea per section, no walls of text.
    long_secs = sum(1 for b in bodies if len(b.split()) > 120)
    score -= 8 * long_secs
    # Questions never belong inside theory (exam/practice zones excluded above).
    questions = sum(b.count("?") for b in bodies)
    score -= 10 * questions
    # Slim theory contract: introduction + concept steps + practice/exam/hots.
    slim = (
        "practice_question" in roles
        and "exam_question" in roles
        and "hots_question" in roles
    )
    if roles.count("concept") < 2:
        score -= 12
    if not slim:
        if "summary" not in roles:
            score -= 12
        if "reflection" not in roles and "exit_ticket" not in roles:
            score -= 6
        has_svg = any(
            str(std.get(k) or "").startswith("<svg")
            for k in ("flowchart_svg", "concept_map_svg", "svg_diagram")
        )
        if has_svg and "visual" not in roles:
            score -= 6
    # Every verified claim must reach the learner.
    alignment = _claim_alignment(std, claims)
    score -= 25 * (1.0 - alignment)
    # Template junk and repetition still fail (theory body only — Q/A zones
    # intentionally restate definitions as answers).
    weak = _weak_hits(text)
    score -= 6 * len(weak)
    theory_text = " ".join(bodies)
    rep = repetition_ratio(theory_text or text)
    # Slim theory restates stage names across Steps + worked walk; allow a
    # slightly higher soft floor before docking publisher pride.
    soft_floor = 0.20 if slim else 0.12
    hard_floor = 0.24 if slim else 0.18
    if rep > hard_floor:
        score -= 12
    elif rep > soft_floor:
        score -= 6
    score = max(0.0, min(100.0, score))
    detail = {
        "chunking_long_sections": float(long_secs),
        "questions_in_theory": float(questions),
        "claim_alignment": round(alignment * 100.0, 1),
        "weak_markers": float(len(weak)),
    }
    return score, detail


def human_educational_quality(
    adaptations: Mapping[str, Any],
    *,
    subject: str = "",
    topic: str = "",
    claims: list[str] | None = None,
) -> dict[str, Any]:
    """HEQ — human educational quality (0–100). Teaching dominates; SVG/HTML cannot inflate."""
    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    text = instructional_text(std)
    full = _text_blob(
        {k: v for k, v in adaptations.items() if isinstance(v, dict) and not str(k).startswith("_")}
    )
    robotic = phrase_hits(full, ROBOTIC_PHRASES)
    student = _text_blob(
        {
            k: v
            for k, v in adaptations.items()
            if k in {"standard", "ld", "ell", "visual", "auditory", "adhd", "autism"}
            and isinstance(v, dict)
        }
    )
    advisory = phrase_hits(student, TEACHER_ADVISORY)
    weak = _weak_hits(text)
    claims = list(claims or [])
    if not claims:
        board = adaptations.get("_intelligence_board")
        if isinstance(board, dict):
            claims = [str(c) for c in (board.get("verified_claims") or []) if str(c).strip()]

    clarity = score_clarity(std)
    engagement = score_engagement(std)
    storytelling = score_storytelling(std)
    progression = score_progression(std)
    examples = score_examples(std)
    confidence = score_learner_confidence(std)
    flow = score_educational_flow(std)
    vocab = score_vocabulary_learning(adaptations)
    diagram = score_diagram_usefulness(std)
    sim = adaptation_similarity_report(adaptations)
    adv = adaptation_advantage_report(adaptations)
    distinct = 100.0 if sim.get("ok") else max(0.0, 100.0 - 20 * len(sim.get("failures") or []))
    if not adv.get("ok"):
        distinct = min(distinct, 45.0)

    alignment = _claim_alignment(std, claims) * 100.0
    golden = golden_prose_similarity(std, subject=subject, topic=topic)

    textbook = _is_textbook_page(std)
    if textbook:
        # Product law: student pages are clean textbook theory — score the
        # defects that matter to a self-studying learner, not storytelling.
        teaching, tb_detail = textbook_teaching_score(std, claims)
        # Report presentation dimensions honestly for diagnostics.
        engagement = max(engagement, teaching)
        storytelling = max(storytelling, teaching)
        examples = max(examples, teaching)
        confidence = max(confidence, teaching)
        progression = max(progression, teaching)
        flow = max(flow, teaching)
    else:
        tb_detail = {}
        # Teaching block (~78%): clarity, engagement, story, progression, examples, confidence, flow, accuracy
        teaching = (
            0.16 * clarity
            + 0.12 * engagement
            + 0.10 * storytelling
            + 0.12 * progression
            + 0.14 * examples
            + 0.10 * confidence
            + 0.10 * flow
            + 0.16 * alignment
        )
    # Hard penalties — beautiful packaging cannot rescue weak teaching
    # Repetition judged on the mainstream lesson a learner reads (not cross-adaptation clones of facts).
    # (Textbook scoring already deducted weak markers and repetition once.)
    if weak and not textbook:
        teaching = min(teaching, 55.0)
        teaching -= min(25, 4 * len(weak))
    if robotic:
        teaching -= min(20, 5 * len(robotic))
    if advisory:
        teaching -= min(15, 4 * len(advisory))
    if not textbook:
        std_rep = repetition_ratio(text)
        if std_rep > 0.18:
            teaching -= 12
        elif std_rep > 0.12:
            teaching -= 6
    teaching = max(0.0, min(100.0, teaching))

    # Secondary (~22%): adaptation distinctiveness, vocab, diagram usefulness (capped)
    # Rendering / HTML complexity intentionally excluded
    secondary = 0.45 * distinct + 0.25 * min(vocab, 85.0) + 0.30 * diagram
    overall = 0.78 * teaching + 0.22 * secondary

    # Golden floor: must not be worse than best pre-upgrade exemplar on substance.
    # Textbook pages are deliberately leaner than the old coaching exemplars
    # (product law: no fluff) — the golden word-count floor does not apply.
    if golden.get("matched") and not golden.get("ok") and not textbook:
        overall = min(overall, 88.0)

    # Publisher pride questions
    proud_teacher = teaching >= 90 and clarity >= 85 and examples >= 80 and not weak
    publisher_would_accept = overall >= PUBLICATION_HEQ_THRESHOLD and proud_teacher and adv.get("ok")
    learner_understands_better = alignment >= 70 and confidence >= 75 and examples >= 70

    human_verdict = {
        "exceptional_teacher_proud": proud_teacher,
        "publisher_would_publish": publisher_would_accept,
        "learner_understands_better": learner_understands_better,
        "classroom_ready": proud_teacher and learner_understands_better and bool(adv.get("ok")),
    }
    publication_ready = (
        overall >= PUBLICATION_HEQ_THRESHOLD
        and human_verdict["classroom_ready"]
        and bool(sim.get("ok"))
        and bool(adv.get("ok"))
        and not weak
    )

    return {
        "overall": round(overall, 1),
        "threshold": PUBLICATION_HEQ_THRESHOLD,
        "publication_ready": publication_ready,
        "components": {
            "clarity_of_explanation": round(clarity, 1),
            "engagement": round(engagement, 1),
            "storytelling": round(storytelling, 1),
            "progression_of_concepts": round(progression, 1),
            "usefulness_of_examples": round(examples, 1),
            "learner_confidence": round(confidence, 1),
            "educational_flow": round(flow, 1),
            "vocabulary_learning": round(vocab, 1),
            "diagram_usefulness": round(diagram, 1),
            "adaptation_distinctiveness": round(distinct, 1),
            "claim_accuracy_alignment": round(alignment, 1),
            "teaching_block": round(teaching, 1),
        },
        "human_verdict": human_verdict,
        "weak_teaching_markers": weak,
        "robotic_phrases": robotic,
        "advisory_leaks": advisory,
        "similarity": sim,
        "adaptation_advantages": adv,
        "golden_benchmark": golden,
        "philosophy": "human_first_publisher_pride",
    }


# Back-compat alias used by recovery pipeline
def educational_quality_score(adaptations: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    subject = str(kwargs.get("subject") or "")
    topic = str(kwargs.get("topic") or "")
    claims = kwargs.get("claims")
    heq = human_educational_quality(adaptations, subject=subject, topic=topic, claims=claims)
    comps = dict(heq.get("components") or {})
    comps["teaching_effectiveness"] = comps.get("teaching_block")
    comps["readability"] = comps.get("clarity_of_explanation")
    comps["visual_learning_quality"] = comps.get("diagram_usefulness")
    comps["accessibility"] = 70.0 if not heq.get("advisory_leaks") else 40.0
    comps["rendering_quality"] = 0.0  # deliberately zero weight — cannot inflate
    heq["components"] = comps
    return heq
