"""Interactive mathematics — wraps deterministic math/graph engines."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.multimodal import interactive_math


def build(context: dict[str, Any] | None = None) -> dict[str, Any]:
    return interactive_math(context)
