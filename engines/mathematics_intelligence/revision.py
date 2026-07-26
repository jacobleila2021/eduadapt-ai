"""Revision / spaced-practice metadata (LMAS/ALE consume; MIP supplies hints)."""

from __future__ import annotations

from typing import Any

from engines.mathematics_intelligence.pedagogy import revision_summary

__all__ = ["revision_summary", "math_revision_for_domains"]


def math_revision_for_domains(
    domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]
) -> dict[str, Any]:
    return revision_summary(domains, misconceptions)
