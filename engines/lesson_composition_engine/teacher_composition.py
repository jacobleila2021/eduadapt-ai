"""Teacher Composition Framework — educational writing without topic template banks.

Educational banks supply classroom materials; the composer weaves them with verified claims
into teacher-authored narratives (curiosity → explanation → example → misconception → recap).

Not a new intelligence engine — LCE authorship only.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping

from engines.lesson_composition_engine.educational_banks import lookup_banks

TEACHER_COMPOSITION_SMOKE_OK = True

# Forbidden learner-facing scaffolds (fail composition if emitted)
FORBIDDEN_SCAFFOLDS = (
    "notice this in the real world",
    "this is an important concept",
    "this lesson explains",
    "today you will",
    "in this lesson",
    "in this chapter",
    "remember:",
    "checkpoint",
    "core idea",
    "now let's",
    "hold that thought",
    "helps you explain the topic clearly",
    "find a living moment with",
    "connect it to this accurate meaning",
    "two scenes — one steady meaning",
    "that living picture is what we mean by",
    "what familiar action with",
    "what single safe observation of",
    "in plain language,",
    "picture this idea happening at home",
    "that careful wording is the meaning",
    "that careful meaning is what we call",
)

_CLAIM_VERBS = (
    "is calculated on",
    "are calculated on",
    "is calculated",
    "are calculated",
    "breaks",
    "break",
    "traps",
    "trap",
    "slows",
    "slow",
    "breathes",
    "breathe",
    "pushes",
    "push",
    "pulls",
    "pull",
    "changes",
    "change",
    "starts",
    "start",
    "stops",
    "stop",
    "grows",
    "grow",
    "stores",
    "store",
    "saves",
    "save",
    "joins",
    "join",
    "connects",
    "connect",
    "turns",
    "turn",
    "becomes",
    "become",
    "forms",
    "form",
    "makes",
    "make",
    "means",
    "mean",
    "includes",
    "include",
    "shows",
    "show",
    "needs",
    "need",
    "helps",
    "help",
    "carries",
    "carry",
    "releases",
    "release",
    "absorbs",
    "absorb",
    "travels",
    "travel",
    "flows",
    "flow",
    "compares",
    "compare",
    "protects",
    "protect",
    "applies",
    "apply",
    "choose",
    "chooses",
    "must",
    "increases",
    "increase",
    "decreases",
    "decrease",
    "names",
    "name",
    "is",
    "are",
    "was",
    "were",
)

STOP = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "is",
    "are",
    "was",
    "were",
    "be",
    "as",
    "by",
    "from",
    "with",
    "that",
    "this",
    "it",
    "into",
    "when",
    "than",
    "then",
    "can",
    "may",
    "will",
    "does",
    "do",
    "not",
    "its",
    "their",
    "your",
    "our",
}


def _clip(text: str, max_words: int = 42) -> str:
    words = (text or "").strip().split()
    out = " ".join(words[:max_words]).rstrip(",;:") if words else ""
    if out and out[-1] not in ".!?":
        out += "."
    return out


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z\-']{2,}", text or "")


def _content_words(text: str) -> list[str]:
    return [w for w in _tokens(text) if w.lower() not in STOP]


def _stable_pick(seed: str, options: list[str]) -> str:
    if not options:
        return ""
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return options[int(digest[:8], 16) % len(options)]


def _article(noun: str) -> str:
    """Indefinite article, or empty for plurals / mass nouns that need none."""
    raw = (noun or "").strip()
    n = raw.lower()
    if not n:
        return "a"
    # Multi-word or clearly plural → prefer "the" / bare
    if " " in n or _is_plural_label(raw):
        return "the"
    if n in {
        "rice",
        "bread",
        "steam",
        "rain",
        "snow",
        "ice",
        "ash",
        "water",
        "air",
        "heat",
        "light",
        "interest",
        "money",
        "soil",
        "blood",
        "food",
        "friction",
        "pressure",
        "force",
        "energy",
        "sediment",
        "sunlight",
        "oxygen",
        "digestion",
        "respiration",
        "photosynthesis",
        "evaporation",
        "condensation",
        "friction",
        "magma",
        "lava",
        "ash",
        "steam",
        "magnetism",
        "heat",
        "sound",
        "speed",
        "vapour",
        "vapor",
        "condensation",
        "precipitation",
        "collection",
    }:
        return ""
    if n[0] in "aeiou":
        return "an"
    return "a"


def _with_article(noun: str) -> str:
    art = _article(noun)
    n = (noun or "").strip()
    return f"{art} {n}".strip() if art else n


def _idea_label(name: str) -> str:
    """Singular-ish label for natural subject–verb grammar in hooks."""
    n = (name or "").strip()
    if not n:
        return "this idea"
    low = n.lower()
    if low.endswith("ies") and len(n) > 4:
        return n[:-3] + ("Y" if n[-3].isupper() else "y")
    if low.endswith(("sses", "ushes", "ches", "xes")):
        return n[:-2]
    if low.endswith("s") and not low.endswith(("ss", "us", "is", "ous", "ics", "nes")):
        return n[:-1]
    return n


def _is_plural_label(name: str) -> bool:
    low = (name or "").strip().lower()
    if not low:
        return False
    if low.endswith(("ss", "us", "is", "ous", "ics", "ness", "water", "law", "interest")):
        return False
    return low.endswith("s")


def _be_verb(name: str) -> str:
    return "are" if _is_plural_label(name) else "is"


_AUX_VERBS = {
    "must",
    "can",
    "may",
    "will",
    "should",
    "would",
    "could",
    "do",
    "does",
    "did",
    "has",
    "have",
    "had",
    "is",
    "are",
    "was",
    "were",
    "be",
}

_BASE_VERBS = {
    "come",
    "go",
    "give",
    "take",
    "put",
    "make",
    "let",
    "keep",
    "hold",
    "show",
    "grow",
    "fall",
    "rise",
    "feel",
    "need",
    "help",
    "cover",
    "carry",
    "apply",
    "protect",
    "support",
    "depend",
    "affect",
    "reduce",
    "remove",
    "store",
    "save",
    "fix",
    "exploit",
    "cross",
    "raise",
    "mean",
    "include",
    "connect",
    "explain",
    "compare",
    "measure",
    "travel",
    "flow",
    "form",
    "turn",
    "become",
    "release",
    "absorb",
    "satisfy",
    "signal",
    "practice",
    "practise",
    "wear",
    "attract",
    "repel",
    "produce",
    "travel",
    "ignore",
    "observe",
    "explain",
    "taste",
    "contain",
    "contains",
    "pump",
    "pumps",
    "let",
    "lets",
    "gather",
    "gathers",
    "return",
    "returns",
}

_WEAK_LABEL_WORDS = {
    "simple",
    "fresh",
    "rule",
    "area",
    "linear",
    "active",
    "passive",
    "formal",
    "clear",
    "local",
    "fundamental",
    "balanced",
    "good",
    "democracy",
    "people",
    "both",
    "each",
    "every",
    "one",
    "two",
    "it",
    "they",
}


def _explicit_verb(token: str) -> bool:
    """Known verb (any inflection) — a confident sentence pivot."""
    t = token.strip(".,;:()[]\"'").lower()
    if not t:
        return False
    if t in _AUX_VERBS or t in _BASE_VERBS:
        return True
    if t in {v.split()[0] for v in _CLAIM_VERBS}:
        return True
    for suffix in ("es", "s", "ed", "ing"):
        if t.endswith(suffix) and len(t) > len(suffix) + 2:
            stem = t[: -len(suffix)]
            if stem in _BASE_VERBS or f"{stem}e" in _BASE_VERBS:
                return True
    return False


def _looks_like_verb(token: str) -> bool:
    """Heuristic finite-verb detector so any claim can be parsed (no fixed verb bank)."""
    raw = token.strip(".,;:()[]\"'")
    if not raw or len(raw) < 2:
        return False
    # Capitalised tokens in mid-sentence are usually nouns ("Magnets attract…")
    if raw[0].isupper() and not raw.isupper():
        return False
    t = raw.lower()
    if _explicit_verb(t):
        return True
    if t in STOP:
        return False
    if len(t) > 4 and t.endswith("ing"):
        return True
    if len(t) > 3 and t.endswith("ed"):
        return True
    if len(t) > 3 and t.endswith(("es", "ys")):
        return True
    # Bare plural "-s" is too ambiguous for noun phrases — only trust known verbs
    if len(t) > 3 and t.endswith("s") and not t.endswith(("ss", "us", "is", "ous", "ics")):
        return _explicit_verb(t) or t in {v.split()[0] for v in _CLAIM_VERBS}
    return False


def _clean_np(phrase: str) -> str:
    p = re.sub(r"^(a|an|the)\s+", "", (phrase or "").strip(), flags=re.IGNORECASE)
    words = [w.strip(".,;:()[]\"'") for w in p.split() if w.strip(".,;:()[]\"'")]
    while words and words[0].lower() in STOP | _COLOR_ORPHANS | _PROP_AVOID:
        words.pop(0)
    while words and (
        words[-1].lower() in STOP | _COLOR_ORPHANS | _PROP_AVOID
        or _explicit_verb(words[-1])
        or words[-1].lower().endswith(("ed", "ing"))
    ):
        words.pop()
    while words and words[0].lower() in _COLOR_ORPHANS | {"one", "two", "some", "many", "any"}:
        words.pop(0)
    return " ".join(words).lower().strip()


def extract_concept_label(claim: str, topic: str = "", *, avoid: set[str] | None = None) -> str:
    """Teachable label from a verified claim — parsed from claim grammar, never a topic bank.

    ``avoid`` holds already-used labels so sibling claims stay distinct instead of
    collapsing into "Topic (2)".
    """
    used = {a.lower() for a in (avoid or set())}
    text = (claim or "").strip()
    topic_s = (topic or "").strip()
    if not text:
        return topic_s or "this idea"
    low = text.lower()

    if topic_s and low.startswith(topic_s.lower()) and topic_s.lower() not in used:
        return topic_s
    if (
        topic_s
        and topic_s.lower() in low[: max(28, len(topic_s) + 12)]
        and topic_s.lower() not in used
    ):
        return topic_s

    tokens = text.split()
    stripped = [w.strip(".,;:()[]\"'") for w in tokens]
    # The parsed subject is the most faithful label ("Carbon dioxide", not "Carbon").
    parsed_subject = ""
    subj = re.sub(r"^(a|an|the)\s+", "", _claim_parts(text, topic_s)["subject"], flags=re.IGNORECASE)
    subj_words = [w for w in subj.split() if w]
    # A compound subject ("Carbon dioxide and water") teaches best as its head phrase.
    for cut, word in enumerate(subj_words):
        if word.lower() in {"and", "or"} and cut > 0:
            subj_words = subj_words[:cut]
            break
    while subj_words and subj_words[-1].lower() in STOP:
        subj_words.pop()
    if 1 <= len(subj_words) <= 3:
        parsed_subject = " ".join(subj_words)
    # Subject phrase = tokens before the sentence verb (max 3 words).
    # A known verb wins over an ambiguous plural noun, so "Green plants make…"
    # yields "Green plants" rather than "Green".
    verb_at = -1
    for idx in range(1, min(len(stripped), 4)):
        if _explicit_verb(stripped[idx]):
            verb_at = idx
            break
    if verb_at < 0:
        for idx in range(1, min(len(stripped), 4)):
            if _looks_like_verb(stripped[idx]):
                verb_at = idx
                break
    candidates: list[str] = []
    if parsed_subject:
        candidates.append(parsed_subject)
    if verb_at > 0:
        phrase = " ".join(tokens[:verb_at]).strip(" ,;:-")
        phrase = re.sub(
            r"^(In|On|At|For|With)\s+(a|an|the)\s+", "", phrase, flags=re.IGNORECASE
        ).strip()
        phrase = re.sub(r"^(A|An|The)\s+", "", phrase, flags=re.IGNORECASE).strip()
        words = phrase.split()
        # Never end a label on a connective ("Rights come with")
        while words and words[-1].lower() in STOP:
            words.pop()
        phrase = " ".join(words)
        if phrase:
            # Gerund openers read better with their object ("Fixing leaks")
            if len(words) == 1 and words[0].lower().endswith("ing") and verb_at < len(stripped):
                candidates.append(f"{phrase} {stripped[verb_at]}")
            if len(words) == 1 and words[0].lower() in _WEAK_LABEL_WORDS and topic_s:
                candidates.append(topic_s)
            candidates.append(phrase)
    # Predicate-derived label distinguishes sibling claims about the same subject
    if verb_at > 0 and verb_at + 1 < len(stripped):
        rest_words = [w for w in stripped[verb_at + 1 :] if w.lower() not in STOP and len(w) >= 3]
        # Skip a leading participle ("measured in square units" → "Square units")
        while rest_words and _looks_like_verb(rest_words[0]):
            rest_words.pop(0)
        if len(rest_words) >= 2:
            candidates.append(f"{rest_words[0].capitalize()} {rest_words[1]}")
        elif rest_words:
            candidates.append(rest_words[0].capitalize())
    if topic_s:
        candidates.append(topic_s)

    for cand in candidates:
        c = cand.strip()
        words = c.split()
        if not c or len(c) < 3 or len(words) > 6:
            continue
        if len(words) == 1 and c.lower() in _WEAK_LABEL_WORDS:
            continue
        if c.lower() in used:
            continue
        # A teachable label is a noun phrase — never carry a verb or participle
        if any(
            w.lower().endswith("ing") or _explicit_verb(w.lower())
            for w in words[1:]
        ):
            continue
        if len(words) > 1 and words[-1].lower() in STOP:
            continue
        return c[:1].upper() + c[1:]
    # Last resort: any distinct content word
    for word in stripped:
        w = word.strip()
        if len(w) >= 4 and w.lower() not in STOP and w.lower() not in used:
            return w.capitalize()
    return topic_s or "this idea"


def _claim_parts(claim: str, concept: str) -> dict[str, str]:
    """Parse subject / verb / rest from any claim — never invent a fake 'is' split."""
    text = (claim or "").strip().rstrip(".")
    # Collect candidate verbs from the bank and from token heuristics,
    # then keep the leftmost (longest on ties) so "lets … flow" does not pick "flow".
    candidates: list[tuple[int, str, int]] = []
    for verb in _CLAIM_VERBS:
        m = re.search(rf"\b{re.escape(verb)}\b", text, flags=re.IGNORECASE)
        if m:
            candidates.append((m.start(), verb.lower(), m.end()))
    stripped = [w.strip(".,;:()[]\"'") for w in text.split()]
    offset = 0
    for idx, tok in enumerate(stripped):
        # Approximate character offset of this token
        found = text.lower().find(tok.lower(), offset)
        if found < 0:
            found = offset
        if idx >= 1 and (_explicit_verb(tok) or _looks_like_verb(tok)):
            nxt = stripped[idx + 1] if idx + 1 < len(stripped) else ""
            if nxt and (_explicit_verb(nxt) or _looks_like_verb(nxt)) and not _explicit_verb(tok):
                offset = found + len(tok)
                continue
            candidates.append((found, tok.lower(), found + len(tok)))
        offset = found + len(tok)
    if candidates:
        candidates.sort(key=lambda c: (c[0], -len(c[1])))
        start, verb, end = candidates[0]
        # Skip leading whitespace after verb for rest
        while end < len(text) and text[end].isspace():
            end += 1
        return {
            "subject": text[:start].strip() or concept,
            "verb": verb,
            "rest": text[end:].strip(),
            "full": text,
        }
    return {"subject": concept or text, "verb": "", "rest": text, "full": text}


# Words that should never become scene props (verbs, abstract fillers, quantifiers)
_PROP_AVOID = {
    "interest",
    "principal",
    "percent",
    "percentage",
    "ratio",
    "democracy",
    "election",
    "algorithm",
    "data",
    "password",
    "process",
    "system",
    "lesson",
    "concept",
    "idea",
    "example",
    "student",
    "learner",
    "teacher",
    "increase",
    "increases",
    "decrease",
    "decreases",
    "using",
    "through",
    "during",
    "before",
    "after",
    "names",
    "name",
    "means",
    "mean",
    "shows",
    "show",
    "makes",
    "make",
    "helps",
    "help",
    "needs",
    "need",
    "each",
    "every",
    "many",
    "some",
    "same",
    "other",
    "unit",
    "units",
    "area",
    "time",
    "order",
    "clear",
    "true",
    "real",
    "single",
    "whole",
    "per",
    "via",
    "onto",
    "into",
    "from",
    "cooler",
    "hotter",
    "denser",
    "faster",
    "slower",
    "greater",
    "lesser",
    "higher",
    "lower",
    "amount",
}


def _domain_places(claim: str, topic: str) -> list[str]:
    """Situational frames from claim meaning — composition operators, not topic banks."""
    low = f"{claim} {topic}".lower()

    def _hits(keys: tuple[str, ...]) -> int:
        n = 0
        for k in keys:
            if " " in k:
                if k in low:
                    n += 1
            elif re.search(rf"\b{re.escape(k)}\b", low):
                n += 1
        return n

    scored = [
        (("mangrove", "sediment", "water", "rain", "river", "ocean", "fog", "cloud", "puddle", "tap"),
         ["near water", "outdoors after rain", "beside a puddle"]),
        (("volcano", "volcanoes", "magma", "lava", "ash", "erupt", "crust"),
         ["near rocky ground", "outdoors on a hillside", "looking at a mountain landscape"]),
        (("digest", "digestion", "stomach", "nutrient", "nutrients", "meal", "tiffin", "onion", "salt", "cook", "kitchen"),
         ["at mealtime", "in the kitchen"]),
        (("plant", "leaf", "sunlight", "photosynthesis", "chlorophyll", "seed", "germinate", "forest", "green plants"),
         ["outdoors in sunlight", "beside a green plant"]),
        (("force", "pressure", "friction", "push", "pull", "brake", "wheel", "magnet", "magnets", "magnetism", "circuit", "current"),
         ["with your hands", "when you push a door", "on a bike or cart"]),
        (("sound", "vibration", "vibrates", "shadow", "reflect", "heat", "thermometer", "cooler", "hotter"),
         ["in the classroom", "outdoors in clear light", "near a warm kettle"]),
        (("respiration", "breathe", "breathing", "oxygen", "energy"),
         ["after climbing stairs", "when you feel your pulse", "after a short run"]),
        (("float", "floating", "sinking", "sink", "dense", "density"),
         ["in a sink of water", "with a ball in a tub", "beside a puddle"]),
        (("speed", "distance travelled", "motion"),
         ["on the way to school", "watching a ball roll", "on a bike or cart"]),
        (("fraction", "share", "half", "third", "percent", "ratio", "divide", "equal part", "laddoo"),
         ["when sharing food fairly", "with equal pieces of one whole"]),
        (("map", "scale", "legend", "symbol", "campus"),
         ["looking at a map", "on a campus plan"]),
        (("trade", "market", "merchant", "price", "money", "goods", "buy", "route"),
         ["in a market", "when people exchange goods", "along a busy road"]),
        (("vote", "election", "right", "law", "democracy", "complaint"),
         ["in a fair classroom vote", "when rules protect everyone"]),
        (("heart", "pulse", "breathe", "blood", "oxygen", "exercise"),
         ["after climbing stairs", "when you feel your pulse"]),
        (("rust", "iron", "rusting", "dissolve", "melt", "ice"),
         ["on an outdoor metal gate", "in a simple kitchen test"]),
        (("acid", "acids", "base", "bases", "litmus", "neutralisation", "neutralization"),
         ["in a simple classroom test", "with safe indicator paper", "in the science lab"]),
        (("password", "algorithm", "sort", "data", "internet", "click"),
         ["on a shared computer", "when following clear steps"]),
        (("paragraph", "sentence", "letter", "recipe", "bias", "infer", "narrative"),
         ["while reading a short text", "when writing one clear paragraph"]),
    ]
    domains: list[tuple[int, list[str]]] = []
    for keys, places in scored:
        n = _hits(keys)
        if re.search(r"\bfood\b", low) and not re.search(
            r"\b(digest|digestion|nutrient|nutrients|meal|stomach)\b", low
        ):
            if keys[0] in {"digest", "digestion"}:
                n = 0
        if n:
            domains.append((n, places))
    domains.sort(key=lambda x: -x[0])
    places: list[str] = []
    for _, group in domains[:2]:
        places.extend(group)
    if not places:
        places = ["in a familiar everyday moment", "around something you can safely observe", "in ordinary life"]
    seen: set[str] = set()
    out: list[str] = []
    for p in places:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


_COLOR_ORPHANS = {
    "green",
    "blue",
    "red",
    "black",
    "white",
    "yellow",
    "brown",
    "grey",
    "gray",
    "across",
    "through",
    "using",
    "along",
    "all",
    "too",
    "small",
    "large",
    "straight",
    "complete",
    "equal",
    "living",
    "sour",
    "soapy",
    "type",
    "kinds",
    "kind",
    "see",
    "whom",
    "who",
    "shape",
    "motion",
    "reproduce",
    "travelled",
    "traveled",
}


def _scene_nouns(claim: str, topic: str) -> list[str]:
    """Concrete nouns from claim grammar (subject / object) — never stock props."""
    parts = _claim_parts(claim, topic)
    nouns: list[str] = []

    def _add(raw: str) -> None:
        clean = _clean_np(raw)
        if not clean or len(clean) < 3:
            return
        if clean in _PROP_AVOID or clean in _COLOR_ORPHANS:
            return
        if clean in {"things", "thing", "object", "objects", "idea", "ideas"}:
            return
        if clean not in nouns:
            nouns.append(clean)

    _add(parts.get("subject") or "")
    # Object-ish chunks from the rest: take noun groups between prepositions
    rest = parts.get("rest") or ""
    # Prefer trailing concrete phrase ("… of cells", "… into nutrients")
    for m in re.finditer(
        r"(?:\b(?:of|into|on|onto|from|with|around|as|to)\s+)([^,.;]+)",
        rest,
        flags=re.IGNORECASE,
    ):
        _add(m.group(1))
    # First content chunk of rest if still thin
    if len(nouns) < 2 and rest:
        chunk = []
        for w in rest.split():
            low = w.strip(".,;:()[]\"'").lower()
            if low in STOP or low in _PROP_AVOID or low in _COLOR_ORPHANS:
                if chunk:
                    break
                continue
            if _looks_like_verb(w) or _explicit_verb(w) or low.endswith(("ed", "ing")):
                if chunk:
                    break
                continue
            chunk.append(low)
            if len(chunk) >= 3:
                break
        if chunk:
            _add(" ".join(chunk))
    # Topic only as last resort, and only multi-word educational titles
    if len(nouns) < 2 and topic and len(topic.split()) >= 2:
        _add(topic)
    if not nouns:
        for w in _content_words(claim):
            low = w.lower()
            if (
                len(low) >= 4
                and low not in _PROP_AVOID
                and low not in _COLOR_ORPHANS
                and not low.endswith(("ed", "ing", "ly"))
                and not _looks_like_verb(w)
            ):
                nouns.append(low)
                if len(nouns) >= 3:
                    break
    nouns.sort(key=lambda n: (0 if " " in n else 1, -len(n)))
    return nouns[:6] or ["this evidence"]


def _scene_props(topic: str, claim: str, seed: str) -> tuple[str, str]:
    """Compose place + prop from claim/topic meaning — never topic paragraph banks."""
    places = _domain_places(claim, topic)
    props = _scene_nouns(claim, topic)
    topic_toks = {w.lower() for w in topic.split()}
    subj = _clean_np(_claim_parts(claim, topic).get("subject") or "")
    # Prefer the claim subject first when ranking props for scenes
    ranked = sorted(
        props,
        key=lambda p: (
            0 if p == subj else 1,
            0 if (" " in p and p in (claim or "").lower()) else 1,
            0 if p not in topic_toks and p.lower() != topic.lower() else 2,
            -len(p),
        ),
    )
    props = ranked[:3] or props
    # Drop any prop that still embeds a verb (e.g. "circuit lets current")
    clean_props: list[str] = []
    for p in props:
        words = p.split()
        kept: list[str] = []
        for w in words:
            if _explicit_verb(w) or w.lower() in {"lets", "let", "make", "makes"}:
                break
            kept.append(w)
        piece = " ".join(kept).strip()
        if piece and piece not in clean_props:
            clean_props.append(piece)
    props = clean_props or props
    place = _stable_pick(seed + "|place", places)
    # Prefer the best-ranked prop; only vary for second examples
    prop = props[0] if "|a" in seed or "|hook" in seed else _stable_pick(seed + "|prop", props)
    if prop.lower() == topic.lower() or prop in topic_toks:
        alts = [p for p in props if p.lower() != topic.lower() and p not in topic_toks]
        if alts:
            prop = _stable_pick(seed + "|prop_alt", alts)
    if "|b" in seed or "|c" in seed:
        alts = [p for p in props if p != prop] or props
        prop = _stable_pick(seed + "|prop2", alts)
    return place, prop


def infer_age_band(board: Mapping[str, Any]) -> str:
    raw = str(
        board.get("age_band")
        or board.get("grade_band")
        or board.get("grade")
        or ""
    ).lower()
    if any(g in raw for g in ("1", "2", "3", "4", "primary", "lower")):
        return "younger"
    if any(g in raw for g in ("9", "10", "11", "12", "senior", "upper")):
        return "older"
    return "middle"


def analyse_claim(claim: str, concept: str = "") -> dict[str, Any]:
    text = (claim or "").strip()
    words = _content_words(text)
    low = text.lower()
    verbs = [
        w
        for w in words
        if w.lower().endswith(("es", "ed", "ing"))
        or w.lower()
        in {
            "turns",
            "makes",
            "moves",
            "flows",
            "carries",
            "breaks",
            "forms",
            "travels",
            "compares",
            "shows",
            "needs",
            "helps",
            "changes",
            "releases",
            "absorbs",
            "pushes",
            "pulls",
        }
    ]
    nouns = [w for w in words if w[:1].isupper() or len(w) >= 5][:6]
    if concept and concept not in nouns:
        nouns = [concept] + nouns
    style = "question"
    if any(k in low for k in ("turn", "become", "flow", "journey", "cycle", "process", "stage")):
        style = "observation"
    elif any(k in low for k in ("more", "less", "higher", "lower", "same", "compare", "than")):
        style = "problem"
    elif any(k in low for k in ("is a", "means", "defined", "called")):
        style = "analogy"
    elif any(k in low for k in ("experiment", "test", "measure", "observe")):
        style = "experiment"
    return {
        "claim": text,
        "concept": concept or (nouns[0] if nouns else "this idea"),
        "nouns": nouns,
        "verbs": verbs,
        "style": style,
        "words": words,
    }


def compose_hook(
    *,
    topic: str,
    claims: list[str],
    concepts: list[str],
    age_band: str = "middle",
    voice: str = "standard",
    subject: str = "",
) -> str:
    """Dynamic hook — prefer educational bank materials when covered."""
    if not claims and not concepts:
        raise CompositionFailure("Cannot compose hook without claims or concepts.")
    banks = lookup_banks(topic, subject=subject, claim=claims[0] if claims else "")
    if banks.get("covered") and banks.get("hook"):
        seed_hook = str(banks["hook"]).strip()
        # Each profile enters through different material — never the same opener re-labelled.
        question = str(banks.get("question") or "").strip()
        real_world = str(banks.get("real_world") or "").strip()
        second = str(banks.get("example2") or "").strip()
        if voice == "visual":
            return (
                f"Before any words, look at the picture. {second or seed_hook} "
                f"Hold that image — the rest of this page explains it."
            )
        if voice == "auditory":
            opener = question or seed_hook
            return (
                f"Here is a question worth saying out loud before you read anything: {opener} "
                f"Answer it in a whisper, even if you are guessing."
            )
        if voice == "ell":
            return (
                f"First a picture, then the words. {real_world or seed_hook} "
                f"You will learn to say this in your own English by the end."
            )
        if voice in {"ld", "dyslexia"}:
            short = " ".join(seed_hook.split()[:16]).rstrip(",.;") + "."
            return f"One small start.\n{short}\nThat is all for now."
        if voice == "adhd":
            challenge = question or seed_hook
            return f"Two-minute challenge: {challenge} Beat the clock, then keep moving."
        if voice == "autism":
            return (
                f"Today follows the same steps as always.\n"
                f"First, one thing to notice: {seed_hook}"
            )
        if voice == "parent":
            return (
                f"Something to try together tonight: {real_world or seed_hook} "
                f"Let your child do the noticing and the talking."
            )
        if voice == "teacher":
            return (
                f"Open with this demonstration: {seed_hook} "
                f"Hold the explanation back until students have described what they saw."
            )
        return seed_hook
    # Fallback dynamic composition when banks miss (benchmark treats uncovered topics as failures)
    claim = claims[0] if claims else f"{concepts[0]} is central to {topic}."
    concept = concepts[0] if concepts else extract_concept_label(claim, topic)
    if concepts and len(str(concepts[0]).split()) == 1:
        concept = extract_concept_label(claim, topic) or concepts[0]
    info = analyse_claim(claim, str(concept))
    n0 = _idea_label(str(concept))
    seed = f"{topic}|{claim}|hook|{voice}"
    styles = ["observation", "story", "question", "problem", "analogy", "experiment", str(info["style"])]
    if any(k in f"{topic} {claim}".lower() for k in ("law", "democra", "right", "interest", "integer", "area", "ratio")):
        styles = ["observation", "story", "question", "experiment", "observation"]
    style = _stable_pick(seed, styles)
    claim_soft = _clip(claim, 22).rstrip(".")
    place, prop = _scene_props(topic, claim, seed + "|hook")
    scene = _with_article(prop)
    if prop in {"this evidence", "evidence"} or "this evidence" in scene:
        if age_band == "younger":
            return f"Why does this matter in real life? {claim_soft}."
        if voice == "teacher":
            return f"Open with verified evidence: {claim_soft}."
        return (
            f"Start {topic} from this true idea, not from a memorised label: {claim_soft}."
        )

    if voice == "visual":
        return (
            f"Before you read, look for {scene} on the {topic} diagram. "
            f"What does that picture already hint about {n0.lower()}?"
        )
    if voice == "auditory":
        return (
            f"Listen first: {claim_soft}. "
            f"Say that line once, then ask where {scene} would fit."
        )
    if voice == "ell":
        return f"New word path for {topic}: picture {scene}. Then hold this true idea: {claim_soft}."
    if voice in {"ld", "dyslexia"}:
        return f"Small start for {topic}: look at {scene}. One clear idea: {claim_soft}."
    if voice == "adhd":
        return f"2-minute opener: find {scene}. Match it fast to this idea — {claim_soft}."
    if voice == "autism":
        return (
            f"Routine start for {topic}. Step 1: look at {scene}. "
            f"Step 2: hold this fact — {claim_soft}."
        )
    if voice == "parent":
        return (
            f"Home opener for {topic}: look for {scene}. "
            f"Ask your child what it has to do with: {claim_soft}."
        )
    if voice == "teacher":
        return f"Launch {topic} from a quick demo with {scene}. Anchor to: {claim_soft}."

    if style == "story":
        return (
            f"{place.capitalize()}, keep {scene} in view for half a minute. "
            f"As soon as you can say “{claim_soft}”, you have met {n0.lower()}."
        )
    if style == "observation":
        return (
            f"Watch {scene} {place}. Have you seen this idea at work there? "
            f"{claim_soft}."
        )
    if style == "experiment":
        return (
            f"{place.capitalize()}, try one careful look at {scene}. "
            f"What must be true if {n0.lower()} is real? {claim_soft}."
        )
    if style == "problem":
        return (
            f"What goes wrong if someone ignores {n0.lower()} around {scene}? "
            f"Start from this evidence: {claim_soft}."
        )
    if style == "analogy":
        return (
            f"{place.capitalize()}, think about {scene}. "
            f"In what precise way does it carry the same job as {n0.lower()}? {claim_soft}."
        )
    if age_band == "younger":
        return f"Why does {n0.lower()} matter around {scene}? Hold this true line: {claim_soft}."
    if age_band == "older":
        return f"Why does this stay true around {scene}: {claim_soft}?"
    return (
        f"Why does {n0.lower()} sit at the heart of {topic}? "
        f"Start from {scene} {place} and test the idea: {claim_soft}."
    )


def compose_simple_explanation(*, name: str, claim: str, age_band: str = "middle") -> str:
    """Child-facing restatement — never invent a fake 'Name is Name…' echo."""
    claim_s = (claim or "").strip().rstrip(".")
    if not claim_s:
        raise CompositionFailure(f"Cannot simplify empty claim for {name}.")
    parts = _claim_parts(claim_s, name)
    verb = (parts["verb"] or "").lower()
    rest = (parts["rest"] or "").strip()
    subject = (parts["subject"] or "").strip()
    nm = name.strip()
    be = _be_verb(nm)
    claim_low = claim_s.lower()
    name_low = nm.lower()
    subj_clean = re.sub(r"^(a|an|the)\s+", "", subject.lower()).strip()
    subject_matches = (
        subj_clean == name_low
        or claim_low.startswith(name_low + " ")
        or (subj_clean and (name_low == subj_clean or name_low in subj_clean or subj_clean in name_low))
    )

    if subject_matches and verb in {"is", "are", "was", "were"} and rest:
        core = f"{nm} {be} {rest}"
    elif subject_matches and verb in {"breaks", "break"}:
        core = f"{nm} takes large pieces and turns them into smaller useful parts"
        if rest:
            core = f"{core}: {rest}"
    elif subject_matches and verb in {"traps", "trap", "slows", "slow"}:
        catch = "catch and hold on to" if _is_plural_label(nm) else "catches and holds on to"
        slow = "slow down" if _is_plural_label(nm) else "slows down"
        action = catch if verb in {"traps", "trap"} else slow
        core = f"{nm} {action} {rest}" if rest else claim_s
    elif subject_matches and verb in {"names", "name", "means", "mean"}:
        core = claim_s
    elif subject_matches and verb in {"helps", "help", "makes", "make", "increases", "increase"}:
        # Prefer the verified claim's own grammar/capitalisation
        core = claim_s
    elif subject_matches and verb and rest:
        # Only rebuild when the label really is the claim's subject; a shortened
        # label ("Carbon" from "Carbon dioxide and water") would break agreement.
        if subj_clean and subj_clean != name_low:
            core = claim_s
        else:
            label = nm[:1].upper() + nm[1:] if nm else nm
            core = f"{label} {verb} {rest}"
    elif subject_matches:
        core = claim_s
    elif verb in {"is", "are", "was", "were"} and rest and subject:
        core = f"{claim_s} — keep that exact meaning when you use the word {nm.lower()}"
    else:
        core = f"{claim_s} — that is the meaning of {nm.lower()} here"

    core = re.sub(r"\s+", " ", core).strip().rstrip(".")
    if re.match(rf"(?i)^{re.escape(nm)}\s+{re.escape(be)}\s+{re.escape(nm)}\b", core):
        core = claim_s
    if re.search(rf"(?i)\b{re.escape(nm)}\s+{re.escape(be)}\s+{re.escape(nm)}\b", core):
        core = claim_s

    # A consequence the learner can act on — so this section teaches even if the
    # restated claim is trimmed as a repeat of the explanation above.
    use_it = _stable_pick(
        f"{nm}|{claim}|use",
        [
            f"In practice, that lets you look at a new situation and decide whether {nm.lower()} is really involved.",
            f"So when someone describes a situation to you, you can tell whether {nm.lower()} explains it or not.",
            f"That sentence is the test you apply whenever {nm.lower()} might be the reason behind something.",
            f"Once you hold that, you can predict what happens next in a situation involving {nm.lower()}.",
        ],
    )

    if age_band == "younger":
        return f"{core}. {use_it} Tell a friend in your own short sentence."
    if age_band == "older":
        return f"{core}. {use_it} Keep neighbouring ideas out of that sentence."
    closers = [
        f"If you can teach {nm.lower()} to a friend, you are ready to go deeper.",
        f"Say that once without looking, and {nm.lower()} is yours.",
        f"Test yourself: explain {nm.lower()} using only everyday words.",
        f"When that sentence comes out cleanly, {nm.lower()} is secure.",
    ]
    return f"{core}. {use_it} {_stable_pick(f'{nm}|{claim}|simple', closers)}"


def _scene_phrase(prop: str, name: str) -> str:
    """A scene a learner can actually picture, or an honest stand-in when the prop is thin."""
    p = re.sub(r"\s+", " ", (prop or "").strip().lower())
    words = p.split()
    unusable = (
        not p
        or len(words) > 3
        or " to " in f" {p} "
        or " of " in f" {p} "
        or p == name.strip().lower()
        or p in name.strip().lower()
    )
    if unusable:
        return "one real situation you have seen yourself"
    return _with_article(p)


def compose_examples(
    *,
    name: str,
    claim: str,
    topic: str,
    age_band: str = "middle",
    voice: str = "standard",
) -> list[str]:
    """Two distinct examples derived from claim meaning — not EXAMPLE_BANK."""
    seed = f"{topic}|{name}|{claim}|{voice}"
    place_a, prop_a = _scene_props(topic, claim, seed + "|a")
    place_b, prop_b = _scene_props(topic, claim, seed + "|b")
    if prop_b == prop_a:
        place_b, prop_b = _scene_props(topic, claim, seed + "|c")
    claim_s = _clip(claim, 24).rstrip(".")
    nm = name.lower()
    scene_a = _scene_phrase(prop_a, name)
    scene_b = _scene_phrase(prop_b, name)
    parts = _claim_parts(claim, name)
    verb = (parts["verb"] or "").lower()
    rest = (parts["rest"] or claim_s).strip()

    if voice == "visual":
        return [
            f"On the diagram, find the part that matches {scene_a}. That picture carries {nm}: {claim_s}.",
            f"Sketch a second icon for {scene_b}. If it still means {nm}, your picture is honest.",
        ]
    if voice == "auditory":
        return [
            f"Say this aloud while picturing {scene_a} {place_a}: {claim_s}. That spoken line is {nm}.",
            f"Now whisper a second case with {scene_b} {place_b}. Keep the same meaning of {nm}.",
        ]
    if voice == "ell":
        return [
            f"Look first: {scene_a} {place_a}. Word: {name}. Meaning: {claim_s}.",
            f"Now look at {scene_b} {place_b}. Same word: {name}. Same meaning.",
        ]
    if voice in {"ld", "dyslexia"}:
        return [
            f"Step picture — {scene_a} {place_a}. Meaning of {nm}: {claim_s}.",
            f"Second picture — {scene_b} {place_b}. Same meaning of {nm}.",
        ]
    if voice == "adhd":
        return [
            f"Quick win: spot {scene_a} {place_a}. Match it to {nm}: {claim_s}.",
            f"Second burst: {scene_b} {place_b}. Same {nm} meaning — move on.",
        ]
    if voice == "autism":
        return [
            f"Literal case A: {scene_a} {place_a}. Fact for {nm}: {claim_s}.",
            f"Literal case B: {scene_b} {place_b}. Same fact for {nm}.",
        ]
    if voice == "parent":
        return [
            f"Tonight at home, look for {scene_a}. Ask: how does this show {nm}? Listen for: {claim_s}.",
            f"Try a second home moment with {scene_b}. Praise clear wording about {nm}.",
        ]
    if voice == "teacher":
        return [
            f"Cold-call demo seed: {scene_a} {place_a} → {nm} = {claim_s}.",
            f"Second case for exit ticket: {scene_b} {place_b} with the same meaning of {nm}.",
        ]

    if verb in {"turns", "turn", "becomes", "become", "forms", "form"}:
        ex1 = (
            f"{place_a.capitalize()}, watch {scene_a}. "
            f"When you can honestly say “{rest}”, you are watching {nm}."
        )
        ex2 = (
            f"{place_b.capitalize()}, switch to {scene_b}. "
            f"If the same change still fits “{rest}”, {nm} is stable — not a one-scene trick."
        )
    elif verb in {
        "breaks",
        "break",
        "traps",
        "trap",
        "slows",
        "slow",
        "helps",
        "help",
        "pushes",
        "push",
        "pulls",
        "pull",
        "carries",
        "carry",
        "absorbs",
        "absorb",
        "releases",
        "release",
        "increases",
        "increase",
        "makes",
        "make",
    }:
        ex1 = (
            f"{place_a.capitalize()}, keep {scene_a} in mind. "
            f"Ask: does this show {nm} at work — {claim_s}?"
        )
        ex2 = (
            f"{place_b.capitalize()}, compare with {scene_b}. "
            f"Same meaning of {nm}, different scene: {claim_s}."
        )
    elif verb in {"is calculated on", "are calculated on", "is calculated", "are calculated", "compares", "compare"}:
        ex1 = (
            f"{place_a.capitalize()}, use {scene_a} as your working example. "
            f"Check whether {nm} really starts from {rest}."
        )
        ex2 = (
            f"{place_b.capitalize()}, try {scene_b} with different numbers. "
            f"The objects change; the rule for {nm} should not."
        )
    elif verb in {"means", "mean", "is", "are", "was", "were", "includes", "include", "names", "name"}:
        ex1 = (
            f"{place_a.capitalize()}, look at {scene_a} and ask whether “{rest}” fits. "
            f"If yes, that is a real case of {nm}."
        )
        ex2 = (
            f"{place_b.capitalize()}, test {scene_b} the same way. "
            f"Two scenes, one steady meaning of {nm}."
        )
    elif age_band == "younger":
        ex1 = f"{place_a.capitalize()}, watch {scene_a}. Link what you see to {nm}: {claim_s}."
        ex2 = (
            f"{place_b.capitalize()}, try a second look with {scene_b}. "
            f"The place changes, but {nm} still means: {claim_s}."
        )
    elif age_band == "older":
        ex1 = (
            f"{place_a.capitalize()}, treat {scene_a} as evidence for {nm}: {claim_s}. "
            f"Name the part of the situation that proves it."
        )
        ex2 = (
            f"{place_b.capitalize()}, switch to a second case with {scene_b}. "
            f"If {nm} still matches “{claim_s}”, your understanding is stable."
        )
    else:
        ex1 = (
            f"{place_a.capitalize()}, think of {scene_a} and ask what it tells you "
            f"about {nm}: {claim_s}."
        )
        ex2 = (
            f"{place_b.capitalize()}, try the same thinking with {scene_b}. "
            f"The scene changes; the meaning of {nm} does not."
        )
    return [ex1, ex2]


def compose_misconception(*, name: str, claim: str, board_misc: list[dict[str, str]] | None = None) -> tuple[str, str]:
    if board_misc:
        for row in board_misc:
            label = str(row.get("label") or row.get("misconception") or "").strip()
            fix = str(row.get("correction") or row.get("remedy") or "").strip()
            if label and name.lower() in label.lower():
                return (
                    f"Many learners believe: {label.rstrip('.')}.",
                    f"Actually: {fix or claim} That is why the careful wording matters.",
                )
        row = board_misc[0]
        label = str(row.get("label") or "").strip()
        fix = str(row.get("correction") or claim).strip()
        if label:
            return f"Many learners believe: {label.rstrip('.')}.", f"Actually: {fix}"

    parts = _claim_parts(claim, name)
    verb = parts["verb"]
    rest = parts["rest"] or _clip(claim, 18)
    nm = name.lower()
    seed = f"{name}|{claim}|misc"

    if verb in {"turns", "turn", "becomes", "become", "forms", "form"}:
        patterns = [
            (
                f"Many learners believe {nm} is only a name, not a real change.",
                f"Actually, {nm} is the change itself: {_clip(claim, 22)}",
            ),
            (
                f"Many learners reverse what happens in {nm}.",
                f"Actually, follow the true order: {_clip(claim, 22)}",
            ),
        ]
    elif verb in {"is calculated", "are calculated"}:
        patterns = [
            (
                f"Many learners believe {nm} uses a changing amount each time.",
                f"Actually, {_clip(claim, 22)} Stay with the original base.",
            ),
        ]
    elif verb in {"means", "mean", "is", "are"}:
        patterns = [
            (
                f"Many learners shrink {nm} to a vague everyday word.",
                f"Actually, keep the precise school meaning: {_clip(claim, 22)}",
            ),
            (
                f"Many learners mix {nm} with a nearby idea that only sounds similar.",
                f"Actually, {nm} stands on this evidence alone: {_clip(claim, 22)}",
            ),
        ]
    elif "not" in claim.lower() or "only" in claim.lower():
        patterns = [
            (
                f"Many learners drop the careful limit inside {nm}.",
                f"Actually, the limit matters: {_clip(claim, 22)}",
            ),
        ]
    else:
        patterns = [
            (
                f"Many learners blur {nm} into the idea taught just before it.",
                f"Actually, {nm} carries its own job: {_clip(claim, 22)} Keep the two ideas separate.",
            ),
            (
                f"Many learners treat {nm} as a label to memorise, not a meaning to use.",
                f"Actually, you must be able to apply: {_clip(claim, 22)}",
            ),
            (
                f"Many learners reverse the cause and effect around {nm}.",
                f"Actually, follow the evidence order in: {_clip(claim, 22)}",
            ),
        ]
    return patterns[int(hashlib.sha256(seed.encode()).hexdigest()[:2], 16) % len(patterns)]

def compose_transition(*, previous: str, nxt: str, topic: str) -> str:
    """What would an excellent teacher say next? No 'Now let's…' scaffolds."""
    if not previous:
        if nxt.lower() in topic.lower() or topic.lower() in nxt.lower():
            return f"Everything in {topic} rests on one idea, so we start there."
        return f"We open with {nxt} because it unlocks the rest of {topic}."
    if previous.lower() == nxt.lower():
        return f"The same idea deserves a second, sharper look inside {topic}."
    prev_be = _be_verb(previous)
    nxt_be = _be_verb(nxt)
    answers = "answer" if _is_plural_label(previous) else "answers"
    nxt_answers = "answer" if _is_plural_label(nxt) else "answers"
    options = [
        f"Once {previous.lower()} {prev_be} clear, {nxt.lower()} {nxt_be} the natural next piece of {topic}.",
        f"With {previous.lower()} in place, the next honest question is about {nxt.lower()}.",
        f"{previous} {answers} one part of {topic}. {nxt} {nxt_answers} the part that follows.",
        f"Hold onto {previous.lower()}; you will need it to make sense of {nxt.lower()}.",
    ]
    return _stable_pick(f"{previous}|{nxt}|{topic}", options)


