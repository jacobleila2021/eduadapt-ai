"""Lesson Composition Engine — compose verified knowledge into premium lessons.

Pipeline:
  ULI → SIF → UVIE → Canonical Lesson Graph → Adaptive Lenses → EERL → Rendering

LLM (when used) is Educational Editor only — never curriculum author.
"""

from __future__ import annotations

import copy
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
    # "adhd" and "autism" lenses cancelled (product decision) — not composed by default.
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


def _teachable_fact(text: str) -> bool:
    """Objectives, authoring lines ('Students will explain…'), classroom-management
    instructions ('Begin by asking students…') and document metadata
    ('Grade Level: 6 | Subject: Earth Science') are not facts a learner can be
    shown as lesson content or a model answer."""
    import re as _re

    from engines.lesson_composition_engine.vocab_quality import is_teacher_facing_text

    if is_teacher_facing_text(text):
        return False
    return not _re.search(
        r"(?i)\b(students?|learners?)\s+will\b|\bobjectives?\b|\byou will learn\b"
        r"|\blesson plan\b|\bmarks?\s*:\s*\d|\bgrade\s*level\b|\bsubject\s*:"
        r"|\btime\s*:|\bduration\b|\bminutes\b|\|"
        r"|\bfor performing activit|\bcollect the samples?\b|\bcaution\s*:"
        r"|\byou will be learning\b|\bin the next section\b|\beasily available\b"
        r"|\bin class\s+(ix|9|x|10)\b|\bactivities?\s+\d",
        text,
    )


