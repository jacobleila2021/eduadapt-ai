"""Benchmark corpus — subjects × curricula × adaptations (specs + sample ULI)."""

from __future__ import annotations

from typing import Any

from uevb.constants import ADAPTATIONS, CORPUS_SEEDS, CURRICULA, SUBJECTS


def _rich_claims(subject: str, topic: str, concept: str) -> list[str]:
    """Classroom-usable claims for product corpus — prefer teaching claims, never filler nodes."""
    seed_claims = {
        "Fractions": [
            f"{concept} name the same share of a whole with different numerals.",
            "A fraction shows equal parts of a whole.",
            "Compare fractions only when the wholes match or amounts are clear.",
        ],
        "Linear Equations": [
            f"{concept} keeps both sides of an equation balanced.",
            "The same operation on both sides preserves equality.",
            "A solution is the value that makes both sides true.",
        ],
        "Force and Pressure": [
            f"{concept} is force on a unit area.",
            "A force can change the shape or motion of an object.",
            "A sharp tip concentrates force and raises pressure.",
        ],
        "Light": [
            f"{concept} bounces light from a surface.",
            "Light travels in straight lines.",
            "Refraction bends light when it enters a new medium.",
        ],
        "Chemical Reactions": [
            f"{concept} keeps atom counts equal on both sides.",
            "Reactants change into products during a reaction.",
            "Mass is conserved when a reaction is balanced.",
        ],
        "Acids and Bases": [
            f"{concept} measures how acidic or basic a solution is.",
            "Acids turn blue litmus red.",
            "Bases turn red litmus blue.",
        ],
        "The Water Cycle": [
            f"{concept} turns liquid water into vapour.",
            "Condensation forms clouds from cooled vapour.",
            "Precipitation returns water as rain, snow, or hail.",
        ],
        "Cell Structure": [
            f"The {concept.lower()} controls the cell.",
            "All living things are made of cells.",
            "The cell membrane controls what enters and leaves.",
        ],
        "Waste Management": [
            f"{concept} separates waste so materials can be reused or disposed safely.",
            "Biodegradable and non-biodegradable waste need different futures.",
            "Reducing waste at source is the first kindness to the environment.",
        ],
        "Ecosystems": [
            f"A {concept.lower()} shows who eats whom in a habitat.",
            "Producers make food; consumers depend on other organisms.",
            "Every living thing in an ecosystem is linked by energy flow.",
        ],
        "Active and Passive Voice": [
            "Active voice names the doer first.",
            "Passive voice can spotlight the receiver or the process.",
            "Choose voice to match what the sentence must emphasise.",
        ],
        "Reading Comprehension": [
            f"{concept} means reading beyond the stated words.",
            "Evidence in the text supports a careful conclusion.",
            "A strong answer quotes or points to the supporting line.",
        ],
        "The Freedom Struggle": [
            f"{concept} withdrew cooperation from unjust rule.",
            "Many people joined the struggle in different ways.",
            "Non-violent protest changed public opinion and power.",
        ],
        "Ancient Civilisations": [
            f"{concept} shows planned cities and shared culture.",
            "Archaeology recovers how people lived long ago.",
            "Trade and farming supported early urban life.",
        ],
        "Climate": [
            f"The {concept.lower()} brings seasonal rains to much of India.",
            "Climate is the long-term pattern of weather in a place.",
            "Latitude, altitude, and nearby seas shape climate.",
        ],
        "Resources": [
            f"{concept} can be replaced naturally over time.",
            "Careful use keeps resources available for the future.",
            "People, technology, and nature together decide resource value.",
        ],
        "Democracy": [
            f"{concept} protect dignity and equality under the law.",
            "Citizens choose representatives and can question power.",
            "Rights come with duties that keep democracy healthy.",
        ],
        "Local Government": [
            f"The {concept.lower()} is local self-government in villages.",
            "Local bodies solve nearby problems with local knowledge.",
            "Participation makes local decisions fairer.",
        ],
        "Demand and Supply": [
            f"{concept} is where demand and supply meet.",
            "Price tends to rise when demand outruns supply.",
            "Markets adjust as buyers and sellers respond to price.",
        ],
        "Money and Banking": [
            f"{concept} lets people borrow money and repay later.",
            "Banks keep deposits safe and lend to others.",
            "Money makes exchange easier than barter.",
        ],
        "Forms of Business": [
            f"A {concept.lower()} shares ownership and responsibility.",
            "Different forms of business suit different risks and sizes.",
            "Clear agreements reduce conflict among owners.",
        ],
        "Marketing": [
            f"The {concept.lower()} balances product, price, place, and promotion.",
            "Marketing matches what customers need with what firms offer.",
            "Honest information builds lasting trust.",
        ],
        "Algorithms": [
            f"{concept} show steps of a process in order.",
            "An algorithm is a clear sequence of instructions.",
            "Good algorithms are precise, finite, and effective.",
        ],
        "Python Basics": [
            f"{concept} store values that a program can reuse.",
            "Programs follow instructions step by step.",
            "Clear names make code easier to read and fix.",
        ],
        "Greetings": [
            f"{concept} shows respect in speech.",
            "Greetings change with age, place, and relationship.",
            "Polite openings make conversation easier.",
        ],
        "Family Vocabulary": [
            f"{concept} are related words across languages.",
            "Family words name people you live with and love.",
            "Accurate words keep relationships clear.",
        ],
    }
    claims = list(seed_claims.get(topic) or [])
    if not claims:
        claims = [
            f"{concept} is a precise idea in {topic}.",
            f"Learners explain {concept.lower()} with one real example from {topic}.",
            f"Keep neighbouring ideas out of the definition of {concept.lower()}.",
        ]
    return claims[:4]