def compose_curiosity_bridge(*, name: str, nxt: str | None, topic: str) -> str:
    if nxt:
        return (
            f"I understand {name.lower()} for now — but how does it connect to {nxt.lower()} "
            f"in {topic}? That is where we go next."
        )
    return (
        f"I understand {name.lower()} because I can explain it with a real example "
        f"and keep the accurate meaning."
    )


def compose_diagram_guidance(
    *,
    topic: str,
    concepts: list[str],
    claims: list[str],
    voice: str = "standard",
) -> str:
    labels = [c for c in concepts[:4] if c] or [topic]
    joined = " → ".join(labels)
    first = labels[0]
    last = labels[-1]
    lead = _clip(claims[0], 20).rstrip(".") if claims else f"{first} matters here"
    _, prop = _scene_props(topic, " ".join(claims[:1]), f"{topic}|diagram|{voice}")
    if voice == "visual":
        return (
            f"The diagram shows {joined} — the whole idea of {topic} in one picture. "
            f"It matters because the order of those stages is the explanation, not decoration. "
            f"Watch what changes between {first} and {last}: something is different at each step. "
            f"Read an arrow as “this causes the next part”, and the picture will say the same thing as {lead}. "
            f"Link one label to {_with_article(prop)} you already know."
        )
    if voice == "auditory":
        return (
            f"Describe the {topic} diagram out loud in this order: {joined}. "
            f"You are saying why each stage has to come before the next, which is the point of the picture. "
            f"Listen for the moment your voice hesitates — that is the stage you do not own yet. "
            f"Each arrow means “this leads to that”, so your sentences should match {lead}. "
            f"Mention {_with_article(prop)} if it keeps the meaning clear."
        )
    if voice == "parent":
        return (
            f"Open the {topic} diagram together. It lays out {joined} in the order things actually happen. "
            f"Ask your child what changes between {first} and {last} — that is where the learning sits. "
            f"An arrow simply means “this leads to that”, so their words should match {lead}. "
            f"Use {_with_article(prop)} as a home bridge if they get stuck."
        )
    if voice == "adhd":
        return (
            f"Diagram sprint: the picture holds {joined}. "
            f"Eyes on {first}, then jump stage by stage to {last}. "
            f"Arrows mean “this causes the next bit” — spot one change per stage. "
            f"Ten seconds, one true sentence, done."
        )
    if voice == "autism":
        return (
            f"Same diagram routine every time for {topic}.\n"
            f"The picture shows this exact order: {joined}.\n"
            f"First, point to {first}. Next, follow each arrow, which always means “this leads to that”.\n"
            f"Then, name what is different at {last}. Do not skip steps."
        )
    if voice in {"ld", "dyslexia"}:
        return (
            f"The picture shows {joined}, in that order.\n"
            f"Start at {first}. One label at a time.\n"
            f"An arrow means “next”. Nothing more.\n"
            f"At the end, say what changed. Keep {_with_article(prop)} in mind as a check."
        )
    if voice == "ell":
        return (
            f"Picture words for {topic}: {joined}. "
            f"The picture shows the order of the stages. Point to {first}. Say: “This shows ____.” "
            f"An arrow means “then this happens”. Move to {last} and say: “Now it is ____.” "
            f"Home word bridge: {prop}."
        )
    if voice == "teacher":
        return (
            f"Use the {topic} diagram as a cold-call map across {joined}. "
            f"Establish first what the picture represents, then why the sequence cannot be reordered. "
            f"Have a student teach {first} from the picture alone and interpret one arrow aloud. "
            f"Check their reading against {lead}, then connect {_with_article(prop)}."
        )
    return (
        f"The diagram lays out {joined} — one picture holding the whole idea of {topic}. "
        f"Ask yourself why those stages cannot swap places; that order is the explanation itself. "
        f"Look for what changes between {first} and {last}, because each stage leaves the situation different. "
        f"Read every arrow as “this causes the next part”, and the diagram will tell you the same thing as {lead}. "
        f"Match one label to {_with_article(prop)} you have seen at home or on the way to school, "
        f"then come back to this picture after each new idea so the connections stay visible."
    )


