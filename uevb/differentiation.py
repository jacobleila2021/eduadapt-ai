"""Adaptation differentiation — reject cosmetic-only variants."""

from __future__ import annotations

import re
from typing import Any, Mapping

from uevb.constants import ADAPTATIONS, DIFFERENTIATION_MIN


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _titles(adaptation: Mapping[str, Any]) -> list[str]:
    return [
        str(s.get("title") or "")
        for s in (adaptation.get("sections") or [])
        if isinstance(s, dict)
    ]


def _roles(adaptation: Mapping[str, Any]) -> set[str]:
    return {
        str(s.get("role") or "")
        for s in (adaptation.get("sections") or [])
        if isinstance(s, dict)
    }


def _body_blob(adaptation: Mapping[str, Any]) -> str:
    parts = [str(adaptation.get("big_idea") or "")]
    for s in adaptation.get("sections") or []:
        if isinstance(s, dict):
            parts.append(str(s.get("body") or ""))
    return _norm(" ".join(parts))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _token_set(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9']+", text.lower()) if len(t) > 2}


SIGNATURES: dict[str, tuple[str, ...]] = {
    "adhd": ("chunk", "mission", "minute", "break", "checklist"),
    "autism": ("routine", "finished", "what we will", "first", "next"),
    "ell": ("key words", "sentence frame", "means"),
    "visual": ("see it", "diagram", "look", "trace", "using the diagram", "see it first"),
    "auditory": ("listen", "aloud", "say", "hear"),
    "dyslexia": ("step by step", "teach step"),
    "ld": ("step by step", "teach step"),
    "teacher": ("teacher guidance", "differentiation"),
    "parent": ("home", "child", "family", "talk about"),
    "vocabulary": ("word", "pronunciation", "flashcard"),
    "worksheet": ("marks", "answer", "short answer"),
}


def score_pair_differentiation(
    a: Mapping[str, Any],
    b: Mapping[str, Any],
    *,
    id_a: str,
    id_b: str,
) -> dict[str, Any]:
    """0–100 how pedagogically different two adaptations are."""
    if id_a == id_b:
        return {"score": 0.0, "cosmetic_only": True, "notes": ["Same adaptation."]}

    titles_a, titles_b = set(_titles(a)), set(_titles(b))
    roles_a, roles_b = _roles(a), _roles(b)
    blob_a, blob_b = _body_blob(a), _body_blob(b)
    tokens_a, tokens_b = _token_set(blob_a), _token_set(blob_b)

    title_overlap = _jaccard(titles_a, titles_b)
    role_overlap = _jaccard(roles_a, roles_b)
    text_overlap = _jaccard(tokens_a, tokens_b)

    # Structure length difference
    len_a = len(_titles(a)) or 1
    len_b = len(_titles(b)) or 1
    structure_delta = abs(len_a - len_b) / max(len_a, len_b)

    # Signature presence
    sig_a = SIGNATURES.get(id_a, ())
    sig_b = SIGNATURES.get(id_b, ())
    sig_hit_a = any(s in blob_a or s in " ".join(titles_a).lower() for s in sig_a) if sig_a else True
    sig_hit_b = any(s in blob_b or s in " ".join(titles_b).lower() for s in sig_b) if sig_b else True

    # Heuristic: high text overlap + high title overlap = cosmetic
    score = 100.0
    score -= title_overlap * 35
    score -= role_overlap * 20
    score -= text_overlap * 30
    score += structure_delta * 15
    if sig_hit_a and sig_hit_b and id_a != id_b:
        score += 8
    if not sig_hit_a and sig_a:
        score -= 12
    if not sig_hit_b and sig_b:
        score -= 12

    score = max(0.0, min(100.0, score))
    # Cosmetic only when nearly cloned AND missing profile signature
    cosmetic = (
        text_overlap > 0.82
        and title_overlap > 0.7
        and float(score) < DIFFERENTIATION_MIN
        and not (sig_hit_b if id_b != "standard" else sig_hit_a)
    )
    notes = []
    if cosmetic:
        notes.append("Likely cosmetic-only adaptation — teaching strategy not distinct enough.")
    if text_overlap > 0.85:
        notes.append("Bodies are nearly identical.")
    if title_overlap > 0.8:
        notes.append("Section titles largely cloned.")

    return {
        "pair": f"{id_a}:{id_b}",
        "score": round(score, 2),
        "title_overlap": round(title_overlap, 3),
        "role_overlap": round(role_overlap, 3),
        "text_overlap": round(text_overlap, 3),
        "cosmetic_only": cosmetic,
        "notes": notes,
    }


def measure_adaptation_differentiation(
    adaptations: Mapping[str, Any],
    *,
    keys: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    keys = keys or tuple(k for k in ADAPTATIONS if k in adaptations and isinstance(adaptations.get(k), dict))
    pairs: list[dict[str, Any]] = []
    cosmetic: list[str] = []
    scores: list[float] = []

    baseline = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else None
    for key in keys:
        if key == "standard" or key in {"vocabulary", "worksheet"}:
            # Specialist pages compared lightly to standard structure only
            if baseline and key != "standard" and isinstance(adaptations.get(key), dict):
                if key == "vocabulary":
                    wall = adaptations[key].get("word_wall") or []
                    ok = len(wall) >= 4
                    pairs.append(
                        {
                            "pair": f"standard:{key}",
                            "score": 92.0 if ok else 40.0,
                            "cosmetic_only": not ok,
                            "notes": [] if ok else ["Vocabulary page too thin."],
                        }
                    )
                    scores.append(92.0 if ok else 40.0)
                    if not ok:
                        cosmetic.append(key)
                continue
            continue
        other = adaptations.get(key)
        if not isinstance(other, dict) or not baseline:
            continue
        row = score_pair_differentiation(baseline, other, id_a="standard", id_b=key)
        pairs.append(row)
        scores.append(float(row["score"]))
        # Fail only true cosmetic clones or severely undifferentiated pairs
        if row.get("cosmetic_only") or float(row["score"]) < 40.0:
            cosmetic.append(key)

    overall = round(sum(scores) / len(scores), 2) if scores else 0.0
    return {
        "schema": "alora.uevb.adaptation_differentiation.v1",
        "adaptation_differentiation_score": overall,
        "threshold": DIFFERENTIATION_MIN,
        "ok": overall >= DIFFERENTIATION_MIN and not cosmetic,
        "cosmetic_failures": cosmetic,
        "pairs": pairs,
    }