def _concept_names(topic: str, concept: str, claims: list[str]) -> list[str]:
    """Teachable noun labels for diagrams — never example fragments or 'Evidence'."""
    topic_defaults = {
        "Fractions": [concept, "Equal parts", "Same whole"],
        "Linear Equations": [concept, "Balance", "Solution"],
        "Force and Pressure": [concept, "Force", "Sharp tip"],
        "Light": [concept, "Straight path", "Refraction"],
        "Chemical Reactions": [concept, "Reactants", "Products"],
        "Acids and Bases": [concept, "Litmus", "Neutralisation"],
        "The Water Cycle": [concept, "Condensation", "Precipitation"],
        "Cell Structure": [concept, "Cell membrane", "Living units"],
        "Waste Management": [concept, "Biodegradable waste", "Reduce first"],
        "Ecosystems": [concept, "Producers", "Consumers"],
        "Active and Passive Voice": ["Active voice", "Passive voice", "Emphasis"],
        "Reading Comprehension": [concept, "Text evidence", "Conclusion"],
        "The Freedom Struggle": [concept, "Public opinion", "Participation"],
        "Ancient Civilisations": [concept, "Archaeology", "Urban life"],
        "Climate": [concept, "Long-term pattern", "Latitude"],
        "Resources": [concept, "Careful use", "Future needs"],
        "Democracy": [concept, "Representation", "Duties"],
        "Local Government": [concept, "Local problems", "Participation"],
        "Demand and Supply": [concept, "Price", "Markets"],
        "Money and Banking": [concept, "Deposits", "Exchange"],
        "Forms of Business": [concept, "Ownership", "Agreements"],
        "Marketing": [concept, "Customer need", "Trust"],
        "Algorithms": [concept, "Instructions", "Precision"],
        "Python Basics": [concept, "Instructions", "Readable names"],
        "Greetings": [concept, "Respect", "Conversation"],
        "Family Vocabulary": [concept, "Family words", "Clear naming"],
    }
    names = list(topic_defaults.get(topic) or [concept, f"{topic} idea", f"{concept} in practice"])
    # Keep unique, short labels
    out: list[str] = []
    for n in names:
        label = str(n).strip()
        if label and label.lower() not in {x.lower() for x in out}:
            out.append(label)
        if len(out) >= 3:
            break
    return out[:3]


