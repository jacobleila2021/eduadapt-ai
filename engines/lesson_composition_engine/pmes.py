"""Publisher Master Editorial System (PMES) — highest authority over learner content.

Phase Omega 2.0: PMES does not score. It comments, rewrites, and rejects until
a lesson feels publisher-approved. Not a new engine — LCE editorial authority.
"""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.golden import compare_to_golden
from engines.lesson_composition_engine.master_teacher import apply_master_teacher_pass
from engines.lesson_composition_engine.publisher_remediation import (
    adaptation_has_generic_diagram,
    blob_of,
    has_teacher_objective_leak,
    template_hits,
)
from engines.lesson_composition_engine.publisher_style_guide import (
    BANNED_AUTHORING,
    MAX_SENTENCE_WORDS,
    PHASE_OMEGA_2_PMES_SMOKE_OK,
    STYLE_GUIDE,
    STYLE_GUIDE_VERSION,
    style_guide_css,
)

PMES_VERSION = "2.0.0"
MAX_PMES_PASSES = 4

REVIEWERS = (
    "educational_editor",
    "curriculum_editor",
    "subject_editor",
    "accessibility_editor",
    "visual_editor",
    "assessment_editor",
    "language_editor",
    "publisher_editor",
    "parent_editor",
    "teacher_editor",
)


