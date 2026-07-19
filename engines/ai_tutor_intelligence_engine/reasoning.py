"""Reasoning orchestrator — pick response strategy from mode + grounding."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.explanations import generate_explanation
from engines.ai_tutor_intelligence_engine.hints import generate_hint
from engines.ai_tutor_intelligence_engine.misconception_handler import handle_misconceptions
from engines.ai_tutor_intelligence_engine.personalization import personalization_rules, select_explanation_depth
from engines.ai_tutor_intelligence_engine.schemas import GroundingPacket, TutorContext
from engines.ai_tutor_intelligence_engine.socratic import socratic_turn
from engines.ai_tutor_intelligence_engine.worked_examples import worked_example


def reason_response(
    ctx: TutorContext,
    grounding: GroundingPacket,
    *,
    mode: str,
    action: str = "tutor",  # tutor|hint|explain|worked_example|socratic
    hint_level: int = 1,
) -> dict[str, Any]:
    pers = personalization_rules(ctx)
    depth = pers.get("depth") or select_explanation_depth(ctx)

    if grounding.insufficient_evidence:
        return {
            "ok": False,
            "mode": mode,
            "action": action,
            "content": grounding.reason,
            "grounding": grounding.to_dict(),
            "personalization": pers,
        }

    if action == "hint":
        payload = generate_hint(ctx, grounding, level=hint_level, allow_full_solution=ctx.allow_direct_answers)
    elif action == "explain":
        payload = generate_explanation(ctx, grounding, depth=depth, personalization=pers)
    elif action == "worked_example":
        payload = worked_example(ctx, grounding)
    elif action == "socratic" or mode == "socratic":
        payload = socratic_turn(ctx, grounding)
    elif mode in ("worked_example", "step_coaching", "direct_instruction"):
        payload = worked_example(ctx, grounding) if mode != "direct_instruction" else generate_explanation(
            ctx, grounding, depth=depth, personalization=pers
        )
    elif mode == "guided_discovery" and ctx.misconceptions:
        payload = handle_misconceptions(ctx, grounding)
        payload["content"] = "\n\n".join(
            c.get("content") or "" for c in payload.get("corrections") or [] if c.get("ok")
        ) or socratic_turn(ctx, grounding).get("content")
    else:
        # Default: socratic + short grounded explanation
        soc = socratic_turn(ctx, grounding)
        exp = generate_explanation(ctx, grounding, depth=depth, personalization=pers)
        payload = {
            "ok": True,
            "content": (soc.get("content") or "") + "\n\n" + (exp.get("content") or ""),
            "questions": soc.get("questions"),
            "explanation": exp,
            "citations": grounding.citations[:8],
        }

    misc = handle_misconceptions(ctx, grounding)
    return {
        "ok": bool(payload.get("ok", True)),
        "mode": mode,
        "action": action,
        "depth": depth,
        "personalization": pers,
        "payload": payload,
        "content": payload.get("content") or "",
        "misconceptions": misc,
        "grounding": grounding.to_dict(),
        "explainability": (
            f"Responded in '{mode}' at depth '{depth}' using {len(grounding.citations)} citations; "
            f"profiles={ctx.accessibility_profiles}; mastery={ctx.mastery_level}; "
            f"confidence={ctx.confidence:.0%}."
        ),
    }
