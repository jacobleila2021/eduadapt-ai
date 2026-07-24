"""Release gate — production allowed only when UEVB suite clears."""

from __future__ import annotations

from typing import Any, Mapping

from uevb.constants import RELEASE_PASS_RATE_MIN, UEVB_VERSION
from uevb.validate import validate_composed_package


def evaluate_release_gate(
    validations: list[Mapping[str, Any]],
    *,
    prior_dashboard: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Aggregate lesson validations into a release decision."""
    total = len(validations)
    passes = sum(1 for v in validations if v.get("ok"))
    pass_rate = (passes / total) if total else 0.0

    regressions: list[str] = []
    if prior_dashboard:
        prior_rate = float(prior_dashboard.get("pass_rate") or 0.0)
        if pass_rate + 1e-9 < prior_rate - 0.02:
            regressions.append(
                f"Pass rate regressed from {prior_rate:.2%} to {pass_rate:.2%}."
            )

    blocking: list[str] = []
    for v in validations:
        if v.get("ok"):
            continue
        topic = v.get("topic") or v.get("subject") or "lesson"
        failed = [k for k, ok in (v.get("gates") or {}).items() if not ok]
        blocking.append(f"{topic}: failed {', '.join(failed) or 'unknown gates'}")

    release_permitted = (
        total > 0
        and pass_rate >= RELEASE_PASS_RATE_MIN
        and not regressions
        and not blocking
    )
    # Allow release if pass_rate meets threshold even with soft notes, but not if blocking list non-empty
    # blocking non-empty means some lessons failed — release_permitted already False

    return {
        "schema": "alora.uevb.release_gate.v1",
        "uevb_version": UEVB_VERSION,
        "release_permitted": release_permitted,
        "pass_rate": round(pass_rate, 4),
        "threshold": RELEASE_PASS_RATE_MIN,
        "total_lessons": total,
        "passed": passes,
        "failed": total - passes,
        "regressions": regressions,
        "blocking_issues": blocking[:40],
        "rules": [
            "Every lesson passes PMES.",
            "Every adaptation is genuinely distinct.",
            "Every core engine demonstrates learner-visible value.",
            "Every page meets the Alora AI Design System.",
            "Every lesson meets publisher-quality standards.",
            "No regressions are detected.",
        ],
    }


def gate_package_for_production(package: Mapping[str, Any]) -> dict[str, Any]:
    """Single-package production gate (compose-time)."""
    validation = validate_composed_package(package, require_pmes=True)
    release = evaluate_release_gate([validation])
    return {
        "ok": bool(validation.get("ok")) and bool(release.get("release_permitted")),
        "validation": validation,
        "release_gate": release,
    }
