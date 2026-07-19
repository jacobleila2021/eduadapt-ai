"""Biology / NCERT curated figure lookup for pilot chapters."""

from __future__ import annotations

import json
import re
from pathlib import Path

from knowledge.build_biology_figures import FIGURES_DIR, build_figure_pack


def _ensure_pack() -> list[dict]:
    index_path = FIGURES_DIR / "index.json"
    if not index_path.is_file():
        build_figure_pack()
    # Refresh absolute paths
    data = json.loads(index_path.read_text(encoding="utf-8"))
    for row in data:
        rel = row.get("relative_path") or ""
        abs_path = FIGURES_DIR.parent / rel if rel.startswith("figures/") else Path(row.get("path") or "")
        # Prefer relative under seed/figures
        candidate = FIGURES_DIR / Path(rel).name if rel else Path(row.get("path") or "")
        if candidate.is_file():
            row["path"] = str(candidate)
        elif Path(row.get("path") or "").is_file():
            pass
        else:
            # rebuild once
            build_figure_pack()
            candidate = FIGURES_DIR / f"{row['id']}.svg"
            row["path"] = str(candidate)
    return data


def _terms(text: str) -> set[str]:
    stop = {
        "about",
        "chapter",
        "class",
        "diagram",
        "functions",
        "lesson",
        "showing",
        "structure",
        "typical",
        "with",
    }
    return {
        word
        for word in re.findall(r"[a-z]{4,}", str(text or "").lower())
        if word not in stop
    }


def match_biology_figures(
    lesson_text: str,
    topic: str = "",
    limit: int = 3,
    *,
    include_ingested: bool = False,
) -> list[dict]:
    """Return only figures with strong topic-level relevance.

    Single generic keyword hits such as ``normal``, ``area`` or ``pressure``
    are insufficient because they caused unrelated pilot figures to leak into
    universal lessons.
    """
    figures = _ensure_pack()
    blob = f"{topic}\n{lesson_text}".lower()
    topic_terms = _terms(topic)
    scored: list[tuple[int, dict]] = []
    for fig in figures:
        matched_keywords = [
            str(kw).lower()
            for kw in fig.get("keywords") or []
            if re.search(rf"\b{re.escape(str(kw).lower())}\b", blob)
        ]
        title = (fig.get("title") or "").lower()
        chapter_title = (fig.get("chapter_title") or "").lower()
        title_phrase = title.split("(")[0].strip()
        exact_title = bool(title_phrase and title_phrase in blob)
        figure_topic_terms = _terms(f"{title} {chapter_title}")
        topic_overlap = topic_terms & figure_topic_terms
        topic_keyword_match = any(
            re.search(rf"\b{re.escape(keyword)}\b", str(topic or "").lower())
            for keyword in matched_keywords
        )
        has_specific_keyword = any(
            " " in keyword or len(keyword) >= 9 for keyword in matched_keywords
        )
        if str(topic or "").strip():
            strongly_relevant = bool(
                exact_title or topic_overlap or topic_keyword_match
            )
        else:
            strongly_relevant = bool(
                exact_title
                or (len(matched_keywords) >= 2 and has_specific_keyword)
            )
        if strongly_relevant:
            score = (
                (6 if exact_title else 0)
                + 3 * len(topic_overlap)
                + 2 * len(matched_keywords)
            )
            scored.append((score, fig))
    scored.sort(key=lambda x: x[0], reverse=True)
    curated = [fig for _, fig in scored[:limit]] if scored else []

    # Global ingested figures are opt-in only. Universal uploaded-source mode
    # must not search unrelated textbook image indexes.
    if include_ingested:
        try:
            from knowledge.ncert_figures_ingest import match_ingested_figures

            ingested = match_ingested_figures(
                lesson_text, topic=topic, limit=limit
            )
            for fig in ingested:
                if fig not in curated:
                    curated.append(fig)
        except Exception:
            pass
    return curated[:limit]
