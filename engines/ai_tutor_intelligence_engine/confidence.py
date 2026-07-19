"""Tutor-side confidence estimate — blends AME/ALE + session signals."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import TutorContext


def estimate_tutor_confidence(
    ctx: TutorContext,
    *,
    hint_usage: int = 0,
    response_latency_sec: float | None = None,
    self_reported: float | None = None,
) -> dict[str, Any]:
    parts = [("mastery_context", float(ctx.confidence or 0.5), 0.4)]
    if self_reported is not None:
        parts.append(("self_reported", float(self_reported), 0.3))
    hint_pen = max(0.0, 1.0 - 0.12 * hint_usage)
    parts.append(("hint_usage", hint_pen, 0.2))
    if response_latency_sec is not None:
        # very fast may mean guessing; very slow may mean struggle — soft signal only
        lat = float(response_latency_sec)
        lat_score = 0.7 if 5 <= lat <= 90 else 0.45
        parts.append(("latency", lat_score, 0.1))

    total_w = sum(w for _, _, w in parts)
    score = sum(v * w for _, v, w in parts) / total_w
    strategy = "scaffold_more" if score < 0.45 else "maintain" if score < 0.75 else "stretch_socratic"
    return {
        "confidence": round(score, 4),
        "strategy": strategy,
        "factors": [{"name": n, "value": v, "weight": w} for n, v, w in parts],
    }
