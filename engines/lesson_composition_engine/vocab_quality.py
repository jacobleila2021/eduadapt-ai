"""Shared educational vocabulary hygiene — reject junk terms, build real definitions."""

from __future__ import annotations

import re
from typing import Any, Iterable

# Words that must never become vocabulary cards / concept-map nodes
VOCAB_STOPWORDS = frozenset(
    {
        "this", "that", "with", "from", "have", "will", "were", "been", "they", "them",
        "their", "about", "which", "while", "where", "when", "what", "into", "also",
        "than", "then", "only", "over", "such", "some", "more", "most", "other", "each",
        "make", "like", "just", "very", "subject", "grade", "level", "objective",
        "objectives", "students", "student", "lesson", "chapter", "learning", "explain",
        "describe", "define", "discuss", "identify", "minutes", "hours", "seconds",
        "earth's", "water's", "using", "used", "uses", "does", "done", "being", "able",
        "should", "could", "would", "must", "need", "needs", "know", "show", "shows",
        "read", "write", "answer", "question", "questions", "example", "examples",
        "diagram", "diagrams", "figure", "figures", "table", "page", "pages", "part",
        "parts", "section", "sections", "unit", "units", "time", "today", "title",
        "introduction", "summary", "revision", "practice", "check", "model", "apply",
        "evidence", "support", "core", "idea", "ideas", "concept", "concepts", "term",
        "terms", "word", "words", "means", "meaning", "called", "name", "named",
        "first", "next", "then", "after", "before", "during", "through", "across",
        "between", "under", "above", "below", "around", "again", "still", "also",
        "because", "however", "therefore", "thus", "hence", "look", "looking",
        # Bare title / prompt fragments that must never become vocab or diagram nodes
        "travel", "travels", "travelling", "traveling", "system", "systems",
        "matter", "life", "why", "how", "together", "points", "fits", "fit",
        "continuous", "movement", "moves", "moving", "among", "among", "surface",
        # Everyday props from teacher warm-ups — never process-stage nodes
        "faucet", "faucets", "tap", "taps", "puddle", "puddles",
        "raindrop", "raindrops", "umbrella", "bucket", "hose",
        # Sentence scraps from NCERT intros that must never become concept titles
        "previous", "evious", "classes", "tastes", "bitter", "sour", "respectively",
        "learnt", "learned", "provided", "tubes", "activity", "chapter", "understanding",
        "laboratory", "substance", "substances", "interesting", "things",
    }
)

META_TOPICS = frozenset(
    {
        "learning objectives",
        "objectives",
        "learning objective",
        "introduction",
        "instructions",
        "directions",
        "warm up",
        "warmup",
        "do now",
        "exit ticket",
        "this lesson",
        "lesson",
        "untitled",
    }
)

WATER_CYCLE_TERMS = (
    ("Evaporation", "Evaporation is when liquid water turns into water vapour and rises into the air."),
    ("Condensation", "Condensation is when water vapour cools and changes back into tiny liquid droplets."),
    ("Precipitation", "Precipitation is water that falls from clouds as rain, snow, sleet, or hail."),
    ("Collection", "Collection is when water gathers in rivers, lakes, oceans, and groundwater."),
    ("Water vapour", "Water vapour is water in the gas state in the air."),
    ("Water cycle", "The water cycle is the continuous movement of water on, above, and below Earth's surface."),
    ("Transpiration", "Transpiration is when plants release water vapour into the air from their leaves."),
)

WATER_CYCLE_PICTURES = {
    "evaporation": "Draw the sun warming a lake or puddle, with curved arrows of vapour rising upward.",
    "condensation": "Draw a cloud forming high in the sky as tiny droplets gather together.",
    "precipitation": "Draw rain (or snow) falling from a dark cloud toward the ground.",
    "collection": "Draw a river, lake, or ocean where water gathers after rain.",
    "water vapour": "Draw invisible steam/vapour above warm water with a small label 'gas'.",
    "water cycle": "Draw a full loop: sun → rising vapour → cloud → rain → lake → back to sun.",
    "transpiration": "Draw a tree with tiny arrows of vapour leaving the leaves toward the sky.",
}

# CBSE Class 8–10 Science — Acids, Bases and Salts (Master Lesson teaching bank).
# Depth includes formulae so Mainstream matches Dyslexia Smart quality — never Grade-6 only.
ACIDS_BASES_SALTS_TERMS = (
    (
        "Acid",
        "An acid is a substance that tastes sour and turns blue litmus red. "
        "Common laboratory acids include hydrochloric acid (HCl), sulphuric acid (H₂SO₄) "
        "and acetic acid (CH₃COOH). Acids release hydrogen ions (H⁺) in water, so acidic "
        "solutions can conduct electricity and react with metals to form a salt and hydrogen gas.",
    ),
    (
        "Base",
        "A base is a substance that tastes bitter, feels soapy or slippery, and turns red litmus blue. "
        "Bases release hydroxide ions (OH⁻) in solution. Common bases include sodium hydroxide (NaOH) "
        "and potassium hydroxide (KOH). Bases react with acids in neutralisation to form salt and water, "
        "which is why mild bases are used in antacids and cleaning products.",
    ),
    (
        "Salt",
        "A salt is the substance formed when an acid and a base cancel each other's effect "
        "(neutralisation), usually along with water. Everyday examples include common salt (NaCl) "
        "from hydrochloric acid and sodium hydroxide, and salts formed when acids react with metals "
        "or metal carbonates.",
    ),
    (
        "Indicator",
        "An indicator is a dye that changes colour in acidic or basic solutions so you can classify "
        "a substance without tasting it. Natural indicators include litmus and turmeric; synthetic "
        "indicators include phenolphthalein and methyl orange.",
    ),
    (
        "Litmus",
        "Litmus is a natural indicator from lichens: blue litmus turns red in an acid; red litmus "
        "turns blue in a base. When a litmus solution is neither acidic nor basic (neutral), "
        "its colour is purple.",
    ),
    (
        "Neutralisation",
        "Neutralisation is the reaction in which an acid and a base cancel each other and form "
        "salt and water. In ionic terms, H⁺ from the acid and OH⁻ from the base combine to form water. "
        "Baking soda solution is a safe everyday remedy for acidity because it is a mild base.",
    ),
    (
        "Baking soda",
        "Baking soda is sodium hydrogencarbonate (NaHCO₃), a mild base used in cooking and as an "
        "antacid. It reacts with acids to form a salt, water and carbon dioxide, which is why it "
        "relieves acidity better than lemon juice or vinegar (both acidic).",
    ),
    (
        "Phenolphthalein",
        "Phenolphthalein is a synthetic indicator that is colourless in acidic solution and turns "
        "pink in a basic solution.",
    ),
    (
        "Methyl orange",
        "Methyl orange is a synthetic indicator that is red in acid and yellow in base.",
    ),
)

