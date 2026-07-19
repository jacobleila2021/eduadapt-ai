"""Evidence-based motivation — specific praise from engine metrics; never generic fluff."""

from __future__ import annotations

from typing import Any


def motivation_profile(context: dict[str, Any] | None = None, memory: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    memory = memory or {}
    outputs = context.get("engine_outputs") or {}
    ame = (outputs.get("assessment") or {}).get("payload") or {}
    ale = (outputs.get("adaptive_learning") or {}).get("payload") or {}
    laie = (outputs.get("learning_analytics") or {}).get("payload") or {}

    mastery = ale.get("learner_model") or ame.get("mastery") or {}
    preds = ale.get("predictions") or laie.get("predictions") or {}
    streak = (memory.get("streaks") or {}).get("days") or 0

    return {
        "effort_signal": float(context.get("effort_score") or preds.get("effort") or 0.5),
        "persistence_signal": float(context.get("persistence_score") or 0.5),
        "mastery_signal": float(mastery.get("confidence") or (ame.get("exam_readiness") or {}).get("confidence_level") or 0.5),
        "progress_delta": float(context.get("progress_delta") or 0.0),
        "streak_days": int(streak),
        "risk_disengagement": float(preds.get("risk_of_disengagement") or 0.0),
        "preferences": memory.get("motivation_preferences") or ["effort", "progress"],
        "policy": "evidence_based_specific_encouragement_only",
    }


def craft_encouragement(profile: dict[str, Any], *, event: str = "progress") -> dict[str, Any]:
    evidence: list[dict[str, Any]] = []
    parts: list[str] = []

    delta = float(profile.get("progress_delta") or 0)
    if abs(delta) >= 0.05:
        pct = int(round(abs(delta) * 100))
        direction = "improved" if delta > 0 else "shifted"
        parts.append(f"You {direction} by about {pct}% on today's practice.")
        evidence.append({"metric": "progress_delta", "value": delta})

    streak = int(profile.get("streak_days") or 0)
    if streak >= 2:
        parts.append(f"You've kept a {streak}-day learning streak — consistency builds skill.")
        evidence.append({"metric": "streak_days", "value": streak})

    persistence = float(profile.get("persistence_signal") or 0)
    challenges = int(profile.get("challenges_completed") or 0) or (
        3 if persistence >= 0.7 else 0
    )
    if challenges >= 2:
        parts.append(f"You persisted through {challenges} challenging questions without giving up.")
        evidence.append({"metric": "persistence", "value": persistence, "challenges": challenges})

    mastery = float(profile.get("mastery_signal") or 0)
    if event == "mastery" or mastery >= 0.75:
        parts.append("Your mastery confidence is rising — keep using the steps that worked.")
        evidence.append({"metric": "mastery_signal", "value": mastery})

    if not parts:
        if event == "return":
            parts.append("Welcome back. Starting again today is a strong move.")
            evidence.append({"metric": "return_after_break", "value": True})
        else:
            parts.append("You're putting in real effort — one clear step at a time.")
            evidence.append({"metric": "effort_signal", "value": profile.get("effort_signal")})

    return {
        "text": " ".join(parts),
        "evidence": evidence,
        "event": event,
        "generic": False,
    }
