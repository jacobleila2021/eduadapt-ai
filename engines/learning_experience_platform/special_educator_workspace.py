"""Special educator workspace — AIE-grounded accommodations & IEP support notes."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.accessibility import apply_aie
from engines.learning_experience_platform.collab_store import load_workspace_notes, save_workspace_note
from engines.learning_experience_platform.permissions import require


def special_educator_workspace(
    *,
    educator_id: str,
    learner_id: str,
    lesson_id: str = "",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gate = require("special_educator", "view_a11y")
    if not gate["ok"]:
        return gate
    context = context or {}
    a11y = apply_aie(learner_id, context)
    outputs = context.get("engine_outputs") or {}
    aie = (outputs.get("accessibility") or {}).get("payload") or {}
    ale = (outputs.get("adaptive_learning") or {}).get("payload") or {}

    observations = load_workspace_notes("special_educator", educator_id, lesson_id)
    goals = [n for n in observations if n.get("kind") == "goal"]
    therapy = [n for n in observations if n.get("kind") == "therapy"]
    iep = [n for n in observations if n.get("kind") == "iep"]
    history = [n for n in observations if n.get("kind") == "accommodation"]

    analytics.track("accessibility", learner_id=learner_id, lesson_id=lesson_id, payload={"role": "special_educator"})
    return {
        "ok": True,
        "workspace": "special_educator",
        "learner_id": learner_id,
        "lesson_id": lesson_id,
        "accommodation_recommendations": aie.get("recommendations") or a11y.get("preferences") or {},
        "executive_function_supports": aie.get("executive_function") or {
            "chunking": True,
            "checklists": True,
            "timers": True,
            "source": "AIE_presentation_only",
        },
        "intervention_planning": ale.get("interventions") or aie.get("interventions") or [],
        "reading_support_recommendations": a11y.get("preferences") or {},
        "accessibility_insights": a11y,
        "learner_observations": [n for n in observations if n.get("kind") == "observation"],
        "progress_monitoring": {
            "adaptive": ale.get("learner_model") or ale.get("pathway") or {},
            "a11y_prefs": a11y.get("preferences"),
        },
        "iep_support_notes": iep,
        "therapy_notes": therapy,
        "accommodation_history": history,
        "goal_tracking": goals,
        "collaboration": {"teacher": True, "parent": True},
        "policy": {"presentation_only": True, "never_alter_curriculum": True},
    }


def sped_add_note(
    educator_id: str,
    learner_id: str,
    text: str,
    *,
    kind: str = "observation",
    lesson_id: str = "",
) -> dict[str, Any]:
    allowed = {"observation", "iep", "therapy", "accommodation", "goal"}
    if kind not in allowed:
        kind = "observation"
    note = save_workspace_note("special_educator", educator_id, {
        "lesson_id": lesson_id,
        "learner_id": learner_id,
        "kind": kind,
        "text": text,
        "curriculum_locked": True,
    })
    return {"ok": True, "note": note}
