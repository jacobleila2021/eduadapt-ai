"""Release Candidate campaign — release engineering only (not a new validation system).

Reuses UEVB corpus, LCE compose, PMES/PEEC/UEVB/POBR gates already in production.
"""

from __future__ import annotations

RELEASE_CANDIDATE_PRODUCTION_READINESS_SMOKE_OK = True
PRODUCT_REFINEMENT_RC1_SMOKE_OK = True
RC_VERSION = "RC1"
RC_TAG = "ALORA-AI-RC1"


def rc1_product_health() -> dict:
    """Lightweight coverage check for RC1 product refinement (golden library)."""
    try:
        from engines.lesson_composition_engine.golden import golden_library_health

        health = golden_library_health()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "smoke_ok": PRODUCT_REFINEMENT_RC1_SMOKE_OK}
    return {
        **health,
        "smoke_ok": PRODUCT_REFINEMENT_RC1_SMOKE_OK,
        "tag": RC_TAG,
        "campaign_hint": "python -m release --target 100",
    }
