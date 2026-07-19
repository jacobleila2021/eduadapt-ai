"""CLI: ingest educational documents via Knowledge Ingestion Engine (KIE)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engines.knowledge_ingestion_engine import ingest_document
from knowledge.pilot_config import ACTIVE_PILOT


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest PDF/DOCX/PPTX/EPUB/TXT/MD/HTML/ZIP via Alora KIE"
    )
    parser.add_argument("source", type=Path, help="Path to document or ZIP package")
    parser.add_argument("--board", default=ACTIVE_PILOT.board)
    parser.add_argument("--grade", default=ACTIVE_PILOT.grade)
    parser.add_argument("--subject", default=ACTIVE_PILOT.subject)
    parser.add_argument("--curriculum", default="NCERT")
    parser.add_argument("--no-figures", action="store_true")
    parser.add_argument("--no-index", action="store_true")
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"File not found: {args.source}", file=sys.stderr)
        return 1

    result = ingest_document(
        args.source,
        board=args.board,
        grade=args.grade,
        subject=args.subject,
        curriculum=args.curriculum,
        extract_figures=not args.no_figures,
        reindex=not args.no_index,
    )
    print(json.dumps({
        "ok": result.get("ok"),
        "package_id": (result.get("package") or {}).get("package_id"),
        "package_path": result.get("package_path"),
        "chunks": len((result.get("package") or {}).get("text_chunks") or []),
        "figures": len((result.get("package") or {}).get("figures") or []),
        "questions": len((result.get("package") or {}).get("questions") or []),
        "equations": len((result.get("package") or {}).get("equations") or []),
        "index_status": (result.get("package") or {}).get("index_status"),
        "warnings": result.get("warnings"),
    }, indent=2, default=str))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
