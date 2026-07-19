"""CLI: ingest NCERT PDF into knowledge store (pilot extension)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from knowledge.ncert_ingest import ingest_pdf_to_chunks, save_ingested_chunks
from knowledge.pilot_config import ACTIVE_PILOT
from knowledge.service import ensure_knowledge_index


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest NCERT PDF for Alora Knowledge Layer pilot")
    parser.add_argument("pdf", type=Path, help="Path to NCERT PDF")
    parser.add_argument("--label", default="ncert_upload", help="Output label")
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"File not found: {args.pdf}", file=sys.stderr)
        return 1

    chunks = ingest_pdf_to_chunks(args.pdf)
    out = save_ingested_chunks(chunks, args.label)
    print(f"Ingested {len(chunks)} chunks -> {out}")
    print(f"Pilot scope: {ACTIVE_PILOT.book_title} (Class {ACTIVE_PILOT.grade})")
    info = ensure_knowledge_index()
    print(f"Index: {info}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
