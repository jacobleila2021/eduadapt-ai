"""Learner-facing quality metrics — no metadata, no validation scores."""

from __future__ import annotations

import json
import re
from collections import Counter
from difflib import SequenceMatcher
from typing import Any

ROBOTIC_PHRASES = (
    "in this lesson we will",
    "as an ai",
    "delve into",
    "furthermore",
    "it is important to note",
    "let's explore",
    "students will be able to",
    "learning objective",
    "notice how",
    "in today's lesson",
    "by the end of this",
    "teacher tip",
    "pedagogical",
    "differentiate instruction",
    "scaffold the",
    "formative assessment",
    "success criteria",
    "as previously mentioned",
    "in conclusion, we have",
    "utilize",
    "facilitate learning",
)

TEACHER_ADVISORY = (
    "ask students",
    "have students",
    "tell the class",
    "circulate",
    "check for understanding",
    "model how",
    "write it on the board",
    "teacher circulates",
    "independent practice",
    "exit ticket",
    "homework:",
    "for the teacher",
)


def _text_blob(obj: Any) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (int, float, bool)):
        return str(obj)
    if isinstance(obj, list):
        return "\n".join(_text_blob(x) for x in obj)
    if isinstance(obj, dict):
        skip = {"_contract", "_meta", "lce", "pqle", "pmes", "peec", "provenance", "source_refs"}
        parts = []
        for k, v in obj.items():
            if k in skip or str(k).startswith("_"):
                continue
            if k in {"flowchart_svg", "concept_map_svg", "svg_diagram", "mermaid_diagram"}:
                if isinstance(v, str) and v.startswith("<svg"):
                    parts.append(f"[SVG len={len(v)}]")
                elif v:
                    parts.append(str(v)[:200])
                continue
            parts.append(_text_blob(v))
        return "\n".join(parts)
    return str(obj)


def _sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [c.strip() for c in chunks if len(c.strip()) > 20]


def repetition_ratio(text: str) -> float:
    sents = _sentences(text)
    if len(sents) < 2:
        return 0.0
    norm = [re.sub(r"\s+", " ", s.lower()) for s in sents]
    counts = Counter(norm)
    dupes = sum(n - 1 for n in counts.values() if n > 1)
    return round(dupes / max(len(sents), 1), 4)


def phrase_hits(text: str, phrases: tuple[str, ...]) -> list[str]:
    low = (text or "").lower()
    return [p for p in phrases if p in low]


def structural_similarity(a: Any, b: Any) -> float:
    ta, tb = _text_blob(a), _text_blob(b)
    if not ta and not tb:
        return 1.0
    return round(SequenceMatcher(None, ta[:8000], tb[:8000]).ratio(), 4)


def vocab_quality(vocab: dict[str, Any] | None) -> dict[str, Any]:
    vocab = vocab or {}
    wall = [r for r in (vocab.get("word_wall") or vocab.get("vocabulary_cards") or []) if isinstance(r, dict)]
    if not wall:
        return {"cards": 0, "score": 0, "issues": ["no_word_wall"]}
    issues = []
    complete = 0
    for row in wall:
        term = str(row.get("term") or "").strip()
        meaning = str(
            row.get("simple_explanation")
            or row.get("definition")
            or row.get("child_friendly")
            or ""
        ).strip()
        example = str(row.get("example_sentence") or row.get("example") or "").strip()
        tip = str(row.get("memory_tip") or row.get("remember_this") or "").strip()
        if not term:
            issues.append("empty_term")
        if len(meaning) < 12:
            issues.append(f"thin_meaning:{term or '?'}")
        if len(example) < 8:
            issues.append(f"thin_example:{term or '?'}")
        if not tip:
            issues.append(f"missing_tip:{term or '?'}")
        if term and len(meaning) >= 12 and len(example) >= 8:
            complete += 1
    score = int(100 * complete / max(len(wall), 1))
    return {"cards": len(wall), "complete": complete, "score": score, "issues": issues[:20]}


def diagram_quality(lesson: dict[str, Any] | None) -> dict[str, Any]:
    lesson = lesson or {}
    svg_fields = []
    for key in ("flowchart_svg", "concept_map_svg", "svg_diagram"):
        val = lesson.get(key) or ""
        ok = isinstance(val, str) and val.strip().startswith("<svg") and len(val) > 200
        svg_fields.append({"field": key, "ok": ok, "len": len(val) if isinstance(val, str) else 0})
    mermaid = str(lesson.get("mermaid_diagram") or "").strip()
    score = int(100 * sum(1 for f in svg_fields if f["ok"]) / max(len(svg_fields), 1))
    if mermaid and not any(f["ok"] for f in svg_fields):
        score = max(score - 30, 0)
    return {"score": score, "svgs": svg_fields, "has_mermaid_only": bool(mermaid) and score == 0}


