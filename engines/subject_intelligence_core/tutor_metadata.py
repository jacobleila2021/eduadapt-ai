"""Shared AI tutor metadata builders — ATIE remains conversation owner."""

from __future__ import annotations

from typing import Any, Sequence


def socratic_block(prompts: Sequence[str], *, owner: str = "ATIE") -> dict[str, Any]:
    return {"mode": "socratic", "prompts": list(prompts), "owner": owner}


def graduated_hints_block(levels: Sequence[str], *, owner: str = "ATIE") -> dict[str, Any]:
    return {"mode": "graduated_hints", "levels": list(levels), "owner": owner}


def worked_example_fading_block(
    scaffolds: Sequence[dict[str, Any]],
    *,
    owner: str = "ATIE",
    limit: int = 3,
) -> dict[str, Any]:
    return {
        "mode": "worked_example_fading",
        "scaffold_ids": [s.get("example_id") for s in scaffolds[:limit]],
        "owner": owner,
    }


def error_diagnosis_block(
    misconceptions: Sequence[dict[str, Any]],
    *,
    owner: str = "ATIE",
    limit: int = 5,
) -> dict[str, Any]:
    return {
        "mode": "error_diagnosis",
        "misconception_ids": [m.get("misconception_id") for m in misconceptions[:limit]],
        "owner": owner,
    }


def reflection_block(prompts: Sequence[str], *, owner: str = "ATIE") -> dict[str, Any]:
    return {"mode": "reflection", "prompts": list(prompts), "owner": owner}


def custom_mode_block(mode: str, *, owner: str = "ATIE", **payload: Any) -> dict[str, Any]:
    return {"mode": mode, "owner": owner, **payload}
