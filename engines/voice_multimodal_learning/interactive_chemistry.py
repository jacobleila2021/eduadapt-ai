"""Interactive chemistry — wraps ChemPy/SymPy balancing & render; never invents."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.multimodal import interactive_chemistry


def build(context: dict[str, Any] | None = None) -> dict[str, Any]:
    out = interactive_chemistry(context)
    # Optionally attach a verified balance visualization descriptor
    eq = (context or {}).get("equation") or ""
    if eq:
        try:
            from engines.chemistry.balancer import balance_equation

            balanced = balance_equation(eq)
            payload = balanced.payload if hasattr(balanced, "payload") else balanced
            out = {**out, "balanced": payload if isinstance(payload, dict) else str(balanced), "visualization": "equation_balancing"}
        except Exception:  # noqa: BLE001
            out = {**out, "balanced": None, "note": "balancer_unavailable_or_invalid"}
    return out