def compose_summary(
    *,
    topic: str,
    concepts: list[str],
    claims: list[str],
    age_band: str = "middle",
    subject: str = "",
    voice: str = "standard",
) -> str:
    """What should the learner genuinely remember — composed for this profile, not shared."""
    banks = lookup_banks(topic, subject=subject, claim=claims[0] if claims else "")
    core = str(banks.get("summary") or "").strip()
    if core:
        nm = (concepts[0] if concepts else topic).lower()
        if voice == "visual":
            return (
                f"Close your eyes and the {topic} diagram should still be there. {core} "
                f"If a stage goes blank, that is the picture to redraw tonight."
            )
        if voice == "auditory":
            return (
                f"Say this out loud once more, then it is yours: {core} "
                f"Your own voice explaining {nm} is the version you will remember."
            )
        if voice == "ell":
            words = ", ".join(concepts[:3]) if concepts else topic
            return f"Words you can now use: {words}. Meaning to keep: {core}"
        if voice in {"ld", "dyslexia"}:
            return f"One thing to keep:\n{core}\nThat is enough. You have it."
        if voice == "adhd":
            return f"Done — here is the one line that was worth the sprint: {core}"
        if voice == "autism":
            return f"Last step, same every time. The fact to keep is this: {core}"
        if voice == "teacher":
            return (
                f"Learning outcome to assess: {core} "
                f"Anything less than this in a student's own words needs another pass."
            )
        if voice == "parent":
            return (
                f"If your child can tell you this at dinner, the lesson landed: {core}"
            )
        return core
    lead = claims[0] if claims else ""
    names = ", ".join(concepts[:3]) if concepts else topic
    if age_band == "younger":
        return (
            f"After {topic}, keep the living meaning of {names}. "
            f"You can show one real example and say the true idea in your own words."
        )
    core = _clip(lead, 20) if lead else f"each idea in {topic} keeps one clear job"
    return (
        f"What should stay with you from {topic}: {names} each keep a precise job. "
        f"Carry this understanding forward — {core} — and you can teach it without mixing ideas."
    )


