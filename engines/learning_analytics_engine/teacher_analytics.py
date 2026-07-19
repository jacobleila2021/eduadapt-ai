"""Teacher analytics facade."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.class_analytics import teacher_analytics as build_teacher_analytics


def teacher_analytics(sources: dict[str, Any], class_bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    return build_teacher_analytics(sources, class_bundle)
