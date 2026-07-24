"""
Product Excellence & Experience Completion (PEEC).

Makes Alora feel like a premium educational product.
Not an intelligence engine — audits, remediations, and experience polish only.
"""

from __future__ import annotations

from peec.audit import run_product_excellence_audit
from peec.constants import (
    PEEC_VERSION,
    PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK,
)
from peec.service import apply_peec

__all__ = [
    "PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK",
    "PEEC_VERSION",
    "run_product_excellence_audit",
    "apply_peec",
]
