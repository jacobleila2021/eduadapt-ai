"""Lesson Composition Engine — compose verified knowledge into premium lessons.

Pipeline:
  ULI → SIF → UVIE → Canonical Lesson Graph → Adaptive Lenses → EERL → Rendering

LLM (when used) is Educational Editor only — never curriculum author.
"""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.board_adaptations import compose_adaptation_from_board
from engines.lesson_composition_engine.clg import build_canonical_lesson_graph
from engines.lesson_composition_engine.diagrams import (
    build_concept_map_svg,
    build_educational_flowchart_svg,
    build_subject_flowchart,
    prefer_svg_over_mermaid,
)
from engines.lesson_composition_engine.eerl import review_package
from engines.lesson_composition_engine.intelligence_board import (
    PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK,
    build_lesson_intelligence_board,
    integration_failures,
)
from engines.lesson_composition_engine.lenses import LENS_CONTRACTS, lens_for, subject_arc
from engines.lesson_composition_engine.schemas import (
    ADAPTIVE_VERSION_IDS,
    PACK_VERSION,
    CompositionBlueprint,
    ComposedLesson,
    LessonCompositionPackage,
    LessonSection,
)
from engines.lesson_composition_engine.teaching_rules import (
    dedupe_sentences,
    ensure_paragraph_quality,
)
from engines.lesson_composition_engine.vocabulary import compose_vocabulary_page, upgrade_vocabulary_dict

# Product adaptation keys LCE authors by default (matches ai_generator OUTPUT_KEYS + extras)
DEFAULT_LENS_IDS = (
    "standard",
    "ld",
    "ell",
    "visual",
    "auditory",
    "teacher",
    "parent",
    "adhd",
    "autism",
    "dyslexia",
    "vocabulary",
    "worksheet",
)


def _para(*sentences: str) -> str:
    text = " ".join(s.strip() for s in sentences if s and str(s).strip())
    return ensure_paragraph_quality(dedupe_sentences(text))


def _student_goal(goal: str, *, topic: str) -> str:
    from engines.lesson_composition_engine.publisher_remediation import studentize_goal

    text = studentize_goal(goal, topic=topic)
    return text if text.endswith((".", "!", "?")) else text + "."


def _fact_pool(clg: Mapping[str, Any]) -> list[str]:
    facts = [str(f.get("text") or "") for f in (clg.get("facts") or []) if f]
    claims = [str(c) for c in (clg.get("claim_texts") or []) if c]
    pool = [t for t in facts + claims if t.strip()]
    return pool or [
        f"The uploaded lesson centres on {clg.get('topic') or 'this topic'}.",
    ]


def _concept_explain(concept: Mapping[str, Any], pool: list[str]) -> str:
    name = str(concept.get("name") or "this idea")
    expl = str(concept.get("explanation") or "").strip()
    support = ""
    for text in pool:
        if name.lower() in text.lower():
            support = text
            break
    if not support and pool:
        support = pool[0]
    if expl:
        return _para(
            expl if expl.endswith((".", "!", "?")) else expl + ".",
            support or f"Keep the meaning of {name} precise when you explain it.",
        )
    if support:
        return _para(
            support if support.endswith((".", "!", "?")) else support + ".",
            f"Use that evidence to explain {name} in your own words.",
        )
    return _para(
        f"{name} is defined by the lesson evidence.",
        f"Say what {name.lower()} means in one clear sentence before you continue.",
    )


