"""Narration planning — verified lesson text only via audio_learning."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.schemas import NarrationPlan


def plan_narration(
    content: Any,
    *,
    spec_id: str = "original",
    speed: float = 1.0,
    language: str = "en",
    voice_style: str = "Female",
    title: str = "",
) -> NarrationPlan:
    from audio_learning import build_narration, extract_speech_text, split_sentences

    if title:
        text = extract_speech_text(title, content, spec_id)
    else:
        text = build_narration(content, spec_id)
    sentences = split_sentences(text) if text else []
    paragraphs = [p.strip() for p in re_split_paragraphs(text)]
    return NarrationPlan(
        text=text or "",
        sentences=sentences,
        paragraphs=paragraphs,
        speed=speed,
        language=language,
        voice_style=voice_style,
        source="verified_lesson",
    )


def re_split_paragraphs(text: str) -> list[str]:
    import re

    parts = re.split(r"\n\s*\n+", text or "")
    return [p for p in parts if p.strip()] or ([text] if text else [])
