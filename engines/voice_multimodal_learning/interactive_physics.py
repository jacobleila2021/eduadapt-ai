"""Interactive physics — wraps verified physics / circuit engines."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.multimodal import interactive_physics


def build(context: dict[str, Any] | None = None) -> dict[str, Any]:
    return interactive_physics(context)
