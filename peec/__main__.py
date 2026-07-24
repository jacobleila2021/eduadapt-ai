"""python -m peec — run Product Excellence audit on a composed sample."""

from __future__ import annotations

import json
import sys

from peec import PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK, apply_peec
from peec.corpus_sample import compose_sample_for_peec


def main() -> int:
    package = compose_sample_for_peec()
    result = apply_peec(
        dict(package.get("adaptations") or {}),
        board=package.get("intelligence_board") or {},
        pmes_report=package.get("publisher_review_report") or package.get("pmes") or {},
        write_reports=True,
    )
    print(
        json.dumps(
            {
                "smoke_ok": PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK,
                "ok": result.get("ok"),
                "open_items": len((result.get("audit") or {}).get("remediation_plan") or []),
                "report_paths": result.get("report_paths"),
            },
            indent=2,
        )
    )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
