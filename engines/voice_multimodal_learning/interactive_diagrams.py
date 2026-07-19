"""Interactive diagram helpers — re-export multimodal diagram planner."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.multimodal import interactive_diagrams as plan_interactive_diagrams


def build(context: dict[str, Any] | None = None) -> dict[str, Any]:
    return plan_interactive_diagrams(context)