def compose_activity(*, topic: str, name: str, claim: str, voice: str = "standard") -> str:
    if voice == "visual":
        return (
            f"Draw {topic} from memory — stages, arrows, labels. "
            f"Then check your sketch against the real diagram and circle whatever you left out."
        )
    if voice == "adhd":
        return (
            f"One-minute hunt: find something around you that shows {name.lower()}. "
            f"Say why it counts in a single sentence. Then you are finished."
        )
    if voice == "parent":
        return (
            f"Sometime today, point at something connected to {name.lower()} and ask your child "
            f"to explain it to you. Let them do the talking; you just look interested."
        )
    return (
        f"Find one safe, real instance of {name.lower()} connected to {topic}. "
        f"Show it, name it, and say how it matches this meaning: {_clip(claim, 18)} "
        f"This is practice for understanding, not a worksheet race."
    )


class CompositionFailure(Exception):
    """Raised when excellent writing cannot be produced — never insert template filler."""


def validate_learner_prose(text: str) -> None:
    low = (text or "").lower()
    for bad in FORBIDDEN_SCAFFOLDS:
        if bad in low:
            raise CompositionFailure(f"Forbidden scaffold in learner prose: {bad}")
    # Grammar / nonsense article checks (composition failure, not soft template)
    if re.search(
        r"\b(a|an)\s+(fairly|digestive|pressure|force|friction|increase|slow|green|magma|crust|straight|travelled|all|see|sour|type|reproduce|vapour|motion)\b(?!\s+[A-Za-z])",
        low,
    ):
        raise CompositionFailure("Incoherent article+noun in learner prose.")
    if re.search(r"\baround (a|an) (per|travelled|see|all|type|sour)\b", low):
        raise CompositionFailure("Incoherent scene framing in learner prose.")
    if "point to a " in low or "point to an " in low:
        raise CompositionFailure("Template pointing scaffold in learner prose.")