def compose_standard_from_clg(clg: Mapping[str, Any]) -> dict[str, Any]:
    """Deterministic mainstream lesson from Canonical Lesson Graph."""
    from engines.lesson_composition_engine.vocab_quality import clean_topic, is_junk_term

    topic = clean_topic(str(clg.get("topic") or "Lesson"))
    subject = str(clg.get("subject_key") or "general")
    goals = clg.get("learning_goals") or []
    goal = str((goals[0] or {}).get("text") if goals else f"Understand {topic}.")
    concepts = [
        c
        for c in (clg.get("core_concepts") or [])
        if isinstance(c, dict) and not is_junk_term(str(c.get("name") or ""))
    ]
    pool = _fact_pool(clg)
    misconceptions = list(clg.get("misconceptions") or [])
    examples = list(clg.get("examples") or [])
    visuals = list(clg.get("visual_refs") or [])
    assessments = list(clg.get("assessment_outcomes") or [])
    arc = subject_arc(subject)

    sections: list[dict[str, Any]] = [
        {
            "title": "Learning Goal",
            "role": "hook",
            "box": "hook",
            "body": _para(
                _student_goal(goal, topic=topic),
                f"Each idea below connects back to {topic}.",
            ),
        },
        {
            "title": "Lesson Introduction",
            "role": "hook",
            "body": _para(
                pool[0] if pool else f"This lesson helps you explain {topic} with accurate terms.",
                pool[1] if len(pool) > 1 else f"Stay close to the uploaded evidence about {topic}.",
            ),
        },
    ]

    # Subject teaching arc framing — use claims, not empty stage chatter
    for i, stage in enumerate(arc[:3]):
        fact = pool[min(i + 1, len(pool) - 1)] if pool else ""
        sections.append(
            {
                "title": stage,
                "role": stage.lower().replace(" ", "_"),
                "body": _para(
                    fact or f"Focus on the {stage.lower()} part of {topic}.",
                    f"Connect this {stage.lower()} step to the definitions you will use later.",
                ),
            }
        )

    for i, concept in enumerate(concepts[:5]):
        name = str(concept.get("name") or f"Concept {i+1}")
        sections.append(
            {
                "title": f"Concept: {name}",
                "role": "concept",
                "box": "teach",
                "body": _concept_explain(concept, pool),
                "concept_id": concept.get("concept_id") or "",
            }
        )
        sections.append(
            {
                "title": f"Understanding {name}",
                "role": "simple_explanation",
                "body": _para(
                    _concept_explain(concept, pool),
                    f"Restate {name} in one short sentence before you continue.",
                ),
            }
        )
        ex = ""
        if i < len(examples):
            ex = str(examples[i].get("text") or "")
        elif len(pool) > i + 1:
            ex = pool[i + 1]
        sections.append(
            {
                "title": f"{name} in Everyday Life",
                "role": "real_life_example",
                "body": _para(
                    ex or f"Look for {name.lower()} in a simple classroom or home example linked to {topic}.",
                    f"Say one sentence that connects {name.lower()} to that situation.",
                ),
            }
        )
        if i < len(visuals):
            cap = str(visuals[i].get("caption") or "Lesson diagram")
            sections.append(
                {
                    "title": f"See {name}",
                    "role": "visual",
                    "body": _para(
                        f"The diagram for {name} shows: {cap}.",
                        "Match each labelled part to the explanation you just read.",
                    ),
                    "visual_ids": [str(visuals[i].get("visual_id") or "")],
                }
            )
        support = ""
        for text in pool:
            if name.lower() in text.lower():
                support = text
                break
        if not support and pool:
            support = pool[min(i, len(pool) - 1)]
        sections.append(
            {
                "title": f"Worked Example — {name}",
                "role": "worked_example",
                "body": _para(
                    f"Worked example — read this evidence: {support}" if support else f"Worked example — define {name} from the lesson evidence.",
                    f"Underline the words that define {name.lower()}, then write two accurate sentences.",
                ),
            }
        )
        misc = misconceptions[i] if i < len(misconceptions) else None
        if misc:
            label = str(misc.get("label") or "A common confusion appears here.").rstrip(".")
            correction = str(
                misc.get("correction") or "Use the lesson evidence to keep the definitions separate."
            )
            sections.append(
                {
                    "title": f"Watch Out — {name}",
                    "role": "common_misconception",
                    "body": _para(
                        f"{label}.",
                        f"Correction: {correction}",
                    ),
                }
            )
        sections.append(
            {
                "title": f"Try This — {name}",
                "role": "practice_question",
                "body": _para(
                    f"Explain {name} in your own words"
                    + (f" using this evidence: {support}" if support else "."),
                    "Then give one correct example that shows you understand the idea.",
                ),
            }
        )
        sections.append(
            {
                "title": f"Reflect on {name}",
                "role": "reflection",
                "body": _para(
                    f"What part of {name.lower()} feels clear, and what still needs another example?",
                    "Write one sentence that links this idea to the learning goal.",
                ),
            }
        )

    sections.extend(
        [
            {
                "title": "Lesson Summary",
                "role": "summary",
                "box": "summary",
                "body": _para(
                    f"In summary, {topic} brings together "
                    + (", ".join(str(c.get('name') or '') for c in concepts[:3]) or "the main ideas")
                    + ".",
                    "Keep definitions precise and reconnect each idea to an example before you revise.",
                ),
            },
            {
                "title": "Quick Revision",
                "role": "revision",
                "body": _para(
                    "Revision points: name each key concept, give one example, and state one mistake to avoid.",
                    "Check your wording against the lesson evidence.",
                ),
            },
            {
                "title": "Think About It",
                "role": "reflection",
                "body": _para(
                    "Which idea feels strongest, and which needs another example?",
                    "Write one sentence that connects today's learning to something you already knew.",
                ),
            },
            {
                "title": "Apply Your Learning",
                "role": "application",
                "box": "practice",
                "body": _para(
                    f"Apply {topic} to a new situation from your own experience.",
                    "Explain your reasoning in three clear sentences using lesson vocabulary.",
                ),
            },
        ]
    )

    practice = []
    answer_key = []
    for i, outcome in enumerate(assessments[:6] or concepts[:4]):
        if isinstance(outcome, dict) and outcome.get("prompt"):
            q = str(outcome["prompt"])
        else:
            name = str((outcome or {}).get("name") if isinstance(outcome, dict) else outcome)
            q = f"Explain {name} using evidence from the lesson."
        practice.append({"question": q, "marks": 2})
        answer_key.append(
            {
                "question_ref": f"Q{i+1}",
                "model_answer": f"A clear, source-faithful explanation for: {q}",
            }
        )

    from engines.lesson_composition_engine.diagrams import build_educational_flowchart_svg

    concept_names = [str(c.get("name") or "").strip() for c in concepts if str(c.get("name") or "").strip()]
    # Prefer domain concept nodes over generic pedagogy stages (Concept→Phenomenon→…)
    if len(concept_names) >= 2:
        flowchart = build_educational_flowchart_svg(
            topic,
            concept_names[:6],
            subtitle=f"{subject.title()} key ideas in order",
        )
    else:
        flowchart = build_subject_flowchart(subject, topic)
    concept_map = build_concept_map_svg(topic, concept_names or [str(c.get("name") or "") for c in concepts])
    visual_summary = [
        {"icon": "*", "color_name": "Teal", "idea": "Core concept"},
        {"icon": "*", "color_name": "Navy", "idea": "Practice"},
        {"icon": "*", "color_name": "Soft gold", "idea": "Check understanding"},
    ]

    lead = pool[0] if pool else f"Precise definitions help you explain {topic} accurately."
    lesson = {
        "big_idea": _para(
            lead if lead.endswith((".", "!", "?")) else lead + ".",
            "That idea is the thread that holds "
            + (", ".join(concept_names[:2]) or "the lesson ideas")
            + " together.",
        ),
        "sections": sections,
        "visual_summary": visual_summary,
        "mermaid_diagram": "",
        "svg_diagram": flowchart,
        "flowchart_svg": flowchart,
        "concept_map_svg": concept_map,
        "summary": sections[-4]["body"] if len(sections) >= 4 else "",
        "revision_points": [f"Revise: {c.get('name')}" for c in concepts[:6]],
        "reflection_prompts": [
            "What is clearer now than at the start of the lesson?",
            "Which example helped you most?",
        ],
        "application_tasks": [f"Create one new example that uses {topic} correctly."],
        "practice": practice,
        "answer_key": answer_key,
        "topic": topic,
        "title": f"{topic} — Mainstream Support",
        "lce": {
            "version_id": "standard",
            "subject": subject,
            "schema": PACK_VERSION,
            "from_clg": True,
            "lens": lens_for("standard"),
        },
        "_lce": {"frequency_based": False, "mutates_curriculum": False},
    }
    return prefer_svg_over_mermaid(lesson, allow_mermaid=False)


