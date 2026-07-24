"""python -m uevb — run Universal Educational Validation & Benchmarking."""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Alora UEVB validation suite")
    parser.add_argument("--subjects", nargs="*", default=None, help="Limit subjects")
    parser.add_argument("--curricula", nargs="*", default=None, help="Limit curricula")
    parser.add_argument("--max-lessons", type=int, default=6, help="Cap composed lessons")
    parser.add_argument("--max-topics", type=int, default=1, help="Topics per subject")
    parser.add_argument("--no-write", action="store_true", help="Do not write report files")
    parser.add_argument("--smoke", action="store_true", help="Minimal smoke (2 lessons)")
    args = parser.parse_args(argv)

    from uevb import pack_health, run_uevb_suite
    from uevb.dashboard import render_dashboard_markdown

    if args.smoke:
        result = run_uevb_suite(
            subjects=("physics", "biology"),
            curricula=("cbse",),
            max_topics_per_subject=1,
            max_lessons=2,
            write=not args.no_write,
        )
    else:
        result = run_uevb_suite(
            subjects=tuple(args.subjects) if args.subjects else None,
            curricula=tuple(args.curricula) if args.curricula else None,
            max_topics_per_subject=args.max_topics,
            max_lessons=args.max_lessons,
            write=not args.no_write,
        )

    print(json.dumps({"health": pack_health(), "ok": result.get("ok"), "release_gate": result.get("release_gate")}, indent=2))
    print()
    print(render_dashboard_markdown(result.get("dashboard") or {}))
    if result.get("report_paths"):
        print("\nReports:")
        for name, path in (result.get("report_paths") or {}).items():
            print(f"  {name}: {path}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