def _compose_worked_example(
    *, name: str, claim: str, topic: str, scene: str, voice: str = "standard"
) -> str:
    """A worked example the learner can follow: set-up, reasoning, result, check."""
    _, prop = _scene_props(topic, claim, f"{topic}|{name}|worked")
    anchor = _scene_phrase(prop, name)
    fact = _clip(claim, 22).rstrip(".")
    lower = name.lower()
    steps = (
        f"Work through it with me. Start here: {scene} "
        f"First, decide what you are actually looking at — where is {lower} in that situation? "
        f"Next, ask what would be different if it were absent, because that difference is the whole point. "
        f"Now say why it happens, using the fact we established: {fact}. "
        f"Finally, run the same four steps on {anchor}. If the reasoning still holds there, "
        f"you have understood {lower} rather than memorised it."
    )
    if voice in {"ld", "dyslexia"}:
        return (
            f"Step 1. Look: {scene}\n"
            f"Step 2. Find {lower} in it.\n"
            f"Step 3. Say why: {fact}.\n"
            f"Step 4. Check with {anchor}. Same answer? Good."
        )
    if voice == "autism":
        return (
            f"Worked example, same four steps every time.\n"
            f"1. The situation: {scene}\n"
            f"2. Locate {lower}.\n"
            f"3. Reason: {fact}.\n"
            f"4. Check the reasoning against {anchor}."
        )
    return steps


