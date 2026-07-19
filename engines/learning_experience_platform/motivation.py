"""LMAS motivation strip — non-distracting XP / journey snapshot."""

from __future__ import annotations

from typing import Any


def motivation_strip(learner_id: str) -> dict[str, Any]:
    try:
        from engines.learning_motivation_engine.service import (
            api_get_xp,
            api_get_rewards,
            api_get_journey,
            api_get_skill_tree,
        )

        return {
            "ok": True,
            "compact": True,
            "xp": api_get_xp(learner_id),
            "rewards": api_get_rewards(learner_id),
            "journey": api_get_journey(learner_id),
            "skill_tree": api_get_skill_tree(context={}),
            "display": "footer_or_drawer_not_over_text",
            "source": "lmas",
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "compact": True}
