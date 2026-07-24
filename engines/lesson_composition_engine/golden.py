"""Golden Lesson Benchmarks — compare composed lessons against publisher exemplars."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

GOLDEN_DIR = Path(__file__).resolve().parents[2] / "golden_lessons"


def _ensure_golden_dir() -> Path:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    return GOLDEN_DIR


def list_golden_lessons() -> list[dict[str, Any]]:
    root = _ensure_golden_dir()
    rows = []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "id": path.stem,
                    "path": str(path),
                    "subject": data.get("subject") or "general",
                    "topic": data.get("topic") or path.stem,
                    "pqi_target": data.get("pqi_target") or 95,
                }
            )
        except Exception:  # noqa: BLE001
            continue
    return rows


def load_golden(lesson_id: str | None = None, *, subject: str = "", topic: str = "") -> dict[str, Any] | None:
    root = _ensure_golden_dir()
    if lesson_id:
        path = root / f"{lesson_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))

    subject_l = (subject or "").lower().strip()
    topic_l = (topic or "").lower().strip()
    subject_aliases = {
        "science": ("physics", "biology", "chemistry", "environmental_science"),
        "maths": ("mathematics",),
        "math": ("mathematics",),
        "env": ("environmental_science",),
        "environmental": ("environmental_science",),
        "social": ("history", "geography"),
        "language": ("english",),
    }

    best: dict[str, Any] | None = None
    best_score = -1
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        score = 0
        sub = str(data.get("subject") or "").lower()
        top = str(data.get("topic") or "").lower()
        stem = path.stem.lower()
        if subject_l and subject_l == sub:
            score += 5
        elif subject_l and subject_l in subject_aliases and sub in subject_aliases[subject_l]:
            score += 3
        elif subject_l and (subject_l in sub or sub in subject_l):
            score += 2
        if topic_l:
            if topic_l == top or topic_l in top or top in topic_l:
                score += 6
            else:
                for token in topic_l.replace("-", " ").split():
                    if len(token) > 3 and (token in top or token in stem):
                        score += 2
                        break
        if score > best_score:
            best_score = score
            best = data
    if best is not None and best_score > 0:
        return best
    files = sorted(root.glob("*.json"))
    if not files:
        return None
    return json.loads(files[0].read_text(encoding="utf-8"))


def _section_count(lesson: Mapping[str, Any]) -> int:
    return len([s for s in (lesson.get("sections") or []) if isinstance(s, dict)])


def _has_svg(lesson: Mapping[str, Any]) -> bool:
    for key in ("svg_diagram", "flowchart_svg", "concept_map_svg"):
        val = str(lesson.get(key) or "")
        if val.startswith("<svg") and len(val) > 150:
            return True
    return False


def compare_to_golden(
    adaptation: Mapping[str, Any],
    *,
    subject: str = "",
    topic: str = "",
    golden: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Return a golden_delta in roughly [-8, +8] applied to PQI overall.
    Positive = meets/exceeds exemplar structural quality.
    """
    topic = topic or str(adaptation.get("topic") or "")
    golden = golden or load_golden(subject=subject, topic=topic) or {}
    if not golden:
        return {"delta": 0.0, "matched": False, "notes": ["No golden exemplar available."]}

    notes: list[str] = []
    delta = 0.0
    g_sections = int(golden.get("min_sections") or _section_count(golden.get("lesson") or golden))
    a_sections = _section_count(adaptation)
    if a_sections >= g_sections:
        delta += 3.0
    else:
        delta -= 4.0
        notes.append(f"Fewer sections than golden ({a_sections}<{g_sections}).")

    if _has_svg(adaptation):
        delta += 2.5
    else:
        delta -= 3.0
        notes.append("Golden requires a premium SVG diagram.")

    if adaptation.get("big_idea") and len(str(adaptation.get("big_idea"))) >= 40:
        delta += 1.5
    else:
        delta -= 2.0
        notes.append("Big idea thinner than golden benchmark.")

    roles = {str(s.get("role") or "") for s in (adaptation.get("sections") or []) if isinstance(s, dict)}
    required = set(golden.get("required_roles") or ["summary", "reflection", "worked_example"])
    missing = required - roles
    if not missing:
        delta += 2.0
    else:
        delta -= 1.5 * min(3, len(missing))
        notes.append(f"Missing golden roles: {', '.join(sorted(missing))}")

    g_vocab_n = int(golden.get("min_vocab_cards") or 5)
    wall = adaptation.get("word_wall") or []
    if wall:
        if len(wall) >= g_vocab_n:
            delta += 1.0
        else:
            delta -= 1.0

    delta = max(-8.0, min(8.0, delta))
    return {
        "delta": delta,
        "matched": True,
        "golden_id": golden.get("id") or golden.get("topic"),
        "notes": notes,
    }


def golden_library_health() -> dict[str, Any]:
    """Product refinement health — coverage of permanent quality benchmarks."""
    rows = list_golden_lessons()
    subjects = sorted({str(r.get("subject") or "") for r in rows if r.get("subject")})
    required = {
        "mathematics",
        "physics",
        "chemistry",
        "biology",
        "geography",
        "history",
        "english",
        "environmental_science",
    }
    missing = sorted(required - set(subjects))
    return {
        "ok": len(rows) >= 10 and not missing,
        "count": len(rows),
        "subjects": subjects,
        "missing_subjects": missing,
        "smoke_ok": True,
        "ids": [r.get("id") for r in rows],
    }


