"""Alora AI Computation Layer — deterministic engines.

Philosophy: one correct answer → engines; AI only explains/adapts.
See docs/THREE_LAYER_SCIENTIFIC_COMPUTING_ARCHITECTURE.md
"""

from engines.answer_router import classify_question, route_question
from engines.router import route
from engines.types import EngineResult, ToolTask, ValidationStatus

__all__ = [
    "route",
    "route_question",
    "classify_question",
    "EngineResult",
    "ToolTask",
    "ValidationStatus",
]
