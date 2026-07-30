"""Publisher authorship via Teacher Composition Framework.

Product law: no canned scaffolds author lessons; educational banks supply materials the composer weaves.
All profiles compose independently from the same verified claims.
"""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.intelligence_board import board_claim_for
from engines.lesson_composition_engine.teacher_composition import (
    CompositionFailure,
    TEACHER_COMPOSITION_SMOKE_OK,
    compose_activity,
    compose_diagram_guidance,
    compose_hook,
    compose_summary,
    concept_plan,
    extract_concept_label,
    infer_age_band,
    teach_compact_for_profile,
    teach_concept_paragraph,
    teach_sections_for_profile,
    validate_learner_prose,
)

# Re-export for master_teacher / tests
__all__ = [
    "TEACHER_COMPOSITION_SMOKE_OK",
    "CompositionFailure",
    "compose_publisher_adaptation",
    "compose_publisher_standard",
    "teach_concept_paragraph",
]


def _claims(board: Mapping[str, Any]) -> list[str]:
    from engines.lesson_composition_engine.vocab_quality import clean_learner_claim

    out: list[str] = []
    for c in board.get("verified_claims") or []:
        fixed = clean_learner_claim(str(c))
        if fixed:
            out.append(fixed)
    return out


def _concept_names(board: Mapping[str, Any], claims: list[str]) -> list[str]:
    skip = {
        "greater",
        "lesser",
        "higher",
        "lower",
        "same",
        "many",
        "some",
        "this",
        "that",
        "when",
        "after",
        "before",
        "using",
        "through",
        "during",
        "simple",
        "fresh",
        "rule",
        "linear",
        "active",
        "clear",
        "good",
    }
    topic = str(board.get("topic") or "").strip()
    concepts_raw = [c for c in (board.get("concepts") or []) if isinstance(c, dict)]
    names: list[str] = []
    seen: set[str] = set()

    def _add(label: str) -> None:
        clean = (label or "").strip()
        if not clean or clean.lower() in skip or clean.lower() in seen:
            return
        seen.add(clean.lower())
        names.append(clean)

    for c in concepts_raw:
        raw = str(c.get("name") or "").strip()
        explain = str(c.get("explanation") or c.get("claim") or "").strip()
        if not raw or raw.lower() in skip or len(raw.split()) == 1:
            # Repair weak board labels from the claim itself
            if explain:
                raw = extract_concept_label(explain, topic, avoid=seen) or raw
        if raw.lower() in seen and explain:
            raw = extract_concept_label(explain, topic, avoid=seen) or raw
        _add(raw)
    for claim in claims[:5]:
        if len(names) >= 5:
            break
        _add(extract_concept_label(claim, topic, avoid=seen))
    if not names and topic:
        return [topic]
    return names[:5] or ([topic] if topic else ["Idea"])