# CBSE mathematics — Fractions (Master Lesson teaching bank).
FRACTIONS_TERMS = (
    (
        "Fraction",
        "A fraction names equal parts of a whole: the numerator (top) counts the parts taken; "
        "the denominator (bottom) counts how many equal parts make one whole. For example, 3/4 "
        "means three of four equal parts.",
    ),
    (
        "Numerator",
        "The numerator is the top number of a fraction. It tells how many equal parts you have.",
    ),
    (
        "Denominator",
        "The denominator is the bottom number of a fraction. It tells into how many equal parts "
        "the whole is divided. It cannot be zero.",
    ),
    (
        "Equivalent fractions",
        "Equivalent fractions name the same amount even when the numbers look different, "
        "such as 1/2 and 2/4. Multiply or divide the numerator and denominator by the same "
        "non-zero number to make an equivalent fraction.",
    ),
    (
        "Proper fraction",
        "A proper fraction has a numerator smaller than its denominator, so its value is less than 1 "
        "(for example, 2/5).",
    ),
    (
        "Improper fraction",
        "An improper fraction has a numerator greater than or equal to its denominator, so its value "
        "is 1 or more (for example, 7/4).",
    ),
    (
        "Mixed number",
        "A mixed number joins a whole number with a proper fraction, such as 1 3/4. It can be rewritten "
        "as an improper fraction.",
    ),
)

# CBSE Class 10 Science — Electricity (Master Lesson teaching bank).
ELECTRICITY_TERMS = (
    (
        "Electric current",
        "Electric current is the rate of flow of electric charge through a conductor. "
        "Conventionally, current direction is opposite to electron flow. Its SI unit is the ampere (A).",
    ),
    (
        "Electric circuit",
        "An electric circuit is a closed path that allows electric current to flow from a source "
        "(cell or battery) through devices such as bulbs, resistors and a switch, and back.",
    ),
    (
        "Potential difference",
        "Potential difference (voltage) between two points is the work done to move a unit charge "
        "from one point to the other. It is measured in volts (V) with a voltmeter.",
    ),
    (
        "Resistance",
        "Resistance is the property of a conductor that opposes the flow of electric current. "
        "Its SI unit is the ohm (Ω). Resistance depends on length, area of cross-section and material.",
    ),
    (
        "Ohm's law",
        "Ohm's law: at constant temperature, the potential difference V across a conductor is "
        "directly proportional to the current I through it, so V = IR where R is resistance.",
    ),
    (
        "Series combination",
        "In a series combination, resistors are joined end to end so the same current flows through each. "
        "Equivalent resistance: R_s = R_1 + R_2 + R_3 + …",
    ),
    (
        "Parallel combination",
        "In a parallel combination, resistors share the same potential difference. "
        "Equivalent resistance: 1/R_p = 1/R_1 + 1/R_2 + 1/R_3 + …",
    ),
    (
        "Electric power",
        "Electric power is the rate of consumption of electrical energy. P = VI = I²R = V²/R. "
        "The SI unit is the watt (W); 1 kW = 1000 W.",
    ),
    (
        "Heating effect",
        "When current flows through a resistor, electrical energy converts to heat: H = VIt = I²Rt. "
        "This heating effect is used in electric irons, toasters and heaters.",
    ),
    (
        "Kilowatt hour",
        "The commercial unit of electrical energy is the kilowatt hour (kWh). "
        "1 kWh = 3.6 × 10⁶ J. Household electricity bills charge energy in kWh.",
    ),
    (
        "Conductor",
        "A conductor allows electric current to pass easily (low resistance), such as copper or aluminium. "
        "An insulator resists current strongly (very high resistance).",
    ),
)

# CBSE Metals and Non-metals (Class 8 / 10 Science) — Master Lesson teaching bank.
METALS_NONMETALS_TERMS = (
    (
        "Metal",
        "Metals are elements that are generally hard, shiny (lustrous), malleable, ductile, "
        "sonorous and good conductors of heat and electricity. Examples: iron, copper, aluminium.",
    ),
    (
        "Non-metal",
        "Non-metals are generally dull, brittle (when solid) and poor conductors of heat and electricity. "
        "Examples: oxygen, sulphur, carbon and nitrogen.",
    ),
    (
        "Malleability",
        "Malleability is the property of metals by which they can be beaten into thin sheets, "
        "such as aluminium foil or gold leaf.",
    ),
    (
        "Ductility",
        "Ductility is the property of metals by which they can be drawn into thin wires, "
        "such as copper electrical wire.",
    ),
    (
        "Lustre",
        "Lustre is the shiny appearance of a clean metal surface. Most non-metals are dull, "
        "except iodine which shows a shiny appearance.",
    ),
    (
        "Sonorous",
        "Sonorous means a metal produces a ringing sound when struck. School bells and utensils "
        "show this property; non-metals are not sonorous.",
    ),
    (
        "Conductivity",
        "Metals are good conductors of heat and electricity. Most non-metals are poor conductors; "
        "graphite is a non-metal that conducts electricity.",
    ),
    (
        "Basic oxide",
        "Metals react with oxygen to form metal oxides, which are generally basic. "
        "Basic oxides turn red litmus blue.",
    ),
    (
        "Acidic oxide",
        "Non-metals react with oxygen to form non-metal oxides, which are generally acidic "
        "(or sometimes neutral). Acidic oxides turn blue litmus red.",
    ),
    (
        "Displacement reaction",
        "A more reactive metal can displace a less reactive metal from its salt solution. "
        "This helps compare metal reactivity.",
    ),
    (
        "Corrosion",
        "Corrosion is the gradual damage of a metal surface by air, moisture or chemicals. "
        "Rusting of iron is a common example; galvanisation helps prevent it.",
    ),
    (
        "Metal oxide",
        "A metal oxide forms when a metal reacts with oxygen. Metal oxides are generally basic "
        "and turn red litmus blue. Example: magnesium burns in air to form magnesium oxide.",
    ),
)