def adaptation_scores(adaptations: dict[str, Any]) -> dict[str, Any]:
    keys = [
        k
        for k, v in adaptations.items()
        if isinstance(v, dict) and not str(k).startswith("_") and k not in {"vocabulary", "worksheet"}
    ]
    pairwise = {}
    flags = []
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            sim = structural_similarity(adaptations[a], adaptations[b])
            pairwise[f"{a}__{b}"] = sim
            if sim >= 0.60:
                flags.append({"pair": [a, b], "similarity": sim, "failure": True})
    return {"keys": keys, "pairwise_similarity": pairwise, "clone_failures": flags}


def score_lesson_surface(adaptations: dict[str, Any]) -> dict[str, Any]:
    """Single learner-facing quality score 0–100 for a package of adaptations."""
    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    text = _text_blob(adaptations)
    robotic = phrase_hits(text, ROBOTIC_PHRASES)
    advisory = phrase_hits(text, TEACHER_ADVISORY)
    # Student adaptations should not be full of teacher advisory (except teacher/parent keys)
    student_blob = _text_blob(
        {
            k: v
            for k, v in adaptations.items()
            if k in {"standard", "ld", "ell", "visual", "auditory", "adhd", "autism"}
            and isinstance(v, dict)
        }
    )
    student_advisory = phrase_hits(student_blob, TEACHER_ADVISORY)
    rep = repetition_ratio(text)
    vocab = vocab_quality(adaptations.get("vocabulary") if isinstance(adaptations.get("vocabulary"), dict) else {})
    diagrams = diagram_quality(std)
    adapt = adaptation_scores(adaptations)

    sections = [s for s in (std.get("sections") or []) if isinstance(s, dict)]
    bodies = [str(s.get("body") or "") for s in sections]
    avg_body = sum(len(b) for b in bodies) / max(len(bodies), 1)
    thin_sections = sum(1 for b in bodies if len(b.strip()) < 40)

    # Score construction (learner-facing only)
    score = 70.0
    score -= min(25, 4 * len(robotic))
    score -= min(20, 3 * len(student_advisory))
    score -= min(20, rep * 40)
    score += (vocab["score"] - 50) * 0.25
    score += (diagrams["score"] - 50) * 0.2
    score -= min(15, 5 * len(adapt["clone_failures"]))
    if len(sections) < 5:
        score -= 10
    if thin_sections:
        score -= min(15, 3 * thin_sections)
    if avg_body < 80:
        score -= 8
    if avg_body > 120:
        score += 4
    score = max(0, min(100, round(score, 1)))

    return {
        "learner_quality_score": score,
        "robotic_phrases": robotic,
        "teacher_advisory_in_student_tabs": student_advisory,
        "teacher_advisory_all": advisory,
        "repetition_ratio": rep,
        "vocabulary": vocab,
        "diagrams": diagrams,
        "adaptations": adapt,
        "section_count": len(sections),
        "thin_sections": thin_sections,
        "avg_section_chars": round(avg_body, 1),
        "char_count": len(text),
    }


def compare_stage_metrics(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Answer Phase-2 questions from metric deltas."""
    b, a = before.get("metrics") or {}, after.get("metrics") or {}
    dq = (a.get("learner_quality_score") or 0) - (b.get("learner_quality_score") or 0)
    return {
        "quality_delta": round(dq, 2),
        "did_quality_improve": dq > 1.5,
        "did_quality_worsen": dq < -1.5,
        "clarity_proxy_delta": round(
            (a.get("avg_section_chars") or 0) - (b.get("avg_section_chars") or 0), 1
        ),
        "readability_proxy": {
            "thin_sections_delta": (a.get("thin_sections") or 0) - (b.get("thin_sections") or 0),
            "repetition_delta": round(
                (a.get("repetition_ratio") or 0) - (b.get("repetition_ratio") or 0), 4
            ),
        },
        "robotic_delta": len(a.get("robotic_phrases") or []) - len(b.get("robotic_phrases") or []),
        "advisory_delta": len(a.get("teacher_advisory_in_student_tabs") or [])
        - len(b.get("teacher_advisory_in_student_tabs") or []),
        "vocab_score_delta": (a.get("vocabulary") or {}).get("score", 0)
        - (b.get("vocabulary") or {}).get("score", 0),
        "diagram_score_delta": (a.get("diagrams") or {}).get("score", 0)
        - (b.get("diagrams") or {}).get("score", 0),
        "clone_failure_delta": len((a.get("adaptations") or {}).get("clone_failures") or [])
        - len((b.get("adaptations") or {}).get("clone_failures") or []),
        "did_repetition_increase": (a.get("repetition_ratio") or 0)
        > (b.get("repetition_ratio") or 0) + 0.01,
        "did_ai_phrasing_increase": len(a.get("robotic_phrases") or [])
        > len(b.get("robotic_phrases") or []),
    }


def dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
