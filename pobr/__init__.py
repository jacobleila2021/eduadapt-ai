"""
Product Optimisation & Beta Readiness (POBR).

Commercial readiness audits — not a new intelligence engine.
"""

from __future__ import annotations

from pobr.constants import (
    POBR_VERSION,
    PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK,
)
from pobr.service import apply_pobr
from pobr.beta_readiness import build_beta_readiness_report

__all__ = [
    "PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK",
    "POBR_VERSION",
    "apply_pobr",
    "build_beta_readiness_report",
]
