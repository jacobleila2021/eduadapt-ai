"""Highlighting timelines for word / sentence / paragraph sync."""

from __future__ import annotations

from typing import Any
import re


def build_highlight_timeline(
    sentences: list[str],
    paragraphs: list[str],
    full_text: str,
    *,
    mode: str = "sentence",
    speed: float = 1.0,
) -> list[dict[str, Any]]:
    """Estimate timing (~150 wpm base) for client sync; not AI-invented content."""
    wpm = 150.0 * max(float(speed), 0.5)
    ms_per_word = 60000.0 / wpm
    cursor = 0.0
    units: list[dict[str, Any]] = []

    if mode == "paragraph":
        chunks = paragraphs or sentences or ([full_text] if full_text else [])
    elif mode == "word":
        chunks = re.findall(r"\S+", full_text or " ".join(sentences))
    else:
        chunks = sentences or ([full_text] if full_text else [])

    for i, chunk in enumerate(chunks):
        words = max(len(str(chunk).split()), 1)
        dur = words * ms_per_word
        units.append(
            {
                "index": i,
                "text": chunk,
                "start_ms": round(cursor, 1),
                "end_ms": round(cursor + dur, 1),
                "mode": mode,
            }
        )
        cursor += dur
    return units


def keywords_to_highlight(text: str, keywords: list[str]) -> list[dict[str, Any]]:
    found = []
    lower = (text or "").lower()
    for kw in keywords or []:
        if kw and kw.lower() in lower:
            found.append({"keyword": kw, "present": True})
    return found
