"""Complete-sentence gate for learner-facing Lesson Wall and diagram text."""

from __future__ import annotations

import re

_INCOMPLETE_TAIL = re.compile(
    r"(?i)\b("
    r"among the most|properties of metals and|metals and|"
    r"at room|must know|linked to|talk about|"
    r"the family tonight|one idea —|one idea -|"
    r"generates a magnetic|flow of electric|around a magnet or a|"
    r"direction of the magnetic|compass needle|"
    r"which are among|can exhibit lustrous|of lesson"
    r")\s*$"
)


def is_complete_teaching_sentence(text: str) -> bool:
    """True only when prose is a finished learner-facing sentence."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(t.split()) < 6:
        return False
    if "…" in t or "..." in t:
        return False
    if t.endswith((",", ";", ":", "-", "—", "(")):
        return False
    if not t.endswith((".", "!", "?")):
        return False
    body = t.rstrip(".!?")
    if _INCOMPLETE_TAIL.search(body):
        return False
    if re.search(r"(?i)\b(must know|reprint|see fig)\b", t):
        return False
    return True


def ensure_complete_teaching_sentence(text: str) -> str:
    """Return a complete sentence, or '' if the prose cannot be repaired."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    if not t:
        return ""
    t = t.replace("…", " ").replace("...", " ")
    t = re.sub(r"\s+", " ", t).strip(" ,;:-—")
    if not t:
        return ""
    if not t.endswith((".", "!", "?")):
        t = t + "."
    if not is_complete_teaching_sentence(t):
        return ""
    return t


def strip_adaptation_suffix(title: str) -> str:
    """Remove ' — Parent' / ' — Ld' lens suffixes from diagram titles."""
    raw = re.sub(r"\s+", " ", str(title or "")).strip()
    raw = re.sub(
        r"\s*[—\-–]\s*(Parent|Ld|Ell|Visual|Auditory|Dyslexia|Standard|Teacher|"
        r"ADHD|Autism)\s*$",
        "",
        raw,
        flags=re.I,
    ).strip()
    return raw
