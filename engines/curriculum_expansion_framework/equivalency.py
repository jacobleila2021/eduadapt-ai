"""Cross-board equivalency — LO/competency/topic overlap & gaps."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.curriculum_registry import list_packages, load_package


def _tokens(text: str) -> set[str]:
    return {w.lower() for w in "".join(c if c.isalnum() or c.isspace() else " " for c in (text or "")).split() if len(w) > 2}


def _topic_texts(pkg: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for t in pkg.get("topics") or []:
        title = str(t.get("title") or "")
        objs = t.get("objectives") or {}
        knowledge = " ".join(str(x) for x in (objs.get("knowledge") or []))
        comps = " ".join(
            str(c.get("description") or c.get("competency_id") or "")
            for c in (t.get("competencies") or [])
            if isinstance(c, dict)
        )
        rows.append({
            "topic_id": t.get("topic_id"),
            "title": title,
            "text": f"{title} {knowledge} {comps}",
            "objectives": objs.get("knowledge") or [],
            "competencies": [c.get("competency_id") for c in (t.get("competencies") or []) if isinstance(c, dict)],
        })
    return rows


def _best_overlap(a: dict[str, Any], candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, float]:
    ta = _tokens(a.get("text") or a.get("title") or "")
    if not ta:
        return None, 0.0
    best = None
    best_score = 0.0
    for b in candidates:
        tb = _tokens(b.get("text") or b.get("title") or "")
        if not tb:
            continue
        score = len(ta & tb) / max(len(ta | tb), 1)
        if score > best_score:
            best_score = score
            best = b
    return best, best_score


def compare_curricula(
    left_package_id: str = "",
    right_package_id: str = "",
    *,
    left_board: str = "",
    right_board: str = "",
    threshold: float = 0.15,
) -> dict[str, Any]:
    """
    Compare two UCF packages (or first packages for given boards).
    Examples: CBSE Class 8 Science ↔ Cambridge Lower Secondary Science.
    """
    left = load_package(left_package_id) if left_package_id else None
    right = load_package(right_package_id) if right_package_id else None
    if not left and left_board:
        pkgs = list_packages(board_id=left_board, status="") or list_packages(board_id=left_board, status="active")
        if pkgs:
            left = load_package(pkgs[0]["package_id"])
    if not right and right_board:
        pkgs = list_packages(board_id=right_board, status="") or list_packages(board_id=right_board, status="active")
        if pkgs:
            right = load_package(pkgs[0]["package_id"])
    if not left or not right:
        return {"ok": False, "error": "packages_not_found", "hint": "Import both curricula into UCF first"}

    lt = _topic_texts(left)
    rt = _topic_texts(right)
    alignments = []
    matched_right: set[str] = set()
    for a in lt:
        b, score = _best_overlap(a, rt)
        if b and score >= threshold:
            matched_right.add(str(b.get("topic_id") or b.get("title")))
            alignments.append({
                "left": a.get("title"),
                "right": b.get("title"),
                "score": round(score, 3),
                "type": "topic_overlap",
            })
    gaps_left = [a.get("title") for a in lt if not any(x["left"] == a.get("title") for x in alignments)]
    gaps_right = [b.get("title") for b in rt if str(b.get("topic_id") or b.get("title")) not in matched_right]

    left_objs = [o for a in lt for o in (a.get("objectives") or [])]
    right_objs = [o for b in rt for o in (b.get("objectives") or [])]

    return {
        "ok": True,
        "left": {"package_id": left.get("package_id"), "board": (left.get("board") or {}).get("board_id"), "topics": len(lt)},
        "right": {"package_id": right.get("package_id"), "board": (right.get("board") or {}).get("board_id"), "topics": len(rt)},
        "topic_alignments": alignments,
        "learning_objective_alignment": {
            "left_count": len(left_objs),
            "right_count": len(right_objs),
            "shared_token_overlap": round(
                len(_tokens(" ".join(str(x) for x in left_objs)) & _tokens(" ".join(str(x) for x in right_objs)))
                / max(len(_tokens(" ".join(str(x) for x in left_objs)) | _tokens(" ".join(str(x) for x in right_objs))), 1),
                3,
            ),
        },
        "gaps": {"in_left_not_right": gaps_left[:20], "in_right_not_left": gaps_right[:20]},
        "assessment_comparison": {
            "left_questions": len(left.get("questions") or []),
            "right_questions": len(right.get("questions") or []),
        },
        "policy": {"deterministic_token_overlap": True, "no_llm_equivalence": True},
    }
