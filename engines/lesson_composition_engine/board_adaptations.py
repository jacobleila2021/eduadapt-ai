"""Board-driven adaptation authorship — pedagogically unique experiences.

Phase Omega: never deep-copy mainstream and wrap. Each profile builds from the
Lesson Intelligence Board with its own sequence, load, examples, and checks.
"""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.intelligence_board import board_claim_for
from engines.lesson_composition_engine.lenses import LENS_CONTRACTS, lens_for
from engines.lesson_composition_engine.teaching_rules import ensure_paragraph_quality, scaffold_chunk

# Profile → which board slices and pacing to emphasise
PROFILE_AUTHORING: dict[str, dict[str, Any]] = {
    "standard": {
        "max_claim_words": 28,
        "use_bullets": False,
        "visual_first": False,
        "listen": False,
        "home": False,
        "teacher": False,
        "chunk_titles": False,
    },
    "ld": {
        "max_claim_words": 16,
        "use_bullets": True,
        "visual_first": True,
        "listen": False,
        "home": False,
        "teacher": False,
        "chunk_titles": True,
        "structure_key": "ld",
    },
    "dyslexia": {
        "max_claim_words": 14,
        "use_bullets": True,
        "visual_first": True,
        "listen": False,
        "home": False,
        "teacher": False,
        "chunk_titles": True,
        "structure_key": "ld",
    },
    "adhd": {
        "max_claim_words": 14,
        "use_bullets": True,
        "visual_first": True,
        "listen": False,
        "home": False,
        "teacher": False,
        "chunk_titles": True,
        "structure_key": "adhd",
        "movement": True,
    },
    "autism": {
        "max_claim_words": 18,
        "use_bullets": False,
        "visual_first": True,
        "listen": False,
        "home": False,
        "teacher": False,
        "literal": True,
        "structure_key": "autism",
    },
    "ell": {
        "max_claim_words": 16,
        "use_bullets": False,
        "visual_first": False,
        "listen": False,
        "home": False,
        "teacher": False,
        "glossary": True,
        "structure_key": "ell",
    },
    "visual": {
        "max_claim_words": 22,
        "use_bullets": False,
        "visual_first": True,
        "listen": False,
        "home": False,
        "teacher": False,
        "structure_key": "visual",
    },
    "auditory": {
        "max_claim_words": 20,
        "use_bullets": False,
        "visual_first": False,
        "listen": True,
        "home": False,
        "teacher": False,
        "structure_key": "auditory",
    },
    "teacher": {
        "max_claim_words": 26,
        "use_bullets": False,
        "visual_first": False,
        "listen": False,
        "home": False,
        "teacher": True,
        "structure_key": "teacher",
    },
    "parent": {
        "max_claim_words": 20,
        "use_bullets": False,
        "visual_first": False,
        "listen": False,
        "home": True,
        "teacher": False,
        "structure_key": "parent",
    },
}


def _shorten(text: str, max_words: int) -> str:
    words = (text or "").split()
    if len(words) <= max_words:
        return text
    cut = " ".join(words[:max_words]).rstrip(",;:")
    return cut + "."


def _body(text: str, *, profile: Mapping[str, Any], title: str) -> str:
    text = ensure_paragraph_quality(text, idea=title)
    text = _shorten(text, int(profile.get("max_claim_words") or 24))
    if profile.get("use_bullets"):
        bullets = scaffold_chunk(text, max_bullets=6)
        text = "\n".join(f"- {b}" for b in bullets)
    if profile.get("listen"):
        text = f"{text}\n\nSay this idea aloud in your own words."
    if profile.get("glossary") and "Important words" not in text:
        pass  # glossary section added separately
    return text.strip()


def _structure_for(version_id: str) -> list[str]:
    key = PROFILE_AUTHORING.get(version_id, {}).get("structure_key") or version_id
    if key == "standard":
        return list((LENS_CONTRACTS.get("standard") or {}).get("structure") or [])
    contract = LENS_CONTRACTS.get(key) or LENS_CONTRACTS.get("standard") or {}
    return list(contract.get("structure") or ["Learning Goal", "Core Ideas", "Practice", "Summary"])