# Common sample metals — short teachable cards (never lab-instruction text).
_ELEMENT_METAL_DEFS = {
    "iron": "Iron is a common metal used for tools and construction. It rusts in moist air (corrosion).",
    "copper": "Copper is a reddish-brown metal that is an excellent conductor of heat and electricity, used in wires.",
    "aluminium": "Aluminium is a light, malleable metal used for foil, utensils and aircraft parts.",
    "aluminum": "Aluminium is a light, malleable metal used for foil, utensils and aircraft parts.",
    "magnesium": "Magnesium is a reactive metal that burns in air with a bright white flame to form magnesium oxide.",
    "sodium": "Sodium is a soft, highly reactive metal that must be handled with care; it reacts vigorously with water.",
    "zinc": "Zinc is a metal used to coat iron (galvanisation) to prevent rusting.",
    "lead": "Lead is a dense, soft metal that is a poor conductor compared with copper.",
    "mercury": "Mercury is the only metal that is liquid at room temperature.",
}

# Sentence fragments that OCR/title scraping wrongly promotes to "concepts".
_FRAGMENT_JUNK = frozenset(
    {
        "previous", "evious", "classes", "class", "tastes", "taste", "bitter", "sour",
        "respectively", "present", "them", "food", "learnt", "learned", "provided",
        "three", "test", "tubes", "tube", "activity", "chapter", "understanding",
        "chemical", "properties", "laboratory", "substance", "substances", "colour",
        "color", "change", "changes", "day", "life", "interesting", "things",
        "many", "more", "study", "reactions", "reaction", "effects", "effect",
        "cancel", "cancels", "out", "each", "other", "you", "have", "been",
    }
)

_OCR_JOIN_PREFIXES = frozenset(
    {
        "pr", "lear", "thr", "und", "resp", "indic", "prov", "chem", "neut",
        "phen", "meth", "litt", "synt",
    }
)

_TEACHER_TEXT_PATTERNS = (
    r"\bstudents?\s+will\b",
    r"\blearners?\s+will\b",
    r"\bby the end of (this|the) lesson\b",
    r"\blearning\s+objectives?\b",
    r"\bsuccess\s+criteria\b",
    r"\bteacher\s+note\b",
    r"\bteacher\s+should\b",
    r"\btell\s+(the\s+)?(students?|class|learners?)\b",
    r"\bdifferentiat",
    r"\bexit\s+ticket\b",
    r"\bwarm[\s-]?up\b",
    r"\binstruct(ion| the class)\b",
    r"\bon the board\b",
    r"\bcold[\s-]?call\b",
    r"\bmodel cue\b",
    r"\bpractice-from-source\b",
    # Teacher lesson-plan voice — classroom management lines that must never
    # reach a self-studying learner ("Begin by asking students…",
    # "I will divide you into pairs…", "Show a short image of a cloud…").
    r"\bask(ing)?\s+(the\s+)?(students?|class|learners?)\b",
    r"\bhave\s+(the\s+)?(students?|class|learners?)\b",
    r"\bstudents?\s+(receive|share|discuss|pair)\b",
    r"\bdivide\s+(you|the\s+class|students?|learners?)\s+into\b",
    r"\bin\s+pairs\b",
    r"\bwith\s+a\s+partner\b",
    r"\bsmall\s+groups?\b",
    r"\beach\s+pair\b",
    r"\banother\s+pair\b",
    r"\bi\s+will\s+(show|write|divide|provide|give|hand|collect|assess|ask)\b",
    r"\bi\s+want\s+you\s+to\b",
    r"\bshow\s+(a|the)\s+(short\s+)?(image|video|clip|animation)\b",
    r"\bwalk\s+around\s+the\s+(room|class)\b",
    r"\bgrade\s+level\b",
    r"\bessential\s+question\b",
    r"\bmaterials?\s*(needed|:)",
    r"\bguided\s+practice\b",
    r"\bindependent\s+practice\b",
    r"\blesson\s+plan(ning)?\b",
    r"\blesson\s+duration\b",
    r"\bintroduction\s*\(\s*\d+\s*minutes?\s*\)",
    r"\b\d+\s*minutes?\b",
    r"\bclosure\b",
    r"\bhomework\b",
    r"\bkick\s+off\b",
    r"\blet'?s\s+(work\s+together|think\s+about)\b",
    # NCERT chapter chrome / textbook asides — never learner answers
    r"\bin this chapter\b",
    r"\bwe will study\b",
    r"\byou already know that\b",
    r"\bsurely you must have\b",
    r"\byou have been provided\b",
    r"\btry this point to each part\b",
    r"\bstudy the labelled diagram\b",
    r"\bfor performing activit",
    r"\bcollect the samples?\b",
    r"\bactivities?\s+\d",
    r"\bcaution\s*:",
    r"\byou will be learning\b",
    r"\bin the next section\b",
    r"\bin class\s+(ix|9|x|10)\b",
    r"\beasily available\b",
)