def concept_plan(
    *,
    name: str,
    claim: str,
    topic: str,
    previous: str | None,
    nxt: str | None,
    age_band: str,
    board_misc: list[dict[str, str]] | None = None,
    voice: str = "standard",
    subject: str = "",
    index: int = 0,
) -> dict[str, Any]:
    """Teacher questions + bank materials woven with verified claims."""
    if not (claim or "").strip():
        raise CompositionFailure(f"No verified claim available to teach {name}.")
    banks = lookup_banks(topic, subject=subject, claim=claim)
    examples = compose_examples(
        name=name, claim=claim, topic=topic, age_band=age_band, voice=voice
    )
    wrong, right = compose_misconception(name=name, claim=claim, board_misc=board_misc)
    use_bank = index == 0  # bank material teaches the lead idea; later ideas use claim-specific prose
    if use_bank and banks.get("misconception"):
        misc = banks["misconception"]
        if isinstance(misc, dict):
            wrong = f"Many learners believe: {misc.get('wrong', '').rstrip('.')}."
            right = f"Actually: {misc.get('right', claim)}"
    if use_bank:
        notice = str(banks.get("example") or examples[0])
        second = str(banks.get("example2") or examples[1])
        analogy = str(banks.get("real_world") or "")
    else:
        notice = examples[0]
        second = examples[1]
        analogy = ""
    if not analogy or analogy in {notice, second}:
        analogy = f"Look for one more everyday case of {name.lower()} on your way home today."
    simple = compose_simple_explanation(name=name, claim=claim, age_band=age_band)
    explain = f"{claim} Put that into your own words before you rush ahead."
    if use_bank and banks.get("real_world") and banks.get("real_world") not in {notice, second}:
        explain = f"{claim} Around you: {_clip(str(banks['real_world']), 26)}"
    guided = (
        str(banks.get("question") or "")
        if use_bank
        else f"Think it through: what would change about {name.lower()} if the evidence did not hold?"
    ) or compose_curiosity_bridge(name=name, nxt=nxt, topic=topic)
    plan = {
        "name": name,
        "notice_first": notice,
        "observation": notice,
        "prior": (
            f"You already notice patterns like this near home, the kitchen, or the playground — "
            f"now we name the precise idea behind them."
        )
        if use_bank
        else f"Keep the previous idea nearby; {name.lower()} builds directly on it.",
        "why_important": (
            str(banks.get("transition") or "")
            if use_bank
            else compose_transition(previous=previous or "", nxt=name, topic=topic)
        )
        or compose_transition(previous=previous or "", nxt=name, topic=topic),
        "real_life": notice,
        "second_example": second,
        "worked_example": _compose_worked_example(
            name=name, claim=claim, topic=topic, scene=second, voice=voice
        ),
        "analogy": analogy,
        "misconception": wrong if wrong.startswith("Many") else f"Many learners believe: {wrong.rstrip('.')}.",
        "correction": right if right.lower().startswith("actually") else f"Actually: {right}",
        "guided": guided,
        "simple": simple,
        "explain": explain,
        "claim": claim,
        "question_next": guided,
        "recap": (
            f"I understand {name.lower()} because I can show a real example "
            f"and keep the accurate meaning without mixing nearby ideas."
        ),
        "summary_seed": str(banks.get("summary") or ""),
        "hook_seed": str(banks.get("hook") or ""),
        "bank_covered": bool(banks.get("covered")),
        "next_concept": nxt,
        "voice": voice,
        "index": index,
    }
    for key in (
        "notice_first",
        "simple",
        "real_life",
        "second_example",
        "misconception",
        "correction",
        "worked_example",
        "recap",
    ):
        validate_learner_prose(str(plan[key]))
    return plan