def seed_default_golden_lessons() -> list[str]:
    """Write built-in exemplars if the folder is empty."""
    root = _ensure_golden_dir()
    written: list[str] = []
    exemplars = [
        {
            "id": "science_force_pressure",
            "subject": "physics",
            "topic": "Force and Pressure",
            "pqi_target": 95,
            "min_sections": 10,
            "min_vocab_cards": 6,
            "required_roles": [
                "concept",
                "simple_explanation",
                "worked_example",
                "summary",
                "reflection",
                "application",
            ],
            "lesson": {
                "big_idea": (
                    "Force and pressure help us explain how pushes and pulls act on surfaces. "
                    "When the same force spreads over a smaller area, pressure rises."
                ),
                "sections": [
                    {"title": "Opening", "role": "hook", "body": "We meet force as a push or pull."},
                    {"title": "Concept: Force", "role": "concept", "body": "Force changes motion or shape."},
                    {
                        "title": "Understanding Force",
                        "role": "simple_explanation",
                        "body": "A force is a push or a pull. It can start, stop, or change motion.",
                    },
                    {
                        "title": "Worked Example",
                        "role": "worked_example",
                        "body": "Compare a sharp pin and a blunt eraser under the same push.",
                    },
                    {"title": "Summary", "role": "summary", "body": "Force acts; pressure depends on area."},
                    {"title": "Reflect", "role": "reflection", "body": "Where do you notice pressure at home?"},
                    {"title": "Apply", "role": "application", "body": "Design one safe classroom demo."},
                ],
                "svg_diagram": '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80" viewBox="0 0 200 80"><rect x="10" y="20" width="180" height="40" rx="12" fill="#e6f7f8"/><text x="100" y="45" text-anchor="middle">Force → Area → Pressure</text></svg>',
            },
        },
        {
            "id": "biology_water_cycle",
            "subject": "biology",
            "topic": "The Water Cycle",
            "pqi_target": 95,
            "min_sections": 10,
            "min_vocab_cards": 5,
            "required_roles": [
                "concept",
                "process",
                "simple_explanation",
                "summary",
                "reflection",
            ],
            "lesson": {
                "big_idea": (
                    "Water moves through evaporation, condensation, and precipitation in a continuous cycle. "
                    "Each stage changes water's form without destroying it."
                ),
                "sections": [
                    {"title": "Opening", "role": "hook", "body": "Follow a drop of water around the Earth."},
                    {"title": "Concept", "role": "concept", "body": "The water cycle is a continuous process."},
                    {"title": "Process", "role": "process", "body": "Evaporation, condensation, precipitation."},
                    {
                        "title": "Understanding",
                        "role": "simple_explanation",
                        "body": "Heat turns liquid water into vapour; cooling forms clouds.",
                    },
                    {"title": "Summary", "role": "summary", "body": "Water changes state and travels."},
                    {"title": "Reflect", "role": "reflection", "body": "Which stage can you observe outdoors?"},
                ],
                "svg_diagram": '<svg xmlns="http://www.w3.org/2000/svg" width="220" height="90" viewBox="0 0 220 90"><rect width="220" height="90" rx="14" fill="#ecfdf5"/><text x="110" y="50" text-anchor="middle">Evaporation → Condensation → Rain</text></svg>',
            },
        },
        {
            "id": "mathematics_fractions",
            "subject": "mathematics",
            "topic": "Understanding Fractions",
            "pqi_target": 95,
            "min_sections": 9,
            "min_vocab_cards": 5,
            "required_roles": [
                "concrete",
                "visual",
                "worked_example",
                "summary",
                "application",
            ],
            "lesson": {
                "big_idea": (
                    "A fraction names equal parts of a whole. "
                    "We move from concrete shares to symbols only after the meaning is clear."
                ),
                "sections": [
                    {"title": "Concrete share", "role": "concrete", "body": "Share a chapati into equal parts."},
                    {"title": "See it", "role": "visual", "body": "Shade two of four equal parts."},
                    {
                        "title": "Worked Example",
                        "role": "worked_example",
                        "body": "Write two-fourths and simplify with a clear model.",
                    },
                    {"title": "Summary", "role": "summary", "body": "Equal parts make fraction meaning."},
                    {"title": "Apply", "role": "application", "body": "Create one kitchen fraction story."},
                ],
                "svg_diagram": '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80" viewBox="0 0 200 80"><rect x="20" y="20" width="160" height="40" rx="10" fill="#eef2ff"/><text x="100" y="45" text-anchor="middle">1 whole = 4 equal parts</text></svg>',
            },
        },
    ]
    for ex in exemplars:
        path = root / f"{ex['id']}.json"
        if not path.exists():
            path.write_text(json.dumps(ex, indent=2, ensure_ascii=False), encoding="utf-8")
            written.append(ex["id"])
    return written