# Isolated planning debris / orphan fragments that must never become learner prose.
_ORPHAN_CLAIM_PATTERNS = (
    r"^(faucets?|minutes?|hours?|materials?|supplies|handout|worksheet)\.?$",
    r"\bteacher notes?\b",
    r"\blesson planning\b",
    r"\bask learners?\b",
    r"\btell students?\b",
)


def repair_ocr_prose(text: str) -> str:
    """Repair common NCERT/PDF OCR damage before any learner-facing use."""
    t = str(text or "")
    if not t.strip():
        return ""
    # Chapter / unit chrome fused into prose (including 4CHAPTER / CHAPTER3)
    t = re.sub(r"(?i)\d{0,2}\s*CHAPTER\s*\d{0,2}", " ", t)
    t = re.sub(r"\bActivity\s+\d+(?:\.\d+)*\b", " ", t, flags=re.I)
    # Textbook running headers / page crumbs
    t = re.sub(
        r"(?i)\bmetals\s+and\s+non[-\s]?metals\s+\d{1,3}\b",
        " ",
        t,
    )
    t = re.sub(r"(?i)\belectricity\s+\d{1,3}\b", " ", t)
    t = re.sub(r"(?i)\bscience\s+\d{1,3}\b", " ", t)
    t = re.sub(r"(?i)\bnot\s+to\s+be\s+republished\b", " ", t)
    t = re.sub(r"(?i)\b©?\s*ncert\b", " ", t)
    # Collapse runaway repeated chunks ("UNDERSTUNDERST…", "ACIDS AND BASESACIDS…")
    t = re.sub(r"(\b[\w']{4,}\b)(?:\s*\1){1,}", r"\1", t, flags=re.I)
    t = re.sub(r"([A-Za-z]{5,})\1{1,}", r"\1", t)
    # Isolated capital + rest of word: "Y ou" → "You"
    t = re.sub(r"\b([A-Z])\s+([a-z]{2,})\b", r"\1\2", t)
    # Mid-word OCR breaks: "lear nt", "pr evious"
    for _ in range(4):
        def _join(m: re.Match[str]) -> str:
            a, b = m.group(1), m.group(2)
            if a.lower() in _OCR_JOIN_PREFIXES or len(a) <= 3 and b.lower()[:2] in {
                "ev", "nt", "ee", "id", "or", "al", "at", "en", "er",
            }:
                return a + b
            return m.group(0)

        nxt = re.sub(r"\b([A-Za-z]{1,4})\s+([a-z]{2,10})\b", _join, t)
        if nxt == t:
            break
        t = nxt
    # Chapter title + page number debris: "Acids, Bases and Salts 19"
    t = re.sub(
        r"(?i)\bacids,\s*bases\s+and\s+salts\s+\d{1,3}\b",
        " ",
        t,
    )
    t = re.sub(r"(?i)\b(water\s+cycle|force\s+and\s+pressure)\s+\d{1,3}\b", " ", t)
    # Bare page-header claims: "Acids, Bases and Salts 19" as whole string
    if re.fullmatch(r"(?i)[\w\s,]{6,50}\s+\d{1,3}", t.strip()):
        return ""
    # Fused article+word OCR: "theatmosphere", "theenergy", "theentire"
    t = re.sub(r"\b(the|a|an|to|of|in|on|for|and)([A-Z][a-z]{2,})", r"\1 \2", t)
    t = re.sub(
        r"\b(the)(atmosphere|energy|entire|earth|ocean|water|sun|air|process)\b",
        r"\1 \2",
        t,
        flags=re.I,
    )
    t = re.sub(r"\s+", " ", t).strip()
    return t


def is_ocr_garbage_claim(text: str) -> bool:
    """True for chapter intros / OCR mush that must never teach learners."""
    original = str(text or "")
    raw = repair_ocr_prose(original)
    if not raw:
        return True
    low = raw.lower()
    # Page header only (title + page number)
    if re.fullmatch(r"(?i)[\w\s,]{6,50}\s+\d{1,3}", original.strip()):
        return True
    if re.search(r"(?i)\bacids,\s*bases\s+and\s+salts\s+\d{1,3}\b", original):
        # Still garbage if the claim is mostly header debris
        stripped = re.sub(r"(?i)\bacids,\s*bases\s+and\s+salts\s+\d{1,3}\b", "", original)
        if len(stripped.split()) < 6:
            return True
    if re.search(r"\bchapter\b|\bactivity\s+\d", low):
        return True
    if "in this chapter" in low or "we will study" in low:
        return True
    if re.search(
        r"for performing activit|collect the samples|caution\s*:|you will be learning|"
        r"in the next section|in class\s+(ix|9|x|10)|easily available",
        low,
    ):
        return True
    # "What you have learnt" is a valuable NCERT summary — not garbage.
    # Only reject the chapter-intro "you have learnt in previous classes…" line.
    if ("you have learnt" in low or "you have learned" in low) and "previous classes" in low:
        return True
    if "you already know that" in low or "surely you must have" in low:
        return True
    if "previous classes" in low and ("sour" in low or "bitter" in low):
        return True
    # Section / page debris from scanned NCERT PDFs
    if re.search(r"\bscience\s*\d{1,3}\b|\b\d+\.\d+(?:\.\d+){1,}\b", low) and (
        "acid" in low or "base" in low or "chapter" in low or "underst" in low
    ):
        return True
    # Concatenated heading mush / broken stems from PDF extractors
    if re.search(
        r"underst|chemicanding|properties ofal|acids and basesacids|anding the chemic",
        low,
    ):
        return True
    if len(re.findall(r"[A-Z]{6,}", original)) >= 3:
        return True
    # Unrepaired OCR letter-splits ("t he", "F orce") — not English "a push" / "is a".
    lonely_letters = [
        m.group(1)
        for m in re.finditer(r"\b([A-Za-z])\s+[a-z]{2,}\b", original)
        if m.group(1).lower() not in {"a", "i"}
    ]
    if len(lonely_letters) >= 2:
        return True
    # Same 8+ letter token repeated → paste/OCR loop
    tokens = re.findall(r"[A-Za-z]{8,}", raw)
    if tokens and tokens.count(max(set(tokens), key=tokens.count)) >= 3:
        return True
    return False