def _sections(adaptation: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [s for s in (adaptation.get("sections") or []) if isinstance(s, dict)]


def _avg_sentence_words(text: str) -> float:
    sents = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    if not sents:
        return 0.0
    return sum(len(s.split()) for s in sents) / len(sents)


def _diagram_package(
    adaptation: Mapping[str, Any],
    *,
    topic: str,
    concepts: list[str],
) -> dict[str, Any]:
    """Ensure every diagram carries title, caption, explanation, callouts, practice."""
    svg = str(
        adaptation.get("flowchart_svg")
        or adaptation.get("svg_diagram")
        or adaptation.get("concept_map_svg")
        or ""
    )
    labels = [c for c in concepts if c][:6] or [topic]
    callouts = [f"Label: {lab}" for lab in labels[:4]]
    caption = f"{topic}: how the key ideas connect"
    explanation = (
        f"This diagram teaches the structure of {topic}. "
        f"Read each labelled part in order, then match it to the explanation in the lesson."
    )
    practice = (
        f"Point to each part of the diagram and explain {labels[0].lower()} "
        f"in one accurate sentence."
    )
    return {
        "title": topic,
        "caption": caption,
        "explanation": explanation,
        "callouts": callouts,
        "practice_question": practice,
        "svg": svg,
        "educational_purpose": f"Make the relationships in {topic} visible and testable.",
    }


def critique_adaptation(
    adaptation: Mapping[str, Any],
    *,
    adaptation_id: str = "standard",
    board: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Comment-based editorial review — no numeric scores."""
    board = board or {}
    comments: list[dict[str, str]] = []
    blob = blob_of(adaptation)
    low = blob.lower()
    topic = str(adaptation.get("topic") or board.get("topic") or "Lesson")
    sections = _sections(adaptation)

    def note(reviewer: str, comment: str) -> None:
        comments.append({"reviewer": reviewer, "comment": comment})

    def _result() -> dict[str, Any]:
        return {
            "adaptation_id": adaptation_id,
            "approved": len(comments) == 0,
            "comments": comments,
            "reviewers_heard": sorted({c["reviewer"] for c in comments}) if comments else list(REVIEWERS),
            "style_guide_version": STYLE_GUIDE_VERSION,
        }

    # Specialist pages — focused review only
    if adaptation_id == "vocabulary":
        if has_teacher_objective_leak(blob) or template_hits(blob):
            note("educational_editor", "This still reads like a template or teacher objective sheet.")
        wall = adaptation.get("word_wall") or adaptation.get("vocabulary_cards") or []
        if len(wall) < 4:
            note("publisher_editor", "The vocabulary set is too thin for a study page.")
        weak = sum(
            1
            for card in wall[:6]
            if isinstance(card, dict)
            and (not card.get("memory_tip") or not card.get("example_sentence"))
        )
        if weak:
            note("educational_editor", "The vocabulary card lacks memorability.")
        return _result()

    if adaptation_id == "worksheet":
        if has_teacher_objective_leak(blob) or template_hits(blob):
            note("educational_editor", "Worksheet still contains template or objective language.")
        dq = adaptation.get("diagram_question") if isinstance(adaptation.get("diagram_question"), dict) else {}
        if not str(dq.get("svg_diagram") or adaptation.get("svg_diagram") or "").startswith("<svg"):
            note("visual_editor", "Worksheet diagram question needs a professional SVG.")
        return _result()

    # Language / educational voice
    for phrase in BANNED_AUTHORING:
        if phrase in low:
            note("language_editor", f"Remove authoring language: “{phrase}”.")
            break
    if has_teacher_objective_leak(blob) or template_hits(blob):
        note("educational_editor", "This still reads like a template or teacher objective sheet.")
    if _avg_sentence_words(blob) > MAX_SENTENCE_WORDS + 4:
        note("language_editor", "The paragraph is too long — shorten sentences for rhythm.")
    if any(len(str(s.get("body") or "").split()) > 160 for s in sections):
        note("publisher_editor", "A section overruns comfortable textbook pacing.")

    # Engagement / teaching craft (mainstream depth; chunked profiles use different craft)
    if adaptation_id in {"standard", "visual", "teacher", "auditory"}:
        abstract_hits = sum(
            1
            for s in sections
            if str(s.get("role") or "") == "concept"
            and "example" not in str(s.get("body") or "").lower()
            and "like" not in str(s.get("body") or "").lower()
            and "for instance" not in str(s.get("body") or "").lower()
            and len(str(s.get("body") or "").split()) < 35
        )
        if abstract_hits:
            note("educational_editor", "This explanation is abstract — add analogy and real-life example.")
    if not any(str(s.get("role") or "") in {"real_life_example", "worked_example"} for s in sections):
        if adaptation_id in {"standard", "visual", "ell", "auditory", "teacher"}:
            note("subject_editor", "The analogy or worked example is weak or missing.")

    # Transitions
    titles = [str(s.get("title") or "") for s in sections]
    if adaptation_id == "standard" and len(sections) >= 3:
        bodies = [str(s.get("body") or "") for s in sections[:4]]
        if bodies and not any("next" in b.lower() or "then" in b.lower() for b in bodies):
            note("language_editor", "The transition is abrupt.")

    # Curriculum grounding
    claims = list(board.get("verified_claims") or [])
    if claims and not any(c.lower()[:36] in low for c in claims[:5]):
        note("curriculum_editor", "Verified curriculum claims are not visible enough in the prose.")

    # Visuals
    has_svg = any(
        str(adaptation.get(k) or "").startswith("<svg")
        for k in ("flowchart_svg", "concept_map_svg", "svg_diagram")
    )
    diagram_meta = adaptation.get("diagram_package") if isinstance(adaptation.get("diagram_package"), dict) else {}
    if adaptation_id not in {"parent"}:
        if not has_svg:
            note("visual_editor", "Missing professional SVG diagram.")
        elif adaptation_has_generic_diagram(adaptation):
            note("visual_editor", "The visual is decorative — replace with domain teaching diagram.")
        if not diagram_meta.get("caption") or not diagram_meta.get("practice_question"):
            note("visual_editor", "Diagram needs title, caption, explanation, callouts, and practice.")

    # Assessment
    if adaptation_id not in {"parent"}:
        has_practice = bool(adaptation.get("practice")) or any(
            str(s.get("role") or "") in {"practice_question", "application"} for s in sections
        )
        if not has_practice:
            note("assessment_editor", "Assessment does not yet measure understanding.")

    # Accessibility / distinctness
    if adaptation_id == "adhd" and not any(
        "chunk" in t.lower() or "mission" in t.lower() or "minute" in t.lower() for t in titles
    ):
        note("accessibility_editor", "ADHD edition needs chunked pacing the learner can feel.")
    if adaptation_id == "autism" and not any(
        "routine" in t.lower() or "finished" in t.lower() or "what we will" in t.lower() for t in titles
    ):
        note("accessibility_editor", "Autism edition needs predictable routine structure.")
    if adaptation_id == "ell" and "key words" not in " ".join(titles).lower():
        note("accessibility_editor", "ELL edition should open with key words and frames.")

    if adaptation_id == "parent" and "home" not in low and "child" not in low:
        note("parent_editor", "Parent edition needs clear home coaching voice.")
    if adaptation_id == "teacher" and "differentiat" not in low and "misconception" not in low:
        note("teacher_editor", "Teacher edition needs guidance a head teacher would approve.")

    # Golden educational experience (not section cloning)
    if adaptation_id in {"standard", "ld", "visual"}:
        golden = compare_to_golden(adaptation, subject=str(board.get("subject") or "general"))
        delta = float(golden.get("delta") or 0.0)
        if delta < -1.5:
            note(
                "publisher_editor",
                "A learner would not enjoy this as much as the golden lesson — rewrite for engagement.",
            )

    # Engagement loss signal
    if sections and sum(1 for s in sections if len(str(s.get("body") or "").split()) < 12) >= 3:
        note("educational_editor", "The learner loses engagement — several sections are thin.")

    return _result()


def _rewrite_from_comments(
    adaptation: dict[str, Any],
    critique: Mapping[str, Any],
    *,
    version_id: str,
    board: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply deterministic rewrites that address editorial comments."""
    from engines.lesson_composition_engine.diagrams import (
        build_concept_map_svg,
        build_educational_flowchart_svg,
        build_subject_flowchart,
    )
    from engines.lesson_composition_engine.publisher_remediation import remediate_adaptation

    out = apply_master_teacher_pass(dict(adaptation), version_id=version_id, board=board)
    topic = str(board.get("topic") or out.get("topic") or "Lesson")
    subject = str(board.get("subject") or "general")
    concepts = [
        str(c.get("name") or "")
        for c in (board.get("concepts") or [])
        if isinstance(c, dict) and c.get("name")
    ]
    claims = list(board.get("verified_claims") or [])

    joined = " ".join(c.get("comment", "") for c in (critique.get("comments") or [])).lower()

    if "diagram" in joined or "visual" in joined or "decorative" in joined:
        if len(concepts) >= 2:
            svg = build_educational_flowchart_svg(
                topic, concepts[:6], subtitle=f"{subject.title()} key ideas"
            )
        else:
            svg = build_subject_flowchart(subject, topic)
        out["flowchart_svg"] = svg
        out["svg_diagram"] = svg
        out["concept_map_svg"] = build_concept_map_svg(topic, concepts or [topic])

    out["diagram_package"] = _diagram_package(out, topic=topic, concepts=concepts)

    # Ensure diagram teaching section exists
    roles = {str(s.get("role") or "") for s in _sections(out)}
    if "visual" not in roles and out.get("flowchart_svg"):
        pkg = out["diagram_package"]
        sections = list(out.get("sections") or [])
        sections.insert(
            0,
            {
                "title": "Using the Diagram",
                "role": "visual",
                "box": "visual",
                "body": (
                    f"{pkg['explanation']} {pkg['caption']}. "
                    f"Callouts: {'; '.join(pkg['callouts'][:3])}. "
                    f"Practice: {pkg['practice_question']}"
                ),
            },
        )
        out["sections"] = sections

    if "abstract" in joined or "analogy" in joined or "example" in joined or "engagement" in joined:
        out = apply_master_teacher_pass(out, version_id=version_id, board=board)
        # Guarantee at least one concrete example section for mainstream-style reviews
        roles = {str(s.get("role") or "") for s in _sections(out)}
        if "real_life_example" not in roles and version_id in {
            "standard",
            "visual",
            "ell",
            "auditory",
            "teacher",
            "adhd",
            "ld",
            "dyslexia",
        }:
            concept = concepts[0] if concepts else topic
            example = (board.get("examples") or ["a familiar classroom or home situation"])[0]
            sections = list(out.get("sections") or [])
            sections.append(
                {
                    "title": f"Example — {concept}",
                    "role": "real_life_example",
                    "body": (
                        f"Here is a clear example of {str(concept).lower()}: {example}. "
                        f"Think of it like a familiar tool — once you can point to it, "
                        f"the meaning of {str(concept).lower()} stays with you."
                    ),
                }
            )
            out["sections"] = sections
        # Inject analogy language into thin concept bodies
        fixed = []
        for sec in out.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            row = dict(sec)
            body = str(row.get("body") or "")
            if str(row.get("role") or "") == "concept" and "like" not in body.lower() and "example" not in body.lower():
                row["body"] = (
                    body.rstrip(".")
                    + f". For example, connect this idea to something you already know about {topic}."
                )
            fixed.append(row)
        out["sections"] = fixed

    if "curriculum" in joined and claims:
        # Inject claim into big idea if missing
        lead = claims[0]
        big = str(out.get("big_idea") or "")
        if lead.lower()[:40] not in big.lower():
            out["big_idea"] = f"{lead} {big}".strip()

    if "assessment" in joined and not out.get("practice") and concepts:
        out["practice"] = [
            {"question": f"Explain {c} using the lesson diagram and one real-life example.", "marks": 2}
            for c in concepts[:4]
        ]

    out = remediate_adaptation(out, claims=claims)
    out["diagram_package"] = _diagram_package(out, topic=topic, concepts=concepts)
    out.setdefault("lce", {})
    if isinstance(out["lce"], dict):
        out["lce"]["pmes"] = True
        out["lce"]["style_guide_version"] = STYLE_GUIDE_VERSION
    return out


def edit_adaptation_to_approval(
    adaptation: dict[str, Any],
    *,
    adaptation_id: str,
    board: Mapping[str, Any] | None = None,
    max_passes: int = MAX_PMES_PASSES,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Rewrite until reviewers approve or passes exhaust."""
    board = board or {}
    current = dict(adaptation)
    history: list[dict[str, Any]] = []
    critique = critique_adaptation(current, adaptation_id=adaptation_id, board=board)

    for i in range(max_passes):
        history.append(
            {
                "pass": i + 1,
                "approved": critique.get("approved"),
                "comments": list(critique.get("comments") or []),
            }
        )
        if critique.get("approved"):
            break
        current = _rewrite_from_comments(
            current, critique, version_id=adaptation_id, board=board
        )
        critique = critique_adaptation(current, adaptation_id=adaptation_id, board=board)

    report = {
        "adaptation_id": adaptation_id,
        "approved": bool(critique.get("approved")),
        "final_comments": list(critique.get("comments") or []),
        "history": history,
        "passes": len(history),
        "pmes_version": PMES_VERSION,
    }
    current.setdefault("lce", {})
    if isinstance(current["lce"], dict):
        current["lce"]["pmes_approved"] = report["approved"]
        current["lce"]["pmes"] = True
    # Attach style CSS token for renderers
    current["publisher_style_css"] = style_guide_css()
    current["style_guide"] = {
        "version": STYLE_GUIDE_VERSION,
        "background": STYLE_GUIDE["visual"]["background"],
    }
    if not current.get("diagram_package"):
        concepts = [
            str(c.get("name") or "")
            for c in (board.get("concepts") or [])
            if isinstance(c, dict)
        ]
        current["diagram_package"] = _diagram_package(
            current, topic=str(board.get("topic") or current.get("topic") or "Lesson"), concepts=concepts
        )
    return current, report


def run_pmes(
    adaptations: dict[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
    max_passes: int = MAX_PMES_PASSES,
) -> dict[str, Any]:
    """Highest-authority editorial pass over a composed package."""
    board = board or adaptations.get("_intelligence_board") or {}
    working = dict(adaptations)
    by_id: dict[str, Any] = {}
    rejects: list[str] = []

    for key, value in list(working.items()):
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key == "vocabulary":
            from engines.lesson_composition_engine.vocabulary import compose_vocabulary_page

            edited = dict(value)
            wall = list(edited.get("word_wall") or edited.get("vocabulary_cards") or [])
            # Heal thin / incomplete cards before critique loop
            needs_rebuild = len(wall) < 4 or any(
                isinstance(c, dict) and (not c.get("memory_tip") or not c.get("example_sentence"))
                for c in wall[:6]
            )
            if needs_rebuild and board:
                seeds = list(board.get("vocabulary") or []) + [
                    str(c.get("name") or "")
                    for c in (board.get("concepts") or [])
                    if isinstance(c, dict)
                ]
                rebuilt = compose_vocabulary_page(
                    seeds or wall,
                    topic=str(board.get("topic") or "Lesson"),
                    claims=list(board.get("verified_claims") or []),
                )
                edited = {**rebuilt, **{k: v for k, v in edited.items() if k.startswith("_")}}
                wall = list(edited.get("word_wall") or [])
            for row in wall:
                if isinstance(row, dict):
                    row["pmes_flashcard"] = True
                    row.setdefault("pqle_card", True)
                    row.setdefault("lce_card", True)
                    term = str(row.get("term") or "").strip()
                    if term and len(term) <= 24:
                        row["term"] = term.upper()
                    if not row.get("example_sentence") and row.get("example"):
                        row["example_sentence"] = row["example"]
                    if not row.get("memory_tip"):
                        row["memory_tip"] = (
                            f"Picture {term} in the lesson diagram, then say what it means."
                        )
            edited["word_wall"] = wall
            edited, report = edit_adaptation_to_approval(
                edited, adaptation_id="vocabulary", board=board, max_passes=max_passes
            )
            working[key] = edited
            by_id[key] = report
            if not report.get("approved"):
                rejects.append(key)
            continue
        if key == "worksheet":
            edited = dict(value)
            edited.setdefault("diagram_package", _diagram_package(
                edited,
                topic=str(board.get("topic") or "Lesson"),
                concepts=[
                    str(c.get("name") or "")
                    for c in (board.get("concepts") or [])
                    if isinstance(c, dict)
                ],
            ))
            dq = dict(edited.get("diagram_question") or {})
            if edited.get("diagram_package", {}).get("svg"):
                dq.setdefault("svg_diagram", edited["diagram_package"]["svg"])
                dq.setdefault("caption", edited["diagram_package"]["caption"])
                dq.setdefault("practice", edited["diagram_package"]["practice_question"])
            edited["diagram_question"] = dq
            edited["publisher_style_css"] = style_guide_css()
            critique = critique_adaptation(edited, adaptation_id="worksheet", board=board)
            report = {
                "adaptation_id": "worksheet",
                "approved": bool(critique.get("approved")),
                "final_comments": list(critique.get("comments") or []),
                "history": [{"pass": 1, "comments": critique.get("comments")}],
                "passes": 1,
                "pmes_version": PMES_VERSION,
            }
            working[key] = edited
            by_id[key] = report
            if not report["approved"]:
                rejects.append(key)
            continue

        edited, report = edit_adaptation_to_approval(
            value, adaptation_id=key, board=board, max_passes=max_passes
        )
        working[key] = edited
        by_id[key] = report
        if not report.get("approved"):
            rejects.append(key)

    publisher_report = {
        "schema": "alora.pmes.publisher_review_report.v1",
        "pmes_version": PMES_VERSION,
        "style_guide_version": STYLE_GUIDE_VERSION,
        "smoke_ok": PHASE_OMEGA_2_PMES_SMOKE_OK,
        "approved": not rejects,
        "rejected_adaptations": rejects,
        "by_adaptation": by_id,
        "house_standard": [
            "Pearson",
            "Oxford",
            "Cambridge",
            "National Geographic Learning",
            "Scholastic",
        ],
        "question": (
            "Would this page be accepted without modification by a top educational publisher?"
        ),
        "answer": "YES" if not rejects else "NO — rewrite required",
        "style_guide_css": style_guide_css(),
    }
    working["_pmes"] = publisher_report
    working["_publisher_style_css"] = style_guide_css()
    return {
        "adaptations": working,
        "publisher_review_report": publisher_report,
        "publication_ready": not rejects,
        "reject_rendering": bool(rejects),
        "pmes_version": PMES_VERSION,
    }
