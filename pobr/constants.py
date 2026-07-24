"""Product Optimisation & Beta Readiness — constants."""

from __future__ import annotations

PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK = True
POBR_VERSION = "1.0.0"
POBR_SCHEMA = "alora.pobr.v1"

# Beta may ship when overall >= this (commercial polish still continues)
BETA_READY_MIN = 85.0

CATEGORIES = (
    "educational_quality",
    "writing_quality",
    "visual_quality",
    "adaptation_quality",
    "accessibility",
    "performance",
    "rendering",
    "reliability",
    "commercial_readiness",
)

JOURNEYS = (
    "teacher_generate",
    "student_learn",
    "parent_support",
    "teacher_export",
)
