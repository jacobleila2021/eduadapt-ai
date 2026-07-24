"""Surface board / engine intelligence into learner-visible lesson text.

Golden rule: metadata that never reaches the learner is a defect.
"""

from __future__ import annotations

from typing import Any, Mapping


def _package_blob(adaptations: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key, value in adaptations.items():
        if str(key).startswith("_") or not isinstance(value, dict):
            continue
        parts.append(str(value.get("big_idea") or ""))
        for sec in value.get("sections") or []:
            if isinstance(sec, dict):
                parts.append(str(sec.get("title") or ""))
                parts.append(str(sec.get("body") or ""))
        wall = value.get("word_wall") or []
        for row in wall:
            if isinstance(row, dict):
                parts.append(str(row.get("term") or ""))
                parts.append(str(row.get("definition") or ""))
        pkg = value.get("diagram_package") if isinstance(value.get("diagram_package"), dict) else {}
        parts.append(str(pkg.get("caption") or ""))
        parts.append(str(pkg.get("practice_question") or ""))
    return " ".join(parts).lower()


def _first_text(items: list[Any], *, keys: tuple[str, ...] = ("text", "label", "name", "correction", "explanation", "caption")) -> str:
    for item in items:
        if isinstance(item, str) and item.strip():
            return item.strip()
        if isinstance(item, dict):
            for k in keys:
                val = str(item.get(k) or "").strip()
                if val:
                    return val
    return ""


def surface_board_into_adaptations(
    adaptations: dict[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Inject missing board signals into standard (and related) learner pages."""
    board = board or adaptations.get("_intelligence_board") or {}
    topic = str(board.get("topic") or "this lesson")
    out = dict(adaptations)
    notes: list[dict[str, str]] = []
    blob = _package_blob(out)

    examples = list(board.get("examples") or [])
    misconceptions = [m for m in (board.get("misconceptions") or []) if isinstance(m, dict) or isinstance(m, str)]
    claims = list(board.get("verified_claims") or [])
    goals = list(board.get("learning_goals") or [])
    visuals = [v for v in (board.get("visual_opportunities") or []) if isinstance(v, dict)]

    example_text = _first_text(examples) or _first_text(
        [{"text": f"A clear classroom or home moment that shows {topic}."}]
    )
    misconception = misconceptions[0] if misconceptions else {}
    if isinstance(misconception, str):
        mis_label, mis_fix = misconception, f"Keep the precise lesson meaning of {topic}."
    else:
        mis_label = str(misconception.get("label") or misconception.get("text") or "").strip()
        mis_fix = str(
            misconception.get("correction") or f"Keep the precise lesson meaning of {topic}."
        ).strip()
    claim_text = _first_text(claims) or f"{topic} is explained with accurate definitions and examples."
    goal_text = _first_text(goals) or f"Explain the key idea in {topic} in your own words."
    visual_caption = _first_text(visuals, keys=("caption", "title", "kind")) or f"{topic} organiser"

    # Surface into standard first — other adaptations inherit via polish when thin
    std = out.get("standard")
    if isinstance(std, dict):
        page = dict(std)
        sections = [dict(s) for s in (page.get("sections") or []) if isinstance(s, dict)]
        roles = {str(s.get("role") or "") for s in sections}
        joined = " ".join(str(s.get("body") or "") for s in sections).lower()

        if example_text and example_text.lower()[:40] not in blob and "real_life_example" not in roles:
            sections.append(
                {
                    "title": "In Real Life",
                    "role": "real_life_example",
                    "box": "example",
                    "body": (
                        f"{example_text} Connect this moment back to the meaning of {topic} "
                        "so the idea stays useful outside the classroom."
                    ),
                }
            )
            notes.append({"kind": "example", "detail": "Surfaced board example into standard."})

        if mis_label and mis_label.lower()[:40] not in joined and "misconception" not in roles:
            sections.append(
                {
                    "title": "Watch Out",
                    "role": "misconception",
                    "box": "caution",
                    "body": (
                        f"A common mix-up is thinking “{mis_label}”. "
                        f"{mis_fix} Check your explanation against the lesson definition."
                    ),
                }
            )
            notes.append({"kind": "misconception", "detail": "Surfaced board misconception into standard."})

        if claim_text and "concept" not in roles and len(sections) < 3:
            sections.insert(
                0,
                {
                    "title": f"Understanding {topic}",
                    "role": "concept",
                    "box": "concept",
                    "body": (
                        f"{claim_text} Say it in your own words, then match it to one example "
                        f"from {topic}."
                    ),
                },
            )
            notes.append({"kind": "explanation", "detail": "Surfaced verified claim into standard."})

        if goal_text and "practice_question" not in roles:
            sections.append(
                {
                    "title": "Try This",
                    "role": "practice_question",
                    "box": "practice",
                    "body": f"{goal_text} Write two clear sentences, then check them against the diagram.",
                }
            )
            notes.append({"kind": "assessment", "detail": "Surfaced learning goal as practice."})

        pkg = dict(page.get("diagram_package") or {})
        if visual_caption and not pkg.get("caption"):
            pkg["caption"] = visual_caption
            pkg.setdefault("practice_question", f"Point to one part of the {topic} diagram and explain it.")
            page["diagram_package"] = pkg
            notes.append({"kind": "visual", "detail": "Surfaced visual opportunity into diagram package."})

        page["sections"] = sections
        out["standard"] = page

    # Vocabulary: ensure board terms appear on the word wall
    vocab_board = [v for v in (board.get("vocabulary") or []) if isinstance(v, dict)]
    vocab_page = out.get("vocabulary")
    if vocab_board and isinstance(vocab_page, dict):
        wall = list(vocab_page.get("word_wall") or [])
        existing = {str(r.get("term") or "").lower() for r in wall if isinstance(r, dict)}
        added = 0
        for row in vocab_board:
            term = str(row.get("term") or row.get("name") or "").strip()
            if not term or term.lower() in existing:
                continue
            wall.append(
                {
                    "term": term,
                    "definition": str(row.get("definition") or row.get("explanation") or f"A key word in {topic}."),
                    "example_sentence": str(row.get("example") or f"Use “{term}” when you explain {topic}."),
                    "memory_tip": f"Draw {term} from the lesson diagram, then say what it means.",
                    "pmes_flashcard": True,
                    "lce_card": True,
                }
            )
            existing.add(term.lower())
            added += 1
        if added:
            vocab_page = dict(vocab_page)
            vocab_page["word_wall"] = wall
            out["vocabulary"] = vocab_page
            notes.append({"kind": "vocabulary", "detail": f"Surfaced {added} board vocabulary cards."})

    return out, notes