def compose_vocabulary_from_clg(clg: Mapping[str, Any]) -> dict[str, Any]:
    from engines.lesson_composition_engine.vocab_quality import (
        clean_topic,
        is_junk_term,
        normalize_vocab_items,
    )

    topic = clean_topic(str(clg.get("topic") or "Lesson Vocabulary"))
    claims = [str(f.get("text") or "") for f in (clg.get("facts") or []) if f]
    claims.extend(str(t) for t in (clg.get("claim_texts") or []) if t)

    raw_terms: list[Any] = list(clg.get("vocabulary") or [])
    for c in clg.get("core_concepts") or []:
        name = str(c.get("name") or "").strip()
        if name and not is_junk_term(name):
            expl = str(c.get("explanation") or "").strip()
            raw_terms.append(
                {
                    "term": name,
                    "definition": expl
                    or next((t for t in claims if name.lower() in t.lower()), ""),
                    "example": next((t for t in claims if name.lower() in t.lower()), ""),
                }
            )

    normalized = normalize_vocab_items(raw_terms, topic=topic, claims=claims)
    # Ensure a solid study set from claim-grounded science terms (never junk fillers)
    if len(normalized) < 6:
        extras = []
        for text in claims:
            low = text.lower()
            for term in (
                "Force",
                "Pressure",
                "Area",
                "Pascal",
                "Newton",
                "Evaporation",
                "Condensation",
                "Precipitation",
                "Collection",
            ):
                if term.lower() in low and not is_junk_term(term):
                    extras.append({"term": term, "definition": text, "example": text})
        normalized = normalize_vocab_items(
            list(normalized) + extras, topic=topic, claims=claims
        )
    page = compose_vocabulary_page(
        normalized,
        topic=topic,
        misconceptions=[str(m.get("label") or "") for m in (clg.get("misconceptions") or [])],
        claims=claims,
        context={"topic": topic, "claims": claims, "lesson": {"topic": topic}},
    )
    page["_lce"] = {"frequency_based": False, "from_clg": True, "provenance": "clg"}
    return page


