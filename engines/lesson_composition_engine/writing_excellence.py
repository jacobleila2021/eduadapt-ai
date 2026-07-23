"""Educational writing excellence — warm teacher voice, never robotic AI prose.

Runs inside LCE before EERL / PQI. Does not invent curriculum facts.
"""

from __future__ import annotations

import re
from typing import Any

from engines.lesson_composition_engine.teaching_rules import (
    dedupe_sentences,
    ensure_paragraph_quality,
    sentence_count,
    word_count,
)

ROBOTIC_OPENERS = (
    r"^in this (section|lesson|part),?\s*",
    r"^it is important to (note|understand|remember) that\s*",
    r"^as (mentioned|discussed|stated) (above|earlier|previously),?\s*",
    r"^furthermore,?\s*",
    r"^moreover,?\s*",
    r"^additionally,?\s*",
    r"^in conclusion,?\s*",
    r"^to summarise,?\s*in conclusion,?\s*",
    r"^let'?s (dive|delve|explore)\b[^.]*\.\s*",
)

WARM_REPLACEMENTS = (
    (r"\butilize\b", "use"),
    (r"\butilise\b", "use"),
    (r"\bin order to\b", "to"),
    (r"\bdue to the fact that\b", "because"),
    (r"\ba large number of\b", "many"),
    (r"\bat this point in time\b", "now"),
    (r"\bwith regard to\b", "about"),
)


def strip_robotic_openers(text: str) -> str:
    out = (text or "").strip()
    for pat in ROBOTIC_OPENERS:
        out = re.sub(pat, "", out, flags=re.I)
    return out.strip()


def humanize_diction(text: str) -> str:
    out = text or ""
    for pat, repl in WARM_REPLACEMENTS:
        out = re.sub(pat, repl, out, flags=re.I)
    return out


def vary_openings(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Avoid identical first four words across consecutive sections."""
    seen: list[str] = []
    out: list[dict[str, Any]] = []
    alts = (
        "Notice how",
        "Here is another way to see",
        "A clear classroom example helps:",
    )
    alt_i = 0
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        row = dict(sec)
        body = str(row.get("body") or "").strip()
        if not body:
            out.append(row)
            continue
        first = " ".join(body.split()[:4]).lower()
        if first in seen and not body.startswith("-"):
            prefix = alts[alt_i % len(alts)]
            alt_i += 1
            # Only prefix if it doesn't already start warmly
            if not body.lower().startswith(tuple(a.lower() for a in alts)):
                body = f"{prefix} {body[0].lower()}{body[1:]}" if body else body
        seen.append(first)
        row["body"] = body
        out.append(row)
    return out


def polish_paragraph(text: str, *, idea: str = "") -> str:
    text = strip_robotic_openers(text)
    text = humanize_diction(text)
    text = dedupe_sentences(text)
    text = ensure_paragraph_quality(text, idea=idea)
    # Soften abrupt one-word connectors used as whole paragraphs
    if word_count(text) < 8 and sentence_count(text) < 2 and idea:
        text = (
            f"{text.rstrip('.')}."
            f" This connects directly to {idea}, so keep the meaning precise as you continue."
        )
    return text


def polish_adaptation(adaptation: dict[str, Any]) -> dict[str, Any]:
    """Rewrite lesson prose for publisher-quality teaching voice."""
    out = dict(adaptation)
    if out.get("big_idea"):
        out["big_idea"] = polish_paragraph(str(out["big_idea"]), idea="the big idea")
    sections = []
    for sec in out.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        row = dict(sec)
        title = str(row.get("title") or "")
        body = str(row.get("body") or "")
        # Preserve intentional bullet scaffolds for ADHD/dyslexia etc.
        if body.lstrip().startswith("-"):
            lines = [polish_paragraph(ln.lstrip("- ").strip(), idea=title) if ln.strip().startswith("-") or True else ln for ln in body.splitlines()]
            # Simpler: polish each bullet line lightly
            polished_lines = []
            for ln in body.splitlines():
                raw = ln.strip()
                if raw.startswith("-"):
                    content = raw[1:].strip()
                    content = strip_robotic_openers(humanize_diction(content))
                    polished_lines.append(f"- {content}")
                elif raw:
                    polished_lines.append(polish_paragraph(raw, idea=title))
            row["body"] = "\n".join(polished_lines)
        else:
            row["body"] = polish_paragraph(body, idea=title)
        sections.append(row)
    out["sections"] = vary_openings(sections)
    if out.get("summary"):
        out["summary"] = polish_paragraph(str(out["summary"]), idea="summary")
    out.setdefault("lce", {})
    if isinstance(out["lce"], dict):
        out["lce"]["writing_excellence"] = True
    return out


def polish_package(adaptations: dict[str, Any]) -> dict[str, Any]:
    out = dict(adaptations)
    for key, value in list(out.items()):
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key in {"vocabulary", "worksheet"}:
            continue
        out[key] = polish_adaptation(value)
    return out