def clean_learner_claim(text: str) -> str:
    """Return cleaned teachable prose, or empty if unsuitable."""
    raw = repair_ocr_prose(text)
    if not raw or is_ocr_garbage_claim(text) or is_teacher_facing_text(raw):
        return ""
    if is_orphan_claim(raw):
        return ""
    if len(raw.split()) < 4:
        return ""
    return raw


def is_plural_concept(name: str) -> bool:
    low = (name or "").strip().lower()
    if low in {"acids", "bases", "salts", "indicators"}:
        return True
    if low.endswith("s") and low not in {"gas", "glass", "basis", "litmus", "focus", "class"}:
        if " " not in low and len(low) > 3:
            return True
    return False


def question_what_is(name: str, *, marks: int = 1) -> str:
    display = (name or "this idea").strip()
    mark_label = f"{marks} mark" if marks == 1 else f"{marks} marks"
    if is_plural_concept(display):
        return f"What are {display.lower()}? ({mark_label})"
    if " " in display:
        return f"What is {display.lower()}? ({mark_label})"
    article = "an" if display[:1].lower() in "aeiou" else "a"
    return f"What is {article} {display.lower()}? ({mark_label})"


def enrich_acids_bases_salts_terms(topic: str, existing: list[str]) -> list[tuple[str, str]]:
    blob = (topic or "").lower() + " " + " ".join(existing).lower()
    if not any(k in blob for k in ("acid", "base", "salt", "litmus", "neutralis", "neutraliz")):
        return []
    have = {e.lower() for e in existing}
    out: list[tuple[str, str]] = []
    for term, definition in ACIDS_BASES_SALTS_TERMS:
        if term.lower() not in have and not is_junk_term(term):
            out.append((term, definition))
    return out


def enrich_fractions_terms(topic: str, existing: list[str]) -> list[tuple[str, str]]:
    blob = (topic or "").lower() + " " + " ".join(existing).lower()
    if not any(k in blob for k in ("fraction", "numerator", "denominator", "mixed number")):
        return []
    have = {e.lower() for e in existing}
    out: list[tuple[str, str]] = []
    for term, definition in FRACTIONS_TERMS:
        if term.lower() not in have and not is_junk_term(term):
            out.append((term, definition))
    return out


def enrich_electricity_terms(topic: str, existing: list[str]) -> list[tuple[str, str]]:
    blob = (topic or "").lower() + " " + " ".join(existing).lower()
    if not any(
        k in blob
        for k in (
            "electric",
            "ohm",
            "resistance",
            "current",
            "circuit",
            "volt",
            "watt",
            "kilowatt",
        )
    ):
        return []
    have = {e.lower() for e in existing}
    out: list[tuple[str, str]] = []
    for term, definition in ELECTRICITY_TERMS:
        if term.lower() not in have and not is_junk_term(term):
            out.append((term, definition))
    return out


def enrich_metals_nonmetals_terms(topic: str, existing: list[str]) -> list[tuple[str, str]]:
    blob = (topic or "").lower() + " " + " ".join(existing).lower()
    if not any(
        k in blob
        for k in (
            "metal",
            "non-metal",
            "nonmetal",
            "non metal",
            "malleab",
            "ductil",
            "lustre",
            "luster",
            "sonorous",
            "corrosion",
            "rust",
        )
    ):
        return []
    have = {e.lower() for e in existing}
    out: list[tuple[str, str]] = []
    for term, definition in METALS_NONMETALS_TERMS:
        if term.lower() not in have and not is_junk_term(term):
            out.append((term, definition))
    return out


def extract_what_you_have_learnt(text: str) -> list[str]:
    """Pull NCERT 'What you have learnt' bullets as-is for Master summary."""
    raw = str(text or "")
    if not raw.strip():
        return []
    m = re.search(
        r"(?is)what\s+you\s+have\s+learnt\s*[:\n]+(.+?)(?=\n\s*(?:exercises?|questions?)\b|\Z)",
        raw,
    )
    if not m:
        return []
    block = m.group(1)
    bullets: list[str] = []
    for line in block.splitlines():
        line = re.sub(r"^[\s•\-\*\d\.\)\(]+", "", line).strip()
        if len(line.split()) >= 5 and not is_ocr_garbage_claim(line):
            bullets.append(line if line.endswith((".", "!", "?")) else line + ".")
        if len(bullets) >= 14:
            break
    return bullets


def extract_source_assessment_prompts(text: str, *, topic: str = "") -> list[dict[str, Any]]:
    """Textbook QUESTIONS / EXERCISES → exam worksheet prompts (platform-wide)."""
    try:
        from engines.knowledge_ingestion_engine.stages.extract import extract_questions
    except Exception:
        extract_questions = None  # type: ignore
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    if extract_questions:
        for row in extract_questions(text, topic=topic, source="uploaded_lesson") or []:
            prompt = str(row.get("question") or "").strip()
            # Strip leading Q1. / 1. numbering noise for cleaner stems
            prompt = re.sub(r"^(?:Q\.?\s*\d+[\)\.]?\s*|Question\s+\d+[\)\.]?\s*|\d+\.\s+)", "", prompt)
            key = prompt.lower()[:80]
            if len(prompt.split()) < 5 or key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "outcome_id": f"src_{len(out)+1:03d}",
                    "prompt": prompt[:400],
                    "bloom": str(row.get("bloom") or "understand"),
                    "marks": int(row.get("marks") or 2),
                    "source": "textbook",
                    "question_type": str(row.get("question_type") or "short_answer"),
                }
            )
            if len(out) >= 16:
                break
    # Also catch in-block questions under a QUESTIONS heading
    if len(out) < 6:
        for m in re.finditer(
            r"(?im)^(?:\d+\.|[•\-])\s*(.+\?)\s*$",
            text or "",
        ):
            prompt = m.group(1).strip()
            key = prompt.lower()[:80]
            if len(prompt.split()) < 5 or key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "outcome_id": f"src_{len(out)+1:03d}",
                    "prompt": prompt[:400],
                    "bloom": "understand",
                    "marks": 2,
                    "source": "textbook",
                    "question_type": "short_answer",
                }
            )
            if len(out) >= 16:
                break
    return out