def compose_adaptation_from_board(
    board: Mapping[str, Any],
    version_id: str,
    *,
    flowchart_svg: str = "",
    concept_map_svg: str = "",
) -> dict[str, Any]:
    """Author one pedagogically unique adaptation from the Intelligence Board."""
    profile = PROFILE_AUTHORING.get(version_id) or PROFILE_AUTHORING["standard"]
    topic = str(board.get("topic") or "Lesson")
    concepts = [c for c in (board.get("concepts") or []) if isinstance(c, dict)]
    claims = list(board.get("verified_claims") or [])
    examples = list(board.get("examples") or [])
    misconceptions = [m for m in (board.get("misconceptions") or []) if isinstance(m, dict)]
    goals = list(board.get("learning_goals") or [])
    vocab = list(board.get("vocabulary") or [])
    visuals = [v for v in (board.get("visual_opportunities") or []) if isinstance(v, dict)]

    structure = _structure_for(version_id)
    sections: list[dict[str, Any]] = []

    # Every adaptation with a diagram must teach from it (referenced, explained, used)
    if flowchart_svg or concept_map_svg:
        cap = (visuals[0].get("caption") if visuals else f"Diagram for {topic}")
        diagram_title = (
            "See It First"
            if version_id == "visual"
            else ("Lesson Diagram" if profile.get("visual_first") else "Using the Diagram")
        )
        sections.append(
            {
                "title": diagram_title,
                "role": "visual",
                "box": "visual",
                "body": _body(
                    f"The diagram shows how the ideas in {topic} connect. "
                    f"{cap}. Trace each labelled part, then match it to the explanation that follows. "
                    f"You will use this diagram again in practice.",
                    profile=profile,
                    title="diagram",
                ),
                "_trace": {
                    "engines": ["uvie", "lce"],
                    "improves": "diagram",
                    "learner_need": version_id,
                },
            }
        )

    if profile.get("home"):
        sections.append(
            {
                "title": "Today's Home Focus",
                "role": "hook",
                "box": "home",
                "body": _body(
                    goals[0] if goals else f"Help your child explain one clear idea from {topic}.",
                    profile=profile,
                    title="home",
                ),
            }
        )

    if version_id == "adhd":
        sections.append(
            {
                "title": "Mission Goal",
                "role": "hook",
                "box": "checkpoint",
                "body": _body(
                    (goals[0] if goals else f"Learn the key ideas in {topic}.")
                    + " Work in short bursts. After each chunk, pause once.",
                    profile=profile,
                    title="mission",
                ),
            }
        )

    if version_id == "autism":
        sections.append(
            {
                "title": "What We Will Learn",
                "role": "hook",
                "box": "predictable",
                "body": _body(
                    f"Today we learn {topic}. First we read the idea. Next we see an example. "
                    f"Then we practise. The order stays the same.",
                    profile=profile,
                    title="routine",
                ),
            }
        )
        sections.append(
            {
                "title": "Today's Routine",
                "role": "hook",
                "box": "predictable",
                "body": _body(
                    "1) Open the idea. 2) Explain it. 3) Example. 4) Practice. 5) Finished summary.",
                    profile=profile,
                    title="routine",
                ),
            }
        )

    if version_id == "ell":
        sections.append(
            {
                "title": "Key Words First",
                "role": "vocabulary",
                "box": "glossary",
                "body": _body(
                    "Learn these lesson words first: "
                    + (", ".join(vocab[:8]) if vocab else "the main lesson terms")
                    + '. Sentence frame: “______ means ______, and an example is ______.”',
                    profile=profile,
                    title="words",
                ),
            }
        )

    if version_id == "auditory":
        sections.append(
            {
                "title": "Listen Goal",
                "role": "hook",
                "box": "listen",
                "body": _body(
                    f"You will hear the ideas in {topic}, say them, and check them. "
                    "Pause after each main idea and repeat one sentence aloud.",
                    profile=profile,
                    title="listen",
                ),
            }
        )

    # Shared teaching spine from board — ordered uniquely per profile
    concept_order = list(concepts)
    if version_id == "visual":
        concept_order = list(reversed(concepts)) if len(concepts) > 1 else concepts
    if version_id == "adhd":
        # Fewer, tighter concept bursts
        concept_order = concepts[:3]

    if not any(s.get("title") == "Learning Goal" for s in sections) and version_id not in {"adhd", "autism", "parent"}:
        sections.append(
            {
                "title": "Learning Goal",
                "role": "hook",
                "box": "hook",
                "body": _body(
                    goals[0] if goals else f"You will learn the key ideas in {topic}.",
                    profile=profile,
                    title="goal",
                ),
            }
        )

    lead = claims[0] if claims else f"{topic} is explained with accurate lesson evidence."
    if version_id == "standard":
        sections.append(
            {
                "title": "Lesson Introduction",
                "role": "hook",
                "body": _body(lead, profile=profile, title="intro"),
            }
        )

    for index, concept in enumerate(concept_order[:5]):
        name = str(concept.get("name") or f"Idea {index + 1}")
        claim = board_claim_for(board, name) or str(concept.get("explanation") or lead)
        example = examples[index] if index < len(examples) else board_claim_for(board, name)

        if version_id == "adhd":
            sections.append(
                {
                    "title": f"2-Minute Chunk {index + 1}: {name}",
                    "role": "concept",
                    "box": "checkpoint",
                    "body": _body(claim, profile=profile, title=name),
                }
            )
            sections.append(
                {
                    "title": f"Quick Check — {name}",
                    "role": "practice_question",
                    "box": "checkpoint",
                    "body": _body(
                        f"In one sentence, what is {name.lower()}? Use the evidence you just read.",
                        profile=profile,
                        title=name,
                    ),
                }
            )
            if index == 0 and profile.get("movement"):
                sections.append(
                    {
                        "title": "Movement Break",
                        "role": "reflection",
                        "box": "checkpoint",
                        "body": _body(
                            "Stand, stretch for twenty seconds, then continue to the next chunk.",
                            profile=profile,
                            title="break",
                        ),
                    }
                )
            continue

        concept_title = (
            f"Teach Step by Step — {name}"
            if version_id in {"ld", "dyslexia"}
            else f"Concept: {name}"
        )
        sections.append(
            {
                "title": concept_title,
                "role": "concept",
                "box": "teach",
                "body": _body(claim, profile=profile, title=name),
                "_trace": {
                    "engines": ["kie", "uli", "lce"],
                    "improves": "explanation",
                    "misconception": "",
                    "learner_need": version_id,
                },
            }
        )
        # Mainstream teaching depth — publisher-grade concept cycle
        if version_id == "standard":
            sections.append(
                {
                    "title": f"Understanding {name}",
                    "role": "simple_explanation",
                    "body": _body(
                        f"{claim} Restate {name.lower()} in one short sentence before you continue.",
                        profile=profile,
                        title=name,
                    ),
                    "_trace": {"engines": ["lce"], "improves": "explanation", "learner_need": "standard"},
                }
            )
            sections.append(
                {
                    "title": f"Worked Example — {name}",
                    "role": "worked_example",
                    "body": _body(
                        f"Read this evidence carefully: {example or claim} "
                        f"Underline the words that define {name.lower()}, then write two accurate sentences.",
                        profile=profile,
                        title=name,
                    ),
                    "_trace": {"engines": ["lce"], "improves": "example", "learner_need": "standard"},
                }
            )
            sections.append(
                {
                    "title": f"Reflect on {name}",
                    "role": "reflection",
                    "body": _body(
                        f"What part of {name.lower()} feels clear, and what still needs another example? "
                        "Write one sentence that links this idea to the learning goal.",
                        profile=profile,
                        title=name,
                    ),
                    "_trace": {"engines": ["lce"], "improves": "reflection", "learner_need": "standard"},
                }
            )
        if version_id not in {"parent"}:
            sections.append(
                {
                    "title": f"Example — {name}",
                    "role": "real_life_example",
                    "body": _body(
                        example or f"Connect {name.lower()} to one clear situation from {topic}.",
                        profile=profile,
                        title=name,
                    ),
                    "_trace": {"engines": ["lce"], "improves": "example", "learner_need": version_id},
                }
            )
        if index < len(misconceptions) and version_id not in {"parent", "ell"}:
            misc = misconceptions[index]
            sections.append(
                {
                    "title": f"Watch Out — {name}",
                    "role": "common_misconception",
                    "body": _body(
                        f"{str(misc.get('label') or '').rstrip('.')}. "
                        f"Correction: {misc.get('correction') or 'Keep the definitions separate.'}",
                        profile=profile,
                        title=name,
                    ),
                    "_trace": {
                        "engines": ["ame", "sif", "lce"],
                        "improves": "explanation",
                        "misconception": str(misc.get("label") or ""),
                        "learner_need": version_id,
                    },
                }
            )
        if version_id not in {"parent"}:
            assess_body = (
                f"Look back at the diagram for {topic}. Point to the part that shows {name.lower()}, "
                f"then explain {name} in your own words with one correct example."
                if (flowchart_svg or concept_map_svg) and index == 0
                else f"Explain {name} in your own words, then give one correct example."
            )
            sections.append(
                {
                    "title": f"Try This — {name}",
                    "role": "practice_question",
                    "body": _body(assess_body, profile=profile, title=name),
                    "_trace": {"engines": ["lce", "ame"], "improves": "assessment", "learner_need": version_id},
                }
            )

    if version_id == "teacher":
        sections.append(
            {
                "title": "Teacher Guidance",
                "role": "teacher_note",
                "box": "teacher",
                "body": _body(
                    (
                        "Warm-up (2 min): ask one curiosity question from the opening. "
                        "Teach with the diagram first, then one worked example. "
                        "Exit ticket: one accurate sentence plus one real-life example. "
                        "Listen for the misconception notes already placed beside each core idea."
                    ),
                    profile=profile,
                    title="teacher",
                ),
            }
        )
        sections.append(
            {
                "title": "Differentiation Map",
                "role": "application",
                "box": "teacher",
                "body": _body(
                    "Use ADHD chunks, Autism routine, ELL key-words-first, and Visual diagram-first editions "
                    "for learners who need them. Do not change verified facts.",
                    profile=profile,
                    title="diff",
                ),
            }
        )

    if version_id == "parent":
        for index, concept in enumerate(concepts[:3]):
            name = str(concept.get("name") or "idea")
            claim = board_claim_for(board, name)
            sections.append(
                {
                    "title": f"Talk About — {name}",
                    "role": "concept",
                    "box": "home",
                    "body": _body(
                        f"Ask: What does {name.lower()} mean? Listen for: {claim or 'a clear lesson definition'}.",
                        profile=profile,
                        title=name,
                    ),
                }
            )
        sections.append(
            {
                "title": "Home Activity",
                "role": "application",
                "box": "home",
                "body": _body(
                    (
                        f"Tonight: ask your child to teach you one idea from {topic} in two minutes. "
                        "Praise clear wording. If they get stuck, look at the lesson diagram together "
                        "and ask them to point to one label and explain it."
                    ),
                    profile=profile,
                    title="home",
                ),
            }
        )
        sections.append(
            {
                "title": "Home Summary",
                "role": "summary",
                "box": "home",
                "body": _body(
                    f"Today you helped your child explain {topic}. "
                    "Praise clear wording and effort — you can check one example together tomorrow.",
                    profile=profile,
                    title="home-summary",
                ),
            }
        )

    # Close
    if version_id == "autism":
        sections.append(
            {
                "title": "Finished Summary",
                "role": "summary",
                "box": "summary",
                "body": _body(
                    f"Finished. Today you learned {topic}. You read the ideas, saw examples, and practised.",
                    profile=profile,
                    title="done",
                ),
            }
        )
    elif version_id == "adhd":
        sections.append(
            {
                "title": "Done Checklist",
                "role": "summary",
                "box": "checkpoint",
                "body": _body(
                    "Tick: I can name each idea · I can give one example · I checked one common mistake.",
                    profile=profile,
                    title="done",
                ),
            }
        )
    elif version_id not in {"parent"}:
        sections.append(
            {
                "title": "Lesson Summary",
                "role": "summary",
                "box": "summary",
                "body": _body(
                    f"{topic} brings together "
                    + (", ".join(str(c.get('name') or '') for c in concepts[:3]) or "the main ideas")
                    + ". Keep each definition precise before you revise.",
                    profile=profile,
                    title="summary",
                ),
            }
        )
        sections.append(
            {
                "title": "Think About It",
                "role": "reflection",
                "body": _body(
                    "Which idea feels strongest, and which needs another example? "
                    "Write one sentence that connects today's learning to something you already knew.",
                    profile=profile,
                    title="reflect",
                ),
            }
        )
        sections.append(
            {
                "title": "Apply Your Learning",
                "role": "application",
                "box": "practice",
                "body": _body(
                    f"Apply {topic} to one new situation from your own experience. "
                    "Explain your reasoning in three clear sentences using lesson words.",
                    profile=profile,
                    title="apply",
                ),
            }
        )

    label = (lens_for(version_id if version_id != "dyslexia" else "ld") or {}).get("title") or version_id
    big = claims[0] if claims else goals[0] if goals else f"Precise ideas help you explain {topic}."
    if version_id == "parent":
        big = f"Today's home focus: {big}"

    return {
        "big_idea": ensure_paragraph_quality(big, idea=topic),
        "sections": sections,
        "topic": topic,
        "title": f"{topic} — {label}",
        "flowchart_svg": flowchart_svg,
        "concept_map_svg": concept_map_svg,
        "svg_diagram": flowchart_svg or concept_map_svg,
        "revision_points": [f"Revise: {c.get('name')}" for c in concepts[:6]],
        "practice": [
            {"question": f"Explain {c.get('name')} using lesson evidence.", "marks": 2}
            for c in concepts[:4]
        ],
        "lce": {
            "version_id": version_id,
            "adaptive_profile": label,
            "pedagogically_distinct": True,
            "from_intelligence_board": True,
            "phase_omega": True,
            "authored_structure": structure[:8],
        },
    }
