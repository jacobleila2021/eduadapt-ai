"""Lesson navigation — TOC, breadcrumbs, next/prev, resume."""

from __future__ import annotations

from typing import Any


def build_toc(lesson: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    lesson = lesson or {}
    sections = lesson.get("sections") or []
    if not sections and lesson.get("body"):
        sections = [{"id": "body", "title": "Lesson", "anchor": "sec_body"}]
    toc = []
    for i, sec in enumerate(sections):
        if isinstance(sec, str):
            toc.append({"id": f"sec_{i}", "title": sec, "anchor": f"sec_{i}", "index": i})
        else:
            toc.append(
                {
                    "id": sec.get("id") or f"sec_{i}",
                    "title": sec.get("title") or sec.get("heading") or f"Section {i + 1}",
                    "anchor": sec.get("anchor") or sec.get("id") or f"sec_{i}",
                    "index": i,
                }
            )
    return toc


def breadcrumbs(*, board: str = "", grade: str = "", subject: str = "", chapter: str = "", topic: str = "") -> list[dict[str, str]]:
    crumbs = []
    for label, value in (("Board", board), ("Grade", grade), ("Subject", subject), ("Chapter", chapter), ("Topic", topic)):
        if value:
            crumbs.append({"label": label, "value": str(value)})
    return crumbs


def navigation_state(
    toc: list[dict[str, Any]],
    *,
    current_index: int = 0,
    resume_anchor: str = "",
) -> dict[str, Any]:
    n = len(toc)
    idx = max(0, min(current_index, max(n - 1, 0)))
    if resume_anchor:
        for i, item in enumerate(toc):
            if item.get("anchor") == resume_anchor or item.get("id") == resume_anchor:
                idx = i
                break
    return {
        "toc": toc,
        "current_index": idx,
        "current": toc[idx] if toc else None,
        "previous": toc[idx - 1] if idx > 0 else None,
        "next": toc[idx + 1] if idx + 1 < n else None,
        "can_prev": idx > 0,
        "can_next": idx + 1 < n,
    }
