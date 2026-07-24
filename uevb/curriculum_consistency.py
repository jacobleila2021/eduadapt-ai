"""Curriculum consistency — educational equivalence across boards."""

from __future__ import annotations

from typing import Any, Mapping

from uevb.publisher_benchmark import curriculum_consistency_report


def compare_curriculum_packages(
    packages: list[Mapping[str, Any]],
    *,
    concept: str = "",
) -> dict[str, Any]:
    return curriculum_consistency_report(packages, concept=concept)