def teach_sections_for_profile(
    plan: Mapping[str, Any],
    *,
    profile: str,
    topic: str,
) -> list[dict[str, Any]]:
    """Full pedagogical arc, independently shaped per learner profile."""
    name = str(plan["name"])
    claim = str(plan["claim"])
    sections: list[dict[str, Any]] = []

    if profile == "standard":
        sections.extend(
            [
                {
                    "title": f"Look closely — {name}",
                    "role": "real_life_example",
                    "body": str(plan["observation"]),
                },
                {
                    "title": f"The clear meaning — {name}",
                    "role": "concept",
                    "body": f"{plan['prior']} {plan['explain']}",
                },
                {
                    "title": f"A simpler way to hold {name}",
                    "role": "simple_explanation",
                    "body": str(plan["simple"]),
                },
                {
                    "title": f"Worked example — {name}",
                    "role": "worked_example",
                    "body": str(plan["worked_example"]),
                },
                {
                    "title": f"Another picture of {name}",
                    "role": "real_life_example",
                    "body": f"{plan['second_example']} {plan['analogy']}",
                },
                {
                    "title": f"A common mix-up about {name}",
                    "role": "common_misconception",
                    "body": f"{plan['misconception']} {plan['correction']}",
                },
                {
                    "title": "Think with me",
                    "role": "practice_question",
                    "body": str(plan["guided"]),
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": str(plan["recap"]),
                },
            ]
        )
    elif profile == "visual":
        sections.extend(
            [
                {
                    "title": f"See {name} first",
                    "role": "concept",
                    "body": (
                        f"Illustration first: find {name} on the diagram before you read further. "
                        f"Trace each labelled part with your finger. Ask where the picture shows: {claim}"
                    ),
                },
                {
                    "title": f"Diagram practice — {name}",
                    "role": "worked_example",
                    "body": (
                        f"On the diagram, point to the stage that matches this evidence: {claim} "
                        f"Then sketch a tiny icon that could only mean {name.lower()} — not a neighbouring idea."
                    ),
                },
                {
                    "title": f"Picture check — {name}",
                    "role": "common_misconception",
                    "body": (
                        f"{plan['misconception']} {plan['correction']} "
                        f"If your icon drifted, redraw it from the diagram labels alone."
                    ),
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": (
                        f"I understand {name.lower()} because I can teach it from the diagram "
                        f"and keep this accurate meaning: {claim}"
                    ),
                },
            ]
        )
    elif profile == "auditory":
        sections.extend(
            [
                {
                    "title": f"Hear {name}",
                    "role": "concept",
                    "body": (
                        f"Listen first to this story beat: {plan['observation']} "
                        f"Now say the fact aloud: {claim} Hear yourself keep the accurate wording."
                    ),
                },
                {
                    "title": f"Say it again — {name}",
                    "role": "worked_example",
                    "body": (
                        f"Repeat after a pause: {plan['second_example']} "
                        f"Then speak the verified line once more: {claim}"
                    ),
                },
                {
                    "title": "Listen for the mix-up",
                    "role": "common_misconception",
                    "body": f"{plan['misconception']} {plan['correction']} Say the accurate version aloud.",
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": str(plan["recap"]),
                },
            ]
        )
    elif profile == "ell":
        sections.extend(
            [
                {
                    "title": f"Key Words — {name}",
                    "role": "concept",
                    "body": (
                        f"Look at this first: {plan['observation']} "
                        f"Word: {name}. Meaning: {plan['simple']} "
                        f"Sentence frame: “{name} means ____.” Say: {claim}"
                    ),
                },
                {
                    "title": f"Frame practice — {name}",
                    "role": "practice_question",
                    "body": (
                        f"Now try this one: {plan['second_example']} "
                        f"Frame: “An example of {name.lower()} is ____.” Say it twice. "
                        f"Keep: {claim}"
                    ),
                },
                {
                    "title": "Watch this mix-up",
                    "role": "common_misconception",
                    "body": f"{plan['misconception']} {plan['correction']}",
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": str(plan["recap"]),
                },
            ]
        )
    elif profile == "ld":
        sections.extend(
            [
                {
                    "title": f"Small steps — {name}",
                    "role": "concept",
                    "body": (
                        f"Step 1. Read slowly: {_clip(claim, 14)}\n"
                        f"Step 2. Say it back in five words.\n"
                        f"Step 3. Cover the page and try again.\n"
                        f"Step 4. Tick the box when it feels steady."
                    ),
                },
                {
                    "title": f"One picture — {name}",
                    "role": "real_life_example",
                    "body": f"Smaller look: {_clip(str(plan['second_example']), 14)}\nSame meaning, smaller load.",
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": f"I can say {name.lower()} in my own short words.",
                },
            ]
        )
    elif profile == "dyslexia":
        sections.extend(
            [
                {
                    "title": f"Calm read — {name}",
                    "role": "concept",
                    "body": (
                        f"{name}\n{_clip(str(plan['observation']), 14)}\n{_clip(claim, 16)}\n"
                        f"Finger-track. One breath. Calm read."
                    ),
                },
                {
                    "title": f"Second look — {name}",
                    "role": "real_life_example",
                    "body": f"{_clip(str(plan['second_example']), 14)}\nCircle {name}. Whisper the meaning.",
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": str(plan["recap"]),
                },
            ]
        )
    elif profile == "adhd":
        sections.extend(
            [
                {
                    "title": f"2-Minute Chunk — {name}",
                    "role": "concept",
                    "body": (
                        f"Mission: get {name.lower()} in two minutes. "
                        f"Chunk one — {_clip(claim, 14)} "
                        f"Stand, stretch ten seconds, sit back down."
                    ),
                },
                {
                    "title": f"Second burst — {name}",
                    "role": "worked_example",
                    "body": (
                        f"Chunk two: say {name.lower()} out loud in one short sentence. "
                        f"Beat the clock — twenty seconds, then move."
                    ),
                },
                {
                    "title": "Mix-up sprint",
                    "role": "common_misconception",
                    "body": f"{plan['misconception']} {plan['correction']} Fix it fast, then tick it off.",
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": f"Win logged: I can fire off {name.lower()} in one clean sentence.",
                },
            ]
        )
    elif profile == "autism":
        sections.extend(
            [
                {
                    "title": f"Routine — {name}",
                    "role": "concept",
                    "body": (
                        f"Same routine every time.\n"
                        f"First, look: {_clip(str(plan['observation']), 16)}\n"
                        f"Next, fact: {_clip(claim, 18)}\n"
                        f"Then, check: one literal sentence with {name}."
                    ),
                },
                {
                    "title": f"Routine example — {name}",
                    "role": "real_life_example",
                    "body": f"Next, look again: {_clip(str(plan['second_example']), 16)}\nThen, same check again.",
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": str(plan["recap"]),
                },
            ]
        )
    elif profile == "teacher":
        sections.extend(
            [
                {
                    "title": f"Teach — {name}",
                    "role": "concept",
                    "body": (
                        f"Model the verified evidence only: {claim} "
                        f"Ask one cold-call: who can show this with a desk object in ten seconds? "
                        f"Assess with: {plan['guided']}"
                    ),
                },
                {
                    "title": f"Misconception watch — {name}",
                    "role": "common_misconception",
                    "body": (
                        f"{plan['misconception']} {plan['correction']} "
                        f"Exit ticket: restate {name} with one example — do not invent new facts."
                    ),
                },
            ]
        )
    elif profile == "parent":
        sections.extend(
            [
                {
                    "title": f"Talk about — {name}",
                    "role": "concept",
                    "body": (
                        f"Tonight at home, ask your child: what does {name.lower()} really mean? "
                        f"Listen for their own words rather than a textbook line. "
                        f"If they hesitate, ask where they have seen it happen this week."
                    ),
                },
                {
                    "title": f"Home try — {name}",
                    "role": "real_life_example",
                    "body": (
                        f"Find one moment at home — in the kitchen, at the tap, or on the way to the market — "
                        f"where {name.lower()} shows up. Let your child point it out and explain it to you. "
                        f"Praise clear wording, not speed."
                    ),
                },
                {
                    "title": f"If they get it wrong — {name}",
                    "role": "common_misconception",
                    "body": (
                        f"{plan['misconception']} {plan['correction']} "
                        f"Do not correct sharply — ask a question that lets them notice it themselves."
                    ),
                },
                {
                    "title": f"I understand {name}",
                    "role": "reflection",
                    "body": (
                        f"Your child understands {name.lower()} when they can explain it at the dinner table "
                        f"with an example nobody gave them."
                    ),
                },
            ]
        )
    else:
        sections.extend(teach_sections_for_profile(plan, profile="standard", topic=topic))

    for sec in sections:
        validate_learner_prose(str(sec.get("body") or ""))
    return sections