def _fact_pool(clg: Mapping[str, Any]) -> list[str]:
    try:
        from engines.lesson_composition_engine.vocab_quality import (
            ACIDS_BASES_SALTS_TERMS,
            clean_learner_claim,
        )
    except Exception:  # pragma: no cover
        clean_learner_claim = lambda t: str(t or "").strip()  # noqa: E731
        ACIDS_BASES_SALTS_TERMS = ()

    facts = [str(f.get("text") or "") for f in (clg.get("facts") or []) if f]
    claims = [str(c) for c in (clg.get("claim_texts") or []) if c]
    pool = []
    for t in facts + claims:
        fixed = clean_learner_claim(t) if callable(clean_learner_claim) else str(t).strip()
        if fixed and _teachable_fact(fixed):
            pool.append(fixed)
    if pool:
        return pool
    topic = str(clg.get("topic") or "").lower()
    if any(k in topic for k in ("acid", "base", "salt")) and ACIDS_BASES_SALTS_TERMS:
        return [defn for _term, defn in ACIDS_BASES_SALTS_TERMS]
    return [
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
    # Vocabulary meanings must come from teaching sentences only — a lesson-plan
    # source is full of classroom instructions ("Begin by asking students where
    # they saw water today…") that must never become a card definition.
    claims = [c for c in claims if c.strip() and _teachable_fact(c)]

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

    # Prefer curriculum banks over OCR token scraping (Iron/Copper from lab lists).
    topic_low = topic.lower()
    if any(k in topic_low for k in ("metal", "non-metal", "nonmetal", "malleab", "ductil")):
        from engines.lesson_composition_engine.vocab_quality import METALS_NONMETALS_TERMS

        for term, definition in METALS_NONMETALS_TERMS:
            raw_terms.append({"term": term, "definition": definition, "example": definition})
    if any(k in topic_low for k in ("electric", "ohm", "circuit", "resistance")):
        from engines.lesson_composition_engine.vocab_quality import ELECTRICITY_TERMS

        for term, definition in ELECTRICITY_TERMS:
            raw_terms.append({"term": term, "definition": definition, "example": definition})
    if any(
        k in topic_low
        for k in ("water cycle", "evaporat", "precipitat", "condens", "transpiration")
    ):
        from engines.lesson_composition_engine.vocab_quality import WATER_CYCLE_TERMS

        for term, definition in WATER_CYCLE_TERMS:
            raw_terms.append({"term": term, "definition": definition, "example": definition})
    # Any subject: seed from dynamic teaching bank on the CLG / board.
    dyn_bank = list(clg.get("teaching_bank") or [])
    if not dyn_bank:
        try:
            from engines.lesson_composition_engine.dynamic_teaching_bank import (
                build_dynamic_teaching_bank,
            )

            dyn_bank = build_dynamic_teaching_bank(
                topic=topic,
                source_text=str(clg.get("source_text") or ""),
                claims=claims,
                concepts=clg.get("core_concepts") or [],
                stem_artifacts=list(clg.get("stem_artifacts") or []),
                assessment_prompts=list(clg.get("assessment_outcomes") or []),
            )
        except Exception:
            dyn_bank = []
    for row in dyn_bank:
        raw_terms.append(
            {
                "term": str(row.get("term") or ""),
                "definition": str(row.get("definition") or ""),
                "example": str(row.get("definition") or ""),
            }
        )

    normalized = normalize_vocab_items(raw_terms, topic=topic, claims=claims)
    # Ensure a solid study set — only claim-grounded terms with teachable definitions
    if len(normalized) < 6:
        from engines.lesson_composition_engine.vocab_quality import (
            canonical_definition,
            student_safe_definition,
        )

        extras: list[dict[str, str]] = []
        seen = {str(n.get("term") or "").strip().lower() for n in normalized}
        stop = {
            "that", "this", "these", "those", "with", "from", "into", "than", "then",
            "when", "where", "which", "while", "their", "there", "because", "about",
            "other", "another", "always", "never", "usually", "often", "shows", "makes",
            "keeps", "gives", "needs", "turns", "means", "using", "unit", "same", "some",
            "most", "many", "each", "every", "both", "also", "must", "does",
            "following", "samples", "collect", "performing", "available",
        }
        for text in claims:
            safe = student_safe_definition(text)
            if not safe:
                continue
            for word in str(safe).replace(",", " ").split():
                token = word.strip(".:;()[]\"'")
                key = token.lower()
                if len(token) < 5 or is_junk_term(token) or key in stop or key in seen:
                    continue
                if not (token[0].isupper() or token.isalpha()):
                    continue
                definition = canonical_definition(token) or safe
                if not student_safe_definition(definition):
                    continue
                # Never attach a long lab paragraph as the definition of a short metal name.
                if key in {
                    "iron", "copper", "aluminium", "aluminum", "magnesium", "sodium",
                    "zinc", "lead", "mercury",
                } and not canonical_definition(token):
                    continue
                seen.add(key)
                extras.append(
                    {
                        "term": token if token[0].isupper() else token.capitalize(),
                        "definition": definition,
                        "example": definition,
                    }
                )
                if len(extras) >= 8:
                    break
            if len(extras) >= 8:
                break
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


def compose_worksheet_from_clg(
    clg: Mapping[str, Any],
    vocabulary: Mapping[str, Any] | None = None,
    *,
    stem_artifacts: list | None = None,
) -> dict[str, Any]:
    from engines.lesson_composition_engine.vocab_quality import (
        build_student_definition,
        canonical_definition,
        definition_from_claims,
        is_junk_term,
    )
    from engines.lesson_pipeline import (
        looks_like_computable_stem,
        verified_or_wall_answer,
    )

    artifacts = list(stem_artifacts or clg.get("stem_artifacts") or [])
    topic = str(clg.get("topic") or "Lesson")
    subject = str(clg.get("subject_key") or "Science")
    pool = _fact_pool(clg)
    assessments = list(clg.get("assessment_outcomes") or [])
    concepts = [
        c
        for c in (clg.get("core_concepts") or [])
        if isinstance(c, dict) and not is_junk_term(str(c.get("name") or ""))
    ]
    # Seed CBSE teaching banks when OCR left the board empty/junk.
    topic_low = topic.lower()
    if any(k in topic_low for k in ("acid", "base", "salt")) and len(concepts) < 3:
        from engines.lesson_composition_engine.vocab_quality import ACIDS_BASES_SALTS_TERMS

        have = {str(c.get("name") or "").lower() for c in concepts}
        for term, definition in ACIDS_BASES_SALTS_TERMS:
            if term.lower() not in have:
                concepts.append({"name": term, "explanation": definition})
                have.add(term.lower())
            if len(concepts) >= 6:
                break
    if any(k in topic_low for k in ("electric", "ohm", "circuit", "resistance")) and len(concepts) < 4:
        from engines.lesson_composition_engine.vocab_quality import ELECTRICITY_TERMS

        have = {str(c.get("name") or "").lower() for c in concepts}
        for term, definition in ELECTRICITY_TERMS:
            if term.lower() not in have:
                concepts.append({"name": term, "explanation": definition})
                have.add(term.lower())
            if len(concepts) >= 8:
                break
    if any(
        k in topic_low for k in ("metal", "non-metal", "nonmetal", "malleab", "ductil")
    ) and len(concepts) < 4:
        from engines.lesson_composition_engine.vocab_quality import METALS_NONMETALS_TERMS

        have = {str(c.get("name") or "").lower() for c in concepts}
        for term, definition in METALS_NONMETALS_TERMS:
            if term.lower() not in have:
                concepts.append({"name": term, "explanation": definition})
                have.add(term.lower())
            if len(concepts) >= 8:
                break
    if any(
        k in topic_low
        for k in ("water cycle", "evaporat", "precipitat", "condens", "transpiration")
    ) and len(concepts) < 4:
        from engines.lesson_composition_engine.vocab_quality import WATER_CYCLE_TERMS

        have = {str(c.get("name") or "").lower() for c in concepts}
        for term, definition in WATER_CYCLE_TERMS:
            if term.lower() not in have:
                concepts.append({"name": term, "explanation": definition})
                have.add(term.lower())
            if len(concepts) >= 8:
                break
    terms = [
        str(w.get("term") or "")
        for w in ((vocabulary or {}).get("word_wall") or clg.get("vocabulary") or [])
        if isinstance(w, dict) and str(w.get("term") or "").strip() and not is_junk_term(str(w.get("term") or ""))
    ][:8]

    # v3.3: every worksheet question must map back to a taught concept —
    # anchor generic official hints ("Give one everyday example.") to the lesson.
    import re as _re

    concept_tokens: set[str] = set()
    for c in concepts:
        concept_tokens.update(_re.findall(r"[a-z]{4,}", str((c or {}).get("name") or "").lower()))
    concept_tokens.update(_re.findall(r"[a-z]{4,}", topic.lower()))
    for fact in pool:
        concept_tokens.update(_re.findall(r"[a-z]{4,}", str(fact).lower()))

    def _anchor_to_lesson(q: str) -> str:
        if set(_re.findall(r"[a-z]{4,}", q.lower())) & concept_tokens:
            return q
        anchor = str((concepts[0] or {}).get("name") or topic) if concepts else topic
        return f"{q.rstrip('.?')} from this lesson on {anchor}."

    short = []
    # Prefer textbook assessment prompts; then concept explainers.
    textbook_assessments = [
        a
        for a in assessments
        if isinstance(a, dict) and str(a.get("prompt") or "").strip()
    ]
    seed = textbook_assessments if textbook_assessments else (assessments + concepts)
    for i, outcome in enumerate(seed[:10] or concepts[:8] or [{"name": topic}]):
        if isinstance(outcome, dict) and outcome.get("prompt"):
            q = str(outcome["prompt"]).strip()
            # Keep uploaded stems faithful — only lightly anchor empty generics.
            if len(q.split()) < 6:
                q = _anchor_to_lesson(q)
            name = next(
                (
                    str(c.get("name") or "")
                    for c in concepts
                    if str(c.get("name") or "").lower() in q.lower()
                ),
                str((outcome or {}).get("name") or topic),
            )
            marks = int(outcome.get("marks") or (3 if str(outcome.get("question_type") or "") == "numerical" else 2))
        else:
            name = str((outcome or {}).get("name") if isinstance(outcome, dict) else f"idea {i+1}")
            q = f"Explain {name} using evidence from the lesson."
            marks = 2
        # Phase 3 — computable stems use EngineResult; else wall/glossary prose.
        policy = verified_or_wall_answer(q, artifacts=artifacts, wall_prose="")
        if policy.get("source") == "engine_result" and policy.get("text"):
            answer = str(policy["text"])
            answer_source = "engine_result"
        elif policy.get("omitted") and looks_like_computable_stem(q):
            continue  # never invent a calculation on the exam sheet
        else:
            answer = (
                canonical_definition(name)
                or build_student_definition(
                    name,
                    str((outcome or {}).get("explanation") or "")
                    if isinstance(outcome, dict)
                    else "",
                    topic=topic,
                )
                or (pool[i % len(pool)] if pool else "")
            )
            answer_source = str((outcome or {}).get("source") or "lesson")
            if answer and answer.rstrip(".").lower() in q.lower():
                answer = canonical_definition(name) or (
                    pool[(i + 1) % len(pool)] if len(pool) > 1 else answer
                )
            if (
                not answer
                or "one of the ideas taught" in answer.lower()
                or "say what it means" in answer.lower()
                or "is a main idea in" in answer.lower()
            ):
                if str((outcome or {}).get("question_type") or "") == "numerical" or _re.search(
                    r"(?i)\b(calculate|determine|find)\b", q
                ):
                    engine_again = verified_or_wall_answer(q, artifacts=artifacts)
                    if engine_again.get("source") == "engine_result" and engine_again.get("text"):
                        answer = str(engine_again["text"])
                        answer_source = "engine_result"
                    else:
                        answer = (
                            canonical_definition("Ohm's law")
                            or canonical_definition("Electric power")
                            or canonical_definition(name)
                            or (pool[i % len(pool)] if pool else "")
                        )
                if not answer:
                    continue
        short.append(
            {
                "question": q
                if not q.lower().startswith("in your own words, explain this idea")
                else f"Explain {name} using evidence from the lesson.",
                "marks": marks,
                "lines": 4 if marks <= 2 else 6,
                "model_answer": answer[:420]
                if answer.endswith((".", "!", "?"))
                else (answer[:420].rstrip(".") + "."),
                "source": answer_source,
            }
        )
    # Surface every verified STEM artifact as Part A when not already covered.
    from engines.lesson_pipeline import format_engine_answer

    covered = " ".join(str(row.get("model_answer") or "") for row in short).lower()
    for art in artifacts:
        if not isinstance(art, dict) or not art.get("ok"):
            continue
        kind = str(art.get("task_kind") or "")
        if kind not in {"balance_equation", "solve_math", "calculate_force", "statistics"}:
            continue
        ans = format_engine_answer(art)
        if not ans or ans.lower()[:40] in covered:
            continue
        payload = art.get("payload") or {}
        stem = (
            payload.get("input")
            or payload.get("equation")
            or payload.get("expression")
            or payload.get("problem")
            or kind.replace("_", " ")
        )
        short.append(
            {
                "question": f"Solve / balance: {stem}",
                "marks": 3,
                "lines": 6,
                "model_answer": ans,
                "source": "engine_result",
            }
        )
        covered += " " + ans.lower()
        if len(short) >= 10:
            break
    # Guarantee exam breadth — distinct concept prompts, never fact-echo fillers.
    while len(short) < 6:
        idx = len(short)
        concept = concepts[idx % len(concepts)] if concepts else {"name": topic}
        name = str(concept.get("name") or topic)
        answer = canonical_definition(name) or (pool[idx % len(pool)] if pool else "")
        if not answer:
            break
        short.append(
            {
                "question": f"Explain {name} using evidence from the lesson.",
                "marks": 2,
                "lines": 4,
                "model_answer": answer if answer.endswith((".", "!", "?")) else answer + ".",
            }
        )
    long_q = []
    for i, concept in enumerate(concepts[:4] or [{"name": topic}]):
        name = str(concept.get("name") or topic)
        # Prefer deterministic curriculum definitions over OCR mush.
        canon = canonical_definition(name) or build_student_definition(
            name, str(concept.get("explanation") or ""), topic=topic
        )
        direct = [t for t in pool if name.lower() in t.lower()]
        context_facts = [t for t in pool if t not in direct]
        explanation = canon or str(concept.get("explanation") or "").strip()
        answer_parts: list[str] = []
        seen_parts: set[str] = set()
        for part in ([explanation] if explanation else []) + direct[:3] + context_facts[:2]:
            cleaned = str(part or "").strip()
            try:
                from engines.lesson_composition_engine.vocab_quality import (
                    clean_learner_claim,
                    repair_ocr_prose,
                )

                cleaned = clean_learner_claim(cleaned) or repair_ocr_prose(cleaned)
            except Exception:
                pass
            key = cleaned.lower()
            if not cleaned or key in seen_parts:
                continue
            if "one of the ideas taught" in key or "in this chapter" in key:
                continue
            if _re.search(r"(?i)\bacids,\s*bases\s+and\s+salts\s+\d{1,3}\b", cleaned):
                continue
            seen_parts.add(key)
            answer_parts.append(cleaned if cleaned.endswith((".", "!", "?")) else cleaned + ".")
            if len(answer_parts) >= 5:
                break
        if not answer_parts and canon:
            answer_parts = [canon]
        # Progressive demand: understanding → application across long answers.
        if i == 0:
            prompt = f"Explain '{name}' in detail with examples from the lesson."
        elif i == 1:
            prompt = (
                f"Apply '{name}' to one everyday situation from the lesson and "
                f"show each step."
            )
        else:
            prompt = f"Explain '{name}' in detail with examples from the lesson."
        long_q.append(
            {
                "question": prompt,
                "marks": 8,
                "lines": 10,
                "model_answer": _para(*answer_parts)
                if answer_parts
                else (
                    canonical_definition(name)
                    or f"{name} is a key idea in {topic}."
                ),
                "bloom": "application" if i == 1 else "understanding",
            }
        )

    # HOTS — topic-aware higher-order items mapped only to taught concepts.
    hots: list[dict[str, Any]] = []
    concept_names_for_hots = [
        str(c.get("name") or "").strip()
        for c in (concepts or [])
        if isinstance(c, dict) and str(c.get("name") or "").strip()
    ] or [topic]
    first = concept_names_for_hots[0]
    second = concept_names_for_hots[1] if len(concept_names_for_hots) > 1 else topic
    first_def = canonical_definition(first) or (pool[0] if pool else f"{first} is taught in this lesson.")
    second_def = canonical_definition(second) or (pool[1] if len(pool) > 1 else f"{second} is a different idea.")
    if any(k in topic_low for k in ("electric", "ohm", "circuit", "resistance")):
        ohm = canonical_definition("Ohm's law") or first_def
        series = canonical_definition("Series combination") or first_def
        parallel = canonical_definition("Parallel combination") or second_def
        power = canonical_definition("Electric power") or second_def
        hots.append(
            {
                "question": (
                    "Predict what happens to current if resistance doubles while "
                    "potential difference stays constant. Reason from Ohm's law."
                ),
                "marks": 5,
                "lines": 8,
                "model_answer": _para(
                    ohm,
                    "From V = IR, if V is constant and R doubles, I becomes half.",
                ),
                "bloom": "hots",
            }
        )
        hots.append(
            {
                "question": (
                    "Distinguish series combination from parallel combination using "
                    "ideas from this lesson."
                ),
                "marks": 5,
                "lines": 8,
                "model_answer": _para(series, parallel),
                "bloom": "hots",
            }
        )
        hots.append(
            {
                "question": (
                    "An electric bulb is marked 220 V, 100 W. Explain what this means "
                    "using electric power from the lesson."
                ),
                "marks": 5,
                "lines": 8,
                "model_answer": _para(
                    power,
                    "At 220 V the bulb is designed to consume 100 J of energy each second (100 W).",
                ),
                "bloom": "hots",
            }
        )
    elif any(k in topic_low for k in ("metal", "non-metal", "nonmetal", "malleab", "ductil")):
        metal = canonical_definition("Metal") or first_def
        nonmetal = canonical_definition("Non-metal") or second_def
        displace = canonical_definition("Displacement reaction") or second_def
        # Prefer uploaded textbook stems when available.
        metal_src = [
            a
            for a in textbook_assessments
            if _re.search(
                r"(?i)\b(malleab|ductil|non-?metal|mercury|magnesium|oxide|property|properties)\b",
                str(a.get("prompt") or ""),
            )
        ][:3]
        if metal_src:
            for row in metal_src:
                prompt = str(row.get("prompt") or "").strip()
                ans = (
                    canonical_definition("Non-metal")
                    if _re.search(r"(?i)non-?metal", prompt)
                    else (
                        canonical_definition("Malleability")
                        if _re.search(r"(?i)malleab", prompt)
                        else (
                            canonical_definition("Ductility")
                            if _re.search(r"(?i)ductil", prompt)
                            else (
                                canonical_definition("Mercury")
                                if _re.search(r"(?i)mercury", prompt)
                                else (
                                    canonical_definition("Metal oxide")
                                    if _re.search(r"(?i)oxide|burns", prompt)
                                    else metal
                                )
                            )
                        )
                    )
                )
                hots.append(
                    {
                        "question": prompt,
                        "marks": 5,
                        "lines": 8,
                        "model_answer": _para(ans or metal, nonmetal),
                        "bloom": "hots",
                    }
                )
        else:
            hots.append(
                {
                    "question": (
                        "Distinguish metals from non-metals using at least two physical "
                        "properties from the lesson."
                    ),
                    "marks": 5,
                    "lines": 8,
                    "model_answer": _para(metal, nonmetal),
                    "bloom": "hots",
                }
            )
            hots.append(
                {
                    "question": (
                        "What happens when a more reactive metal is placed in the "
                        "salt solution of a less reactive metal? Give a reason."
                    ),
                    "marks": 5,
                    "lines": 8,
                    "model_answer": _para(
                        displace,
                        "The more reactive metal displaces the less reactive metal from its salt solution.",
                    ),
                    "bloom": "hots",
                }
            )
    elif any(k in topic_low for k in ("acid", "base", "salt")):
        hots.append(
            {
                "question": (
                    "Predict what would change if an acid were mixed with a base until "
                    "the solution became neutral. Give a reason from the lesson."
                ),
                "marks": 5,
                "lines": 8,
                "model_answer": _para(
                    first_def,
                    "When an acid and a base cancel each other's effect, salt and water form (neutralisation).",
                    "The sharp sour or bitter properties become milder as the mixture approaches neutral.",
                ),
                "bloom": "hots",
            }
        )
        hots.append(
            {
                "question": (
                    f"Explain how {first.lower()} differs from {second.lower()} "
                    f"using ideas from this lesson."
                ),
                "marks": 5,
                "lines": 8,
                "model_answer": _para(
                    f"{first} and {second} are different ideas in {topic}.",
                    first_def,
                    second_def,
                ),
                "bloom": "hots",
            }
        )
    else:
        # Prefer textbook assessment stems when present (never invent classmate prompts).
        textbook_hots = [
            a
            for a in textbook_assessments
            if _re.search(
                r"(?i)\b(why|how|compare|predict|distinguish|advantage|explain|list two)\b",
                str(a.get("prompt") or ""),
            )
        ][:3]
        if textbook_hots:
            for row in textbook_hots:
                prompt = str(row.get("prompt") or "").strip()
                name = next(
                    (
                        str(c.get("name") or "")
                        for c in concepts
                        if str(c.get("name") or "").lower() in prompt.lower()
                    ),
                    first,
                )
                ans = canonical_definition(name) or first_def
                hots.append(
                    {
                        "question": prompt,
                        "marks": 5,
                        "lines": 8,
                        "model_answer": _para(ans),
                        "bloom": "hots",
                    }
                )
        else:
            hots.append(
                {
                    "question": (
                        f"Explain how {first.lower()} differs from {second.lower()} "
                        f"using ideas from this lesson."
                    ),
                    "marks": 5,
                    "lines": 8,
                    "model_answer": _para(
                        f"{first} and {second} are different ideas in {topic}.",
                        first_def,
                        second_def,
                    ),
                    "bloom": "hots",
                }
            )
            hots.append(
                {
                    "question": (
                        f"Describe one everyday situation that shows {topic.lower()} "
                        f"and name the main ideas inside it."
                    ),
                    "marks": 5,
                    "lines": 8,
                    "model_answer": _para(first_def, second_def),
                    "bloom": "hots",
                }
            )

    vocab_q = []
    for t in terms[:6]:
        if is_junk_term(t):
            continue
        answer = (
            canonical_definition(t)
            or definition_from_claims(t, pool)
            or build_student_definition(t, "", topic=topic)
        )
        if not answer or "key idea" in answer.lower() or "is taught in this lesson" in answer.lower():
            answer = next(
                (p for p in pool if t.lower() in str(p).lower() and len(str(p).split()) >= 5),
                "",
            )
        if not answer:
            continue
        vocab_q.append(
            {
                "question": f"Use the term '{t}' correctly in an exam-style sentence.",
                "marks": 2,
                "model_answer": str(answer).rstrip(".") + ".",
                "bloom": "recall",
            }
        )
    if not vocab_q:
        vocab_q = [
            {
                "question": f"Define a key term from {topic}.",
                "marks": 2,
                "model_answer": pool[0] if pool else f"State the lesson definition of a key term in {topic}.",
                "bloom": "recall",
            }
        ]

    from engines.lesson_composition_engine.diagrams import build_educational_flowchart_svg
    from engines.lesson_composition_engine.vocab_quality import filter_diagram_stages

    concept_names = filter_diagram_stages(
        [
            str(c.get("name") or "").strip()
            for c in concepts
            if isinstance(c, dict) and str(c.get("name") or "").strip()
        ],
        topic=topic,
        claims=pool,
        limit=6,
    )
    if len(concept_names) < 2 and any(k in topic.lower() for k in ("acid", "base", "salt")):
        from engines.lesson_composition_engine.vocab_quality import ACIDS_BASES_SALTS_TERMS

        concept_names = [t for t, _ in ACIDS_BASES_SALTS_TERMS][:5]

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
    for i, row in enumerate(hots):
        answer_key.append(
            {"question_ref": f"Part E Q{i+1}", "model_answer": row["model_answer"], "marks_notes": "5 marks"}
        )

    # Tag short answers as recall / understanding for progressive exam design.
    for i, row in enumerate(short):
        row.setdefault("bloom", "recall" if i < 3 else "understanding")

    return {
        "header": {
            "subject": subject,
            "topic": topic,
            "time_allowed": "45-60 minutes",
            "total_marks": 40,
            "progression": ["recall", "understanding", "application", "hots"],
        },
        "short_answer": short,
        "long_answer": long_q,
        "hots": hots,
        "diagram_question": {
            "question": (
                f"Study the labelled diagram for {topic}. "
                f"Redraw it and label each main idea accurately."
            ),
            "marks": 5,
            "svg_diagram": flowchart,
            "model_answer": (
                "A correct response redraws the pathway and labels each main idea exactly: "
                + ", ".join(concept_names[:6])
                + "."
            ),
            "alt_text": f"Labelled concept pathway for {topic}: {', '.join(concept_names[:6])}.",
        },
        "vocab_questions": vocab_q,
        "student_checklist": [
            "Read every question twice before writing.",
            "Use lesson vocabulary in answers.",
            "Check timing: short answers first, then long answers, then HOTS.",
            "Review the diagram question labels.",
            "Every answer must use a Must Know idea from the Master Lesson.",
        ],
        "teacher_differentiation": (
            "Same worksheet for every learner — progressive recall → understanding → "
            "application → HOTS. Assign chunked Parts for ADHD/dyslexia supports; keep "
            "board vocabulary for ELL; prefer visual organiser for visual learners. "
            "Do not change verified facts or remove questions."
        ),
        "answer_key": answer_key,
        "_lce": {"frequency_based": False, "from_clg": True, "from_master_lesson": True},
    }


def _diagrams_from_board(board: Mapping[str, Any], clg: Mapping[str, Any]) -> tuple[str, str]:
    """Return (primary_svg, secondary_svg). Prefer domain visuals (water cycle) first."""
    from engines.lesson_composition_engine.publisher_remediation import (
        is_generic_subject_flowchart,
    )
    from engines.lesson_composition_engine.vocab_quality import filter_diagram_stages

    topic = str(board.get("topic") or clg.get("topic") or "Lesson")
    subject = str(board.get("subject") or clg.get("subject_key") or "general")
    claims = [str(c) for c in (board.get("verified_claims") or []) if str(c).strip()]
    concept_names = [
        str(c.get("name") or "").strip()
        for c in (board.get("concepts") or [])
        if isinstance(c, dict) and str(c.get("name") or "").strip()
    ]
    # Also accept plain string concepts from some boards.
    for c in board.get("concepts") or []:
        if isinstance(c, str) and c.strip():
            concept_names.append(c.strip())
    stages = filter_diagram_stages(concept_names, topic=topic, claims=claims, limit=6)
    concept_map = build_concept_map_svg(topic, stages or [topic])
    if len(stages) >= 2:
        flowchart = build_educational_flowchart_svg(
            topic,
            stages,
            subtitle=f"{subject.title()} key ideas in order",
        )
    else:
        flowchart = build_subject_flowchart(subject, topic)
    # Domain cycle / water visual wins over a vertical or generic pedagogy stack.
    primary = concept_map if concept_map and (
        is_generic_subject_flowchart(flowchart) or "water" in topic.lower() or "cycle" in topic.lower()
    ) else flowchart
    if not primary:
        primary = flowchart or concept_map
    secondary = flowchart if primary == concept_map else concept_map
    return primary, secondary


def compose_adaptations_from_clg(
    clg: Mapping[str, Any],
    *,
    lens_ids: list[str] | None = None,
    board: Mapping[str, Any] | None = None,
    uli: Mapping[str, Any] | None = None,
    sif: Mapping[str, Any] | None = None,
    uvie: Mapping[str, Any] | None = None,
    stem_artifacts: list | None = None,
) -> dict[str, Any]:
    """Compose all adaptive versions from the Lesson Intelligence Board (Phase Omega).

    Lesson Wall (Master concept cards) is the single source of truth for vocabulary,
    exam long answers, voice reading, and every adaptation — presentation only differs.
    STEM numerical/balance answers come from verified EngineResult artifacts.
    """
    ids = list(lens_ids or DEFAULT_LENS_IDS)
    clg_seed = dict(clg)
    artifacts_early = list(
        stem_artifacts or clg_seed.get("stem_artifacts") or []
    )
    if artifacts_early:
        clg_seed["stem_artifacts"] = artifacts_early
    intelligence = dict(
        board
        or build_lesson_intelligence_board(clg_seed, uli=uli, sif=sif, uvie=uvie)
    )
    artifacts = list(
        stem_artifacts
        or intelligence.get("stem_artifacts")
        or clg_seed.get("stem_artifacts")
        or []
    )
    if artifacts:
        intelligence["stem_artifacts"] = artifacts
    # Carry upload teaching bank onto CLG so vocab/worksheet share Master concepts.
    clg_work = dict(clg_seed)
    if intelligence.get("teaching_bank"):
        clg_work["teaching_bank"] = list(intelligence.get("teaching_bank") or [])
    if artifacts:
        clg_work["stem_artifacts"] = artifacts
    flowchart, concept_map = _diagrams_from_board(intelligence, clg_work)
    primary_svg = flowchart or concept_map
    secondary_svg = concept_map if concept_map and concept_map != primary_svg else flowchart

    out: dict[str, Any] = {
        "_intelligence_board": intelligence,
        "_integration_failures": integration_failures(intelligence),
        "_phase_omega": True,
        "_stem_artifacts": copy.deepcopy(artifacts),
    }

    # ------------------------------------------------------------------
    # Master Lesson Architecture:
    # ONE canonical Mainstream lesson → Lesson Wall → every adaptation.
    # ------------------------------------------------------------------
    from engines.lesson_composition_engine.canonical import (
        PRESENTATION_LENSES,
        augment_support_version,
        build_canonical_lesson,
        derive_presentation_adaptation,
        extract_essential_learning_core,
        freeze_canonical,
        validate_curriculum_fidelity,
    )
    from engines.lesson_composition_engine.lesson_wall import (
        extract_lesson_wall,
        wall_long_answers,
        wall_vocab_terms,
    )

    canonical = build_canonical_lesson(
        intelligence,
        flowchart_svg=primary_svg,
        concept_map_svg=secondary_svg or primary_svg,
        stem_artifacts=artifacts,
    )
    core = extract_essential_learning_core(canonical, intelligence)
    frozen = freeze_canonical(canonical, core)

    # Lesson Wall = what the learner needs to know (square tab boxes).
    # Phase 2: fill thin/OCR-weak walls from the dynamic teaching bank.
    from engines.lesson_composition_engine.dynamic_teaching_bank import (
        build_dynamic_teaching_bank,
        ensure_wall_from_bank,
    )

    wall = extract_lesson_wall(frozen)
    # Always rebuild with stem artifacts so thin PDFs get engine-backed cards.
    teaching_bank = build_dynamic_teaching_bank(
        topic=str(intelligence.get("topic") or clg_work.get("topic") or ""),
        source_text=str(
            intelligence.get("source_text") or clg_work.get("source_text") or ""
        ),
        claims=[str(c) for c in (intelligence.get("verified_claims") or [])],
        concepts=list(intelligence.get("concepts") or []),
        stem_artifacts=artifacts,
        assessment_prompts=list(clg_work.get("assessment_outcomes") or []),
    )
    if teaching_bank:
        intelligence["teaching_bank"] = teaching_bank
        clg_work["teaching_bank"] = teaching_bank
    wall = ensure_wall_from_bank(
        wall,
        teaching_bank,
        topic=str(intelligence.get("topic") or clg_work.get("topic") or ""),
        min_cards=3,
    )
    frozen["lesson_wall"] = copy.deepcopy(wall)
    frozen["teaching_bank"] = copy.deepcopy(teaching_bank)
    if primary_svg:
        frozen["svg_diagram"] = primary_svg
        frozen["flowchart_svg"] = primary_svg
        frozen["concept_map_svg"] = secondary_svg or primary_svg
        pkg = dict(frozen.get("diagram_package") or {})
        pkg["svg"] = primary_svg
        pkg.setdefault("title", str(frozen.get("topic") or "Lesson diagram"))
        pkg.setdefault("caption", "A labelled teaching diagram for this lesson.")
        frozen["diagram_package"] = pkg

    # Vocabulary + Exam built FROM the wall (not a parallel generation).
    topic = str(intelligence.get("topic") or clg_work.get("topic") or "Lesson")
    wall_terms = wall_vocab_terms(wall, topic=topic)
    if wall_terms:
        clg_for_vocab = dict(clg_work)
        clg_for_vocab["vocabulary"] = wall_terms + list(clg_work.get("vocabulary") or [])
        # Prefer wall teaching text as claim seeds for definitions.
        clg_for_vocab["claim_texts"] = [
            str(c.get("idea") or "") for c in wall if str(c.get("idea") or "").strip()
        ] + list(clg_work.get("claim_texts") or [])
        vocabulary = compose_vocabulary_from_clg(clg_for_vocab)
    else:
        vocabulary = compose_vocabulary_from_clg(clg_work)
    if "vocabulary" in ids:
        out["vocabulary"] = vocabulary
        if isinstance(out["vocabulary"], dict):
            out["vocabulary"]["lesson_wall"] = copy.deepcopy(wall)
            if primary_svg:
                out["vocabulary"]["svg_diagram"] = primary_svg
                out["vocabulary"]["concept_map_svg"] = primary_svg
                out["vocabulary"]["flowchart_svg"] = primary_svg

    if "worksheet" in ids:
        worksheet = compose_worksheet_from_clg(
            clg_work, vocabulary, stem_artifacts=artifacts
        )
        # Replace Part B (8-mark) answers with Lesson Wall teaching text.
        wall_long = wall_long_answers(wall, topic=topic, limit=4)
        if wall_long:
            worksheet["long_answer"] = wall_long
            # Keep answer key aligned with wall-sourced long answers.
            key_rows = [
                row
                for row in (worksheet.get("answer_key") or [])
                if isinstance(row, dict)
                and not str(row.get("question_ref") or "").startswith("Part B")
            ]
            for i, row in enumerate(wall_long):
                key_rows.append(
                    {
                        "question_ref": f"Part B Q{i + 1}",
                        "model_answer": row.get("model_answer"),
                        "marks_notes": "8 marks",
                    }
                )
            worksheet["answer_key"] = key_rows
        worksheet["lesson_wall"] = copy.deepcopy(wall)
        if primary_svg:
            dq = worksheet.get("diagram_question")
            if isinstance(dq, dict):
                dq["svg_diagram"] = primary_svg
            else:
                worksheet["diagram_question"] = {
                    "question": (
                        f"Study the labelled diagram for {topic}. "
                        "Redraw it and label each main idea accurately."
                    ),
                    "marks": 5,
                    "svg_diagram": primary_svg,
                }
            worksheet["svg_diagram"] = primary_svg
        out["worksheet"] = worksheet

    for vid in ids:
        if vid in {"vocabulary", "worksheet"}:
            continue
        if vid == "standard":
            out[vid] = copy.deepcopy(frozen)
        elif vid in {"teacher", "parent"}:
            out[vid] = augment_support_version(frozen, core, intelligence, vid)
        elif vid in PRESENTATION_LENSES:
            out[vid] = derive_presentation_adaptation(frozen, core, vid)
        else:
            continue
        out[vid].setdefault("lce", {})
        if isinstance(out[vid]["lce"], dict):
            out[vid]["lce"]["lens"] = lens_for("ld" if vid == "dyslexia" else vid)
            out[vid]["lce"]["intelligence_board_version"] = intelligence.get("version")
            out[vid]["lce"]["composed_from_clg"] = True
            out[vid]["lce"]["not_a_clone"] = True
            out[vid]["lce"]["lesson_wall_source"] = True
        # Shared wall + domain diagram on every adaptation (including Parent).
        out[vid]["lesson_wall"] = copy.deepcopy(wall)
        if primary_svg:
            out[vid]["svg_diagram"] = primary_svg
            out[vid]["flowchart_svg"] = primary_svg
            out[vid]["concept_map_svg"] = secondary_svg or primary_svg
        if frozen.get("diagram_package"):
            pkg = copy.deepcopy(frozen["diagram_package"])
            if isinstance(pkg, dict) and primary_svg:
                pkg["svg"] = primary_svg
            out[vid]["diagram_package"] = pkg

    out["_lesson_wall"] = copy.deepcopy(wall)
    out["_canonical"] = {
        "core": core,
        "hash": core.get("hash"),
        "frozen": True,
        "gold_standard": "standard",
    }
    # Curriculum fidelity — hard gate: identical curriculum in every version.
    out["_curriculum_fidelity"] = validate_curriculum_fidelity(core, out)

    # Stamp similarity audit for publication gate
    try:
        from engines.lesson_composition_engine.recovery import adaptation_similarity_report

        out["_adaptation_similarity"] = adaptation_similarity_report(out)
    except Exception:  # noqa: BLE001
        pass
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
    stem_artifacts = list(kwargs.get("stem_artifacts") or [])

    clg = build_canonical_lesson_graph(uli, sif=sif, uvie=uvie, topic_hint=topic_hint)
    clg_dict = clg.to_dict()
    if stem_artifacts:
        clg_dict["stem_artifacts"] = stem_artifacts
    # Phase Omega — Intelligence Board before any paragraph authorship
    board = build_lesson_intelligence_board(
        clg_dict,
        uli=uli if isinstance(uli, Mapping) else {},
        sif=sif if isinstance(sif, Mapping) else {},
        uvie=uvie if isinstance(uvie, Mapping) else {},
    )
    if stem_artifacts:
        board["stem_artifacts"] = stem_artifacts
    adaptations = compose_adaptations_from_clg(
        clg_dict,
        board=board,
        uli=uli if isinstance(uli, Mapping) else {},
        sif=sif if isinstance(sif, Mapping) else {},
        uvie=uvie if isinstance(uvie, Mapping) else {},
        stem_artifacts=stem_artifacts,
    )
    import copy

    lce_authored = copy.deepcopy(adaptations)
    original_source = {
        "adaptations": {
            "standard": {
                "topic": board.get("topic"),
                "big_idea": (board.get("verified_claims") or [""]),
                "sections": [
                    {"title": "Source claim", "role": "concept", "body": str(c)}
                    for c in (board.get("verified_claims") or [])[:6]
                ],
            }
        },
        "_intelligence_board": board,
    }
    if isinstance(original_source["adaptations"]["standard"]["big_idea"], list):
        claims0 = original_source["adaptations"]["standard"]["big_idea"]
        original_source["adaptations"]["standard"]["big_idea"] = str(claims0[0] if claims0 else "")

    # Publisher-Quality Lesson Excellence — polish, golden compare, editorial board
    from engines.lesson_composition_engine.revise import apply_publisher_quality_excellence

    pqle = apply_publisher_quality_excellence(
        adaptations, clg=clg_dict, board=board
    )
    adaptations = pqle.get("adaptations") or adaptations
    eerl = pqle.get("eerl") or review_package(adaptations, clg_dict)
    pqi = pqle.get("pqi") or {}
    editorial = pqle.get("editorial") or {}

    contribution_log = list(pqle.get("contribution_log") or [])
    try:
        from engines.lesson_composition_engine.recovery import measure_upstream_engine_contributions

        contribution_log = measure_upstream_engine_contributions(
            clg_dict,
            uli=uli if isinstance(uli, Mapping) else {},
            sif=sif if isinstance(sif, Mapping) else {},
            uvie=uvie if isinstance(uvie, Mapping) else {},
            full_adaptations=adaptations,
        ) + contribution_log
    except Exception as exc:  # noqa: BLE001
        contribution_log.append(
            {
                "engine": "ULI/SIF/UVIE",
                "bypassed": True,
                "error": str(exc)[:300],
                "log": "ENGINE CONTRIBUTION FAILURE",
            }
        )

    side_by_side: dict[str, Any] = {}
    try:
        from engines.lesson_composition_engine.recovery import side_by_side_quality_report

        side_by_side = side_by_side_quality_report(
            original=original_source,
            lce={"adaptations": lce_authored},
            final={"adaptations": adaptations},
            subject=str(board.get("subject") or ""),
            topic=str(board.get("topic") or topic_hint or ""),
        )
    except Exception as exc:  # noqa: BLE001
        side_by_side = {"ok": False, "error": str(exc)[:300]}

    publication_ready = bool(pqle.get("publication_ready"))
    publisher_review = pqle.get("publisher_review_report") or {}

    # v3.3 Curriculum Fidelity — re-validated AFTER all polish passes so no
    # downstream engine can silently remove curriculum. Hard gate.
    curriculum_fidelity: dict[str, Any] = {}
    try:
        from engines.lesson_composition_engine.canonical import validate_curriculum_fidelity

        canonical_meta = adaptations.get("_canonical") or lce_authored.get("_canonical") or {}
        core = dict(canonical_meta.get("core") or {})
        if core:
            curriculum_fidelity = validate_curriculum_fidelity(core, adaptations)
    except Exception as exc:  # noqa: BLE001
        curriculum_fidelity = {"ok": False, "failures": [f"validator error: {exc}"]}
    fidelity_ok = bool(curriculum_fidelity.get("ok", True))
    reject_reasons = list(pqle.get("reject_reasons") or [])
    if not fidelity_ok:
        reject_reasons.append(
            "curriculum_fidelity_failed: " + "; ".join(curriculum_fidelity.get("failures", [])[:4])
        )
    publication_ready = publication_ready and fidelity_ok

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
        "eqs": pqle.get("eqs") or {},
        "heq": pqle.get("heq") or pqle.get("eqs") or {},
        "human_verdict": pqle.get("human_verdict") or {},
        "adaptation_advantages": pqle.get("adaptation_advantages") or {},
        "side_by_side": side_by_side,
        "adaptation_similarity": pqle.get("adaptation_similarity") or {},
        "golden_gate": pqle.get("golden_gate") or {},
        "contribution_log": contribution_log,
        "reject_reasons": reject_reasons,
        "canonical": adaptations.get("_canonical") or {},
        "curriculum_fidelity": curriculum_fidelity,
        "pqle": {
            "publication_ready": publication_ready,
            "reject_rendering": bool(pqle.get("reject_rendering")),
            "threshold": pqle.get("threshold"),
            "worst_score": pqi.get("worst_score"),
            "editorial_approved": bool(editorial.get("approved")),
            "pmes_approved": bool((pqle.get("pmes") or {}).get("approved")),
            "uevb_approved": bool((pqle.get("uevb") or {}).get("ok")),
            "peec_ok": bool((pqle.get("peec") or {}).get("ok")),
            "mode": "formatting_only",
            "eqs": (pqle.get("eqs") or {}).get("overall"),
            "heq": (pqle.get("heq") or pqle.get("eqs") or {}).get("overall"),
            "recovery_sprint": True,
            "human_first": True,
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
            "pqle_formatting_only": True,
            "pmes_clarity_only": True,
            "adaptation_similarity_max": 0.40,
            "engine_contribution_bypass": True,
            "golden_minimum_standard": True,
            "phase_omega": True,
            "phase_omega_2_pmes": True,
            "pmes_highest_authority": True,
            "uevb_final_authority": True,
            "peec_product_excellence": True,
            "pobr_beta_readiness": True,
            "intelligence_board_required": True,
            "no_new_engines": True,
            "recovery_sprint": True,
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
        stem_artifacts=list(meta.get("engine_artifacts") or meta.get("stem_artifacts") or []),
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
    stem_arts = list(meta.get("engine_artifacts") or meta.get("stem_artifacts") or [])
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
        stem_artifacts=stem_arts,
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
        # Keep the LCE-authored worksheet in versions — dropping it forced the
        # Streamlit path onto LLM/extractive fallbacks and broke the exam module.
        versions={k: v for k, v in adaptations.items() if k != "vocabulary" and not str(k).startswith("_")},
        vocabulary=adaptations.get("vocabulary") or {},
        quality=quality,
        publisher_meta={
            "clg": result.get("clg") or {},
            "intelligence_board": result.get("intelligence_board") or {},
            "canonical": result.get("canonical") or {},
            "curriculum_fidelity": result.get("curriculum_fidelity") or {},
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
            # Still scrub prompt leaks / clones — vocab-only path must not skip fidelity
            try:
                from engines.lesson_composition_engine.content_fidelity import (
                    ensure_classroom_content_fidelity,
                )

                adaptations = ensure_classroom_content_fidelity(
                    adaptations,
                    board=board if isinstance(board, dict) else {},
                )
            except Exception:  # noqa: BLE001
                pass
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