def _misc(board: Mapping[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in board.get("misconceptions") or []:
        if isinstance(item, dict):
            out.append(
                {
                    "label": str(item.get("label") or item.get("misconception") or ""),
                    "correction": str(item.get("correction") or item.get("remedy") or ""),
                }
            )
    return out


def _fail_package(topic: str, reason: str, *, version_id: str = "standard") -> dict[str, Any]:
    """Fail generation rather than insert template filler."""
    return {
        "big_idea": "",
        "sections": [],
        "topic": topic,
        "title": f"{topic} — composition failed",
        "flowchart_svg": "",
        "concept_map_svg": "",
        "svg_diagram": "",
        "lce": {
            "version_id": version_id,
            "composition_failed": True,
            "composition_failure_reason": reason[:400],
            "teacher_composition": True,
            "no_template_banks": True,
        },
        "_composition_error": reason[:400],
    }


def _teaching_units(board: Mapping[str, Any], claims: list[str], names: list[str]) -> list[tuple[str, str]]:
    """One teaching unit per concept, then remaining claims — never drop verified claims."""
    topic = str(board.get("topic") or "").strip()
    units: list[tuple[str, str]] = []
    used_claims: set[str] = set()
    used_labels: set[str] = set()
    for index, name in enumerate(names[:4]):
        claim = board_claim_for(board, name) or (
            claims[index] if index < len(claims) else (claims[0] if claims else "")
        )
        claim = str(claim or "").strip()
        if not claim or claim in used_claims:
            # Never teach the same claim twice under a second label
            claim = next((c for c in claims if c not in used_claims), "")
            claim = str(claim or "").strip()
        if not claim:
            continue
        label = str(name).strip()
        if label.lower() in used_labels or len(label.split()) == 1:
            label = extract_concept_label(claim, topic, avoid=used_labels) or label
        if label.lower() in used_labels:
            continue
        # Never teach a unit whose label is just the lesson title when claim subject differs
        if label.lower() == topic.lower():
            repaired = extract_concept_label(claim, topic, avoid=used_labels | {topic.lower()})
            if not repaired or repaired.lower() == topic.lower():
                continue
            label = repaired
        units.append((label, claim))
        used_labels.add(label.lower())
        used_claims.add(claim)
    for claim in claims:
        if claim in used_claims:
            continue
        if len(units) >= 4:
            break
        label = extract_concept_label(claim, topic, avoid=used_labels)
        if not label or len(label) < 3 or label.lower() in used_labels:
            continue
        units.append((label, claim))
        used_labels.add(label.lower())
        used_claims.add(claim)
    return units


def _dedupe_prose(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """No learner sentence may repeat verbatim — a teacher never says the same line twice."""
    import re as _re

    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for sec in sections:
        body = str(sec.get("body") or "")
        if not body.strip():
            continue
        role = str(sec.get("role") or "")
        keep_lines: list[str] = []
        for line in body.split("\n"):
            parts = _re.split(r"(?<=[.!?])\s+", line)
            kept: list[str] = []
            for part in parts:
                norm = _re.sub(r"[^a-z0-9 ]", "", part.lower()).strip()
                norm = _re.sub(r"\s+", " ", norm)
                if not norm:
                    continue
                if len(norm.split()) <= 3:
                    kept.append(part)
                    continue
                if norm in seen:
                    continue
                seen.add(norm)
                kept.append(part)
            if kept:
                keep_lines.append(" ".join(kept))
        new_body = "\n".join(keep_lines).strip()
        # A gutted section teaches nothing — drop it rather than leave a fragment
        original_words = len(body.split())
        if len(new_body.split()) < max(8, int(0.35 * original_words)) and role not in {
            "hook",
            "summary",
            "reflection",
            "vocabulary",
        }:
            continue
        if not new_body:
            continue
        sec = dict(sec)
        sec["body"] = new_body
        out.append(sec)
    return out


# Teaching journey: curiosity → explanation → worked example → visual understanding
# → guided thinking → independent thinking → real-life application → reflection.
_JOURNEY_STAGE = {
    "hook": 0,
    "real_life_example": 1,
    "concept": 2,
    "simple_explanation": 3,
    "worked_example": 4,
    "visual": 5,
    "common_misconception": 6,
    "practice_question": 7,
    "application": 8,
    "vocabulary": 9,
    "summary": 10,
    "reflection": 11,
}


def _sequence_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the lesson in teaching order — no stage may arrive before the one it depends on."""
    staged: list[tuple[int, int, dict[str, Any]]] = []
    seen_observation = False
    for position, sec in enumerate(sections):
        role = str(sec.get("role") or "")
        stage = _JOURNEY_STAGE.get(role, 6)
        if role == "real_life_example":
            # The opening observation earns curiosity; later scenes are real-life application.
            if seen_observation:
                stage = _JOURNEY_STAGE["application"]
            else:
                seen_observation = True
        staged.append((stage, position, dict(sec)))
    staged.sort(key=lambda row: (row[0], row[1]))
    out = [sec for _, _, sec in staged]
    # One closing reflection, not a queue of them.
    closers = [s for s in out if s.get("role") == "reflection"]
    if len(closers) > 1:
        keep = closers[-1]
        out = [s for s in out if s.get("role") != "reflection" or s is keep]
    return out


def _practice_set(names: list[str], claims: list[str], topic: str) -> list[dict[str, Any]]:
    """Varied assessment — explain, apply, compare, predict, correct. Never one repeated stem."""
    out: list[dict[str, Any]] = []
    first = names[0] if names else topic
    second = names[1] if len(names) > 1 else ""
    third = names[2] if len(names) > 2 else ""
    lead = str(claims[0]).rstrip(".") if claims else f"{first} matters in {topic}"
    out.append(
        {
            "question": f"Explain {first.lower()} in your own words, then give one example you have seen yourself.",
            "marks": 3,
        }
    )
    out.append(
        {
            "question": f"A classmate says “{lead}” is just a definition to memorise. Show them one situation where it changes what happens.",
            "marks": 4,
        }
    )
    if second:
        out.append(
            {
                "question": f"How are {first.lower()} and {second.lower()} different? Give one sentence for each.",
                "marks": 4,
            }
        )
    if third:
        out.append(
            {
                "question": f"Predict what would change about {third.lower()} if the conditions around it were reversed. Say why.",
                "marks": 5,
            }
        )
    out.append(
        {
            "question": f"Write one wrong statement about {topic.lower()} that a learner might believe, then correct it.",
            "marks": 4,
        }
    )
    return out[:5]


# Student lenses read textbook theory — questions live only in the exam
# module and vocabulary practice (product decision). Teacher/Parent keep
# the classroom composition.
_TEXTBOOK_LENSES = frozenset(
    {"standard", "visual", "auditory", "ell", "ld", "dyslexia", "adhd", "autism"}
)


def _textbook_concept_names(board: Mapping[str, Any], claims: list[str]) -> list[str]:
    """Technical terms exactly as the curriculum names them.

    Textbook theory teaches "Evaporation", "Condensation" — never label
    repairs like "Rising" or heading junk like "Introduction (10"."""
    topic = str(board.get("topic") or "").strip()
    names: list[str] = []
    seen: set[str] = set()
    for c in board.get("concepts") or []:
        if not isinstance(c, dict):
            continue
        raw = str(c.get("name") or "").strip()
        low = raw.lower()
        if (
            not raw
            or len(low) < 3
            or low in seen
            or any(ch.isdigit() for ch in low)
            or any(ch in raw for ch in "(|:")
            or low in {"how", "what", "why", "when", "where", "which", "who", "does"}
        ):
            continue
        seen.add(low)
        names.append(raw)
    if not names:
        for claim in claims[:5]:
            label = extract_concept_label(claim, topic, avoid=seen)
            if label and label.lower() not in seen:
                seen.add(label.lower())
                names.append(label)
    return names[:6] or ([topic] if topic else ["Idea"])


def _format_theory_body(sentences: list[str], *, version_id: str) -> str:
    """Lens-specific presentation of the same verified theory sentences."""
    rows = [s.strip().rstrip(".") + "." for s in sentences if s.strip()]
    if not rows:
        return ""
    if version_id == "ld":
        return "\n".join(f"- {r}" for r in rows)
    if version_id == "dyslexia":
        return "\n".join(rows)
    return " ".join(rows)


def _compose_textbook_adaptation(
    board: Mapping[str, Any],
    version_id: str,
    *,
    topic: str,
    claims: list[str],
    names: list[str],
    misc: list[dict[str, str]],
    flowchart_svg: str,
    concept_map_svg: str,
    age: str,
) -> dict[str, Any]:
    """Clean self-study theory: overview → one section per concept → diagram →
    mix-up → summary → self-check. No questions, hooks, or activities —
    learners study the theory; questions belong to the exam and vocabulary."""
    # Curriculum names verbatim — not repaired labels.
    names = _textbook_concept_names(board, claims)
    # Questions never teach theory — keep only declarative claims.
    teach_claims = [c for c in claims if not c.strip().endswith("?")]
    used: set[str] = set()

    def _take(pred, limit: int) -> list[str]:
        out: list[str] = []
        for c in teach_claims:
            if c in used or not pred(c):
                continue
            used.add(c)
            out.append(c)
            if len(out) >= limit:
                break
        return out

    overview_titles = {
        "standard": f"Understanding {topic}",
        "visual": f"{topic} — the whole picture first",
        "auditory": f"{topic} — read this aloud",
        "ell": f"{topic} — the key idea in plain words",
        "ld": f"{topic}, one step at a time",
        "dyslexia": f"{topic} — calm and clear",
    }
    sections: list[dict[str, Any]] = []
    topic_low = topic.lower()
    overview = _take(lambda c: topic_low in c.lower(), 2) or _take(lambda c: True, 2)
    if overview:
        sections.append(
            {
                "title": overview_titles.get(version_id, f"Understanding {topic}"),
                "role": "concept",
                "body": _format_theory_body(overview, version_id=version_id),
            }
        )

    concept_titles = {
        "standard": "{name}",
        "visual": "{name} — see it in the diagram",
        "auditory": "{name} — say it once aloud",
        "ell": "Key word: {name}",
        "ld": "{name} — step by step",
        "dyslexia": "{name}",
    }
    for name in names[:5]:
        low = name.lower()
        if low == topic_low:
            continue
        body_claims = _take(lambda c: low in c.lower(), 3)
        if not body_claims:
            continue
        sections.append(
            {
                "title": concept_titles.get(version_id, "{name}").format(
                    name=name[:1].upper() + name[1:]
                ),
                "role": "concept",
                "body": _format_theory_body(body_claims, version_id=version_id),
            }
        )

    leftovers = _take(lambda c: True, 3)
    if leftovers:
        sections.append(
            {
                "title": "More ideas from this lesson",
                "role": "concept",
                "body": _format_theory_body(leftovers, version_id=version_id),
            }
        )

    if flowchart_svg or concept_map_svg:
        stage_names = [n for n in names if n.lower() != topic_low][:5]
        flow = " → ".join(stage_names) if len(stage_names) >= 2 else topic
        sections.append(
            {
                "title": "What the diagram shows",
                "role": "visual",
                "body": (
                    f"The diagram shows {topic} as connected stages: {flow}. "
                    f"Read each labelled part in order and match it to the "
                    f"explanation above."
                ),
            }
        )

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

    recap = [n[:1].upper() + n[1:] for n in names[:5] if n.lower() != topic_low]
    summary_lines = [
        f"{topic} is the main idea of this lesson.",
    ]
    if recap:
        summary_lines.append(
            "The technical terms to remember are: " + ", ".join(recap) + "."
        )
    first_claim = next((c for c in teach_claims if topic_low in c.lower()), "")
    if first_claim:
        summary_lines.append(first_claim)
    sections.append(
        {
            "title": "What should stay with you",
            "role": "summary",
            "body": " ".join(s.rstrip(".") + "." for s in summary_lines),
        }
    )
    sections.append(
        {
            "title": "I understand this",
            "role": "reflection",
            "body": (
                f"I can explain {topic} in my own words, and I can state the "
                f"meaning of each technical term without looking back."
            ),
        }
    )

    sections = _sequence_sections(_dedupe_prose(sections))
    for sec in sections:
        validate_learner_prose(str(sec.get("body") or ""))

    big = teach_claims[0] if teach_claims else f"Clear ideas help you explain {topic}."
    if len(teach_claims) >= 2 and len(str(big).split()) < 12:
        big = f"{teach_claims[0]} {teach_claims[1]}"

    from engines.lesson_composition_engine.educational_banks import lookup_banks
    from engines.lesson_composition_engine.pmes import _diagram_package

    bank_meta = lookup_banks(
        topic, subject=str(board.get("subject") or ""), claim=teach_claims[0] if teach_claims else ""
    )
    svg = flowchart_svg or concept_map_svg
    page = {
        "big_idea": str(big)[:400],
        "sections": sections,
        "topic": topic,
        "title": f"{topic} — {version_id.title()}",
        "flowchart_svg": flowchart_svg,
        "concept_map_svg": concept_map_svg,
        "svg_diagram": svg,
        "revision_points": [f"Explain: {n}" for n in names[:6]],
        "practice": _practice_set(names, claims, topic),
        "lce": {
            "version_id": version_id,
            "teacher_composition": True,
            "textbook_theory": True,
            "educational_banks": True,
            "bank_covered": bool(bank_meta.get("covered")),
            "no_generic_fallback": bool(bank_meta.get("covered")),
            "composed_independently": True,
            "from_intelligence_board": True,
            "pedagogically_distinct": True,
            "age_band": age,
        },
    }
    if str(svg or "").startswith("<svg"):
        page["diagram_package"] = _diagram_package(page, topic=topic, concepts=names)
    return page


def compose_publisher_adaptation(
    board: Mapping[str, Any],
    version_id: str,
    *,
    flowchart_svg: str = "",
    concept_map_svg: str = "",
) -> dict[str, Any]:
    """Independently compose one learner profile from curriculum claims."""
    topic = str(board.get("topic") or "Lesson")
    claims = _claims(board)
    names = _concept_names(board, claims)
    age = infer_age_band(board)
    misc = _misc(board)

    if not claims and not names:
        return _fail_package(topic, "No verified claims or concepts on the board.", version_id=version_id)

    if version_id in _TEXTBOOK_LENSES:
        try:
            return _compose_textbook_adaptation(
                board,
                version_id,
                topic=topic,
                claims=claims,
                names=names,
                misc=misc,
                flowchart_svg=flowchart_svg,
                concept_map_svg=concept_map_svg,
                age=age,
            )
        except CompositionFailure as exc:
            return _fail_package(topic, str(exc), version_id=version_id)
        except Exception as exc:  # noqa: BLE001
            return _fail_package(topic, f"Composition error: {exc}", version_id=version_id)

    try:
        sections: list[dict[str, Any]] = []
        # Profile-specific opening — still dynamic from claims, not a bank
        hook = compose_hook(
            topic=topic, claims=claims, concepts=names, age_band=age, voice=version_id,
            subject=str(board.get("subject") or ""),
        )
        validate_learner_prose(hook)
        openers = {
            "standard": ("Have you noticed?", hook),
            "visual": ("See It First", hook),
            "auditory": ("Listen First", hook),
            "ell": ("Key Words First", hook),
            "ld": ("One Step at a Time", hook),
            "dyslexia": ("Calm Start", hook),
            "adhd": (
                "Mission Start",
                (
                    f"Two minutes. One idea from {topic}. "
                    f"Read once, stand and stretch for ten seconds, then keep going. "
                    f"{' '.join(str(hook).split()[:22])}."
                ),
            ),
            "autism": ("Today's Routine", hook),
            "teacher": ("Lesson Intent", hook),
            "parent": ("Home Focus", hook),
        }
        title, body = openers.get(version_id, openers["standard"])
        sections.append({"title": title, "role": "hook", "body": body})

        units = _teaching_units(board, claims, names)[:3]
        if version_id == "visual" and len(units) > 1:
            units = list(reversed(units))
        if version_id in {"adhd", "parent", "ld", "dyslexia"}:
            units = units[:2]

        # One full-depth concept; at most two compact follow-ons.
        full_depth = 1
        units = units[:3]
        for index, (name, claim) in enumerate(units):
            prev = units[index - 1][0] if index > 0 else None
            nxt = units[index + 1][0] if index + 1 < len(units) else None
            plan = concept_plan(
                name=name,
                claim=claim,
                topic=topic,
                previous=prev,
                nxt=nxt,
                age_band=age,
                board_misc=misc,
                voice=version_id,
                subject=str(board.get("subject") or ""),
                index=index,
            )
            if index < full_depth:
                sections.extend(teach_sections_for_profile(plan, profile=version_id, topic=topic))
            else:
                sections.extend(teach_compact_for_profile(plan, profile=version_id, topic=topic))

        # Visual understanding sits after the first worked example, never as a stray banner.
        if flowchart_svg or concept_map_svg:
            dbody = compose_diagram_guidance(
                topic=topic, concepts=names, claims=claims, voice=version_id
            )
            validate_learner_prose(dbody)
            visual_section = {
                "title": f"What the {topic} diagram shows you",
                "role": "visual",
                "body": dbody,
            }
            anchor = next(
                (i for i, s in enumerate(sections) if s.get("role") == "worked_example"),
                None,
            )
            if anchor is None:
                anchor = next(
                    (i for i, s in enumerate(sections) if s.get("role") == "concept"),
                    len(sections) - 1,
                )
            sections.insert(anchor + 1, visual_section)
            if version_id == "standard" and units:
                first_name = units[0][0]
                sections.insert(
                    anchor + 2,
                    {
                        "title": f"Read the diagram for {first_name}",
                        "role": "practice_question",
                        "body": (
                            f"Put a finger on {first_name.lower()} in the diagram. "
                            f"Say what is happening there, then say why it has to happen "
                            f"before the next stage. If you cannot, read that stage again."
                        ),
                    },
                )

        # Every verified claim must reach the learner — no idea taught to the composer only.
        prose_so_far = " ".join(str(s.get("body") or "") for s in sections).lower()
        leftovers = [
            c
            for c in claims[:6]
            if str(c).strip() and str(c).strip().rstrip(".").lower() not in prose_so_far
        ]
        if leftovers:
            joined = " ".join(str(c).strip().rstrip(".") + "." for c in leftovers[:3])
            if version_id == "teacher":
                body = f"Also state and check these before the exit ticket: {joined}"
            elif version_id == "parent":
                body = f"Two more things worth hearing at home: {joined} Ask for one example of each."
            elif version_id in {"ld", "dyslexia"}:
                body = "\n".join(str(c).strip().rstrip(".") + "." for c in leftovers[:2])
            elif version_id == "adhd":
                body = (
                    f"Final sprint — thirty seconds only. "
                    f"Fire these facts once out loud, then tick them off: "
                    + " | ".join(str(c).strip().rstrip(".") for c in leftovers[:2])
                    + "."
                )
            elif version_id == "ell":
                body = f"More sentences to say slowly: {joined} Frame: “One example is ____.”"
            elif version_id == "autism":
                body = "Next, two more facts in the same routine:\n" + "\n".join(
                    str(c).strip().rstrip(".") + "." for c in leftovers[:2]
                )
            elif version_id == "visual":
                body = f"Find these on the diagram too: {joined}"
            elif version_id == "auditory":
                body = f"Say these aloud once each: {joined}"
            else:
                body = (
                    f"Two more true things belong with this idea: {joined} "
                    f"Give each one a real example of your own before you move on."
                )
            sections.append(
                {
                    "title": "Ideas that complete the picture",
                    "role": "concept",
                    "body": body,
                }
            )

        if version_id == "standard" and names:
            woven = ", ".join(names[:3])
            sections.append(
                {
                    "title": "Words you now own",
                    "role": "vocabulary",
                    "body": (
                        f"You met {woven} inside real situations first. "
                        f"Use each word in one spoken sentence before you leave the page."
                    ),
                }
            )

        if version_id in {"standard", "parent", "adhd", "visual"}:
            act_name = names[0] if names else topic
            act_claim = claims[0] if claims else act_name
            sections.append(
                {
                    "title": "Try this (understanding, not a worksheet)",
                    "role": "application",
                    "body": compose_activity(
                        topic=topic, name=act_name, claim=str(act_claim), voice=version_id
                    ),
                }
            )

        summary = compose_summary(
            topic=topic, concepts=names, claims=claims, age_band=age,
            subject=str(board.get("subject") or ""), voice=version_id,
        )
        validate_learner_prose(summary)
        sections.append({"title": "What should stay with you", "role": "summary", "body": summary})
        closers = {
            "standard": (
                f"I understand {topic} because I can explain one idea with a real example "
                f"and keep the accurate meaning without mixing nearby ideas."
            ),
            "visual": (
                f"I understand {topic} because I can teach it from the diagram alone, "
                f"stage by stage, without reading the words again."
            ),
            "auditory": (
                f"I understand {topic} because I can explain it out loud to someone "
                f"who cannot see the page, and they follow me."
            ),
            "ell": (
                f"I understand {topic} because I can use the key words in my own sentences: "
                f"“{topic} means ____” and “One example is ____.”"
            ),
            "ld": f"I understand {topic}. I can say it in a few short words. That counts.",
            "dyslexia": f"I understand {topic}. Slow and clear beats fast and fuzzy. I got there.",
            "adhd": f"Logged: I can fire off {topic} in one clean sentence, no notes.",
            "autism": (
                f"Finished. I followed the same steps every time, and I can state "
                f"the facts of {topic} exactly."
            ),
            "teacher": (
                f"Exit check for {topic}: students restate one idea accurately and defend it "
                f"with an example that was not given to them."
            ),
            "parent": (
                f"You will know {topic} landed when your child brings it up on their own "
                f"and points at something real."
            ),
        }
        sections.append(
            {
                "title": "I understand this",
                "role": "reflection",
                "body": closers.get(version_id, closers["standard"]),
            }
        )

        for sec in sections:
            validate_learner_prose(str(sec.get("body") or ""))

        sections = _sequence_sections(_dedupe_prose(sections))

        big = claims[0] if claims else f"Clear ideas help you explain {topic}."
        if len(claims) >= 2:
            big = f"{claims[0]} {claims[1]}"
        if len(str(big).split()) < 12 and len(claims) >= 3:
            big = f"{claims[0]} {claims[1]} {claims[2]}"
        if version_id == "parent":
            big = f"Home focus: {big}"

        from engines.lesson_composition_engine.educational_banks import lookup_banks

        bank_meta = lookup_banks(topic, subject=str(board.get("subject") or ""), claim=claims[0] if claims else "")
        svg = flowchart_svg or concept_map_svg
        from engines.lesson_composition_engine.pmes import _diagram_package

        page = {
            "big_idea": str(big)[:400],
            "sections": sections,
            "topic": topic,
            "title": f"{topic} — {version_id.title()}",
            "flowchart_svg": flowchart_svg,
            "concept_map_svg": concept_map_svg,
            "svg_diagram": svg,
            "revision_points": [f"Explain: {n}" for n in names[:6]],
            "practice": _practice_set(names, claims, topic),
            "lce": {
                "version_id": version_id,
                "teacher_composition": True,
                "educational_banks": True,
                "bank_covered": bool(bank_meta.get("covered")),
                "no_generic_fallback": bool(bank_meta.get("covered")),
                "composed_independently": True,
                "from_intelligence_board": True,
                "classroom_teacher_voice": True,
                "pedagogically_distinct": True,
                "age_band": age,
            },
        }
        if str(svg or "").startswith("<svg"):
            page["diagram_package"] = _diagram_package(page, topic=topic, concepts=names)
        return page
    except CompositionFailure as exc:
        return _fail_package(topic, str(exc), version_id=version_id)
    except Exception as exc:  # noqa: BLE001
        return _fail_package(topic, f"Composition error: {exc}", version_id=version_id)


def compose_publisher_standard(
    board: Mapping[str, Any],
    *,
    flowchart_svg: str = "",
    concept_map_svg: str = "",
) -> dict[str, Any]:
    return compose_publisher_adaptation(
        board,
        "standard",
        flowchart_svg=flowchart_svg,
        concept_map_svg=concept_map_svg,
    )
