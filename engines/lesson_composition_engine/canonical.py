"""Master Lesson Architecture (v3.4) — Professional publishing quality.

FUNDAMENTAL DESIGN PRINCIPLE
    Alora AI never generates different lessons for different learners.
    There is ONLY ONE lesson: the Canonical Mainstream Lesson (Gold Standard).
    It is generated first, frozen (read-only), and every adaptation inherits
    it unchanged. Adaptation engines change PRESENTATION ONLY — they never
    remove curriculum, omit concepts, invent replacements, reorder the
    teaching sequence, or weaken outcomes.

v3.4 PROFESSIONAL PUBLISHING
    Every learner sentence must teach something new. No AI title/definition
    loops, no teacher chrome, mark-depth answers, textbook page flow
    (introduction → explanation → key points → mini recap), Bloom-balanced
    assessment, and fidelity gates before display.

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

# Master Lesson Contract — slim theory + assessed practice (product law).
# Reading lesson = introduction + concept steps + worked example + Practice /
# Exam / HOTS with answers. Vocabulary lives on the Vocabulary page only.
CANONICAL_ROLE_SEQUENCE = (
    "introduction",         # Lesson Introduction
    "concept",              # Theory steps (one idea each)
    "worked_example",       # Worked example / process walk
    "practice_question",    # Practice Questions (Q then Answer)
    "exam_question",        # Exam Questions (Q then Answer)
    "hots_question",        # HOTS Questions (Q then Answer)
)

# Roles every student adaptation must keep at Mainstream educational depth.
MASTER_CONTRACT_ROLES = CANONICAL_ROLE_SEQUENCE

# Student presentation lenses derived from the canonical lesson.
PRESENTATION_LENSES = ("visual", "auditory", "ell", "ld", "dyslexia", "adhd", "autism")


def _qa_pairs_block(pairs: list[tuple[str, str]]) -> str:
    """One question per line, answer on the next, blank line between items."""
    blocks: list[str] = []
    for i, (question, answer) in enumerate(pairs, 1):
        q = str(question or "").strip()
        a = str(answer or "").strip()
        if not q:
            continue
        if not a:
            a = "See the theory steps above for the lesson meaning."
        # Explicit blank line after each Answer (survives strip/polish passes).
        blocks.append(f"{i}. {q}\nAnswer: {a}\n")
    return "\n".join(blocks).rstrip() + "\n"


def _norm_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _unique_sentences(*chunks: str, seen: set[str] | None = None) -> tuple[list[str], set[str]]:
    """Keep only sentences that add new information (semantic near-dedupe)."""
    seen = seen if seen is not None else set()
    out: list[str] = []
    for chunk in chunks:
        for sent in _sentences(str(chunk or "")):
            key = _norm_key(sent)
            if len(key) < 12:
                continue
            prefix = key[:56]
            if key in seen or any(prefix == s[:56] for s in seen):
                continue
            seen.add(key)
            out.append(sent.rstrip(".") + ".")
    return out, seen


def _point_bank(board: Mapping[str, Any], name: str, claims: list[str]) -> list[str]:
    """Distinct teaching points for mark-depth answers — never one recycled line."""
    points: list[str] = []
    seen: set[str] = set()
    expl = _concept_explanation(board, name, claims)
    pool = [expl] + [c for c in claims if name.lower() in str(c).lower()]
    for raw in pool:
        for sent in _sentences(str(raw or "")):
            key = _norm_key(sent)
            if len(key) < 12 or key in seen:
                continue
            seen.add(key)
            points.append(sent.rstrip(".") + ".")
            if len(points) >= 8:
                return points
    if not points:
        from engines.lesson_composition_engine.vocab_quality import canonical_definition

        canon = canonical_definition(name)
        if canon:
            points.append(canon.rstrip(".") + ".")
        else:
            # Prefer silence over hollow stubs — caller skips empty banks.
            return []
    return points


def _mark_answer(
    marks: int,
    points: list[str],
    *,
    topic: str,
    lead: str = "",
    example: str = "",
) -> str:
    """Exam-ready model answer — no coaching filler, no repeated openers."""
    del lead  # never surface coaching leads in learner answers
    pts: list[str] = []
    seen: set[str] = set()
    for p in points:
        sent = str(p or "").strip()
        if not sent:
            continue
        if not sent.endswith((".", "!", "?")):
            sent += "."
        key = _norm_key(sent)
        if len(key) < 12 or key in seen or any(key[:56] == s[:56] for s in seen):
            continue
        low = sent.lower()
        if any(
            bad in low
            for bad in (
                "link each point",
                "altogether, these points",
                "start from the taught",
                "choose one clear",
                "secure understanding",
                "begin with what",
                "correct the confusion with the taught",
                "the answer is",
            )
        ):
            continue
        seen.add(key)
        pts.append(sent)
    topic_l = (topic or "this lesson").strip() or "this lesson"
    if not pts:
        pts = [f"{topic_l[:1].upper() + topic_l[1:]} is explained by the ideas taught above."]

    if marks <= 1:
        return pts[0]
    if marks == 2:
        return " ".join(pts[:2])
    if marks == 3:
        return " ".join(pts[:3])
    if marks == 4:
        a, b = pts[0], pts[1] if len(pts) > 1 else pts[0]
        c = pts[2] if len(pts) > 2 else ""
        d = pts[3] if len(pts) > 3 else ""
        return f"Both ideas belong to {topic_l.lower()}. {a} {b} {c} {d}".strip()
    bits = list(pts[: max(4, marks)])
    if example:
        ex = example.strip()
        if ex and _norm_key(ex) not in seen:
            if not ex.endswith((".", "!", "?")):
                ex += "."
            bits.insert(0, ex)
            seen.add(_norm_key(ex))
    # Ensure higher-mark answers name enough distinct taught points for the paper.
    while len(bits) < min(marks, 6) and len(pts) > len(bits):
        for p in pts:
            if _norm_key(p) not in {_norm_key(b) for b in bits}:
                bits.append(p)
                break
        else:
            break
    return " ".join(bits)


def _textbook_step_body(
    name: str,
    explanation: str,
    body_claims: list[str],
    *,
    next_name: str | None,
    seen: set[str],
) -> tuple[str, set[str]]:
    """One clear teaching paragraph — never repeat as Key points / In short / Next."""
    del next_name  # section order already shows what comes next
    del name
    expl_sents, seen = _unique_sentences(explanation, seen=seen)
    claim_sents, seen = _unique_sentences(*body_claims, seen=seen)
    lines: list[str] = []
    para = " ".join(expl_sents[:2] or claim_sents[:2])
    if para:
        lines.append(para)
    para_key = _norm_key(para)
    extras: list[str] = []
    for b in claim_sents:
        key = _norm_key(b)
        if not key or key[:56] == para_key[:56] or key in para_key or para_key in key:
            continue
        words = b.split()
        short = b if len(words) <= 22 else " ".join(words[:20]).rstrip(".,;") + "."
        extras.append(f"• {short}")
        if len(extras) >= 2:
            break
    if extras:
        lines.extend(extras)
    return "\n".join(lines).strip(), seen


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

    Junk title fragments (earth, science) are always dropped. For water-cycle
    lessons, scientific stage terms are preferred when present in the source.
    """
    from engines.lesson_composition_engine.vocab_quality import (
        ACIDS_BASES_SALTS_TERMS,
        WATER_CYCLE_TERMS,
        enrich_acids_bases_salts_terms,
        enrich_water_cycle_terms,
        is_junk_term,
        repair_ocr_prose,
    )

    topic = str(board.get("topic") or "").strip()
    names: list[str] = []
    seen: set[str] = set()

    def _add(raw: str) -> None:
        text = repair_ocr_prose(str(raw or "")).strip()
        low = text.lower()
        if (
            not text
            or len(low) < 3
            or low in seen
            or is_junk_term(text)
            or any(ch.isdigit() for ch in low)
            or any(ch in text for ch in "(|:")
            # Skip long topic titles as concepts ("The Water Cycle"), but keep
            # a single-word topic that is itself the examinable idea ("Force").
            or (low == topic.lower() and (" " in topic or len(topic) > 24))
        ):
            return
        seen.add(low)
        names.append(text)

    for item in board.get("concepts") or []:
        if isinstance(item, dict):
            _add(str(item.get("name") or item.get("title") or ""))
        else:
            _add(str(item or ""))

    if not names:
        for n in _textbook_concept_names(board, claims):
            _add(n)

    # Water-cycle lessons: prefer real process stages over title tokens.
    claim_blob = " ".join(str(c) for c in claims).lower() + " " + topic.lower()
    if any(
        k in claim_blob
        for k in ("water cycle", "evaporat", "precipitat", "condens", "water vapour", "water vapor")
    ):
        stages: list[str] = []
        for term, _definition in WATER_CYCLE_TERMS:
            low = term.lower()
            if low == "water cycle":
                continue
            stem = low.split()[0][:6]
            if stem in claim_blob or low in claim_blob:
                stages.append(term)
        if len(stages) >= 3:
            return stages[:8]
        for term, _definition in enrich_water_cycle_terms(topic, names):
            _add(term)
        if stages:
            # Put scientific stages first, then any remaining clean names.
            ordered = stages + [n for n in names if n.lower() not in {s.lower() for s in stages}]
            return ordered[:8]

    # Acids / Bases / Salts — prefer CBSE Class 8 teaching bank over OCR scraps.
    if any(k in claim_blob for k in ("acid", "base", "salt", "litmus", "neutralis", "neutraliz")):
        pack = [t for t, _ in ACIDS_BASES_SALTS_TERMS]
        # If names are mostly junk fragments, replace with the pack.
        clean_names = [n for n in names if not is_junk_term(n)]
        if len(clean_names) < 3:
            return pack[:8]
        for term, _definition in enrich_acids_bases_salts_terms(topic, clean_names):
            _add(term)
        # Lead with curriculum terms already present, then remaining pack order.
        lead = [t for t in pack if t.lower() in seen]
        rest = [n for n in names if n.lower() not in {t.lower() for t in lead}]
        return (lead + rest)[:8] or pack[:8]

    return names[:8] or [n for n in _textbook_concept_names(board, claims) if not is_junk_term(n)][:8]