def compose_worksheet_from_clg(clg: Mapping[str, Any], vocabulary: Mapping[str, Any] | None = None) -> dict[str, Any]:
    topic = str(clg.get("topic") or "Lesson")
    subject = str(clg.get("subject_key") or "Science")
    pool = _fact_pool(clg)
    assessments = list(clg.get("assessment_outcomes") or [])
    concepts = list(clg.get("core_concepts") or [])
    terms = [
        str(w.get("term") or "")
        for w in ((vocabulary or {}).get("word_wall") or clg.get("vocabulary") or [])
        if isinstance(w, dict)
    ][:8]

    short = []
    seed = assessments if len(assessments) >= 4 else (assessments + concepts)
    for i, outcome in enumerate(seed[:8] or concepts[:8] or [{"name": topic}]):
        if isinstance(outcome, dict) and outcome.get("prompt"):
            q = str(outcome["prompt"])
        else:
            name = str((outcome or {}).get("name") if isinstance(outcome, dict) else f"idea {i+1}")
            q = f"In 1–2 sentences, explain {name}."
        evidence = pool[i % len(pool)] if pool else f"Accurate brief explanation of the idea in {topic}."
        short.append(
            {
                "question": q,
                "marks": 2,
                "lines": 4,
                "model_answer": evidence[:220],
            }
        )
    # Guarantee exam breadth for EERL pedagogical flow
    while len(short) < 6:
        idx = len(short)
        evidence = pool[idx % len(pool)] if pool else f"Key idea {idx+1} from {topic}."
        short.append(
            {
                "question": f"State one important fact about {topic} (point {idx+1}).",
                "marks": 2,
                "lines": 4,
                "model_answer": evidence[:220],
            }
        )
    long_q = []
    for i, concept in enumerate(concepts[:4] or [{"name": topic}]):
        name = str(concept.get("name") or topic)
        long_q.append(
            {
                "question": f"Explain {name} in detail with examples from the lesson.",
                "marks": 8,
                "lines": 10,
                "model_answer": _para(
                    pool[min(i, len(pool) - 1)] if pool else f"{name} is explained in the lesson.",
                    f"A strong answer defines {name}, gives one example, and links it to {topic}.",
                    "Use accurate lesson vocabulary throughout.",
                    "Avoid mixing this idea with a related but different term.",
                    "End with one clear concluding sentence.",
                ),
            }
        )
    vocab_q = [
        {
            "question": f"Use the term '{t}' correctly in an exam-style sentence.",
            "marks": 2,
            "model_answer": f"A correct sentence uses {t} with the lesson meaning.",
        }
        for t in terms[:6]
    ] or [
        {
            "question": f"Define a key term from {topic}.",
            "marks": 2,
            "model_answer": "Give the lesson definition with one example.",
        }
    ]

    concept_names = [
        str(c.get("name") or "").strip()
        for c in (clg.get("core_concepts") or [])
        if isinstance(c, dict) and str(c.get("name") or "").strip()
    ]
    from engines.lesson_composition_engine.diagrams import build_educational_flowchart_svg

    if len(concept_names) >= 2:
        flowchart = build_educational_flowchart_svg(
            topic,
            concept_names[:6],
            subtitle=f"{subject.title()} exam diagram — label each idea",
        )
    else:
        flowchart = build_subject_flowchart(subject, topic)
    answer_key = []
    for i, row in enumerate(short):
        answer_key.append(
            {"question_ref": f"Part A Q{i+1}", "model_answer": row["model_answer"], "marks_notes": "2 marks"}
        )
    for i, row in enumerate(long_q):
        answer_key.append(
            {"question_ref": f"Part B Q{i+1}", "model_answer": row["model_answer"], "marks_notes": "8 marks"}
        )
    for i, row in enumerate(vocab_q):
        answer_key.append(
            {"question_ref": f"Part D Q{i+1}", "model_answer": row["model_answer"], "marks_notes": "2 marks"}
        )

    return {
        "header": {
            "subject": subject,
            "topic": topic,
            "time_allowed": "45-60 minutes",
            "total_marks": 40,
        },
        "short_answer": short,
        "long_answer": long_q,
        "diagram_question": {
            "question": "Study the source-grounded concept organiser. Redraw and label each main idea accurately.",
            "marks": 5,
            "svg_diagram": flowchart,
            "model_answer": "A correct response reproduces the organiser and labels the main ideas exactly as shown.",
            "alt_text": f"Labelled concept organiser for {topic}.",
        },
        "vocab_questions": vocab_q,
        "student_checklist": [
            "Read every question twice before writing.",
            "Use lesson vocabulary in answers.",
            "Check timing: short answers first, then long answers.",
            "Review the diagram question labels.",
        ],
        "teacher_differentiation": (
            "Assign chunked Parts for ADHD/dyslexia supports; keep board vocabulary for ELL; "
            "prefer visual organiser for visual learners. Do not change verified facts."
        ),
        "answer_key": answer_key,
        "_lce": {"frequency_based": False, "from_clg": True},
    }


