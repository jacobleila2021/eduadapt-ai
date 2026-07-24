"""python -m pobr — generate Beta Readiness Report."""

from __future__ import annotations

import json
import sys

from pobr import PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK, apply_pobr


def main() -> int:
    package = {}
    try:
        from peec.corpus_sample import compose_sample_for_peec

        package = compose_sample_for_peec()
    except Exception as exc:  # noqa: BLE001
        package = {"ok": False, "error": str(exc)}
    result = apply_pobr(package, write_reports=True)
    print(
        json.dumps(
            {
                "smoke_ok": PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK,
                "beta_ready": result.get("beta_ready"),
                "overall": result.get("overall_beta_readiness"),
                "report_paths": result.get("report_paths"),
            },
            indent=2,
        )
    )
    return 0 if result.get("beta_ready") else 1


if __name__ == "__main__":
    sys.exit(main())