def build_sample_uli(
    *,
    subject: str,
    topic: str,
    concept: str,
    curriculum: str = "cbse",
) -> dict[str, Any]:
    """Deterministic ULI-shaped payload for corpus composition — product-ready claims."""
    claims = _rich_claims(subject, topic, concept)
    names = _concept_names(topic, concept, claims)
    example = claims[-1] if claims else f"A real example helps explain {concept.lower()}."
    return {
        "universal_profile": {
            "topic": topic,
            "subject": subject,
            "curriculum": curriculum,
            "concepts": [
                {"name": names[i], "explanation": claims[i] if i < len(claims) else claims[0]}
                for i in range(len(names))
            ],
            "claim_ledger": [{"text": c} for c in claims],
            "vocabulary": [
                {"term": names[i], "definition": claims[i] if i < len(claims) else claims[0]}
                for i in range(len(names))
            ]
            + [
                {"term": "Example", "definition": "A real situation that shows the idea."},
            ],
            "learning_objectives": [f"Explain {concept} within {topic} using a real example."],
            "examples": [{"text": example}],
            "misconceptions": [
                {
                    "label": f"{concept} is often confused with a related everyday word",
                    "correction": f"Keep the lesson definition of {concept} precise and use a real example.",
                }
            ],
            "prerequisites": [{"text": f"Know everyday language related to {topic}."}],
        }
    }


def build_sample_sif(*, subject: str, topic: str, concept: str) -> dict[str, Any]:
    return {
        "subject_key": subject if subject != "business_studies" else "business",
        "analysis": {
            "misconceptions": [
                {
                    "label": f"Learners mix up {concept} with a nearby idea",
                    "correction": f"Separate {concept} using lesson evidence.",
                }
            ],
            "assessment_hints": [
                {"prompt": f"Explain {concept} in your own words."},
                {"prompt": f"Give one real-life example from {topic}."},
                {"prompt": f"State one mistake to avoid about {concept}."},
                {"prompt": f"Connect {concept} to another idea in {topic}."},
            ],
            "prerequisites": [{"text": f"Basic familiarity with {topic}"}],
        },
    }


def build_sample_uvie(*, topic: str, concept: str) -> dict[str, Any]:
    return {
        "preferred_visuals": [
            {
                "caption": f"{topic} organiser showing {concept}",
                "kind": "flowchart",
                "visual_id": f"uvie_{concept.lower().replace(' ', '_')}",
            }
        ],
        "visuals": [],
    }


def iter_corpus_specs(
    *,
    subjects: tuple[str, ...] | None = None,
    curricula: tuple[str, ...] | None = None,
    max_topics_per_subject: int = 2,
) -> list[dict[str, Any]]:
    """Expand the full subject × curriculum matrix (topic seeds × curricula)."""
    subjects = subjects or SUBJECTS
    curricula = curricula or CURRICULA
    specs: list[dict[str, Any]] = []
    for subject in subjects:
        seeds = (CORPUS_SEEDS.get(subject) or [{"topic": subject.title(), "concept": "Core idea"}])[
            :max_topics_per_subject
        ]
        for seed in seeds:
            for curriculum in curricula:
                specs.append(
                    {
                        "subject": subject,
                        "curriculum": curriculum,
                        "topic": seed["topic"],
                        "concept": seed["concept"],
                        "adaptations": list(ADAPTATIONS),
                        "corpus_id": f"{subject}.{curriculum}.{seed['topic']}".replace(" ", "_").lower(),
                    }
                )
    return specs


def corpus_size(
    *,
    subjects: tuple[str, ...] | None = None,
    curricula: tuple[str, ...] | None = None,
    max_topics_per_subject: int = 2,
) -> dict[str, int]:
    specs = iter_corpus_specs(
        subjects=subjects, curricula=curricula, max_topics_per_subject=max_topics_per_subject
    )
    return {
        "lesson_specs": len(specs),
        "subjects": len(subjects or SUBJECTS),
        "curricula": len(curricula or CURRICULA),
        "adaptations_per_lesson": len(ADAPTATIONS),
        "adaptation_pages": len(specs) * len(ADAPTATIONS),
    }