def is_teacher_facing_text(text: str) -> bool:
    """True for lesson-plan / objective wording that must never appear as student content."""
    low = (text or "").strip().lower()
    if not low:
        return False
    return any(re.search(p, low) for p in _TEACHER_TEXT_PATTERNS)


def is_orphan_claim(text: str) -> bool:
    """True for isolated planning debris or fragments with no teachable meaning."""
    raw = (text or "").strip()
    if not raw:
        return True
    low = raw.lower()
    if len(raw.split()) <= 2 and not any(ch in raw for ch in ".!?"):
        # Bare nouns without a teaching sentence ("faucets", "minutes").
        if re.fullmatch(r"[a-z][a-z\s-]{0,40}", low):
            return True
    return any(re.search(p, low) for p in _ORPHAN_CLAIM_PATTERNS)


def is_learner_safe_claim(text: str) -> bool:
    """Source sentence eligible for student theory (not teacher chrome / orphans)."""
    raw = (text or "").strip()
    if len(raw.split()) < 4:
        return False
    if is_teacher_facing_text(raw) or is_orphan_claim(raw):
        return False
    return True


def student_safe_definition(text: str) -> str:
    """Return empty string when text is teacher-facing or template filler."""
    raw = (text or "").strip()
    if not raw:
        return ""
    if is_teacher_facing_text(raw) or is_ocr_garbage_claim(raw):
        return ""
    low = raw.lower()
    for bad in (
        "core concept in this lesson",
        "key lesson term",
        "key word connected",
        "not found in verified glossary",
        "ask ai tutor",
        "for performing activit",
        "collect the samples",
        "you will be learning",
        "in the next section",
        "3chapter",
        "chapter i n",
        "lear nt",
    ):
        if bad in low:
            return ""
    return raw


def canonical_definition(term: str) -> str:
    key = (term or "").strip().lower()
    # Singularize common exam plurals so "Bases" / "Acids" resolve.
    aliases = {
        "acids": "acid",
        "bases": "base",
        "salts": "salt",
        "indicators": "indicator",
        "neutralization": "neutralisation",
        "metals": "metal",
        "non-metals": "non-metal",
        "nonmetals": "non-metal",
        "non metals": "non-metal",
        "metal oxides": "metal oxide",
        "metallic lustre": "lustre",
        "metallic luster": "lustre",
    }
    key = aliases.get(key, key)
    for name, definition in (
        WATER_CYCLE_TERMS
        + ACIDS_BASES_SALTS_TERMS
        + FRACTIONS_TERMS
        + ELECTRICITY_TERMS
        + METALS_NONMETALS_TERMS
    ):
        if name.lower() == key:
            return definition
    if key in _ELEMENT_METAL_DEFS:
        return _ELEMENT_METAL_DEFS[key]
    return ""


def picture_cue_for_term(term: str, *, definition: str = "") -> str:
    key = (term or "").strip().lower()
    if key in WATER_CYCLE_PICTURES:
        return WATER_CYCLE_PICTURES[key]
    if definition and not is_teacher_facing_text(definition):
        return f"Draw a simple labelled sketch that shows: {definition[:120]}"
    display = (term or "this idea").strip()
    return f"Draw a simple classroom sketch that helps you remember what {display} means."


def is_diagram_stage(term: str, *, topic: str = "", claim_blob: str = "") -> bool:
    """True only for concepts safe to put on a flowchart / concept map."""
    raw = (term or "").strip()
    # Stage labels are short nouns by design — do not apply sentence orphan rules.
    if not raw or is_junk_term(raw) or is_teacher_facing_text(raw):
        return False
    low = raw.lower()
    topic_l = (topic or "").lower()
    blob = f"{claim_blob} {topic_l}".lower()
    # Water-cycle lessons: only scientific stages (never warm-up nouns).
    if any(k in blob for k in ("water cycle", "evaporat", "condens", "precipitat")):
        allowed = {t.lower() for t, _ in WATER_CYCLE_TERMS}
        allowed |= {"runoff", "infiltration", "groundwater"}
        if low not in allowed and not any(a in low or low in a for a in allowed):
            return False
    return True


def filter_diagram_stages(
    stages: list[str],
    *,
    topic: str = "",
    claims: list[str] | None = None,
    limit: int = 6,
) -> list[str]:
    """Semantic filter for diagram nodes — drop unrelated / hallucinated labels."""
    blob = " ".join(str(c) for c in (claims or []))
    topic_blob = f"{topic} {blob}".lower()
    out: list[str] = []
    seen: set[str] = set()
    for raw in stages:
        text = str(raw or "").strip()
        key = text.lower()
        if not text or key in seen or not is_diagram_stage(text, topic=topic, claim_blob=blob):
            continue
        # Question stems / connector chrome never become diagram nodes.
        if re.match(
            r"(?i)^(can you|do you|for example|this property|reprint|gold is gold)\b",
            text,
        ):
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= limit:
            break
    # Prefer canonical water-cycle order when teaching that topic.
    if any(k in topic_blob for k in ("water cycle", "evaporat")):
        order = [t for t, _ in WATER_CYCLE_TERMS if t.lower() != "water cycle"]
        by = {n.lower(): n for n in out}
        ordered = [by[o.lower()] for o in order if o.lower() in by]
        rest = [n for n in out if n.lower() not in {x.lower() for x in ordered}]
        out = (ordered + rest)[:limit]
        return out
    # Metals / non-metals — never seed Acid/Base taxonomy into this chapter.
    if any(k in topic_blob for k in ("metal", "non-metal", "nonmetal", "malleab", "ductil", "lustre", "luster")):
        order = [t for t, _ in METALS_NONMETALS_TERMS][:limit]
        by = {n.lower(): n for n in out}
        ordered = [by[o.lower()] for o in order if o.lower() in by]
        if len(ordered) < 3:
            ordered = order
        # Drop acid/base/salt nodes that leaked from neighbouring chapters.
        rest = [
            n
            for n in out
            if n.lower() not in {x.lower() for x in ordered}
            and not re.search(r"(?i)\b(acid|base|salt|litmus|neutral)\b", n)
        ]
        return (ordered + rest)[:limit]
    # Acids / Bases / Salts — only when this lesson is actually about them.
    if any(k in topic.lower() for k in ("acid", "base", "salt", "litmus", "neutralis")):
        order = [t for t, _ in ACIDS_BASES_SALTS_TERMS][:limit]
        by = {n.lower(): n for n in out}
        ordered = [by[o.lower()] for o in order if o.lower() in by]
        if len(ordered) < 3:
            ordered = order
        rest = [n for n in out if n.lower() not in {x.lower() for x in ordered}]
        out = (ordered + rest)[:limit]
    return out


