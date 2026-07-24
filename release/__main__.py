"""python -m release — RC1 campaign + Beta Readiness Report."""

from __future__ import annotations

import argparse
import json
import sys

from release import RC_TAG, RELEASE_CANDIDATE_PRODUCTION_READINESS_SMOKE_OK
from release.campaign import run_rc1_campaign
from release.report import build_rc1_report, write_rc1_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Alora AI Release Candidate campaign")
    parser.add_argument("--target", type=int, default=100, help="Lesson packages to generate (default 100)")
    parser.add_argument("--smoke", action="store_true", help="Fast smoke: 4 packages")
    parser.add_argument("--subjects", nargs="*", default=None)
    parser.add_argument("--curricula", nargs="*", default=None)
    parser.add_argument("--no-auto-fix", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    target = 4 if args.smoke else args.target
    subjects = tuple(args.subjects) if args.subjects else (("physics", "biology", "mathematics", "english") if args.smoke else None)
    curricula = tuple(args.curricula) if args.curricula else (("cbse",) if args.smoke else None)

    campaign = run_rc1_campaign(
        target_packages=target,
        subjects=subjects,
        curricula=curricula,
        max_topics_per_subject=1,
        compose=True,
        auto_fix=not args.no_auto_fix,
    )

    pobr_meta = {}
    try:
        from pobr import apply_pobr

        pobr_meta = apply_pobr({"ok": campaign.get("rc1_ready")}, write_reports=False)
    except Exception:  # noqa: BLE001
        pobr_meta = {}

    report = build_rc1_report(campaign, pobr=pobr_meta)
    paths = {} if args.no_write else write_rc1_report(report)

    print(
        json.dumps(
            {
                "smoke_ok": RELEASE_CANDIDATE_PRODUCTION_READINESS_SMOKE_OK,
                "tag": RC_TAG,
                "rc1_ready": campaign.get("rc1_ready"),
                "packages_ok": campaign.get("packages_ok"),
                "packages_targeted": campaign.get("packages_targeted"),
                "critical_open": (campaign.get("defects") or {}).get("critical_open_count"),
                "high_open": (campaign.get("defects") or {}).get("high_open_count"),
                "performance": campaign.get("performance"),
                "report_paths": paths,
            },
            indent=2,
        )
    )
    return 0 if campaign.get("rc1_ready") else 1


if __name__ == "__main__":
    sys.exit(main())