def _concept_explanation(board: Mapping[str, Any], name: str, claims: list[str]) -> str:
    """Best available explanation for a concept — never invent hollow stubs."""
    from engines.lesson_composition_engine.vocab_quality import (
        build_student_definition,
        canonical_definition,
        clean_learner_claim,
        definition_from_claims,
        is_ocr_garbage_claim,
    )

    low = name.lower()
    topic = str(board.get("topic") or "this lesson")
    canon = canonical_definition(name)
    if canon:
        return canon.rstrip(".") + "."
    for item in board.get("concepts") or []:
        if isinstance(item, dict):
            item_name = str(item.get("name") or "").strip().lower()
            expl = str(item.get("explanation") or item.get("definition") or "").strip()
            expl = clean_learner_claim(expl) or ("" if is_ocr_garbage_claim(expl) else expl)
            if (
                item_name == low
                and expl
                and "key idea" not in expl.lower()
                and "one of the ideas taught" not in expl.lower()
            ):
                return expl.rstrip(".") + "."
    from_claims = definition_from_claims(name, claims)
    if from_claims and not is_ocr_garbage_claim(from_claims):
        return from_claims.rstrip(".") + "."
    # Prefer a claim that defines THIS term as the subject — never steal a
    # neighbouring definition that merely mentions the word (Area ≠ Pressure).
    subject_hits: list[str] = []
    mention_hits: list[str] = []
    for claim in claims:
        cl = clean_learner_claim(str(claim or "")) or ""
        if not cl or low not in cl.lower() or len(cl.split()) < 6:
            continue
        cl_low = cl.lower()
        if (
            cl_low.startswith(low + " ")
            or cl_low.startswith(low + " is ")
            or f"{low} is " in cl_low[:48]
        ):
            subject_hits.append(cl)
        else:
            lead = cl_low.split()[0]
            if lead in {low, "the", "a", "an", "for", "when", "in"}:
                mention_hits.append(cl)
    if subject_hits:
        return subject_hits[0].rstrip(".") + "."
    if mention_hits:
        return mention_hits[0].rstrip(".") + "."
    built = build_student_definition(name, "", topic=topic)
    if (
        built
        and "key idea" not in built.lower()
        and "find where the lesson" not in built.lower()
        and "one of the ideas taught" not in built.lower()
    ):
        return built.rstrip(".") + "."
    # Never publish hollow stubs — skip with empty string (caller filters).
    return ""

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
    from engines.lesson_composition_engine.vocab_quality import (
        clean_learner_claim,
        clean_topic,
        is_learner_safe_claim,
        is_teacher_facing_text,
    )

    raw_topic = str(board.get("topic") or "Lesson").strip()
    topic = clean_topic(raw_topic, fallback="Lesson")
    # Drop long subtitles that pollute every sentence ("The Water Cycle: How Earth's…").
    if ":" in topic and len(topic) > 36:
        topic = topic.split(":", 1)[0].strip() or topic
    topic_low = topic.lower()
    raw_claims = [c for c in _claims(dict(board)) if not c.strip().endswith("?")]
    claims = []
    for c in raw_claims:
        fixed = clean_learner_claim(c)
        if fixed and is_learner_safe_claim(fixed):
            claims.append(fixed)
    if not claims:
        for c in raw_claims:
            fixed = clean_learner_claim(c)
            if fixed and not is_teacher_facing_text(fixed):
                claims.append(fixed)
            if len(claims) >= 12:
                break
    names = _master_concept_names(board, claims)
    # Prefer scientific process order for science cycles.
    _PROCESS_ORDER = (
        "evaporation",
        "condensation",
        "precipitation",
        "collection",
        "transpiration",
        "water vapour",
        "water vapor",
        "water cycle",
    )
    by_low = {n.lower(): n for n in names}
    ordered = [by_low[k] for k in _PROCESS_ORDER if k in by_low]
    rest = [n for n in names if n.lower() not in set(_PROCESS_ORDER)]
    term_names = (ordered + rest) or list(names)
    misc = _misc(dict(board))
    goals = [str(g) for g in (board.get("learning_goals") or []) if str(g).strip()]
    examples = [str(e) for e in (board.get("examples") or []) if str(e).strip()]
    assessments = [
        str(a) for a in (board.get("assessment_objectives") or []) if str(a).strip()
    ]
    experiments = [str(e) for e in (board.get("experiments") or []) if str(e).strip()]
    # Diagram / worked-example stages: process steps first (skip state nouns alone).
    stage_names = [
        n[:1].upper() + n[1:]
        for n in term_names
        if n.lower() not in {"water vapour", "water vapor"}
    ][:6] or [n[:1].upper() + n[1:] for n in term_names[:6]]

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
    prose_seen: set[str] = set()

    # 1) Lesson Introduction — teach, do not announce the title
    intro_claims = _take(lambda c: topic_low in c.lower(), 2) or _take(lambda c: True, 2)
    goal_text = _studentize(goals[0], topic) if goals else ""
    intro_bits, prose_seen = _unique_sentences(goal_text, *intro_claims, seen=prose_seen)
    if not intro_bits:
        intro_bits = [
            f"Each idea below helps you explain {topic.lower()} accurately, in the order it is taught."
        ]
        prose_seen.add(_norm_key(intro_bits[0]))
    intro_body = " ".join(intro_bits[:3])
    if flowchart_svg or concept_map_svg:
        cue = "Study the labelled diagram with each stage before you continue."
        if _norm_key(cue) not in prose_seen:
            intro_body = f"{intro_body} {cue}".strip()
            prose_seen.add(_norm_key(cue))
    if any("area" in c.lower() and "pressure" in c.lower() for c in claims):
        pin = (
            "Start with a familiar picture: a drawing pin or a sharp knife — "
            "the same push on a small tip creates high pressure."
        )
        pin_sents, prose_seen = _unique_sentences(pin, seen=prose_seen)
        if pin_sents:
            intro_body = f"{intro_body} {' '.join(pin_sents)}".strip()
    sections.append(
        {"title": "Introduction", "role": "introduction", "body": intro_body.strip()}
    )

    # 2) Theory steps — textbook flow: explanation → key points → mini recap
    used_claims: set[str] = set()
    claim_owners: dict[str, list[str]] = {n: [] for n in term_names[:6]}

    def _owner_for_claim(claim: str) -> str | None:
        cl = claim.lower()
        for name in term_names[:6]:
            low = name.lower()
            if (
                cl.startswith(low + " ")
                or cl.startswith(low + " is ")
                or cl.startswith(low + ":")
                or f"{low} is " in cl[:48]
            ):
                return name
        hits = [
            name
            for name in term_names[:6]
            if re.search(rf"\b{re.escape(name.lower())}\b", cl)
        ]
        if not hits:
            return None
        return max(hits, key=lambda n: len(n))

    for claim in claims:
        owner = _owner_for_claim(claim)
        if owner and len(claim_owners[owner]) < 2:
            claim_owners[owner].append(claim)
            used_claims.add(claim)
    for claim in claims:
        if claim in used_claims:
            continue
        cl = claim.lower()
        candidates = [
            n
            for n in term_names[:6]
            if re.search(rf"\b{re.escape(n.lower())}\b", cl) and len(claim_owners[n]) < 2
        ]
        if not candidates:
            continue
        owner = min(candidates, key=lambda n: (len(claim_owners[n]), len(n)))
        claim_owners[owner].append(claim)
        used_claims.add(claim)

    teach_names = [n for n in term_names[:6]]
    for idx, name in enumerate(teach_names):
        explanation = _concept_explanation(board, name, claims)
        if not explanation:
            continue
        body_claims = claim_owners.get(name) or []
        next_name = teach_names[idx + 1] if idx + 1 < len(teach_names) else None
        merged_body, prose_seen = _textbook_step_body(
            name,
            explanation,
            body_claims,
            next_name=next_name,
            seen=prose_seen,
        )
        if not merged_body.strip():
            continue
        display = name[:1].upper() + name[1:]
        # Pedagogical section titles (same depth for Mainstream and Dyslexia Smart).
        from engines.lesson_composition_engine.vocab_quality import is_plural_concept

        low_name = name.strip().lower()
        if low_name in {"acid", "acids", "base", "bases", "salt", "salts"}:
            plural = {
                "acid": "Acids",
                "acids": "Acids",
                "base": "Bases",
                "bases": "Bases",
                "salt": "Salts",
                "salts": "Salts",
            }[low_name]
            section_title = f"What are {plural}?"
        elif is_plural_concept(name):
            section_title = f"What are {display}?"
        else:
            section_title = f"Understanding {display}"
        sections.append(
            {
                "title": section_title,
                "role": "concept",
                "body": merged_body,
            }
        )
    # Carry any leftover verified claims into the last theory step (curriculum fidelity).
    leftovers = [c for c in claims if c not in used_claims]
    if leftovers and sections:
        last = sections[-1]
        if last.get("role") == "concept":
            extra, prose_seen = _unique_sentences(*leftovers[:3], seen=prose_seen)
            if extra:
                last["body"] = (str(last.get("body") or "").rstrip() + " " + " ".join(extra)).strip()
                used_claims.update(leftovers[:3])

    # 3) Worked Examples — process walk / CRA (theory essential)
    if _is_mathematics(board) and stage_names:
        walk = (
            f"Concrete–Representational–Abstract (CRA) path for {stage_names[0].lower()}. "
            f"Concrete: use objects, drawings or a real situation to show "
            f"{stage_names[0].lower()}. "
            f"Representational: draw a diagram or table that shows "
            + ", ".join(n.lower() for n in stage_names[:4])
            + ". "
            f"Abstract: write the formal statement or calculation using the lesson "
            f"symbols and vocabulary. "
        )
        if examples:
            walk += "Example: " + examples[0].rstrip(".") + "."
    elif len(stage_names) >= 2 and any(
        n.lower()
        in {
            "evaporation",
            "condensation",
            "precipitation",
            "collection",
            "transpiration",
        }
        for n in stage_names
    ):
        walk_bits: list[str] = ["Follow the process from start to finish."]
        for i, n in enumerate(stage_names):
            pts = _point_bank(board, n, claims)
            lead = "First" if i == 0 else ("Finally" if i == len(stage_names) - 1 else "Next")
            walk_bits.append(f"{lead}, {pts[0]}")
        walk = " ".join(walk_bits)
        if examples:
            walk += " Example: " + examples[0].rstrip(".") + "."
    else:
        walk = (
            "Use a sharp knife or a drawing pin: the same push on a smaller tip "
            "means higher pressure."
            if any(n.lower() in {"force", "pressure", "area"} for n in term_names)
            else f"Apply each idea above to one clear everyday case of {topic.lower()}."
        )
        if examples and examples[0].rstrip(".").lower() not in {
            c.rstrip(".").lower() for c in claims
        }:
            walk += " Example: " + examples[0].rstrip(".") + "."
    if _is_science(board) and experiments and not is_teacher_facing_text(experiments[0]):
        walk += " Try this check: " + experiments[0].rstrip(".") + "."
    walk_clean, prose_seen = _unique_sentences(walk, seen=prose_seen)
    sections.append(
        {
            "title": "Worked Example",
            "role": "worked_example",
            "body": " ".join(walk_clean) if walk_clean else walk,
        }
    )

    # 4–6) Practice / Exam / HOTS — Bloom progression + mark-depth answers
    from engines.lesson_composition_engine.vocab_quality import question_what_is

    example_line = examples[0].rstrip(".") + "." if examples else ""

    practice_pairs: list[tuple[str, str]] = []
    for name in (term_names[:4] or [topic]):
        ans = _mark_answer(1, _point_bank(board, name, claims), topic=topic)
        if not ans or "one of the ideas taught" in ans.lower():
            continue
        practice_pairs.append((question_what_is(name, marks=1), ans))
    if len(term_names) >= 2:
        practice_pairs.append(
            (
                f"How are {term_names[0].lower()} and {term_names[1].lower()} connected "
                f"in {topic.lower()}? (2 marks)",
                _mark_answer(
                    2,
                    _point_bank(board, term_names[0], claims)
                    + _point_bank(board, term_names[1], claims),
                    topic=topic,
                ),
            )
        )
    sections.append(
        {
            "title": "Practice Questions",
            "role": "practice_question",
            "body": _qa_pairs_block(practice_pairs[:5]),
        }
    )

    exam_pairs: list[tuple[str, str]] = []
    for name in (term_names[:3] or [topic]):
        exam_pairs.append(
            (
                f"Explain {name.lower()}. Include its meaning and how it connects to "
                f"{topic.lower()}. (3 marks)",
                _mark_answer(3, _point_bank(board, name, claims), topic=topic),
            )
        )
    if len(term_names) >= 2:
        exam_pairs.append(
            (
                f"Compare {term_names[0].lower()} and {term_names[1].lower()}. "
                f"State one similarity and one difference. (4 marks)",
                _mark_answer(
                    4,
                    _point_bank(board, term_names[0], claims)
                    + _point_bank(board, term_names[1], claims),
                    topic=topic,
                ),
            )
        )
    sections.append(
        {
            "title": "Exam Questions",
            "role": "exam_question",
            "body": _qa_pairs_block(exam_pairs[:5]),
        }
    )

    hots_anchor = term_names[0] if term_names else topic
    hots_second = term_names[1] if len(term_names) > 1 else topic
    hots_pairs = [
        (
            f"Predict what would change about {hots_anchor.lower()} if the conditions around it "
            f"were reversed. Give a reason from the lesson. (5 marks)",
            _mark_answer(
                5,
                [
                    f"If the conditions that cause {hots_anchor.lower()} were reversed, that stage would slow or stop."
                ]
                + _point_bank(board, hots_anchor, claims),
                topic=topic,
                lead=f"Begin with what {hots_anchor.lower()} needs in order to happen",
                example=example_line,
            ),
        ),
        (
            f"A classmate confuses {hots_anchor.lower()} with {hots_second.lower()}. "
            f"Write the correction using ideas from this lesson. (5 marks)",
            _mark_answer(
                5,
                [
                    f"{hots_anchor[:1].upper() + hots_anchor[1:]} and "
                    f"{hots_second[:1].upper() + hots_second[1:]} are different ideas in {topic.lower()}, not the same thing."
                ]
                + _point_bank(board, hots_anchor, claims)
                + _point_bank(board, hots_second, claims),
                topic=topic,
                lead="Correct the confusion with the taught meanings",
            ),
        ),
        (
            f"Describe one everyday situation that shows {topic.lower()} at work, and name each "
            f"main idea inside it. (6 marks)",
            _mark_answer(
                6,
                [
                    example_line
                    or f"Watch {topic.lower()} at work in nature or at home."
                ]
                + [
                    f"{n[:1].upper() + n[1:]} — {_point_bank(board, n, claims)[0]}"
                    for n in (term_names[:4] or [topic])
                ],
                topic=topic,
                lead=f"Choose one clear everyday situation that shows {topic.lower()}",
                example=example_line,
            ),
        ),
    ]
    sections.append(
        {
            "title": "HOTS Questions",
            "role": "hots_question",
            "body": _qa_pairs_block(hots_pairs),
        }
    )

    # Curriculum completeness — uncovered claims ride on the last theory step.
    section_blob = re.sub(
        r"\s+",
        " ",
        " ".join(
            f"{s.get('title') or ''} {s.get('body') or ''}"
            for s in sections
            if isinstance(s, dict) and str(s.get("role") or "") in {"introduction", "concept", "worked_example"}
        ),
    ).lower()
    uncovered_claims = [c for c in claims if not _claim_present(c, section_blob)]
    if uncovered_claims:
        carried = " ".join(str(c).strip().rstrip(".") + "." for c in uncovered_claims[:8])
        for sec in reversed(sections):
            if sec.get("role") == "concept":
                sec["body"] = (str(sec.get("body") or "").rstrip() + " " + carried).strip()
                break

    practice = _practice_set(names, claims, topic)
    big_sents, _ = _unique_sentences(*(claims[:3] or [f"Clear ideas help you explain {topic}."]))
    big = " ".join(big_sents[:2]) if big_sents else f"Clear ideas help you explain {topic}."

    svg = flowchart_svg or concept_map_svg
    page: dict[str, Any] = {
        "big_idea": str(big)[:400],
        "sections": sections,
        "topic": topic,
        "title": topic,
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
            "slim_theory": True,
            "professional_publishing": True,
            "publishing_v": "3.4",
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
        or any(
            str(s.get("role") or "") == "visual"
            for s in (canonical.get("sections") or [])
            if isinstance(s, dict)
        ),
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
        "note": "Lexend 18–22px, large spacing, reading strips, colour emphasis, ≤80 words/paragraph",
        "css": {
            "font_family": "Lexend, 'OpenDyslexic', sans-serif",
            "font_size_px": 20,
            "line_height": 1.9,
            "letter_spacing": "0.03em",
            "max_paragraph_sentences": 1,
            "max_paragraph_words": 80,
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

_COLOUR_MARKERS = ("●", "◆", "▲", "■", "★", "✦", "▀")


def strip_colour_markers(text: str) -> str:
    """Remove decorative emphasis glyphs from learner prose (Visual lens legacy)."""
    if not text:
        return text
    out = re.sub(r"[●◆▲■★✦▀]", "", text)
    # Restore acid-base compounds broken by mid-word marker removal.
    out = re.sub(r"\b(acid)-\s*(base)-?\s*", r"\1-\2 ", out, flags=re.IGNORECASE)
    out = re.sub(r"(?i)\b(base)-\s*(acid)-?\s*", r"\1-\2 ", out)
    # Collapse spaces left by removed markers, keep newlines.
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r" *\n *", "\n", out)
    return out.strip() if text.strip() == text else out


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
    """Visual emphasis without injecting decorative characters into the text.

    Diagrams and layout carry the visual load — wrapping terms in ★/●/◆ made
    the lesson look broken and did not help learners.
    """
    del concepts  # reserved for future CSS/HTML highlighting
    return strip_colour_markers(body)


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
    text = "\n".join(lines)
    clean = [c for c in concepts if str(c).strip()]
    if clean:
        text = text.rstrip() + "\n\nImportant words: " + ", ".join(clean[:6]) + "."
    return text


def _chunk_paragraphs_by_words(body: str, max_words: int = 80) -> str:
    """Break walls of text for reading-support lenses."""
    lines: list[str] = []
    for line in body.split("\n"):
        raw = line.strip()
        if not raw:
            lines.append("")
            continue
        if raw.lstrip().startswith(("-", "•", "☐")) or re.match(r"^\d+\.", raw):
            lines.append(raw)
            continue
        words = raw.split()
        if len(words) <= max_words:
            lines.append(raw)
            continue
        for i in range(0, len(words), max_words):
            lines.append(" ".join(words[i : i + max_words]))
            lines.append("")
    return "\n".join(lines).strip()


def _present_qa_zone(body: str, version_id: str) -> str:
    """Same assessed questions — presentation differs by learner profile."""
    text = body.strip()
    if version_id in {"ld", "adhd", "dyslexia"}:
        chunks = [c.strip() for c in re.split(r"\n\s*\n", text) if c.strip()]
        spaced = []
        for chunk in chunks:
            spaced.append(chunk)
            spaced.append("")
        return "\n".join(spaced).rstrip() + "\n"
    if version_id == "ell":
        # Keep stems; add a one-line frame before the block.
        return "Answer in short, clear sentences. Use the key words from the lesson.\n\n" + text
    if version_id == "visual":
        if "diagram" not in text.lower():
            return "Use the lesson diagram to help you answer.\n\n" + text
        return text
    if version_id == "auditory":
        parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        out: list[str] = []
        for i, part in enumerate(parts):
            out.append(part)
            if i < len(parts) - 1:
                out.append("[Pause — try the question aloud before the answer]")
        return "\n\n".join(out)
    return text


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

    # Question zones keep every stem; only layout / support cues may change.
    if role in _QUESTION_ZONE_ROLES:
        return _present_qa_zone(body, version_id)

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
        return _chunk_paragraphs_by_words("\n".join(lines), 80)

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
        return _chunk_paragraphs_by_words("\n".join(strips).rstrip(), 80)

    if version_id == "visual":
        # Visual load is the diagram + cream cards — never decorate the prose.
        return strip_colour_markers(body)

    if version_id == "auditory":
        # Conversational teaching cues — content unchanged; never re-read titles.
        parts = [p.strip() for p in re.split(r"\n+", body) if p.strip()]
        out: list[str] = []
        if role == "introduction" and parts:
            out.append("Let's begin together.")
        elif role == "concept" and parts:
            out.append("Here is the next idea — listen carefully.")
        elif role == "worked_example" and parts:
            out.append("Now follow how it works, step by step.")
        for i, part in enumerate(parts):
            out.append(part)
            if i < len(parts) - 1 and role in {"concept", "worked_example", "summary"}:
                out.append("[Pause — listen again]")
            if role == "concept" and i == 0 and len(parts) > 1:
                out.append("Think: can you say that idea in your own words?")
        if role == "concept":
            out.append("Quick recap: hold that idea before we move on.")
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

    Student lenses keep curriculum theory only (no teacher-procedure frames,
    toolkits, or “how you will learn” chrome). Formatting changes via
    ``_present_body`` (chunking, emphasis, read-aloud pauses).
    """
    page = copy.deepcopy(dict(frozen))
    spec = _LENS_PRESENTATION.get(version_id, {})
    topic = str(page.get("topic") or "Lesson")
    concepts = [str(c) for c in (core.get("concepts") or [])]
    sections = [dict(s) for s in (page.get("sections") or []) if isinstance(s, dict)]

    out_sections: list[dict[str, Any]] = []
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

    for sec in sections:
        row = dict(sec)
        role = str(row.get("role") or "")
        # Never carry teacher-procedure chrome into a student lens.
        if row.get("presentation_only") or role.startswith("presentation_") or role.endswith(
            "_support"
        ):
            continue
        # Slim theory: drop Must-Learn / Summary chrome if a post-processor added it.
        if role in {"concept_primer", "summary", "revision", "exit_ticket", "assessment"}:
            continue
        if role == "visual" and str(row.get("title") or "").lower().startswith("using the diagram"):
            continue
        row["body"] = _present_body(
            str(row.get("body") or ""),
            version_id,
            role=role,
            concepts=concepts,
        )
        if role in title_map:
            row["title"] = title_map[role]
        out_sections.append(row)

    # Guarantee a lens-specific presentation marker so HEQ advantage stays honest
    # without restoring teacher-advice chrome.
    _LENS_CUES = {
        "visual": "See it — match each idea to the lesson diagram as you read.",
        "auditory": "Read each idea aloud, then say it once more in your own words.",
        "ell": "Key words stay exact — read the plain-words framing beside them.",
        "ld": "One step at a time — finish each idea before the next.",
        "dyslexia": "Calm and clear — one sentence per line as you read.",
        "adhd": "Short steps — finish one idea, then pause.",
        "autism": "Same order every time — follow the Steps from first to last.",
    }
    cue = _LENS_CUES.get(version_id, "")
    if cue and out_sections:
        for row in out_sections:
            if row.get("role") == "introduction":
                body = str(row.get("body") or "").strip()
                if cue.lower() not in body.lower():
                    row["body"] = f"{cue}\n\n{body}".strip()
                break

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
    lce["learner_theory_only"] = True
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
                    "Teach the Master Lesson in print order: Introduction → each concept "
                    "(explanation, key points, mini recap) → Worked Example → Practice → "
                    "Exam → HOTS. Every adaptation keeps this curriculum sequence — only "
                    "presentation changes. Do not insert Must Know / Exit Ticket chrome "
                    "into student pages."
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
                    "Cold-call after each concept: “Explain this idea in one sentence.” "
                    "Before Exam Questions: “Which taught idea does this item test?” "
                    "Close with a verbal check that every learner can name the main ideas "
                    "in order — keep exit-ticket language in teacher notes only."
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
        "introduction",
        "concept",
        "worked_example",
        "practice_question",
        "exam_question",
        "hots_question",
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