def is_junk_term(term: str) -> bool:
    raw = (term or "").strip()
    if len(raw) < 3:
        return True
    key = raw.lower().strip(" .,;:!?\"'`")
    if not key or key in VOCAB_STOPWORDS or key in _FRAGMENT_JUNK:
        return True
    if key.endswith("'s") and key[:-2] in VOCAB_STOPWORDS:
        return True
    if re.fullmatch(r"\d+", key):
        return True
    # Question stems / connector chrome as "terms"
    if re.match(
        r"(?i)^(can you|do you|did you|what |why |how |name some|for example|"
        r"this property|that property|reprint|gold is gold|extend|stretch)\b",
        key,
    ):
        return True
    if key in {
        "for example",
        "this property",
        "that property",
        "gold is gold",
        "extend",
        "stretch",
        "challenge",
        "cold",
        "reprint",
    }:
        return True
    if " is " in key and key.split(" is ", 1)[0].strip() == key.split(" is ", 1)[-1].strip():
        return True  # "gold is gold"
    if re.search(r"(?i)\breprint\b|\b\d{4}\s*[-–]\s*\d{2,4}\b", key):
        return True
    if key.endswith("?") or re.search(r"(?i)\b(that|these|those|which)$", key):
        return True
    if len(key.split()) > 6:
        return True
    # OCR crumbs: leading vowel missing ("evious"), or ALLCAPS fragment under 8 with no curriculum meaning
    if key in {"evious", "nderstanding", "hemical", "roperties"}:
        return True
    if re.fullmatch(r"[a-z]{4,8}", key) and key.startswith(("evi", "prv", "cls")):
        return True
    if key in {"earth's", "water's", "sun's", "water", "cycle", "earth", "science"}:
        # Bare fragments from titles — prefer "Water cycle" as one term
        return True
    if key in {
        "physics",
        "chemistry",
        "biology",
        "geography",
        "history",
        "civics",
        "economics",
        "english",
        "mathematics",
        "maths",
        "math",
        "general",
        "studies",
        "subject",
        "topic",
    }:
        return True
    if key.endswith("'s") and len(key) <= 8:
        return True
    if key in {"explain", "describe", "define", "minutes", "diagram"}:
        return True
    return False


def clean_topic(topic: str, *, fallback: str = "Lesson Topic") -> str:
    t = re.sub(r"\s+", " ", (topic or "").strip())
    if not t or t.lower() in META_TOPICS:
        return fallback
    t = re.sub(r"^(learning\s+objectives?|objectives?)\s*[:\-–]?\s*", "", t, flags=re.I).strip()
    if not t or t.lower() in META_TOPICS:
        return fallback
    # Drop long subtitle tails ("The Water Cycle: How Earth's Water Moves…")
    # so learner prose stays short and readable.
    if ":" in t and len(t) > 36:
        head = t.split(":", 1)[0].strip()
        if len(head) >= 8:
            t = head
    return t[:120]


def definition_from_claims(term: str, claims: Iterable[str]) -> str:
    """Pick the best claim sentence that actually teaches this term (never objectives)."""
    needle = (term or "").strip().lower()
    if not needle:
        return ""
    best = ""
    best_score = 0
    for claim in claims:
        text = student_safe_definition(str(claim or ""))
        if not text or needle not in text.lower():
            continue
        low = text.lower()
        score = 1
        # Strong preference: this term is the grammatical subject being defined.
        if (
            low.startswith(needle + " ")
            or low.startswith(needle + " is ")
            or low.startswith(needle + ":")
            or f"{needle} is " in low[: max(48, len(needle) + 8)]
            or f"{needle} are " in low[: max(48, len(needle) + 8)]
            or f"{needle} means" in low[: max(48, len(needle) + 12)]
        ):
            score += 8
        elif "is when" in low or "is the" in low:
            # Weak: term is only mentioned inside another definition.
            score += 1
        if "students will" in low or "learning objective" in low:
            continue
        lead = low.split()[0] if low.split() else ""
        if lead and lead != needle and lead not in {"the", "a", "an", "for", "when", "in"}:
            # Another noun leads the sentence — probably not defining this term.
            score -= 5
        if len(text) > 40:
            score += 1
        if score > best_score:
            best_score = score
            best = text
    return best[:280] if best_score >= 5 else (best[:280] if best_score >= 3 else "")


def enrich_water_cycle_terms(topic: str, existing: list[str]) -> list[tuple[str, str]]:
    """If the lesson is about the water cycle, ensure canonical scientific terms."""
    blob = (topic or "").lower() + " " + " ".join(existing).lower()
    if not any(
        k in blob
        for k in ("water cycle", "evaporat", "precipitat", "condens", "water vapour", "water vapor")
    ):
        return []
    have = {e.lower() for e in existing}
    out: list[tuple[str, str]] = []
    for term, definition in WATER_CYCLE_TERMS:
        if term.lower() not in have and not is_junk_term(term):
            out.append((term, definition))
    return out


