"""Publisher remediation — restore teachability without new engines.

Addresses audit findings: template prose, teacher-objective leakage,
generic subject-sequence diagrams scored as excellent, and cosmetic
adaptation wrappers. Used by LCE polish, PQLE, and EATS.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

ALORA_PUBLISHER_REMEDIATION_SMOKE_OK = True
REMEDIATION_VERSION = "1.0.0"

# Stock LCE / adaptive wrappers that must never pass as publisher teaching.
TEMPLATE_PHRASES = (
    "is a core idea in this lesson",
    "worth mastering because it helps you explain",
    "we begin with",
    "feels clear and organised",
    "worked example: identify where",
    "appears in the lesson evidence",
    "practice: explain",
    "a useful way to remember",
    "connect it to a familiar situation",
    "remember: the big idea helps you explain",
    "today we study",
    "with careful classroom language",
    "say the definition of",
    "say the definitions aloud",
    "once in your own words before moving on",
    "name the key parts, then explain the idea in two clear sentences",
    "check for understanding with a quick cold-call",
    "keep verified facts unchanged; differentiate presentation only",
    "as you read, notice how",
    "notice how",
    "here is another way to see",
    "a clear classroom example helps:",
    "study the diagram or colour cues",
    "look first, then read",
    "**checkpoint:**",
    "checkpoint: pause",
    "*key words in this section:*",
    "key words in this section:",
)

TEACHER_OBJECTIVE_PATTERNS = (
    r"\bstudents?\s+will\b",
    r"\blearners?\s+will\b",
    r"\blearning\s+objectives?\b",
    r"\bby the end of (this|the) lesson\b",
    r"\bsuccess\s+criteria\b",
    r"\bteacher\s+note\b",
)

# Subject-sequence flowchart labels that are pedagogy stages, not science.
GENERIC_DIAGRAM_STAGES = frozenset(
    {
        "concept",
        "phenomenon",
        "experiment",
        "diagram",
        "formula",
        "example",
        "practice",
        "explore",
        "explain",
        "practise",
        "apply",
        "introduction",
        "summary",
        "revision",
        "hook",
        "stage 1",
        "stage 2",
        "stage 3",
        "stage 4",
    }
)


def blob_of(adaptation: Mapping[str, Any]) -> str:
    parts = [str(adaptation.get("big_idea") or ""), str(adaptation.get("topic") or "")]
    for sec in adaptation.get("sections") or []:
        if isinstance(sec, dict):
            parts.append(str(sec.get("title") or ""))
            parts.append(str(sec.get("body") or ""))
    for card in adaptation.get("word_wall") or adaptation.get("vocabulary_cards") or []:
        if isinstance(card, dict):
            parts.append(str(card.get("definition") or ""))
            parts.append(str(card.get("simple_explanation") or ""))
            parts.append(str(card.get("example") or card.get("example_sentence") or ""))
    return "\n".join(parts)


def template_hits(text: str) -> list[str]:
    low = (text or "").lower()
    return [p for p in TEMPLATE_PHRASES if p in low]


def has_teacher_objective_leak(text: str) -> bool:
    low = (text or "").strip().lower()
    if not low:
        return False
    return any(re.search(p, low) for p in TEACHER_OBJECTIVE_PATTERNS)


def svg_text_labels(svg: str) -> list[str]:
    labels: list[str] = []
    for m in re.finditer(r"<tspan[^>]*>([^<]*)</tspan>|<text[^>]*>([^<]*)</text>", svg or "", flags=re.I):
        label = (m.group(1) or m.group(2) or "").strip()
        if label:
            labels.append(label)
    return labels


def is_generic_subject_flowchart(svg: str) -> bool:
    """True when an SVG is mostly pedagogy-stage boxes, not domain content."""
    if not (svg or "").strip().startswith("<svg"):
        return False
    labels = [L.lower() for L in svg_text_labels(svg)]
    if len(labels) < 3:
        return False
    # Ignore title-like long labels
    short = [L for L in labels if 2 <= len(L) <= 24]
    if not short:
        return False
    generic = sum(1 for L in short if L in GENERIC_DIAGRAM_STAGES)
    return generic >= 3 and generic / max(len(short), 1) >= 0.45


def adaptation_has_generic_diagram(adaptation: Mapping[str, Any]) -> bool:
    for key in ("flowchart_svg", "svg_diagram", "concept_map_svg"):
        if is_generic_subject_flowchart(str(adaptation.get(key) or "")):
            return True
    dq = adaptation.get("diagram_question")
    if isinstance(dq, dict) and is_generic_subject_flowchart(str(dq.get("svg_diagram") or "")):
        return True
    return False


def teachability_penalties(adaptation: Mapping[str, Any]) -> tuple[float, list[str]]:
    """Return (score_penalty_0_to_40, issues) for EATS/PQLE recalibration."""
    issues: list[str] = []
    penalty = 0.0
    blob = blob_of(adaptation)
    hits = template_hits(blob)
    if hits:
        penalty += min(28.0, 4.5 * len(hits))
        issues.append(f"Template teaching phrases: {', '.join(hits[:4])}")
    if has_teacher_objective_leak(blob):
        penalty += 18.0
        issues.append("Teacher/objective wording leaked into student lesson.")
    if adaptation_has_generic_diagram(adaptation):
        penalty += 22.0
        issues.append("Generic subject-sequence flowchart is not a domain diagram.")
    big = str(adaptation.get("big_idea") or "").lower()
    if "worth mastering" in big or "helps you explain" in big and "accuracy and confidence" in big:
        penalty += 8.0
        issues.append("Meta big idea (not a teachable claim).")
    return penalty, issues


def studentize_goal(text: str, *, topic: str = "this topic") -> str:
    raw = (text or "").strip()
    if not raw:
        return f"You will learn the key ideas in {topic} using clear examples."
    if not has_teacher_objective_leak(raw):
        return raw if raw.endswith((".", "!", "?")) else raw + "."
    # Strip "Students will …" → learner-facing stem
    cleaned = re.sub(r"^(students?|learners?)\s+will\s+", "You will ", raw, flags=re.I)
    cleaned = re.sub(r"\blearning\s+objectives?\s*[:\-–]?\s*", "", cleaned, flags=re.I)
    cleaned = cleaned.strip()
    if has_teacher_objective_leak(cleaned) or len(cleaned) < 12:
        return f"You will learn how the ideas in {topic} fit together, using accurate lesson terms."
    return cleaned if cleaned.endswith((".", "!", "?")) else cleaned + "."


def claim_first_sentence(pool: list[str], needle: str = "") -> str:
    needle_l = (needle or "").lower()
    for text in pool:
        t = str(text or "").strip()
        if not t or has_teacher_objective_leak(t) or template_hits(t):
            continue
        if needle_l and needle_l not in t.lower():
            continue
        return t if t.endswith((".", "!", "?")) else t + "."
    for text in pool:
        t = str(text or "").strip()
        if t and not has_teacher_objective_leak(t):
            return t if t.endswith((".", "!", "?")) else t + "."
    return ""


def rewrite_stock_body(body: str, *, title: str = "", claim: str = "", topic: str = "") -> str:
    """Replace known stock openers with claim-grounded teaching lines."""
    text = (body or "").strip()
    if not text:
        return text
    low = text.lower()
    name = re.sub(r"^(core idea:|understanding|worked example —|try this —|reflect on|watch out —)\s*", "", title, flags=re.I).strip() or "this idea"
    fact = claim or ""

    if "is a core idea in this lesson" in low:
        if fact:
            return f"{fact} Hold onto that meaning as you study {name}."
        return f"{name} matters in {topic or 'this lesson'}. Use the lesson evidence to say what {name.lower()} means in one clear sentence."

    if low.startswith("worked example:") or "identify where" in low and "lesson evidence" in low:
        if fact:
            return (
                f"Worked example — read this evidence: {fact} "
                f"Underline the words that define {name.lower()}, then write two sentences that restate the idea."
            )
        return (
            f"Worked example — write two accurate sentences that define {name.lower()} "
            f"using only words you can defend from the lesson."
        )

    if low.startswith("practice: explain") or "using evidence from the lesson" in low and low.startswith("practice"):
        if fact:
            return f"Try this: explain {name} in your own words. Start from this evidence: {fact}"
        return f"Try this: explain {name} in your own words, then give one correct example."

    if "we begin with" in low and "feels clear and organised" in low:
        if fact:
            return fact
        return f"Focus on this part of {topic or 'the lesson'} carefully before you move on."

    if "a useful way to remember" in low and "familiar situation" in low:
        if fact:
            return f"Everyday link: {fact} Picture where you would see this outside the classroom."
        return f"Everyday link: notice where {name.lower()} shows up in a simple real situation connected to {topic or 'the topic'}."

    if low.startswith("notice how") or low.startswith("as you read, notice how") or low.startswith("here is another way to see"):
        cleaned = re.sub(
            r"^(as you read,\s*)?(notice how|here is another way to see)\s+",
            "",
            text,
            flags=re.I,
        ).strip()
        if cleaned:
            return cleaned[0].upper() + cleaned[1:] if cleaned[0].islower() else cleaned
        return fact or text

    if "study the diagram or colour cues" in low or "look first, then read" in low:
        cleaned = re.sub(
            r"(?i)study the diagram or colour cues for this idea, then read on\.?\s*",
            "",
            text,
        )
        cleaned = re.sub(r"(?i)look first, then read\.?\s*", "", cleaned).strip()
        return cleaned or (fact if fact else text)

    if "**checkpoint:**" in low or low.startswith("checkpoint:"):
        cleaned = re.sub(r"(?i)\*\*checkpoint:\*\*\s*", "", text)
        cleaned = re.sub(r"(?i)^checkpoint:\s*", "", cleaned).strip()
        return cleaned or "Pause here. Explain the last step in one sentence."

    if "key words in this section" in low:
        return re.sub(r"(?i)\*?key words in this section:?\*?\s*", "Important words: ", text).strip()

    if has_teacher_objective_leak(text):
        return studentize_goal(text, topic=topic or name)

    return text


def remediate_adaptation(adaptation: dict[str, Any], *, claims: list[str] | None = None) -> dict[str, Any]:
    """Polish one adaptation toward teachable, student-facing prose."""
    out = dict(adaptation)
    topic = str(out.get("topic") or "")
    pool = [str(c) for c in (claims or []) if str(c).strip()]
    # Harvest claims already present in section bodies
    for sec in out.get("sections") or []:
        if isinstance(sec, dict):
            body = str(sec.get("body") or "")
            for sent in re.split(r"(?<=[.!?])\s+", body):
                if len(sent.split()) >= 6 and not template_hits(sent) and not has_teacher_objective_leak(sent):
                    pool.append(sent.strip())

    big = str(out.get("big_idea") or "")
    if template_hits(big) or "worth mastering" in big.lower() or has_teacher_objective_leak(big):
        lead = claim_first_sentence(pool) or claim_first_sentence(pool, topic.split()[0] if topic else "")
        if lead:
            out["big_idea"] = (
                f"{lead} That idea is the thread that holds {topic or 'this lesson'} together."
            )
        else:
            out["big_idea"] = (
                f"In {topic or 'this lesson'}, precise definitions and clear examples help you explain each idea accurately."
            )

    new_sections: list[dict[str, Any]] = []
    teacher_note_used = False
    for sec in out.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        row = dict(sec)
        title = str(row.get("title") or "")
        body = str(row.get("body") or "")
        # Deduplicate identical teacher notes across sections
        if "**teacher note:**" in body.lower():
            if teacher_note_used:
                body = re.sub(
                    r"\n*\*\*Teacher note:\*\*[^\n]*(\n[^\n*]*)?",
                    "",
                    body,
                    flags=re.I,
                ).strip()
            else:
                teacher_note_used = True
        claim = claim_first_sentence(pool, title.split(":")[-1].strip() if ":" in title else title)
        if template_hits(body) or has_teacher_objective_leak(body):
            body = rewrite_stock_body(body, title=title, claim=claim, topic=topic)
        # Fix smashed misconception lines: "same Pressure" → "same. Pressure"
        body = re.sub(r"\bsame\s+(Pressure|Force|Area)\b", r"same. \1", body)
        row["body"] = body
        new_sections.append(row)
    out["sections"] = new_sections

    # Strip teacher-objective leaks from vocab walls if present
    for key in ("word_wall", "vocabulary_cards", "picture_words", "flashcards"):
        rows = out.get(key)
        if not isinstance(rows, list):
            continue
        cleaned = []
        for item in rows:
            if not isinstance(item, dict):
                cleaned.append(item)
                continue
            row = dict(item)
            for field in (
                "definition",
                "simple_explanation",
                "child_friendly",
                "academic_definition",
                "example",
                "example_sentence",
                "picture",
                "draw_this",
                "back",
            ):
                val = str(row.get(field) or "")
                if has_teacher_objective_leak(val) or template_hits(val):
                    row[field] = ""
            cleaned.append(row)
        out[key] = cleaned

    out.setdefault("lce", {})
    if isinstance(out["lce"], dict):
        out["lce"]["publisher_remediation"] = True
        out["lce"]["remediation_version"] = REMEDIATION_VERSION
    return out


def remediate_package(adaptations: dict[str, Any], *, claims: list[str] | None = None) -> dict[str, Any]:
    out = dict(adaptations)
    for key, value in list(out.items()):
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key == "worksheet":
            # Worksheet: scrub only objective leaks in text fields; keep structure
            out[key] = remediate_adaptation(value, claims=claims)
            continue
        if key == "vocabulary":
            # Do not empty premium card fields — scrub leaks only without wiping study assets
            page = dict(value)
            for wall_key in ("word_wall", "vocabulary_cards"):
                rows = page.get(wall_key)
                if not isinstance(rows, list):
                    continue
                cleaned = []
                for item in rows:
                    if not isinstance(item, dict):
                        cleaned.append(item)
                        continue
                    row = dict(item)
                    for field in (
                        "definition",
                        "simple_explanation",
                        "child_friendly",
                        "academic_definition",
                        "example",
                        "example_sentence",
                    ):
                        val = str(row.get(field) or "")
                        if has_teacher_objective_leak(val):
                            row[field] = re.sub(
                                r"(?i)\bstudents?\s+will\b[^.]*\.?",
                                "",
                                val,
                            ).strip() or row.get("term") or ""
                    row.setdefault("lce_card", True)
                    row.setdefault("pqle_card", True)
                    cleaned.append(row)
                page[wall_key] = cleaned
            page.setdefault("lce", {})
            if isinstance(page["lce"], dict):
                page["lce"]["publisher_remediation"] = True
            out[key] = page
            continue
        out[key] = remediate_adaptation(value, claims=claims)
    return out


def pack_health() -> dict[str, Any]:
    return {
        "ok": True,
        "smoke": ALORA_PUBLISHER_REMEDIATION_SMOKE_OK,
        "version": REMEDIATION_VERSION,
        "template_phrase_count": len(TEMPLATE_PHRASES),
    }
