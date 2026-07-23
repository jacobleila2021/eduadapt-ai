"""EATS golden lesson library — promote 98+ exemplars; compare rendered lessons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from eats.constants import GOLDEN_PROMOTION_SCORE

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = ROOT / "golden_lessons"
EATS_GOLDEN_INDEX = GOLDEN_DIR / "eats_index.json"


def _ensure_dir() -> Path:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    return GOLDEN_DIR


def list_eats_goldens() -> list[dict[str, Any]]:
    _ensure_dir()
    rows: list[dict[str, Any]] = []
    for path in sorted(GOLDEN_DIR.glob("*.json")):
        if path.name == "eats_index.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        score = float(data.get("publisher_score") or data.get("eats_score") or 0)
        rows.append(
            {
                "id": path.stem,
                "path": str(path),
                "subject": str(data.get("subject") or ""),
                "topic": str(data.get("topic") or ""),
                "publisher_score": score,
                "eats_certified": score >= GOLDEN_PROMOTION_SCORE or bool(data.get("eats_certified")),
            }
        )
    return rows


def load_closest_golden(*, subject: str = "", topic: str = "") -> dict[str, Any] | None:
    rows = list_eats_goldens()
    if not rows:
        return None
    sub = (subject or "").lower()
    top = (topic or "").lower()
    scored: list[tuple[float, dict[str, Any]]] = []
    for row in rows:
        pts = 0.0
        if sub and sub in str(row.get("subject") or "").lower():
            pts += 5
        if top and any(w in str(row.get("topic") or "").lower() for w in top.split()[:4] if len(w) > 3):
            pts += 3
        pts += float(row.get("publisher_score") or 0) / 100.0
        scored.append((pts, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]
    path = Path(best["path"])
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return best


def compare_to_eats_golden(
    adaptation: Mapping[str, Any],
    *,
    subject: str = "",
    overall_score: float = 0.0,
) -> dict[str, Any]:
    """Compare lesson quality signals against closest golden exemplar."""
    golden = load_closest_golden(
        subject=subject or str(adaptation.get("subject") or ""),
        topic=str(adaptation.get("topic") or adaptation.get("big_idea") or ""),
    )
    if not golden:
        return {"matched": False, "delta": 0.0, "notes": ["No golden exemplar available."]}

    g_score = float(golden.get("publisher_score") or golden.get("eats_score") or 95)
    # Prefer LCE compare when available (read-only)
    notes = [f"Compared to golden {golden.get('id') or golden.get('topic') or 'exemplar'}."]
    try:
        from engines.lesson_composition_engine.golden import compare_to_golden

        lce = compare_to_golden(dict(adaptation), subject=subject)
        delta = float(lce.get("delta") or 0.0)
        notes.extend(list(lce.get("notes") or [])[:4])
        # Also factor score gap vs golden publisher score
        score_gap = overall_score - g_score if overall_score else delta
        return {
            "matched": True,
            "delta": round(score_gap if overall_score else delta, 2),
            "golden_score": g_score,
            "notes": notes,
            "golden_id": golden.get("id") or Path(str(golden.get("path") or "")).stem,
        }
    except Exception:
        delta = (overall_score or 0) - g_score
        return {
            "matched": True,
            "delta": round(delta, 2),
            "golden_score": g_score,
            "notes": notes,
            "golden_id": golden.get("id"),
        }


def promote_to_golden(
    adaptations: Mapping[str, Any],
    *,
    subject: str,
    topic: str,
    publisher_score: float,
    lesson_id: str = "",
) -> str | None:
    """Store only lessons with publisher score >= 98."""
    if publisher_score < GOLDEN_PROMOTION_SCORE:
        return None
    _ensure_dir()
    slug = (lesson_id or f"{subject}_{topic}").lower()
    slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in slug)[:80]
    path = GOLDEN_DIR / f"{slug}.json"
    # Store a compact exemplar (standard + vocab summary) — not full private payloads
    standard = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    vocab = adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {}
    payload = {
        "id": slug,
        "subject": subject,
        "topic": topic,
        "publisher_score": round(publisher_score, 2),
        "eats_score": round(publisher_score, 2),
        "eats_certified": True,
        "big_idea": standard.get("big_idea") or "",
        "section_titles": [
            str(s.get("title") or "")
            for s in (standard.get("sections") or [])
            if isinstance(s, dict)
        ][:20],
        "vocabulary_terms": [
            str(w.get("term") or w.get("word") or "")
            for w in (vocab.get("words") or vocab.get("cards") or [])
            if isinstance(w, dict)
        ][:20],
        "has_svg": bool(
            str(standard.get("flowchart_svg") or "").startswith("<svg")
            or str(standard.get("concept_map_svg") or "").startswith("<svg")
        ),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    _update_index(slug, publisher_score, subject, topic)
    return str(path)


def _update_index(lesson_id: str, score: float, subject: str, topic: str) -> None:
    _ensure_dir()
    index: dict[str, Any] = {"lessons": []}
    if EATS_GOLDEN_INDEX.exists():
        try:
            index = json.loads(EATS_GOLDEN_INDEX.read_text(encoding="utf-8"))
        except Exception:
            index = {"lessons": []}
    lessons = [x for x in (index.get("lessons") or []) if x.get("id") != lesson_id]
    lessons.append(
        {
            "id": lesson_id,
            "publisher_score": score,
            "subject": subject,
            "topic": topic,
        }
    )
    index["lessons"] = lessons
    EATS_GOLDEN_INDEX.write_text(json.dumps(index, indent=2), encoding="utf-8")