def build_student_definition(term: str, academic: str, *, topic: str = "") -> str:
    academic = student_safe_definition(academic)
    display = (term or "").strip()
    if not display or is_junk_term(display):
        return ""
    canonical = canonical_definition(display)
    if canonical:
        return canonical
    if academic:
        if len(academic.split()) > 28:
            first = re.split(r"(?<=[.!?])\s+", academic)[0]
            return first.strip()
        return academic
    # Never emit hollow filler ("X is taught in this lesson") — empty means skip.
    return ""


def normalize_vocab_items(
    terms: list[Any],
    *,
    topic: str = "",
    claims: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter junk and attach student-safe, claim-grounded definitions."""
    cleaned_claims: list[str] = []
    for c in claims or []:
        fixed = clean_learner_claim(str(c)) or student_safe_definition(str(c))
        if fixed and "one of the ideas taught" not in fixed.lower():
            cleaned_claims.append(fixed)
    claims = cleaned_claims
    topic = clean_topic(topic)
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    waterish = any(
        k in topic.lower()
        for k in ("water cycle", "evaporat", "precipitat", "condens")
    )
    chemistryish = any(
        k in topic.lower() for k in ("acid", "base", "salt", "litmus", "neutralis", "neutraliz")
    )
    metalsish = any(
        k in topic.lower()
        for k in ("metal", "non-metal", "nonmetal", "malleab", "ductil", "corrosion")
    )

    for item in terms:
        if isinstance(item, dict):
            term = str(item.get("term") or item.get("word") or "").strip()
            definition = student_safe_definition(
                str(
                    item.get("definition")
                    or item.get("academic_definition")
                    or item.get("simple_explanation")
                    or ""
                )
            )
            example = student_safe_definition(
                str(item.get("example") or item.get("example_sentence") or "")
            )
        else:
            term = str(item or "").strip()
            definition = ""
            example = ""
        if not term or is_junk_term(term):
            continue
        # Repair OCR crumbs in the term itself before accepting
        term = repair_ocr_prose(term).strip() or term
        if is_junk_term(term):
            continue
        key = term.lower()
        if key in seen:
            continue

        # Prefer scientific canonical wording for known curriculum packs
        canon = canonical_definition(term)
        if (waterish or chemistryish or metalsish) and canon:
            definition = canon
        elif not definition or is_ocr_garbage_claim(definition) or "one of the ideas taught" in definition.lower():
            definition = canon or definition_from_claims(term, claims)
        if not definition:
            definition = build_student_definition(term, "", topic=topic)
        definition = student_safe_definition(definition) or ""
        # Reject recycled blurbs: card must define THIS term as the sentence subject.
        stem = key.rstrip("s")

        def _definition_about(defn: str, needle: str) -> bool:
            low = (defn or "").lower().strip()
            n = (needle or "").lower().strip()
            if not low or not n:
                return False
            head = low[: max(48, len(n) + 16)]
            return (
                head.startswith(n + " ")
                or head.startswith(n + " is")
                or head.startswith(n + " are")
                or head.startswith("the " + n)
                or f"{n} is " in low[:90]
                or f"{n} are " in low[:90]
                or f"{n} means " in low[:90]
            )

        teaches_term = bool(canon) or _definition_about(definition, key) or _definition_about(
            definition, stem
        )
        if not teaches_term:
            rebuilt = definition_from_claims(term, claims) or ""
            if rebuilt and (
                _definition_about(rebuilt, key) or _definition_about(rebuilt, stem)
            ):
                definition = student_safe_definition(rebuilt) or ""
                teaches_term = True
        if (
            not definition
            or not teaches_term
            or "is taught in this lesson" in definition.lower()
            or "one of the ideas taught" in definition.lower()
            or is_ocr_garbage_claim(definition)
        ):
            continue

        seen.add(key)
        if not example or is_teacher_facing_text(example) or is_ocr_garbage_claim(example):
            example = student_safe_definition(definition_from_claims(term, claims) or "") or definition

        picture = picture_cue_for_term(term, definition=definition)
        out.append(
            {
                "term": term[:1].upper() + term[1:] if term else term,
                "definition": definition,
                "academic_definition": definition,
                "simple_explanation": build_student_definition(term, definition, topic=topic) or definition,
                "example": example[:220],
                "example_sentence": example[:220],
                "picture": picture,
                "lesson_context": f"You need the word {term} to explain {topic} clearly.",
            }
        )

    for term, definition in (
        enrich_water_cycle_terms(topic, list(seen))
        + enrich_acids_bases_salts_terms(topic, list(seen))
        + enrich_fractions_terms(topic, list(seen))
        + enrich_electricity_terms(topic, list(seen))
        + enrich_metals_nonmetals_terms(topic, list(seen))
    ):
        if term.lower() in seen:
            continue
        seen.add(term.lower())
        out.append(
            {
                "term": term,
                "definition": definition,
                "academic_definition": definition,
                "simple_explanation": definition,
                "example": definition,
                "example_sentence": definition,
                "picture": picture_cue_for_term(term, definition=definition),
                "lesson_context": f"{term} is a key idea in {topic}.",
            }
        )

    priority = {
        "evaporation": 0,
        "condensation": 1,
        "precipitation": 2,
        "collection": 3,
        "transpiration": 4,
        "water vapour": 5,
        "water vapor": 5,
        "water cycle": 6,
        "runoff": 7,
        "acid": 0,
        "base": 1,
        "salt": 2,
        "indicator": 3,
        "litmus": 4,
        "neutralisation": 5,
        "neutralization": 5,
        "baking soda": 6,
    }
    out.sort(key=lambda r: priority.get(str(r.get("term") or "").lower(), 50))
    return out[:12]
