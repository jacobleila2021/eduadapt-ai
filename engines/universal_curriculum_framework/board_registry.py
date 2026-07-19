"""Board registry — supported educational boards & catalogues."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.schemas import BoardMetadata, SUPPORTED_BOARDS

_BOARD_CATALOGUE: dict[str, BoardMetadata] = {
    "cbse": BoardMetadata("cbse", "CBSE", country="IN", assessment_system="board_exams", certification="CBSE"),
    "ncert": BoardMetadata("ncert", "NCERT", country="IN", copyright_status="ncert_restricted", certification="NCERT"),
    "icse": BoardMetadata("icse", "ICSE", country="IN", certification="CISCE"),
    "isc": BoardMetadata("isc", "ISC", country="IN", certification="CISCE"),
    "cambridge": BoardMetadata("cambridge", "Cambridge", country="UK", certification="Cambridge Assessment"),
    "ib": BoardMetadata("ib", "IB", country="CH", certification="IBO"),
    "nios": BoardMetadata("nios", "NIOS", country="IN", certification="NIOS"),
    "state_board": BoardMetadata("state_board", "State Board", country="IN", region="varies"),
    "kerala_scert": BoardMetadata("kerala_scert", "Kerala SCERT", country="IN", region="Kerala"),
    "university": BoardMetadata("university", "University", country="", certification="degree"),
    "professional": BoardMetadata("professional", "Professional Certification", certification="credential"),
    "corporate": BoardMetadata("corporate", "Corporate Learning", certification="internal"),
}


def list_boards() -> list[dict[str, Any]]:
    return [b.to_dict() for b in _BOARD_CATALOGUE.values()]


def get_board(board_id: str) -> BoardMetadata:
    key = (board_id or "").strip().lower().replace(" ", "_")
    aliases = {"scert": "state_board", "igcse": "cambridge", "state": "state_board"}
    key = aliases.get(key, key)
    return _BOARD_CATALOGUE.get(key) or BoardMetadata(key or "unknown", board_id or "Unknown")


def supported_board_names() -> list[str]:
    return list(SUPPORTED_BOARDS)
