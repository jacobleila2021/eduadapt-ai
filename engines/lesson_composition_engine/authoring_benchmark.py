"""100-lesson Teacher Composition consistency benchmark.

Includes known topics and previously unseen topics.
Success = quality does not depend on whether a topic was hand-banked.

Run: python -m engines.lesson_composition_engine.authoring_benchmark
     python -m engines.lesson_composition_engine.authoring_benchmark 100
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from engines.lesson_composition_engine import compose_lesson_package
from engines.lesson_composition_engine.human_quality import (
    PUBLICATION_HEQ_THRESHOLD,
    score_clarity,
    score_diagram_usefulness,
    score_educational_flow,
    score_engagement,
    score_examples,
    score_storytelling,
)
from engines.lesson_composition_engine.recovery import instructional_text

# 100 lessons: mix of known curriculum topics + deliberately unseen titles
BENCHMARK_LESSONS: list[tuple[str, str, str, str]] = [
    ("physics", "Force and Pressure", "6-8", "A force can change the shape or motion of an object. Pressure is force on a unit area. A sharp tip has high pressure."),
    ("physics", "Light", "6-8", "Light travels in straight lines. Reflection bounces light. Refraction bends light when it enters a new medium."),
    ("physics", "Electric Circuits", "6-8", "A complete circuit lets current flow. A switch can open or close the path. A bulb lights when current passes through it."),
    ("physics", "Sound", "6-8", "Sound is produced by vibration. Sound needs a medium to travel. Louder sounds carry more energy."),
    ("physics", "Heat", "6-8", "Heat flows from hotter to cooler objects. Conduction transfers heat through solids. Insulation slows heat flow."),
    ("physics", "Magnetism", "6-8", "Magnets attract some metals. Opposite poles attract. Like poles repel."),
    ("physics", "Floating and Sinking", "5-7", "Objects denser than water sink. Objects less dense than water float. Shape can change floating behaviour."),
    ("physics", "Speed", "6-8", "Speed is distance travelled per unit time. Faster objects cover more distance in the same time. Units must stay consistent."),
    ("biology", "The Water Cycle", "4-6", "Evaporation turns liquid water into vapour. Condensation forms clouds. Precipitation returns water as rain. Collection gathers water in oceans."),
    ("biology", "Photosynthesis", "6-8", "Green plants make food using sunlight. Chlorophyll traps light. Carbon dioxide and water become glucose and oxygen."),
    ("biology", "Digestive System", "6-8", "Digestion breaks food into nutrients. The stomach mixes food with acid. The small intestine absorbs nutrients."),
    ("biology", "Respiration", "6-8", "Respiration releases energy from food. Oxygen helps cells release energy. Carbon dioxide is breathed out."),
    ("biology", "Cell Structure", "8-10", "All living things are made of cells. The nucleus controls the cell. The cell membrane controls what enters and leaves."),
    ("biology", "Human Heart", "8-10", "The heart pumps blood around the body. Arteries carry blood away from the heart. Veins return blood to the heart."),
    ("biology", "Plant Reproduction", "6-8", "Flowers help plants reproduce. Pollen transfers to the stigma. Seeds grow into new plants."),
    ("biology", "Food Chains", "5-7", "A food chain shows who eats whom. Producers make food. Consumers depend on other organisms."),
    ("biology", "Microorganisms", "6-8", "Microorganisms are living things too small to see. Some help us. Some cause disease."),
    ("chemistry", "Acids and Bases", "7-9", "Acids taste sour and turn blue litmus red. Bases feel soapy and turn red litmus blue. Neutralisation makes salt and water."),
    ("chemistry", "States of Matter", "5-7", "Solids keep shape. Liquids take the shape of a container. Gases fill the whole space available."),
    ("chemistry", "Elements and Compounds", "7-9", "An element contains one type of atom. A compound joins different atoms chemically. Mixtures can be separated physically."),
    ("chemistry", "Physical and Chemical Changes", "6-8", "A physical change does not make a new substance. A chemical change makes a new substance. Rusting is a chemical change."),
    ("chemistry", "Solutions", "6-8", "A solution is a uniform mixture. The solute dissolves in the solvent. Stirring and warming can speed dissolving."),
    ("chemistry", "Air Around Us", "5-7", "Air is a mixture of gases. Oxygen supports burning and breathing. Nitrogen makes up most of the air."),
    ("mathematics", "Fractions", "4-6", "A fraction shows parts of a whole. The numerator is the count of parts. The denominator is the total equal parts."),
    ("mathematics", "Percentages", "6-8", "A percentage is a number out of one hundred. 50 percent means half. Percentages compare parts of a whole."),
    ("mathematics", "Ratio", "6-8", "A ratio compares two quantities. The order in a ratio matters. Equivalent ratios represent the same comparison."),
    ("mathematics", "Simple Interest", "7-9", "Simple interest is calculated on the original principal. Interest equals principal times rate times time. Amount equals principal plus interest."),
    ("mathematics", "Area of a Triangle", "6-8", "Area of a triangle is half base times height. Base and height must be perpendicular. Area is measured in square units."),
    ("mathematics", "Linear Equations", "7-9", "A linear equation has variables to the first power. The same operation must be done on both sides. A solution makes both sides equal."),
    ("mathematics", "Integers", "6-7", "Integers include positive numbers, negative numbers, and zero. Adding a negative is like subtracting. Number lines show integer order."),
    ("mathematics", "Decimals", "5-7", "Decimals show parts of a whole using tenths and hundredths. Place value matters after the point. 0.5 equals one half."),
    ("mathematics", "Perimeter", "4-6", "Perimeter is the distance around a shape. Add all outer sides. Units stay length units."),
    ("geography", "Volcanoes", "6-8", "Magma rises through cracks in the crust. Lava is magma that reaches the surface. Ash and gases can erupt violently."),
    ("geography", "Earthquakes", "6-8", "Earthquakes release energy along faults. Seismic waves travel through Earth. Magnitude describes earthquake strength."),
    ("geography", "Rivers", "5-7", "Rivers flow from high land to the sea. Erosion wears rock away. Deposition drops sediment where water slows."),
    ("geography", "Climate and Weather", "5-7", "Weather is day-to-day conditions. Climate is the average pattern over many years. Latitude affects climate."),
    ("geography", "Maps and Scale", "4-6", "A map is a drawing of a place from above. Scale compares map distance to real distance. A legend explains map symbols."),
    ("geography", "Oceans", "5-7", "Oceans cover most of Earth's surface. Currents move seawater. Oceans influence climate and life."),
    ("geography", "Soil", "5-7", "Soil supports plant growth. It contains minerals, air, water, and organic matter. Erosion can remove soil."),
    ("history", "Trade Routes", "6-8", "Trade routes connected cities across land and sea. Merchants carried goods, ideas, and culture along the routes."),
    ("history", "Indus Valley Civilisation", "6-8", "Indus cities had planned streets and drainage. Trade linked the Indus with distant lands. Seals show organised administration."),
    ("history", "Ashoka", "6-8", "Ashoka ruled a large empire in ancient India. After the Kalinga war he promoted dhamma. Pillar edicts shared his messages."),
    ("history", "Freedom Struggle", "7-9", "Indians organised to end colonial rule. Non-violent protest was one important method. Independence came with partition."),
    ("history", "Medieval Kingdoms", "6-8", "Medieval kingdoms controlled land and trade. Temples and forts show power and belief. Farmers paid revenue to rulers."),
    ("history", "Villages and Cities", "6-8", "Villages often depended on farming. Cities grew around trade and administration. People specialised in different work."),
    ("english", "Clear Paragraphs", "5-7", "A paragraph develops one main idea. A topic sentence states the idea. Supporting sentences add detail and examples."),
    ("english", "Subject Verb Agreement", "5-7", "A singular subject needs a singular verb. A plural subject needs a plural verb. Agreement keeps sentences clear."),
    ("english", "Active and Passive Voice", "7-9", "Active voice puts the doer first. Passive voice puts the receiver first. Choose voice to control emphasis."),
    ("english", "Reading for Inference", "6-8", "Inference means reading between the lines. Clues in the text support an inference. Evidence must be quoted or pointed to."),
    ("english", "Narrative Writing", "5-7", "A narrative has characters, setting, and a problem. Events move in a clear order. An ending resolves the problem."),
    ("english", "Formal Letters", "6-8", "A formal letter uses polite language. It has a clear purpose. Layout includes address, date, greeting, and closing."),
    ("environmental_science", "Waste Management", "4-6", "Reduce means use less. Reuse means use again. Recycle means make new materials from used ones."),
    ("environmental_science", "Water Conservation", "4-6", "Fresh water is limited. Fixing leaks saves water. Rainwater harvesting stores water for later use."),
    ("environmental_science", "Air Pollution", "6-8", "Air pollution harms health and the environment. Vehicles and factories release pollutants. Cleaner choices reduce emissions."),
    ("environmental_science", "Forests", "5-7", "Forests give oxygen, wood, and homes for wildlife. Cutting forests without care damages soil and climate. Conservation protects forests."),
    ("environmental_science", "Biodiversity", "6-8", "Biodiversity means variety of living things. Habitats support many species. Losing habitats reduces biodiversity."),
    ("civics", "Democracy", "6-8", "In a democracy people choose their leaders. Elections must be free and fair. Rights come with responsibilities."),
    ("civics", "Fundamental Rights", "7-9", "Fundamental rights protect freedom and equality. The constitution guarantees these rights. Courts can defend rights."),
    ("civics", "Local Government", "6-8", "Local governments solve nearby problems. Panchayats work in villages. Municipalities work in towns and cities."),
    ("civics", "Rule of Law", "7-9", "Rule of law means laws apply to everyone. No one is above the law. Fair procedures protect justice."),
    ("economics", "Needs and Wants", "5-7", "Needs are essential for living. Wants are desires beyond needs. Resources are limited so choices matter."),
    ("economics", "Goods and Services", "6-8", "Goods are things we can touch. Services are useful activities people provide. Both satisfy human wants."),
    ("economics", "Money", "5-7", "Money makes exchange easier. It stores value. Prices help people decide what to buy."),
    ("computer_science", "Algorithms", "6-8", "An algorithm is a clear step-by-step solution. Steps must be in order. A good algorithm ends and gives a result."),
    ("computer_science", "Internet Safety", "5-7", "Never share passwords. Think before you click unknown links. Tell a trusted adult about online problems."),
    ("computer_science", "Data", "6-8", "Data is information we collect. Organising data makes patterns easier to see. Charts can display data clearly."),
    ("health", "Balanced Diet", "4-6", "A balanced diet includes different food groups. Proteins help growth. Fruits and vegetables provide vitamins."),
    ("health", "Hygiene", "4-6", "Washing hands removes germs. Clean water protects health. Hygiene habits reduce illness."),
    # Previously unseen / odd titles — must match quality of known topics
    ("physics", "Bicycle Brakes", "6-8", "Bicycle brakes increase friction on the wheel. Greater friction slows the bicycle. Dry clean pads grip better than greasy ones."),
    ("physics", "Kitchen Thermometers", "6-8", "A thermometer measures temperature. Liquid in a thermometer expands when heated. Accurate reading needs enough time."),
    ("biology", "Why Onions Make Eyes Water", "6-8", "Cutting an onion releases vapour that irritates the eyes. Tears help wash the irritation away. Ventilation reduces the vapour near the face."),
    ("biology", "Seed Germination on Cotton", "5-7", "Seeds need water, air, and warmth to germinate. Cotton holds moisture around the seed. A sprout shows germination has begun."),
    ("chemistry", "Rust on a Gate", "6-8", "Iron reacts with oxygen and moisture to form rust. Rust is a new substance. Painting iron slows rusting."),
    ("chemistry", "Salt in Cooking Water", "6-8", "Salt dissolves in water to make a solution. Stirring spreads salt particles. Undissolved salt settles if too much is added."),
    ("mathematics", "Sharing Laddoos Fairly", "4-6", "Equal sharing needs equal parts. A fraction names the share each person gets. The whole must be divided completely."),
    ("mathematics", "Cricket Over Fractions", "5-7", "An over has six balls. One ball is one sixth of an over. Three balls are three sixths of an over."),
    ("geography", "Fog on Winter Mornings", "5-7", "Fog forms when moist air cools near the ground. Tiny water droplets hang in the air. Sunlight often clears fog later."),
    ("geography", "School Campus Map Skills", "4-6", "A campus map uses symbols for buildings. Scale compares map distance to walking distance. A legend explains each symbol."),
    ("history", "Village Market Exchange", "6-8", "Markets let people exchange goods. Specialisation makes trade useful. Prices help buyers and sellers agree."),
    ("history", "Stone Tools and Daily Work", "5-7", "Early stone tools helped cut and scrape. Tool shape matched the job. Evidence of tools shows how people worked."),
    ("english", "Writing a Clear Recipe", "5-7", "A recipe is an ordered set of steps. Clear verbs tell the cook what to do. Missing a step can spoil the result."),
    ("english", "Spotting Bias in a Poster", "6-8", "Bias favours one side unfairly. Word choice and images can create bias. Readers should check missing viewpoints."),
    ("environmental_science", "Leaking Tap Audit", "4-6", "A leaking tap wastes fresh water. Measuring drip rate estimates loss. Fixing the washer stops the waste."),
    ("environmental_science", "Classroom Energy Waste", "5-7", "Lights left on waste electricity. Switching off unused devices saves energy. Small habits add up across a school."),
    ("civics", "Class Monitor Elections", "5-7", "Class elections practice democratic choice. Every vote should count equally. Fair rules protect trust."),
    ("civics", "School Complaint Box Fairness", "6-8", "A complaint box lets students raise problems safely. Fair handling needs listening and clear responses. Rights include being heard."),
    ("economics", "Pocket Money Choices", "5-7", "Pocket money is a limited resource. Choosing one want can mean giving up another. Planning reduces regret."),
    ("economics", "School Canteen Pricing", "6-8", "Prices signal cost and demand. A higher price may reduce how many items sell. Buyers compare value before purchasing."),
    ("computer_science", "Sorting Library Cards", "6-8", "Sorting puts items in order by a rule. Alphabetical order is one sorting rule. Clear rules make finding cards faster."),
    ("computer_science", "Strong Passwords for Email", "5-7", "A strong password is long and hard to guess. Reusing passwords increases risk. Keeping passwords private protects accounts."),
    ("health", "Packing a Healthy Tiffin", "4-6", "A healthy tiffin includes different food groups. Too many fried snacks leave less room for nutrition. Water matters as well as food."),
    ("health", "Posture While Writing", "5-7", "Good posture supports comfortable writing. A straight back reduces strain. Desk height should match the writer."),
    ("physics", "Shadows at Noon Versus Evening", "5-7", "Shadows are short near noon when the Sun is high. Shadows lengthen when the Sun is low. Light travels in straight lines past the object."),
    ("biology", "Pulse After Stair Climbing", "6-8", "Exercise makes the heart beat faster. A faster pulse moves blood more quickly. Rest returns the pulse toward normal."),
    ("chemistry", "Ice Melting in Two Cups", "5-7", "Ice melts when it gains heat. A warmer room melts ice faster. The water produced is the same substance in liquid form."),
    ("mathematics", "Comparing Two Pizza Shares", "4-6", "Equal pizza shares need equal areas. One half is larger than one third of the same pizza. Comparing fractions needs the same whole."),
    ("geography", "Why Coastal Breezes Feel Cooler", "6-8", "Water changes temperature more slowly than land. Breezes can carry cooler air from sea to shore. Local winds affect comfort."),
    ("history", "Letters Across Old Trade Roads", "6-8", "Messages and goods travelled together on trade roads. Carriers connected distant towns. Ideas spread with merchandise."),
    ("english", "Turning Notes Into One Paragraph", "5-7", "Notes are fragments. A paragraph joins related notes under one main idea. Order and connectives create flow."),
    ("environmental_science", "Plastic Bottle Journey After Disposal", "5-7", "A discarded bottle may be landfilled, littered, or recycled. Recycling makes new material from used plastic. Reducing use prevents the journey."),
]


def _uli(subject: str, topic: str, text: str) -> dict[str, Any]:
    from engines.lesson_composition_engine.teacher_composition import extract_concept_label

    claims = [{"text": s.strip()} for s in text.replace(". ", ".|").split("|") if s.strip()]
    uniq: list[dict[str, Any]] = []
    seen: set[str] = set()
    for claim in claims:
        label = extract_concept_label(claim["text"], topic, avoid=seen)
        if not label or label.lower() in seen:
            continue
        seen.add(label.lower())
        uniq.append({"name": label, "explanation": claim["text"]})
    if not uniq:
        uniq = [{"name": topic, "explanation": text[:120]}]
    return {
        "universal_profile": {
            "topic": topic,
            "subject": subject,
            "concepts": uniq,
            "claim_ledger": claims,
            "key_concepts": uniq,
        },
        "claim_ledger": claims,
    }


def _bank_leak(blob: str) -> list[str]:
    leaks = []
    for p in (
        "notice this in the real world",
        "this is an important concept",
        "this lesson explains",
        "today you will",
        "in short:",
        "hold that thought",
        "picture this idea happening at home, in the playground",
        "try explaining the same idea with a second situation",
        "helps you explain the topic clearly",
        "find a living moment with",
        "connect it to this accurate meaning",
        "two scenes — one steady meaning",
        "what familiar action with",
        "what single safe observation of",
        "in plain language,",
    ):
        if p in blob:
            leaks.append(p)
    return leaks


def _failure_why(std: Mapping[str, Any], heq: Mapping[str, Any], *, bank_covered: bool) -> list[str]:
    """Human rewrite targets — not just a numeric HEQ."""
    reasons: list[str] = []
    blob = instructional_text(std).lower()
    comps = heq.get("components") or {}
    if not bank_covered:
        reasons.append("Generic writing — topic not covered by authoring banks")
    if float(comps.get("engagement") or 0) < 90:
        reasons.append("Weak hook")
    if float(comps.get("storytelling") or 0) < 90:
        reasons.append("Missing analogy or story")
    if float(comps.get("usefulness_of_examples") or 0) < 95:
        reasons.append("Insufficient worked example")
    if "many learners" not in blob and "actually" not in blob:
        reasons.append("No misconception")
    if float(comps.get("educational_flow") or 0) < 90:
        reasons.append("Poor transition / flow")
    if "i understand" not in blob:
        reasons.append("Weak recap")
    if float(comps.get("adaptation_distinctiveness") or 0) < 100:
        reasons.append("Low adaptation uniqueness")
    if float(comps.get("claim_accuracy_alignment") or 0) < 90:
        reasons.append("Weak claim alignment in prose")
    if float(comps.get("clarity_of_explanation") or 0) < 90:
        reasons.append("Unclear explanation (sentence length or weak markers)")
    if float(comps.get("diagram_usefulness") or 0) < 85:
        reasons.append("Diagram does not teach")
    if float(comps.get("learner_confidence") or 0) < 90:
        reasons.append("Learner cannot restate the big idea")
    if float(comps.get("progression_of_concepts") or 0) < 90:
        reasons.append("Weak pedagogical progression")
    if float(comps.get("teaching_block") or 0) < 95:
        reasons.append("Repetitive prose / teaching block penalty")
    for marker in heq.get("weak_teaching_markers") or []:
        reasons.append(f"Weak teaching phrase: {marker}")
    golden = heq.get("golden_benchmark") or {}
    if golden.get("matched") and not golden.get("ok"):
        reasons.append("Shorter or less concrete than golden exemplar")
    if float(heq.get("overall") or 0) < PUBLICATION_HEQ_THRESHOLD and not reasons:
        reasons.append(f"HEQ {heq.get('overall')} below publisher floor")
    return reasons


_LEARNER_VERSIONS = (
    "standard",
    "visual",
    "auditory",
    "ell",
    "ld",
    "dyslexia",
    "adhd",
    "autism",
    "teacher",
    "parent",
)


def _teacher_voice_score(text: str) -> float:
    """Master teacher voice: stories, questions, short paragraphs, no AI stiffness."""
    low = (text or "").lower()
    score = 60.0
    if "?" in text:
        score += 10
    if any(w in low for w in ("imagine", "picture", "watch", "notice", "listen", "press", "feel", "try")):
        score += 10
    if any(w in low for w in ("like ", "just as", "the same way", "think of")):
        score += 10
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if sents:
        avg = sum(len(s.split()) for s in sents) / len(sents)
        if 8 <= avg <= 22:
            score += 10
    for stiff in ("it is important to note", "in conclusion", "as an ai", "this lesson will", "delve into"):
        if stiff in low:
            score -= 25
    return max(0.0, min(100.0, score))


def _visual_integration_score(std: Mapping[str, Any]) -> float:
    """Is the diagram explained — what it shows, why it matters, what to observe, how to read it?"""
    bodies = [
        str(s.get("body") or "")
        for s in (std.get("sections") or [])
        if isinstance(s, dict) and str(s.get("role")) in {"visual", "practice_question"}
    ]
    blob = " ".join(bodies).lower()
    if not blob:
        return 20.0
    score = 40.0
    if any(w in blob for w in ("shows", "lays out", "picture", "represents")):
        score += 15
    if any(w in blob for w in ("why", "matters", "because", "cannot")):
        score += 15
    if any(w in blob for w in ("look for", "watch", "changes", "point to", "finger", "trace")):
        score += 15
    if any(w in blob for w in ("arrow", "order", "stage", "label", "leads to")):
        score += 15
    return min(100.0, score)


def _adaptation_scores(adaptations: Mapping[str, Any], heq: Mapping[str, Any]) -> dict[str, Any]:
    """Score every adaptation separately — none may ride on the mainstream version."""
    sim = (heq.get("similarity") or {}).get("vs_mainstream") or {}
    advantages = {
        str(row.get("version_id")): row
        for row in ((heq.get("adaptation_advantages") or {}).get("by_adaptation") or [])
    }
    out: dict[str, Any] = {}
    for version in _LEARNER_VERSIONS:
        ad = adaptations.get(version)
        if not isinstance(ad, dict) or not ad.get("sections"):
            continue
        text = instructional_text(ad)
        similarity = float(sim.get(version) or 0.0)
        row = advantages.get(version) or {}
        out[version] = {
            "clarity": round(score_clarity(ad), 1),
            "engagement": round(score_engagement(ad), 1),
            "storytelling": round(score_storytelling(ad), 1),
            "examples": round(score_examples(ad), 1),
            "flow": round(score_educational_flow(ad), 1),
            "teacher_voice": round(_teacher_voice_score(text), 1),
            "distinctiveness": round(100.0 * (1.0 - similarity), 1) if version != "standard" else 100.0,
            "independent": bool(row.get("ok")) if version != "standard" else True,
            "advantage": str(row.get("advantage") or ("mainstream classroom arc" if version == "standard" else "")),
            "words": len(text.split()),
        }
    return out


def _teacher_would_use(std: Mapping[str, Any], heq: Mapping[str, Any]) -> dict[str, Any]:
    blob = instructional_text(std).lower()
    leaks = _bank_leak(blob)
    bank_covered = bool(((std.get("lce") or {}).get("bank_covered")))
    checks = {
        "no_template_leaks": not leaks,
        "has_curiosity_or_story": any(
            p in blob for p in ("have you", "why ", "what ", "watch ", "follow ", "how ", "if you", "look for", "notice", "press", "feel")
        ),
        "has_two_examples": blob.count("example") + blob.count("picture") + blob.count("situation") + blob.count("compare") >= 2
        or "second" in blob,
        "has_misconception": "many learners" in blob or "actually" in blob,
        "has_confidence_close": "i understand" in blob,
        "diagram_referenced": "diagram" in blob,
        "bank_covered": bank_covered,
        "human_classroom_ready": bool((heq.get("human_verdict") or {}).get("classroom_ready")),
        "heq_at_threshold": float(heq.get("overall") or 0) >= PUBLICATION_HEQ_THRESHOLD,
        "composition_ok": not bool(((std.get("lce") or {}).get("composition_failed"))),
    }
    why = _failure_why(std, heq, bank_covered=bank_covered) if not all(checks.values()) else []
    return {"would_use_without_editing": all(checks.values()), "checks": checks, "leaks": leaks, "why": why}


def run_benchmark(limit: int | None = None) -> dict[str, Any]:
    rows = []
    weaknesses: dict[str, int] = {}
    items = BENCHMARK_LESSONS if limit is None else BENCHMARK_LESSONS[: max(1, limit)]
    known_mark = 68  # first chunk treated as "known"; rest include unseen titles
    for idx, (subject, topic, grade, text) in enumerate(items):
        pkg = compose_lesson_package(_uli(subject, topic, text), topic_hint=topic)
        adaptations = pkg.get("adaptations") or {}
        std = adaptations.get("standard") or {}
        heq = pkg.get("heq") or pkg.get("eqs") or {}
        judge = _teacher_would_use(std, heq)
        for key, ok in (judge.get("checks") or {}).items():
            if not ok:
                weaknesses[key] = weaknesses.get(key, 0) + 1
        comps = heq.get("components") or {}
        ad_scores = _adaptation_scores(adaptations, heq)
        std_text = instructional_text(std)
        rows.append(
            {
                "subject": subject,
                "topic": topic,
                "grade_band": grade,
                "unseen_topic": idx >= known_mark,
                "heq": heq.get("overall"),
                "publish": float(heq.get("overall") or 0) >= PUBLICATION_HEQ_THRESHOLD,
                "dimensions": {
                    "claim_alignment": comps.get("claim_accuracy_alignment"),
                    "educational_flow": comps.get("educational_flow"),
                    "teacher_voice": round(_teacher_voice_score(std_text), 1),
                    "visual_integration": round(_visual_integration_score(std), 1),
                    "vocabulary_quality": comps.get("vocabulary_learning"),
                    "diagram_integration": comps.get("diagram_usefulness"),
                    "adaptation_distinctiveness": comps.get("adaptation_distinctiveness"),
                },
                "adaptation_scores": ad_scores,
                "min_adaptation_distinctiveness": round(
                    min(
                        [float(v.get("distinctiveness") or 0) for v in ad_scores.values()] or [0.0]
                    ),
                    1,
                ),
                "all_adaptations_independent": all(
                    bool(v.get("independent")) for v in ad_scores.values()
                ),
                "section_flow": [
                    str(s.get("role") or "")
                    for s in (std.get("sections") or [])
                    if isinstance(s, dict)
                ],
                "publication_ready": bool((pkg.get("pqle") or {}).get("publication_ready")),
                "classroom_ready": bool((heq.get("human_verdict") or {}).get("classroom_ready")),
                "teacher_would_use": judge.get("would_use_without_editing"),
                "teacher_checks": judge.get("checks"),
                "template_leaks": judge.get("leaks") or [],
                "why": judge.get("why") or [],
                "composition_failed": bool(((std.get("lce") or {}).get("composition_failed"))),
                "bank_covered": bool(((std.get("lce") or {}).get("bank_covered"))),
                "no_template_banks": bool(((std.get("lce") or {}).get("no_generic_fallback"))),
                "reject_reasons": pkg.get("reject_reasons") or [],
                "excerpt_hook": str(((std.get("sections") or [{}])[0]).get("body") or "")[:220],
                "big_idea": str(std.get("big_idea") or "")[:220],
            }
        )

    n = len(rows)
    known = [r for r in rows if not r["unseen_topic"]]
    unseen = [r for r in rows if r["unseen_topic"]]
    why_counts: dict[str, int] = {}
    for r in rows:
        for w in r.get("why") or []:
            why_counts[w] = why_counts.get(w, 0) + 1

    def _avg(rs: list[dict[str, Any]]) -> float:
        vals = [float(r["heq"] or 0) for r in rs]
        return round(sum(vals) / max(len(vals), 1), 2)

    def _dim_avg(key: str) -> float:
        vals = [float((r.get("dimensions") or {}).get(key) or 0) for r in rows]
        return round(sum(vals) / max(len(vals), 1), 2)

    heq_pass = sum(1 for r in rows if (r["heq"] or 0) >= PUBLICATION_HEQ_THRESHOLD)
    return {
        "schema": "alora.teacher_composition_benchmark.v3",
        "dimension_averages": {
            key: _dim_avg(key)
            for key in (
                "claim_alignment",
                "educational_flow",
                "teacher_voice",
                "visual_integration",
                "vocabulary_quality",
                "diagram_integration",
                "adaptation_distinctiveness",
            )
        },
        "publishable_count": sum(1 for r in rows if r.get("publish")),
        "all_adaptations_independent_count": sum(
            1 for r in rows if r.get("all_adaptations_independent")
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "count": n,
        "heq_threshold": PUBLICATION_HEQ_THRESHOLD,
        "heq_pass_rate": round(100.0 * heq_pass / max(n, 1), 1),
        "target_heq_pass_rate": 95.0,
        "teacher_use_count": sum(1 for r in rows if r["teacher_would_use"]),
        "classroom_ready_count": sum(1 for r in rows if r["classroom_ready"]),
        "publication_ready_count": sum(1 for r in rows if r["publication_ready"]),
        "heq_pass_count": heq_pass,
        "template_leak_count": sum(1 for r in rows if r["template_leaks"]),
        "composition_fail_count": sum(1 for r in rows if r["composition_failed"]),
        "bank_coverage_count": sum(1 for r in rows if r["bank_covered"]),
        "known_avg_heq": _avg(known),
        "unseen_avg_heq": _avg(unseen),
        "known_unseen_gap": round(abs(_avg(known) - _avg(unseen)), 2),
        "consistency_ok": abs(_avg(known) - _avg(unseen)) <= 5.0 if known and unseen else False,
        "recovery_complete": n > 0
        and heq_pass >= int(0.95 * n)
        and all(not r["template_leaks"] for r in rows),
        "recurring_weaknesses": sorted(weaknesses.items(), key=lambda kv: -kv[1]),
        "recurring_why": sorted(why_counts.items(), key=lambda kv: -kv[1]),
        "lessons": rows,
    }


def write_benchmark(limit: int | None = None, out_dir: Path | None = None) -> Path:
    report = run_benchmark(limit=limit)
    root = out_dir or Path("forensics") / "runs" / f"authoring_benchmark_{report['generated_at']}"
    root.mkdir(parents=True, exist_ok=True)
    (root / "AUTHORING_BENCHMARK.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Teacher Composition Benchmark",
        "",
        f"Generated: {report['generated_at']}",
        f"Lessons: {report['count']}",
        f"Teacher would use: {report['teacher_use_count']}/{report['count']}",
        f"Classroom ready: {report['classroom_ready_count']}/{report['count']}",
        f"HEQ ≥ {report['heq_threshold']}: {report['heq_pass_count']}/{report['count']} ({report.get('heq_pass_rate')}%; target {report.get('target_heq_pass_rate')}%)",
        f"Template leaks: {report['template_leak_count']}",
        f"Bank coverage: {report.get('bank_coverage_count')}/{report['count']}",
        f"Known avg HEQ: {report['known_avg_heq']} | Unseen avg HEQ: {report['unseen_avg_heq']} | Gap: {report['known_unseen_gap']}",
        f"Consistency OK (|known−unseen|≤5): {report['consistency_ok']}",
        f"Recovery complete (≥95% HEQ pass): {report['recovery_complete']}",
        f"Publishable (HEQ ≥ {report['heq_threshold']}): {report.get('publishable_count')}/{report['count']}",
        f"All adaptations independently authored: {report.get('all_adaptations_independent_count')}/{report['count']}",
        "",
        "## Dimension averages",
    ]
    for key, value in (report.get("dimension_averages") or {}).items():
        lines.append(f"- {key.replace('_', ' ')}: {value}")
    lines += ["", "## Recurring WHY (rewrite targets)"]
    for key, n in (report.get("recurring_why") or [])[:12]:
        lines.append(f"- {key}: {n}")
    lines.extend(
        [
            "",
            "## Recurring weaknesses",
        ]
    )
    for name, count in report.get("recurring_weaknesses") or []:
        lines.append(f"- {name}: {count}")
    lines += [
        "",
        "| Topic | Unseen | HEQ | Publish | Claim align | Flow | Voice | Visual | Vocab | Diagram | Min adapt distinct | Why |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in report["lessons"]:
        why = "; ".join(r.get("why") or []) or "—"
        d = r.get("dimensions") or {}
        lines.append(
            f"| {r['topic']} | {r['unseen_topic']} | {r['heq']} | {r.get('publish')} | "
            f"{d.get('claim_alignment')} | {d.get('educational_flow')} | {d.get('teacher_voice')} | "
            f"{d.get('visual_integration')} | {d.get('vocabulary_quality')} | {d.get('diagram_integration')} | "
            f"{r.get('min_adaptation_distinctiveness')} | {why.replace('|', '/')} |"
        )
    lines += ["", "## Adaptation scores (first 5 lessons)", ""]
    for r in report["lessons"][:5]:
        lines.append(f"### {r['topic']}")
        lines.append("")
        lines.append("| Version | Clarity | Engagement | Story | Examples | Voice | Distinct | Independent | Advantage |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for version, s in (r.get("adaptation_scores") or {}).items():
            lines.append(
                f"| {version} | {s.get('clarity')} | {s.get('engagement')} | {s.get('storytelling')} | "
                f"{s.get('examples')} | {s.get('teacher_voice')} | {s.get('distinctiveness')} | "
                f"{s.get('independent')} | {s.get('advantage') or '—'} |"
            )
        lines.append("")
    (root / "AUTHORING_BENCHMARK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return root


def main() -> None:
    import sys

    limit = 100
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        limit = int(sys.argv[1])
    path = write_benchmark(limit=limit)
    print(f"AUTHORING_BENCHMARK_WRITTEN:{path}")


if __name__ == "__main__":
    main()