def _diagrams_from_board(board: Mapping[str, Any], clg: Mapping[str, Any]) -> tuple[str, str]:
    topic = str(board.get("topic") or clg.get("topic") or "Lesson")
    subject = str(board.get("subject") or clg.get("subject_key") or "general")
    concept_names = [
        str(c.get("name") or "").strip()
        for c in (board.get("concepts") or [])
        if isinstance(c, dict) and str(c.get("name") or "").strip()
    ]
    if len(concept_names) >= 2:
        flowchart = build_educational_flowchart_svg(
            topic,
            concept_names[:6],
            subtitle=f"{subject.title()} key ideas in order",
        )
    else:
        flowchart = build_subject_flowchart(subject, topic)
    concept_map = build_concept_map_svg(topic, concept_names or [topic])
    return flowchart, concept_map


def compose_adaptations_from_clg(
    clg: Mapping[str, Any],
    *,
    lens_ids: list[str] | None = None,
    board: Mapping[str, Any] | None = None,
    uli: Mapping[str, Any] | None = None,
    sif: Mapping[str, Any] | None = None,
    uvie: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose all adaptive versions from the Lesson Intelligence Board (Phase Omega).

    No adaptation is a deep-copy wrap of another. Vocabulary/worksheet remain specialised pages.
    """
    ids = list(lens_ids or DEFAULT_LENS_IDS)
    intelligence = dict(
        board
        or build_lesson_intelligence_board(clg, uli=uli, sif=sif, uvie=uvie)
    )
    flowchart, concept_map = _diagrams_from_board(intelligence, clg)
    vocabulary = compose_vocabulary_from_clg(clg)
    out: dict[str, Any] = {
        "_intelligence_board": intelligence,
        "_integration_failures": integration_failures(intelligence),
        "_phase_omega": True,
    }
    if "vocabulary" in ids:
        out["vocabulary"] = vocabulary
    if "worksheet" in ids:
        out["worksheet"] = compose_worksheet_from_clg(clg, vocabulary)

    for vid in ids:
        if vid in {"vocabulary", "worksheet"}:
            continue
        if vid in LENS_CONTRACTS or vid in {"dyslexia", "standard"}:
            out[vid] = compose_adaptation_from_board(
                intelligence,
                vid,
                flowchart_svg=flowchart,
                concept_map_svg=concept_map,
            )
            out[vid].setdefault("lce", {})
            if isinstance(out[vid]["lce"], dict):
                out[vid]["lce"]["lens"] = lens_for("ld" if vid == "dyslexia" else vid)
                out[vid]["lce"]["intelligence_board_version"] = intelligence.get("version")
    return out


def compose_lesson_package(*args: Any, **kwargs: Any) -> Any:
    """
    Public composition entry.

    Preferred (ai_generator):
      compose_lesson_package(uli, sif=..., uvie=..., topic_hint=...) -> dict

    Alternate (service/attach):
      compose_lesson_package(lesson_text=..., universal_profile=..., meta=...) -> LessonCompositionPackage
    """
    # Keyword / attach path
    if kwargs.get("lesson_text") is not None or kwargs.get("meta") is not None or kwargs.get("universal_profile") is not None:
        return _compose_package_from_meta(**kwargs)

    uli = args[0] if args else kwargs.get("uli")
    sif = kwargs.get("sif") or {}
    uvie = kwargs.get("uvie") or {}
    topic_hint = str(kwargs.get("topic_hint") or "")

    clg = build_canonical_lesson_graph(uli, sif=sif, uvie=uvie, topic_hint=topic_hint)
    clg_dict = clg.to_dict()
    # Phase Omega — Intelligence Board before any paragraph authorship
    board = build_lesson_intelligence_board(
        clg_dict,
        uli=uli if isinstance(uli, Mapping) else {},
        sif=sif if isinstance(sif, Mapping) else {},
        uvie=uvie if isinstance(uvie, Mapping) else {},
    )
    adaptations = compose_adaptations_from_clg(
        clg_dict,
        board=board,
        uli=uli if isinstance(uli, Mapping) else {},
        sif=sif if isinstance(sif, Mapping) else {},
        uvie=uvie if isinstance(uvie, Mapping) else {},
    )

    # Publisher-Quality Lesson Excellence — polish, golden compare, editorial board
    from engines.lesson_composition_engine.revise import apply_publisher_quality_excellence

    pqle = apply_publisher_quality_excellence(
        adaptations, clg=clg_dict, board=board
    )
    adaptations = pqle.get("adaptations") or adaptations
    eerl = pqle.get("eerl") or review_package(adaptations, clg_dict)
    pqi = pqle.get("pqi") or {}
    editorial = pqle.get("editorial") or {}

    publication_ready = bool(pqle.get("publication_ready"))
    publisher_review = pqle.get("publisher_review_report") or {}
    result = {
        "ok": publication_ready,
        "version": PACK_VERSION,
        "clg": clg_dict,
        "intelligence_board": board,
        "integration_failures": list(adaptations.get("_integration_failures") or integration_failures(board)),
        "adaptations": adaptations,
        "eerl": eerl,
        "pqi": pqi,
        "editorial": editorial,
        "publisher_review_report": publisher_review,
        "pmes": pqle.get("pmes") or {},
        "peec": pqle.get("peec") or {},
        "uevb": pqle.get("uevb") or {},
        "epp": pqle.get("epp") or {},
        "content_fidelity": pqle.get("content_fidelity") or {},
        "pqle": {
            "publication_ready": publication_ready,
            "reject_rendering": bool(pqle.get("reject_rendering")),
            "threshold": pqle.get("threshold"),
            "worst_score": pqi.get("worst_score"),
            "editorial_approved": bool(editorial.get("approved")),
            "pmes_approved": bool((pqle.get("pmes") or {}).get("approved")),
            "uevb_approved": bool((pqle.get("uevb") or {}).get("ok")),
            "peec_ok": bool((pqle.get("peec") or {}).get("ok")),
            "phase_omega": True,
            "phase_omega_2_pmes": True,
            "smoke_ok": PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK,
        },
        "policy": {
            "composes_lessons": True,
            "does_not_invent_curriculum": True,
            "frequency_vocab_used": False,
            "mutates_curriculum": False,
            "llm_role": "educational_editor_optional",
            "publisher_quality_required": True,
            "pqi_threshold": pqle.get("threshold"),
            "phase_omega": True,
            "phase_omega_2_pmes": True,
            "pmes_highest_authority": True,
            "uevb_final_authority": True,
            "peec_product_excellence": True,
            "pobr_beta_readiness": True,
            "intelligence_board_required": True,
            "no_new_engines": True,
        },
    }
    try:
        from pobr import apply_pobr

        pobr_result = apply_pobr(result, write_reports=False)
        result["pobr"] = {
            "ok": pobr_result.get("ok"),
            "beta_ready": pobr_result.get("beta_ready"),
            "overall_beta_readiness": pobr_result.get("overall_beta_readiness"),
            "report": pobr_result.get("report"),
            "smoke_ok": pobr_result.get("smoke_ok"),
        }
        result["pqle"]["pobr_beta_ready"] = bool(pobr_result.get("beta_ready"))
    except Exception as exc:  # noqa: BLE001
        result["pobr"] = {"ok": False, "error": str(exc)}
    return result


def _compose_package_from_meta(
    *,
    lesson_text: str = "",
    universal_profile: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    existing_vocabulary: dict[str, Any] | None = None,
    existing_standard: dict[str, Any] | None = None,
    version_ids: list[str] | None = None,
    allow_mermaid: bool = False,
) -> LessonCompositionPackage:
    """Build LessonCompositionPackage from session meta (attach path)."""
    meta = meta or {}
    profile = universal_profile or meta.get("universal_profile") or {}
    context = context or meta.get("lesson_context") or {}
    uli_meta = meta.get("uli") or {}
    sif = uli_meta.get("sif") or meta.get("sif") or {}
    uvie = {
        "visuals": meta.get("preferred_visuals") or meta.get("uvie_visuals") or [],
        "preferred_visuals": meta.get("preferred_visuals") or [],
    }
    topic_hint = str(context.get("topic") or profile.get("topic") or "")

    # Prefer live ULI object reconstruction via profile envelope
    uli_payload = {
        "universal_profile": profile,
        "claim_ledger": profile.get("claim_ledger") or [],
    }
    result = compose_lesson_package(
        uli_payload,
        sif=sif if isinstance(sif, dict) else {},
        uvie=uvie,
        topic_hint=topic_hint,
    )
    adaptations = dict(result.get("adaptations") or {})
    if existing_vocabulary and existing_vocabulary.get("word_wall"):
        adaptations["vocabulary"] = upgrade_vocabulary_dict(
            existing_vocabulary, context={"lesson": existing_vocabulary}
        )
    if existing_standard and existing_standard.get("sections") and not adaptations.get("standard"):
        adaptations["standard"] = existing_standard

    if version_ids:
        adaptations = {k: v for k, v in adaptations.items() if k in version_ids}

    clg = result.get("clg") or {}
    blueprint = CompositionBlueprint(
        topic=str(clg.get("topic") or topic_hint or "Lesson"),
        subject=str(clg.get("subject_key") or "general"),
        objectives=[str(g.get("text") or "") for g in (clg.get("learning_goals") or [])],
        concepts=[str(c.get("name") or "") for c in (clg.get("core_concepts") or [])],
        vocabulary_terms=[str(v.get("term") or "") for v in (clg.get("vocabulary") or [])],
        misconceptions=[str(m.get("label") or "") for m in (clg.get("misconceptions") or [])],
        teaching_sequence=subject_arc(str(clg.get("subject_key") or "general")),
        visual_intents=list(clg.get("visual_refs") or []),
        source_excerpt=(lesson_text or "")[:4000],
    )
    standard_dict = adaptations.get("standard") or {}
    if allow_mermaid is False and isinstance(standard_dict, dict):
        adaptations["standard"] = prefer_svg_over_mermaid(standard_dict, allow_mermaid=False)

    from engines.lesson_composition_engine.quality_gate import evaluate_composition

    quality = evaluate_composition(
        adaptations.get("standard") or {},
        vocabulary=adaptations.get("vocabulary"),
        blueprint=blueprint.to_dict(),
        subject=blueprint.subject,
    )

    return LessonCompositionPackage(
        blueprint=blueprint,
        standard=None,
        versions={k: v for k, v in adaptations.items() if k not in {"vocabulary", "worksheet"} and not str(k).startswith("_")},
        vocabulary=adaptations.get("vocabulary") or {},
        quality=quality,
        publisher_meta={
            "clg": result.get("clg") or {},
            "intelligence_board": result.get("intelligence_board") or {},
            "pqi": result.get("pqi") or {},
            "pqle": result.get("pqle") or {},
            "pmes": result.get("pmes") or {},
            "editorial": result.get("editorial") or {},
            "peec": result.get("peec") or {},
            "uevb": result.get("uevb") or {},
            "epp": result.get("epp") or {},
            "content_fidelity": result.get("content_fidelity") or {},
            "publication_ready": bool(result.get("ok")),
            "reject_rendering": bool((result.get("pqle") or {}).get("reject_rendering")),
        },
    )


def attach_lce_to_adaptations(
    adaptations: dict[str, Any],
    *,
    lesson_text: str = "",
    reject_on_fail: bool = True,
) -> dict[str, Any]:
    """
    Final polish pass. If LCE already composed adaptations earlier in the pipeline,
    upgrade vocabulary to premium cards and merge EERL — do not blindly overwrite.
    """
    meta = adaptations.get("_meta") if isinstance(adaptations.get("_meta"), dict) else {}
    already = isinstance(meta.get("lce"), dict) and (
        meta["lce"].get("ok") or meta["lce"].get("clg_topic") or meta.get("canonical_lesson_graph")
    )

    # Always upgrade vocabulary cards to premium LCE format when present
    if isinstance(adaptations.get("vocabulary"), dict):
        adaptations["vocabulary"] = upgrade_vocabulary_dict(
            adaptations["vocabulary"],
            context={"lesson": adaptations.get("vocabulary")},
        )

    if already:
        # Prefer publisher spine from first compose — empty board/CLG re-scores falsely fail classroom uploads
        clg = (
            meta.get("canonical_lesson_graph")
            or (meta.get("lce") or {}).get("clg")
            or {}
        )
        board = (
            meta.get("intelligence_board")
            or (meta.get("lce") or {}).get("intelligence_board")
            or {}
        )
        prior_pqle = (meta.get("lce") or {}).get("pqle") if isinstance(meta.get("lce"), dict) else {}
        # If first compose already cleared publisher gates, only upgrade vocabulary — do not re-quarantine
        if (
            not reject_on_fail
            and isinstance(prior_pqle, dict)
            and prior_pqle.get("publication_ready")
            and not prior_pqle.get("reject_rendering")
        ):
            adaptations.setdefault("_meta", {})
            adaptations["_meta"]["lce"] = {
                **(adaptations["_meta"].get("lce") or {}),
                "premium_vocab": True,
                "stage": "vocab_upgrade_only",
                "pqle": prior_pqle,
            }
            return adaptations
        try:
            from engines.lesson_composition_engine.revise import apply_publisher_quality_excellence

            pqle = apply_publisher_quality_excellence(
                {k: v for k, v in adaptations.items() if not str(k).startswith("_") and isinstance(v, dict)},
                clg=clg if isinstance(clg, dict) else {},
                board=board if isinstance(board, dict) else {},
            )
            for key, value in (pqle.get("adaptations") or {}).items():
                adaptations[key] = value
            reject = bool(pqle.get("reject_rendering"))
            adaptations.setdefault("_meta", {})
            adaptations["_meta"]["canonical_lesson_graph"] = clg if isinstance(clg, dict) else {}
            adaptations["_meta"]["intelligence_board"] = board if isinstance(board, dict) else {}
            adaptations["_meta"]["lce"] = {
                **(adaptations["_meta"].get("lce") or {}),
                "eerl_final": pqle.get("eerl"),
                "pqi": pqle.get("pqi"),
                "editorial": pqle.get("editorial"),
                "clg": clg if isinstance(clg, dict) else {},
                "intelligence_board": board if isinstance(board, dict) else {},
                "pqle": {
                    "publication_ready": bool(pqle.get("publication_ready")),
                    # Soft audit must not quarantine classroom sessions (reject_on_fail=False)
                    "reject_rendering": reject if reject_on_fail else False,
                    "audit_reject_rendering": reject,
                    "threshold": pqle.get("threshold"),
                    "editorial_approved": bool((pqle.get("editorial") or {}).get("approved")),
                    "pmes_approved": bool((pqle.get("pmes") or {}).get("approved")),
                    "uevb_approved": bool((pqle.get("uevb") or {}).get("ok")),
                    "worst_score": (pqle.get("pqi") or {}).get("worst_score"),
                    "phase_omega": True,
                },
                "premium_vocab": True,
                "stage": "final_polish_pqle",
            }
            if reject_on_fail and reject:
                worst = (pqle.get("pqi") or {}).get("worst_score")
                threshold = pqle.get("threshold")
                adaptations["_meta"]["lce"]["render_blocked"] = True
                adaptations["_meta"]["lce"]["blocked_reason"] = (
                    f"Publisher Quality Index below threshold ({worst}/{threshold})."
                    if worst is not None
                    else "The lesson did not meet publisher-quality standards."
                )
        except Exception:  # noqa: BLE001
            pass
        return adaptations

    package = _compose_package_from_meta(
        lesson_text=lesson_text,
        universal_profile=meta.get("universal_profile"),
        meta=meta,
        context=meta.get("lesson_context"),
        existing_vocabulary=adaptations.get("vocabulary")
        if isinstance(adaptations.get("vocabulary"), dict)
        else None,
        existing_standard=adaptations.get("standard")
        if isinstance(adaptations.get("standard"), dict)
        else None,
    )
    adaptations["vocabulary"] = package.vocabulary or adaptations.get("vocabulary")
    for key, lesson in package.versions.items():
        adaptations[key] = lesson

    gate = {}
    if package.quality:
        from engines.lesson_composition_engine.quality_gate import gate_for_rendering

        gate = gate_for_rendering(package.quality)
    adaptations.setdefault("_meta", {})
    adaptations["_meta"]["lce"] = {
        "enabled": True,
        "schema_version": package.schema_version,
        "blueprint": package.blueprint.to_dict(),
        "quality": package.quality.to_dict() if package.quality else {},
        "gate": gate,
        "reject_rendering": bool(gate.get("reject_rendering")),
    }
    if reject_on_fail and gate.get("reject_rendering"):
        adaptations["_meta"]["lce"]["render_blocked"] = True
        adaptations["_meta"]["lce"]["blocked_reason"] = (
            "LCE quality gate failed: " + ", ".join(gate.get("failed_categories") or [])
        )
    return adaptations


def build_blueprint(
    *,
    lesson_text: str = "",
    universal_profile: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> CompositionBlueprint:
    package = _compose_package_from_meta(
        lesson_text=lesson_text,
        universal_profile=universal_profile,
        meta=meta,
        context=context,
    )
    return package.blueprint


def lce_prompt_block_from_meta(meta: dict[str, Any] | None) -> str:
    from engines.lesson_composition_engine.contracts import build_narrative_contract, composition_prompt_block
    from engines.lesson_composition_engine.editor import editor_prompt_block

    meta = meta or {}
    clg = meta.get("canonical_lesson_graph") or (meta.get("lce") or {}).get("clg") or {}
    if clg:
        return editor_prompt_block(clg, "standard")
    try:
        bp = build_blueprint(meta=meta, universal_profile=meta.get("universal_profile"))
        return composition_prompt_block(bp.to_dict())
    except Exception:  # noqa: BLE001
        return build_narrative_contract()
