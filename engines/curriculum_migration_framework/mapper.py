"""Map CMIF packages into UCF via CEF (engines stay UCF-only)."""

from __future__ import annotations

from typing import Any

from engines.curriculum_expansion_framework.mapping import map_to_ucf_payload, resolve_ucf_board
from engines.curriculum_expansion_framework.schemas import CURRICULUM_FAMILIES


def resolve_curriculum_id(board: str) -> str:
    b = (board or "").lower()
    if b in CURRICULUM_FAMILIES:
        return b
    # Map coarse boards to CEF family ids
    coarse = {
        "cambridge": "cambridge_lower_secondary",
        "ib": "ib_myp",
        "state_board": "kerala_scert",
        "professional": "professional_cert",
    }
    return coarse.get(b, b if b in CURRICULUM_FAMILIES else "cbse")


def map_to_ucf(normalized: dict[str, Any]) -> dict[str, Any]:
    curriculum_id = resolve_curriculum_id(str(normalized.get("board") or "cbse"))
    payload = map_to_ucf_payload(normalized, curriculum_id=curriculum_id)
    payload["cmif_curriculum_id"] = curriculum_id
    payload["ucf_board"] = resolve_ucf_board(curriculum_id)
    return {"ok": True, "curriculum_id": curriculum_id, "ucf_payload": payload}


def cross_board_compare(left_board: str, right_board: str) -> dict[str, Any]:
    """Reuse CEF equivalency / CIE-friendly UCF packages."""
    from engines.curriculum_expansion_framework.equivalency import compare_curricula
    from engines.curriculum_expansion_framework.mapping import resolve_ucf_board

    return compare_curricula(
        left_board=resolve_ucf_board(resolve_curriculum_id(left_board)),
        right_board=resolve_ucf_board(resolve_curriculum_id(right_board)),
    )