def teach_compact_for_profile(
    plan: Mapping[str, Any],
    *,
    profile: str,
    topic: str,
) -> list[dict[str, Any]]:
    """Lighter follow-on teaching so multi-concept lessons stay readable."""
    name = str(plan["name"])
    claim = str(plan["claim"])
    if profile == "standard":
        sections = [
            {
                "title": f"Build on this — {name}",
                "role": "concept",
                "body": f"{plan['why_important']} {claim}",
            },
            {
                "title": f"Check {name} for yourself",
                "role": "worked_example",
                "body": f"{plan['observation']} {plan['simple']}",
            },
            {
                "title": f"Mix-up to avoid — {name}",
                "role": "common_misconception",
                "body": f"{plan['misconception']} {plan['correction']}",
            },
        ]
    elif profile == "teacher":
        sections = [
            {
                "title": f"Teach next — {name}",
                "role": "concept",
                "body": f"Evidence: {claim} Demo: {plan['observation']} Watch for: {plan['misconception']}",
            }
        ]
    elif profile == "adhd":
        sections = [
            {
                "title": f"Quick build — {name}",
                "role": "concept",
                "body": f"Next chunk, twenty seconds: {_clip(claim, 14)} Then tick and move.",
            },
        ]
    else:
        sections = [
            {
                "title": f"Build on — {name}",
                "role": "concept",
                "body": f"{plan['observation']} Fact: {claim}",
            },
            {"title": f"I understand {name}", "role": "reflection", "body": str(plan["recap"])},
        ]
    for sec in sections:
        validate_learner_prose(str(sec.get("body") or ""))
    return sections



def teach_concept_paragraph(
    *,
    name: str,
    claim: str,
    topic: str,
    profile: str = "standard",
) -> str:
    """Compat paragraph API for master_teacher — still bank-free."""
    age = "middle"
    examples = compose_examples(name=name, claim=claim, topic=topic, age_band=age)
    simple = compose_simple_explanation(name=name, claim=claim, age_band=age)
    if profile == "visual":
        return f"Find {name} on the diagram first. {examples[0]} Fact: {claim}"
    if profile == "auditory":
        return f"Listen: {examples[0]} Say aloud: {claim}"
    if profile == "ell":
        return f"Look: {examples[0]} Word: {name}. {simple} Frame: “{name} means ____.”"
    if profile in {"ld", "dyslexia", "adhd", "autism"}:
        return f"{examples[0]} {simple}"
    if profile == "teacher":
        return f"Model: {claim} Demo: {examples[0]} Second case: {examples[1]}"
    if profile == "parent":
        return f"Ask about {name.lower()}. Listen for: {claim} Try: {examples[0]}"
    return f"{examples[0]} {claim} Another look: {examples[1]}"
