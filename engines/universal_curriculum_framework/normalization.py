"""Normalization — board labels → UCF structure (wraps KIE aliases)."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.board_registry import get_board


def normalize_board_id(raw: str) -> str:
    try:
        from engines.knowledge_ingestion_engine.normalization import normalize_board

        name = normalize_board(raw)
    except Exception:  # noqa: BLE001
        name = (raw or "Unknown").strip()
    board = get_board(name)
    return board.board_id


def normalize_to_structure(raw: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = raw or {}
    try:
        from engines.knowledge_ingestion_engine.normalization import normalize_hierarchy

        h = normalize_hierarchy(
            chapter=int(raw.get("chapter") or raw.get("chapter_number") or 0),
            chapter_title=str(raw.get("chapter_title") or raw.get("chapter") or ""),
            topic=str(raw.get("topic") or ""),
            concepts=list(raw.get("concepts") or []),
            learning_objectives=list(raw.get("learning_objectives") or []),
            original_labels=raw.get("original_labels"),
        )
    except Exception:  # noqa: BLE001
        h = {"internal": raw, "preserves_source_terminology": True}
    return {
        "board_id": normalize_board_id(str(raw.get("board") or "Unknown")),
        "hierarchy": h,
        "grade": str(raw.get("grade") or ""),
        "subject": str(raw.get("subject") or ""),
        "source_labels_preserved": True,
    }
