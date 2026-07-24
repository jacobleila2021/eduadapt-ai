"""One-shot expander for golden lesson library (RC1 product refinement)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "golden_lessons"
ROOT.mkdir(parents=True, exist_ok=True)

ROLES = [
    "hook",
    "visual",
    "concept",
    "simple_explanation",
    "real_life_example",
    "worked_example",
    "practice_question",
    "summary",
    "reflection",
    "application",
]


def cream_svg(title: str, labels: list[str], width: int = 440, height: int = 150) -> str:
    n = max(1, len(labels))
    box_w = min(110, (width - 40) // n - 10)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        '<rect width="100%" height="100%" fill="#FFF9EE"/>',
        f'<text x="{width // 2}" y="28" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="16" fill="#0B2E59">{title}</text>',
    ]
    colors = ["#e6f7f8", "#e3f2fd", "#ecfdf5", "#fff7ed", "#fdf2f8"]
    gap = 12
    total = n * box_w + (n - 1) * gap
    x0 = (width - total) // 2
    y = 55
    for i, lab in enumerate(labels):
        x = x0 + i * (box_w + gap)
        parts.append(
            f'<rect x="{x}" y="{y}" width="{box_w}" height="48" rx="14" '
            f'fill="{colors[i % len(colors)]}" stroke="#0B2E59"/>'
        )
        parts.append(
            f'<text x="{x + box_w // 2}" y="{y + 30}" text-anchor="middle" '
            f'font-family="Georgia, serif" font-size="12" fill="#0B2E59">{lab}</text>'
        )
        if i < n - 1:
            parts.append(
                f'<line x1="{x + box_w}" y1="{y + 24}" x2="{x + box_w + gap}" y2="{y + 24}" '
                f'stroke="#008C95" stroke-width="2"/>'
            )
    parts.append("</svg>")
    return "".join(parts)


def pack(big: str, sections: list[dict], topic: str, labels: list[str], practice: str) -> dict:
    svg = cream_svg(topic, labels)
    return {
        "big_idea": big,
        "sections": sections,
        "diagram_package": {
            "title": topic,
            "caption": " → ".join(labels),
            "explanation": f"This diagram teaches how the ideas in {topic} connect.",
            "practice_question": practice,
            "callouts": [f"Label: {label}" for label in labels],
        },
        "svg_diagram": svg,
        "flowchart_svg": svg,
    }


def add(
    items: list[dict],
    *,
    gid: str,
    subject: str,
    topic: str,
    big: str,
    secs: list[dict],
    labels: list[str],
    practice: str,
    stage: str = "middle",
) -> None:
    items.append(
        {
            "id": gid,
            "subject": subject,
            "topic": topic,
            "stage": stage,
            "pqi_target": 98,
            "min_sections": 10,
            "min_vocab_cards": 5,
            "required_roles": list(ROLES),
            "educational_personality": (
                "exceptional classroom teacher; cream textbook; diagram teaches"
            ),
            "lesson": pack(big, secs, topic, labels, practice),
        }
    )


def main() -> None:
    items: list[dict] = []
    add(
        items,
        gid="biology_photosynthesis",
        subject="biology",
        topic="Photosynthesis",
        big=(
            "Green plants make food using light, water, and carbon dioxide. "
            "Photosynthesis turns those inputs into sugar and oxygen."
        ),
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "Have you ever wondered how a quiet green leaf can feed a whole plant? The answer is photosynthesis."},
            {"title": "Using the Diagram", "role": "visual", "body": "Trace Light → Water + CO₂ → Sugar + Oxygen. The diagram shows the recipe a leaf follows."},
            {"title": "Concept: Photosynthesis", "role": "concept", "body": "Photosynthesis is the process plants use to make food. Chlorophyll in leaves captures light energy."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "In simple words: plants use sunlight to cook sugar from water and carbon dioxide, and they release oxygen."},
            {"title": "In Real Life", "role": "real_life_example", "body": "A sunny windowsill plant grows faster than one in a dark cupboard because more light means more photosynthesis."},
            {"title": "Worked Example", "role": "worked_example", "body": "If light is blocked with black paper on one leaf, that patch cannot make food well. Compare it with an uncovered leaf."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Oxygen on the diagram and explain why forests help the air we breathe."},
            {"title": "Lesson Summary", "role": "summary", "body": "Photosynthesis needs light, water, and carbon dioxide. It makes sugar for the plant and oxygen for us."},
            {"title": "Think About It", "role": "reflection", "body": "Where have you seen green plants thriving in strong light? Write one sentence linking that to today's idea."},
            {"title": "Apply Your Learning", "role": "application", "body": "Design a fair classroom test that changes only one thing — light, water, or air — and predict what happens."},
        ],
        labels=["Light", "Water+CO2", "Sugar", "Oxygen"],
        practice="Point to Sugar and explain what the plant gains from photosynthesis.",
    )
    add(
        items,
        gid="physics_electric_circuits",
        subject="physics",
        topic="Electric Circuits",
        big="An electric circuit is a complete path for current. A break anywhere stops the flow.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "Why does a torch stay dark when one wire is loose? Electricity needs a complete loop."},
            {"title": "Using the Diagram", "role": "visual", "body": "Follow Cell → Switch → Bulb → Wire back to the cell. If any link is open, the bulb stays off."},
            {"title": "Concept: Circuit", "role": "concept", "body": "A circuit is a closed path that lets electric current travel from the power source through components and back again."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "Think of current like a bicycle on a track: it only keeps going if the track is unbroken."},
            {"title": "In Real Life", "role": "real_life_example", "body": "When fairy lights fail because one bulb is out, that broken bulb opens the series path."},
            {"title": "Worked Example", "role": "worked_example", "body": "Draw a cell, switch, and bulb in a loop. Open the switch and predict: current stops, so the bulb goes dark."},
            {"title": "Try This", "role": "practice_question", "body": "Point to the switch on the diagram and explain what open and closed mean for the bulb."},
            {"title": "Lesson Summary", "role": "summary", "body": "Current needs a complete circuit. A cell supplies energy; wires carry it; a switch can open or close the path."},
            {"title": "Think About It", "role": "reflection", "body": "Where do you use a switch at home? Explain how it changes the circuit."},
            {"title": "Apply Your Learning", "role": "application", "body": "Build a safe paper model of a circuit and label each part with its job."},
        ],
        labels=["Cell", "Switch", "Bulb", "Wire"],
        practice="Point to Cell and explain what it provides in the circuit.",
    )
    add(
        items,
        gid="physics_light",
        subject="physics",
        topic="Light",
        big="Light travels in straight lines. Shadows form when an opaque object blocks the path.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "Why is your shadow long in the evening and short at noon? Light and blockers tell the story."},
            {"title": "Using the Diagram", "role": "visual", "body": "Trace Source → Object → Shadow. The diagram shows light blocked and darkness on the other side."},
            {"title": "Concept: Light Path", "role": "concept", "body": "Light travels in straight lines called rays. Opaque objects stop those rays and cast shadows."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "Light goes straight. When something solid stands in the way, a shadow appears behind it."},
            {"title": "In Real Life", "role": "real_life_example", "body": "A tree's shadow on a playground stretches as the sun lowers because the light arrives at a shallower angle."},
            {"title": "Worked Example", "role": "worked_example", "body": "Hold a pencil in front of a torch. Move the pencil closer to the wall and watch the shadow grow."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Shadow on the diagram and explain why it appears opposite the light source."},
            {"title": "Lesson Summary", "role": "summary", "body": "Light travels straight. Opaque objects block light and create shadows we can predict."},
            {"title": "Think About It", "role": "reflection", "body": "When is your shadow longest outdoors? Link that to the sun's position."},
            {"title": "Apply Your Learning", "role": "application", "body": "Design a shadow-puppet scene that uses straight-line light to make clear shapes."},
        ],
        labels=["Source", "Object", "Shadow"],
        practice="Point to Source and explain how moving it changes the shadow.",
    )
    add(
        items,
        gid="biology_digestive_system",
        subject="biology",
        topic="Digestive System",
        big="Digestion breaks food into smaller pieces the body can absorb. Each organ has a clear job.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "How does a bite of bread become energy your body can use? Digestion is the journey."},
            {"title": "Using the Diagram", "role": "visual", "body": "Follow Mouth → Stomach → Small intestine. Each stop changes food so nutrients can enter the blood."},
            {"title": "Concept: Digestion", "role": "concept", "body": "Digestion is the breakdown of food. Mechanical chewing and chemical juices work together."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "Your body takes big food pieces and turns them into tiny nutrients it can absorb."},
            {"title": "In Real Life", "role": "real_life_example", "body": "Chewing a chapati thoroughly helps digestion start in the mouth before the stomach continues the work."},
            {"title": "Worked Example", "role": "worked_example", "body": "Track a rice grain: teeth crush it, saliva moistens it, the stomach mixes it, and the small intestine absorbs nutrients."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Small intestine and explain why absorption matters."},
            {"title": "Lesson Summary", "role": "summary", "body": "Digestion is a team effort. Food is broken down step by step so nutrients can feed your cells."},
            {"title": "Think About It", "role": "reflection", "body": "Why do doctors ask you to chew slowly? Connect that advice to today's lesson."},
            {"title": "Apply Your Learning", "role": "application", "body": "Make a labelled journey map of one meal through the digestive system."},
        ],
        labels=["Mouth", "Stomach", "Intestine"],
        practice="Point to Mouth and explain two ways digestion begins there.",
    )
    add(
        items,
        gid="geography_volcanoes",
        subject="geography",
        topic="Volcanoes",
        big="A volcano forms where molten rock rises to Earth's surface. Eruptions reshape land over time.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "How can a mountain suddenly pour glowing rock? Magma under pressure finds a way up."},
            {"title": "Using the Diagram", "role": "visual", "body": "Trace Magma chamber → Vent → Lava. The diagram shows the path from inside Earth to the surface."},
            {"title": "Concept: Volcano", "role": "concept", "body": "A volcano is an opening in Earth's crust that lets magma, gas, and ash escape."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "Hot melted rock rises. When it reaches the surface, we call it lava."},
            {"title": "In Real Life", "role": "real_life_example", "body": "Ash from eruptions can travel far on the wind, affecting farms and flights hundreds of kilometres away."},
            {"title": "Worked Example", "role": "worked_example", "body": "Compare a quiet lava flow with an explosive ash column: gas content and magma thickness change the style."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Vent and explain what travels through it during an eruption."},
            {"title": "Lesson Summary", "role": "summary", "body": "Volcanoes release magma and gas. They build and reshape landscapes while creating hazards people must respect."},
            {"title": "Think About It", "role": "reflection", "body": "Why might people still live near volcanoes despite the risks?"},
            {"title": "Apply Your Learning", "role": "application", "body": "Draw a safety poster that uses the diagram labels to warn travellers."},
        ],
        labels=["Magma", "Vent", "Lava"],
        practice="Point to Magma and explain how it differs from lava.",
    )
    add(
        items,
        gid="chemistry_acids_bases",
        subject="chemistry",
        topic="Acids and Bases",
        big="Acids and bases have different properties. Indicators help us classify them safely.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "Why does lemon juice taste sharp while soap feels slippery? Acids and bases behave differently."},
            {"title": "Using the Diagram", "role": "visual", "body": "See Acid → Indicator → Base. The diagram shows how an indicator reports what you have."},
            {"title": "Concept: Acids and Bases", "role": "concept", "body": "Acids often taste sour and can turn blue litmus red. Bases often feel soapy and can turn red litmus blue."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "An indicator is like a traffic light for chemistry — its colour tells you acid or base."},
            {"title": "In Real Life", "role": "real_life_example", "body": "Vinegar on chips is acidic; baking soda used in cleaning is a base."},
            {"title": "Worked Example", "role": "worked_example", "body": "Dip litmus in lemon water: blue litmus turns red, so the sample behaves as an acid."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Indicator and explain what a colour change tells you."},
            {"title": "Lesson Summary", "role": "summary", "body": "Acids and bases have different properties. Indicators help us identify them without tasting unknown chemicals."},
            {"title": "Think About It", "role": "reflection", "body": "Why is tasting laboratory chemicals never acceptable, even if lemons are safe at home?"},
            {"title": "Apply Your Learning", "role": "application", "body": "Plan a safe indicator test using kitchen samples a teacher approves."},
        ],
        labels=["Acid", "Indicator", "Base"],
        practice="Point to Acid and give one safe everyday example.",
    )
    add(
        items,
        gid="mathematics_percentages",
        subject="mathematics",
        topic="Percentages",
        big="A percentage is a special fraction out of 100. It lets us compare parts of different wholes fairly.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "If one test scores 18/20 and another 40/50, which is stronger? Percentages make the comparison fair."},
            {"title": "Using the Diagram", "role": "visual", "body": "See Part → Whole → Percent. The diagram reminds you to compare against 100 equal parts."},
            {"title": "Concept: Percent", "role": "concept", "body": "Percent means out of one hundred. 25% means 25 of every 100 equal parts."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "Percent is a way of writing a fraction with denominator 100."},
            {"title": "In Real Life", "role": "real_life_example", "body": "A shop's 20% off tag means you pay 80 of every 100 rupees of the original price."},
            {"title": "Worked Example", "role": "worked_example", "body": "Find 25% of 80: 25/100 × 80 = 20. Check with a bar split into four equal parts."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Percent on the diagram and explain how to turn 1/4 into a percentage."},
            {"title": "Lesson Summary", "role": "summary", "body": "Percentages compare parts using a whole of 100. That common scale makes different scores comparable."},
            {"title": "Think About It", "role": "reflection", "body": "Where do you see % signs this week — shops, weather, or sports?"},
            {"title": "Apply Your Learning", "role": "application", "body": "Write one real shopping story that uses a percentage discount correctly."},
        ],
        labels=["Part", "Whole", "Percent"],
        practice="Point to Whole and explain why percent needs a whole of 100.",
    )
    add(
        items,
        gid="history_trade_routes",
        subject="history",
        topic="Ancient Trade Routes",
        big="Ancient trade routes moved goods, ideas, and cultures across long distances.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "How did silk from faraway lands reach distant markets long before aeroplanes? Trade routes connected people."},
            {"title": "Using the Diagram", "role": "visual", "body": "Follow Source → Route → Market. The diagram shows movement of goods and the exchange of ideas along the way."},
            {"title": "Concept: Trade Route", "role": "concept", "body": "A trade route is a path merchants used to carry goods. Along it, languages, skills, and beliefs also travelled."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "Trade routes were ancient highways for products and for new ideas."},
            {"title": "In Real Life", "role": "real_life_example", "body": "Spices valued in one region could be rare elsewhere, so merchants risked long journeys for high reward."},
            {"title": "Worked Example", "role": "worked_example", "body": "Map a caravan moving cloth east and spices west: each stop may add taxes, rest, and cultural exchange."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Route and explain one challenge travellers might face."},
            {"title": "Lesson Summary", "role": "summary", "body": "Trade routes carried goods and ideas. Understanding the path helps explain how cultures influenced each other."},
            {"title": "Think About It", "role": "reflection", "body": "What modern route — road, rail, or shipping — reminds you of ancient trade networks?"},
            {"title": "Apply Your Learning", "role": "application", "body": "Create a postcard from a merchant describing one goods exchange along the route."},
        ],
        labels=["Source", "Route", "Market"],
        practice="Point to Market and explain what arrives there besides goods.",
    )
    add(
        items,
        gid="english_clear_paragraphs",
        subject="english",
        topic="Clear Paragraphs",
        big="A clear paragraph has one main idea, supporting sentences, and a neat finish.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "Why do some paragraphs feel easy while others feel muddled? Structure makes the difference."},
            {"title": "Using the Diagram", "role": "visual", "body": "Follow Topic sentence → Support → Closing. The diagram is a map for one focused idea."},
            {"title": "Concept: Paragraph", "role": "concept", "body": "A paragraph clusters sentences around one idea. The topic sentence announces it; support proves it."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "One paragraph, one job. Everything in it should help that job."},
            {"title": "In Real Life", "role": "real_life_example", "body": "A message to a friend about weekend plans works best when the main plan comes first, then details."},
            {"title": "Worked Example", "role": "worked_example", "body": "Topic: Libraries are quiet places to focus. Support with two reasons. Close by restating the benefit."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Topic sentence and write one for a paragraph about teamwork."},
            {"title": "Lesson Summary", "role": "summary", "body": "Clear paragraphs start with a main idea, add support, and finish cleanly so readers never get lost."},
            {"title": "Think About It", "role": "reflection", "body": "Which sentence in your last paragraph was the true topic sentence?"},
            {"title": "Apply Your Learning", "role": "application", "body": "Rewrite a messy three-sentence note into one clear paragraph using the diagram."},
        ],
        labels=["Topic", "Support", "Close"],
        practice="Point to Support and explain what those sentences must do.",
        stage="primary",
    )
    add(
        items,
        gid="environmental_waste_cycle",
        subject="environmental_science",
        topic="Waste and Recycling",
        big="Waste management reduces harm by refusing, reducing, reusing, and recycling.",
        secs=[
            {"title": "Have You Wondered?", "role": "hook", "body": "Where does yesterday's plastic bottle go if we toss it carelessly? Waste choices travel farther than we see."},
            {"title": "Using the Diagram", "role": "visual", "body": "Follow Refuse → Reduce → Reuse → Recycle. The diagram prioritises prevention before recycling."},
            {"title": "Concept: Waste Hierarchy", "role": "concept", "body": "The waste hierarchy ranks actions. Preventing waste beats recycling something that did not need to exist."},
            {"title": "Say It Simply", "role": "simple_explanation", "body": "Best first: don't create waste. Then use less, use again, and recycle what remains."},
            {"title": "In Real Life", "role": "real_life_example", "body": "Carrying a refillable bottle refuses a new disposable bottle before recycling is even needed."},
            {"title": "Worked Example", "role": "worked_example", "body": "Sort a lunch scrap pile: food to compost, clean paper to recycle, and a broken toy to repair or reuse."},
            {"title": "Try This", "role": "practice_question", "body": "Point to Reduce and give one school action that creates less waste."},
            {"title": "Lesson Summary", "role": "summary", "body": "Smart waste habits follow a hierarchy. Prevention and reuse protect environments better than last-minute recycling alone."},
            {"title": "Think About It", "role": "reflection", "body": "Which bin at home is fullest, and what does that reveal about your week's choices?"},
            {"title": "Apply Your Learning", "role": "application", "body": "Design a classroom poster that uses the four diagram steps in the correct order."},
        ],
        labels=["Refuse", "Reduce", "Reuse", "Recycle"],
        practice="Point to Recycle and explain why it is not the first choice.",
    )

    for item in items:
        path = ROOT / f"{item['id']}.json"
        path.write_text(json.dumps(item, indent=2), encoding="utf-8")
        print("wrote", path.name)
    print("total_goldens", len(list(ROOT.glob("*.json"))))


if __name__ == "__main__":
    main()
