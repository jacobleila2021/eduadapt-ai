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


def _author_concept_prose(
    version_id: str,
    *,
    name: str,
    claim: str,
    example: str,
    topic: str,
) -> str:
    """Profile-unique instructional authorship — not a shortened clone of the same claim."""
    from engines.lesson_composition_engine.master_teacher import craft_teaching_paragraph

    claim_s = (claim or f"{name} is defined clearly in this lesson.").strip()
    ex = (example or f"a familiar situation from {topic}").strip()
    # Prefer dedicated voice per profile; craft_teaching_paragraph already diverges.
    prose = craft_teaching_paragraph(
        claim=claim_s,
        topic=topic,
        concept=name,
        example=ex,
        profile=version_id,
    )
    if version_id == "visual":
        return (
            f"Illustration first for {name}: find it on the diagram, then read. "
            f"{claim_s} Callout: match the labels to this scene — {ex}. "
            f"Keep your finger on the picture while you explain {name.lower()}."
        )
    if version_id == "auditory":
        return (
            f"Conversation about {name}: hear the idea, then say it. "
            f"{claim_s} Memory cue: {ex}. "
            f"Repeat one clear sentence about {name.lower()} without looking."
        )
    if version_id == "ell":
        return (
            f"Word: {name}. Short meaning: {claim_s} "
            f"Sentence frame: “{name} means ____, and an example is ____.” "
            f"Fill the frame using: {ex}. Say the frame twice."
        )
    if version_id == "ld":
        return (
            f"- Focus: {name}\n"
            f"- Fact: {_shorten(claim_s, 16)}\n"
            f"- Example: {_shorten(ex, 12)}\n"
            f"- Check: Say {name.lower()} in five words."
        )
    if version_id == "dyslexia":
        return (
            f"{name}.\n"
            f"{_shorten(claim_s, 14)}\n"
            f"Slow line. Circle {name}.\n"
            f"Whisper: {_shorten(ex, 10)}"
        )
    if version_id == "adhd":
        return (
            f"Chunk goal — {name}: {_shorten(claim_s, 14)} "
            f"Do: underline the key fact. Example burst: {_shorten(ex, 10)}. "
            f"Done check: one sentence, then move."
        )
    if version_id == "autism":
        return (
            f"Idea: {name}. Fact: {claim_s} "
            f"Example (same routine every time): {ex}. "
            f"Check: write one literal sentence about {name.lower()}."
        )
    if version_id == "teacher":
        return (
            f"Teach {name} with verified evidence: {claim_s} "
            f"Anticipate confusion; model a strong answer that uses: {ex}. "
            f"Assess with one oral check and one written sentence."
        )
    if version_id == "parent":
        return (
            f"Ask at home: What is {name.lower()}? Listen for: {claim_s} "
            f"Try together: {ex}. Praise a clear explanation."
        )
    # mainstream classroom
    return prose or (
        f"{claim_s} In class, explain {name.lower()} with one partner check. "
        f"Worked example: {ex}. Then write two accurate sentences."
    )


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

    # Profile-unique lead so adaptations cannot collapse into clones.
    lead_by_profile = {
        "standard": f"Today you will master {topic} with clear explanations, examples, and practice.",
        "visual": f"Start with the picture of {topic}. Every idea below links back to what you see.",
        "auditory": f"Listen as we talk through {topic}. Say each key idea out loud before you write.",
        "ell": f"We learn {topic} with short sentences, useful words, and sentence frames you can copy.",
        "ld": f"We learn {topic} in small clear steps. Read one bullet, then check you understand.",
        "dyslexia": f"Take {topic} slowly. Short lines, clear words, and one idea at a time.",
        "adhd": f"Mission: finish {topic} in short bursts. Each chunk has a goal and a quick check.",
        "autism": f"Today's routine for {topic} stays the same: idea, example, check, next step.",
        "teacher": f"Teaching notes for {topic}: watch misconceptions, model answers, and check evidence.",
        "parent": f"Home learning for {topic}: talk, try a real-life example, and praise clear explanations.",
    }
    sections.append(
        {
            "title": {
                "standard": "Learning Goal",
                "visual": "See the Big Picture",
                "auditory": "Listen First",
                "ell": "Key Words First",
                "ld": "Step-by-Step Start",
                "dyslexia": "Calm Start",
                "adhd": "Mission Goal",
                "autism": "Today's Routine",
                "teacher": "Lesson Intent",
                "parent": "Home Focus",
            }.get(version_id, "Learning Goal"),
            "role": "hook",
            "body": lead_by_profile.get(version_id) or lead_by_profile["standard"],
        }
    )

    # Every adaptation with a diagram must teach from it (referenced, explained, used)
    if flowchart_svg or concept_map_svg:
        cap = (visuals[0].get("caption") if visuals else f"Diagram for {topic}")
        diagram_bodies = {
            "visual": (
                f"Start here: the illustration of {topic}. {cap}. "
                f"Read every label before any paragraph. You will keep returning to this picture."
            ),
            "auditory": (
                f"Describe the diagram of {topic} out loud. {cap}. "
                f"Name each label, then listen to yourself and correct any fuzzy words."
            ),
            "ell": (
                f"Diagram words for {topic}: look, point, say. {cap}. "
                f"Touch each label and say its name slowly."
            ),
            "ld": (
                f"Diagram steps for {topic}:\n- Look at the whole picture\n- Point to each label\n- Match one label to one sentence\n{cap}."
            ),
            "dyslexia": (
                f"Picture guide for {topic}. {cap}. One label at a time. Point. Read. Rest."
            ),
            "adhd": (
                f"30-second diagram mission for {topic}: scan labels, pick one, explain it. {cap}."
            ),
            "autism": (
                f"Same diagram routine for {topic}: 1) Open picture. 2) Read labels in order. 3) Match to the next idea. {cap}."
            ),
            "teacher": (
                f"Use the {topic} diagram as the teaching anchor. {cap}. "
                f"Cold-call labels before definitions; do not skip the visual check."
            ),
            "parent": (
                f"At home, open the {topic} diagram together. {cap}. "
                f"Ask your child to point to one label and explain it in their own words."
            ),
            "standard": (
                f"The diagram shows how the ideas in {topic} connect. {cap}. "
                f"Trace each labelled part, then match it to the explanation that follows."
            ),
        }
        diagram_title = {
            "visual": "See It First",
            "auditory": "Speak the Diagram",
            "ell": "Picture Words",
            "ld": "Diagram Steps",
            "dyslexia": "Picture Guide",
            "adhd": "Diagram Mission",
            "autism": "Diagram Routine",
            "teacher": "Visual Anchor",
            "parent": "Home Diagram",
            "standard": "Lesson Diagram",
        }.get(version_id, "Lesson Diagram")
        sections.append(
            {
                "title": diagram_title,
                "role": "visual",
                "box": "visual",
                "body": diagram_bodies.get(version_id) or diagram_bodies["standard"],
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

    # Shared teaching spine from board — ordered uniquely per profile.
    # Parent editions are authored only in the home block below (no student clone).
    concept_order = list(concepts)
    if version_id == "visual":
        concept_order = list(reversed(concepts)) if len(concepts) > 1 else concepts
    if version_id == "adhd":
        concept_order = concepts[:3]
    if version_id == "auditory":
        concept_order = concepts[:4]
    if version_id == "ell":
        concept_order = concepts[:4]

    if (
        not any(s.get("title") == "Learning Goal" for s in sections)
        and version_id not in {"adhd", "autism", "parent", "visual", "auditory", "ell"}
    ):
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

    if version_id != "parent":
        for index, concept in enumerate(concept_order[:5]):
            name = str(concept.get("name") or f"Idea {index + 1}")
            claim = board_claim_for(board, name) or str(concept.get("explanation") or lead)
            example = examples[index] if index < len(examples) else board_claim_for(board, name)
            if isinstance(example, dict):
                example = str(example.get("text") or example.get("example") or example.get("caption") or "")
            else:
                example = str(example or "")
            authored = _author_concept_prose(
                version_id, name=name, claim=str(claim), example=example, topic=topic
            )

            if version_id == "adhd":
                sections.append(
                    {
                        "title": f"2-Minute Chunk {index + 1}: {name}",
                        "role": "concept",
                        "box": "checkpoint",
                        "body": authored,
                    }
                )
                sections.append(
                    {
                        "title": f"Quick Check — {name}",
                        "role": "practice_question",
                        "box": "checkpoint",
                        "body": (
                            f"Timer check: what is {name.lower()} in one sentence? "
                            f"Use only the chunk evidence — no extra guessing."
                        ),
                    }
                )
                if index == 0 and profile.get("movement"):
                    sections.append(
                        {
                            "title": "Movement Break",
                            "role": "reflection",
                            "box": "checkpoint",
                            "body": "Stand, stretch for twenty seconds, then continue to the next chunk.",
                        }
                    )
                continue

            concept_title = {
                "ld": f"Small Step — {name}",
                "dyslexia": f"Calm Read — {name}",
                "visual": f"Picture Idea — {name}",
                "auditory": f"Say and Hear — {name}",
                "ell": f"Word Lesson — {name}",
                "autism": f"Routine Idea — {name}",
                "teacher": f"Teach — {name}",
                "standard": f"Concept: {name}",
            }.get(version_id, f"Concept: {name}")
            sections.append(
                {
                    "title": concept_title,
                    "role": "concept",
                    "box": "teach",
                    "body": authored,
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
                        "body": (
                            f"{claim} Restate {name.lower()} in one short sentence before you continue."
                        ),
                        "_trace": {"engines": ["lce"], "improves": "explanation", "learner_need": "standard"},
                    }
                )
                sections.append(
                    {
                        "title": f"Worked Example — {name}",
                        "role": "worked_example",
                        "body": (
                            f"Read this evidence carefully: {example or claim} "
                            f"Underline the words that define {name.lower()}, then write two accurate sentences."
                        ),
                        "_trace": {"engines": ["lce"], "improves": "example", "learner_need": "standard"},
                    }
                )
                sections.append(
                    {
                        "title": f"Life Link — {name}",
                        "role": "real_life_example",
                        "body": (
                            f"Connect {name.lower()} to everyday life: {example or claim}. "
                            f"Tell a partner where you would see {name.lower()} outside class."
                        ),
                        "_trace": {"engines": ["lce"], "improves": "example", "learner_need": "standard"},
                    }
                )
                sections.append(
                    {
                        "title": f"Reflect on {name}",
                        "role": "reflection",
                        "body": (
                            f"What part of {name.lower()} feels clear, and what still needs another example? "
                            "Write one sentence that links this idea to the learning goal."
                        ),
                        "_trace": {"engines": ["lce"], "improves": "reflection", "learner_need": "standard"},
                    }
                )
            elif version_id == "visual":
                sections.append(
                    {
                        "title": f"Diagram Practice — {name}",
                        "role": "real_life_example",
                        "body": (
                            f"On the diagram, circle {name.lower()}. Then sketch a tiny icon for: {example or claim}. "
                            f"Caption your sketch in eight words or fewer."
                        ),
                        "_trace": {"engines": ["uvie", "lce"], "improves": "diagram", "learner_need": "visual"},
                    }
                )
            elif version_id == "auditory":
                sections.append(
                    {
                        "title": f"Story Cue — {name}",
                        "role": "real_life_example",
                        "body": (
                            f"Tell a 20-second story that includes {name.lower()}. "
                            f"Start from: {example or claim}. End by repeating the accurate definition aloud."
                        ),
                        "_trace": {"engines": ["lce"], "improves": "example", "learner_need": "auditory"},
                    }
                )
            elif version_id == "ell":
                sections.append(
                    {
                        "title": f"Frame Practice — {name}",
                        "role": "practice_question",
                        "body": (
                            f"Complete: “{name} means ____.” Then: “An example of {name.lower()} is ____.” "
                            f"Use these words if helpful: {(example or claim).split()[:6]}"
                        ),
                        "_trace": {"engines": ["lce"], "improves": "assessment", "learner_need": "ell"},
                    }
                )
            elif version_id == "teacher":
                sections.append(
                    {
                        "title": f"Misconception Watch — {name}",
                        "role": "common_misconception",
                        "body": (
                            f"When teaching {name.lower()}, listen for fuzzy wording. "
                            f"Anchor students to: {claim}. Strong example to model: {example or 'a concrete classroom case'}."
                        ),
                        "_trace": {"engines": ["ame", "sif", "lce"], "improves": "explanation", "learner_need": "teacher"},
                    }
                )
            elif version_id in {"ld", "dyslexia"}:
                sections.append(
                    {
                        "title": f"Show Me — {name}",
                        "role": "practice_question",
                        "body": (
                            f"Point to the words that mean {name.lower()}. "
                            f"Then copy one short true sentence about it."
                            if version_id == "dyslexia"
                            else f"Bullet check: write three words that belong with {name.lower()}, then one example."
                        ),
                    }
                )
            if index < len(misconceptions) and version_id not in {"ell", "teacher"}:
                misc = misconceptions[index]
                sections.append(
                    {
                        "title": f"Watch Out — {name}",
                        "role": "common_misconception",
                        "body": (
                            f"{str(misc.get('label') or '').rstrip('.')}. "
                            f"Correction: {misc.get('correction') or 'Keep the definitions separate.'}"
                        ),
                        "_trace": {
                            "engines": ["ame", "sif", "lce"],
                            "improves": "explanation",
                            "misconception": str(misc.get("label") or ""),
                            "learner_need": version_id,
                        },
                    }
                )
            if version_id == "standard":
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
                        "body": assess_body,
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
    elif version_id == "visual":
        sections.append(
            {
                "title": "Picture Check",
                "role": "summary",
                "box": "visual",
                "body": (
                    f"Close the lesson by redrawing the {topic} diagram from memory. "
                    f"Label {', '.join(str(c.get('name') or '') for c in concepts[:3]) or 'each part'} without peeking."
                ),
            }
        )
    elif version_id == "auditory":
        sections.append(
            {
                "title": "Say the Summary",
                "role": "summary",
                "box": "listen",
                "body": (
                    f"Record a 45-second spoken summary of {topic}. "
                    "Include each key idea and one example. Play it back once."
                ),
            }
        )
    elif version_id == "ell":
        sections.append(
            {
                "title": "Word Review",
                "role": "summary",
                "box": "glossary",
                "body": (
                    f"Review the {topic} words. For each word, say the sentence frame again. "
                    "Keep the frames for homework."
                ),
            }
        )
    elif version_id == "teacher":
        sections.append(
            {
                "title": "Exit Ticket Plan",
                "role": "summary",
                "box": "teacher",
                "body": (
                    f"Collect one accurate sentence on {topic} plus one example. "
                    "Mark misconceptions against the verified claim list before tomorrow."
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
        if version_id == "standard":
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
