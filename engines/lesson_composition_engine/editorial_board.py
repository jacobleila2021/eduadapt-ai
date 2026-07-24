"""Publisher Editorial Board — multi-editor acceptance inside LCE/EATS.

Phase Omega: replace score-only acceptance with editorial vetoes.
Not a new engine — review layer over composed learner content.
"""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.publisher_remediation import (
    adaptation_has_generic_diagram,
    blob_of,
    has_teacher_objective_leak,
    template_hits,
)

EDITORS = (
    "educational",
    "curriculum",
    "subject",
    "accessibility",
    "visual",
    "assessment",
    "language",
    "publisher",
    "parent",
    "teacher",
)


def _sections(adaptation: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [s for s in (adaptation.get("sections") or []) if isinstance(s, dict)]


def _roles(adaptation: Mapping[str, Any]) -> set[str]:
    return {str(s.get("role") or "").lower() for s in _sections(adaptation)}


def review_adaptation_editorial(
    adaptation: Mapping[str, Any],
    *,
    adaptation_id: str = "standard",
    board: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Independent editor votes. Any reject blocks publication."""
    board = board or {}

    # Specialist pages: light editorial pass (still checked for teacher leakage)
    if adaptation_id in {"vocabulary", "worksheet"}:
        blob = blob_of(adaptation)
        leak = has_teacher_objective_leak(blob) or bool(template_hits(blob))
        votes = {
            name: {
                "approve": not leak if name in {"educational", "language", "publisher"} else True,
                "notes": (["Scaffold/leak on specialist page."] if leak and name in {"educational", "language", "publisher"} else ["Specialist page light pass."]),
            }
            for name in EDITORS
        }
        rejects = [name for name, vote in votes.items() if not vote.get("approve")]
        return {
            "adaptation_id": adaptation_id,
            "votes": votes,
            "approved": not rejects,
            "rejected_by": rejects,
            "notes": [n for v in votes.values() for n in (v.get("notes") or []) if "leak" in n.lower() or "Scaffold" in n],
        }

    blob = blob_of(adaptation)
    votes: dict[str, dict[str, Any]] = {}

    # Educational Editor — natural teacher voice, no scaffold leakage
    hits = template_hits(blob)
    edu_ok = not hits and not has_teacher_objective_leak(blob)
    votes["educational"] = {
        "approve": edu_ok,
        "notes": [] if edu_ok else [f"Authoring/scaffold language: {', '.join(hits[:4]) or 'objective leak'}"],
    }

    # Curriculum Editor — claims / topic present
    claims = list(board.get("verified_claims") or [])
    has_claim = any(c.lower()[:40] in blob.lower() for c in claims[:4]) if claims else len(blob) > 120
    votes["curriculum"] = {
        "approve": has_claim,
        "notes": [] if has_claim else ["Lesson does not surface verified curriculum claims."],
    }

    # Subject Editor — concept coverage
    concepts = [str(c.get("name") or "") for c in (board.get("concepts") or []) if isinstance(c, dict)]
    covered = sum(1 for c in concepts if c and c.lower() in blob.lower())
    subject_ok = covered >= min(2, len(concepts)) if concepts else len(_sections(adaptation)) >= 4
    votes["subject"] = {
        "approve": subject_ok,
        "notes": [] if subject_ok else ["Core concepts under-taught."],
    }

    # Accessibility Editor — profile adaptations must differ structurally for non-standard
    roles = _roles(adaptation)
    if adaptation_id in {"adhd", "autism", "ld", "dyslexia", "ell", "visual", "auditory"}:
        distinct_markers = {
            "adhd": any("chunk" in str(s.get("title") or "").lower() or "mission" in str(s.get("title") or "").lower() or "minute" in str(s.get("title") or "").lower() for s in _sections(adaptation)),
            "autism": any("routine" in str(s.get("title") or "").lower() or "what we will" in str(s.get("title") or "").lower() or "finished" in str(s.get("title") or "").lower() for s in _sections(adaptation)),
            "ell": any("word" in str(s.get("title") or "").lower() or "frame" in blob.lower() for s in _sections(adaptation)),
            "visual": any("diagram" in blob.lower() or "see" in str(s.get("title") or "").lower() for s in _sections(adaptation)),
            "auditory": "aloud" in blob.lower() or "listen" in blob.lower() or "say" in blob.lower(),
            "ld": bool(adaptation.get("lce", {}).get("adaptive_profile")) or any(str(s.get("body") or "").lstrip().startswith("-") for s in _sections(adaptation)),
            "dyslexia": any(str(s.get("body") or "").lstrip().startswith("-") for s in _sections(adaptation)),
        }
        a11y_ok = distinct_markers.get(adaptation_id, True)
        votes["accessibility"] = {
            "approve": a11y_ok,
            "notes": [] if a11y_ok else [f"{adaptation_id} adaptation is not structurally distinct."],
        }
    else:
        votes["accessibility"] = {"approve": True, "notes": ["Mainstream path."]}

    # Visual Editor
    has_svg = any(
        str(adaptation.get(k) or "").startswith("<svg")
        for k in ("flowchart_svg", "concept_map_svg", "svg_diagram")
    )
    generic = adaptation_has_generic_diagram(adaptation)
    visual_ok = (has_svg and not generic) or adaptation_id in {"vocabulary", "parent"}
    if adaptation_id == "worksheet":
        dq = adaptation.get("diagram_question") or {}
        visual_ok = str(dq.get("svg_diagram") or "").startswith("<svg") and not adaptation_has_generic_diagram(
            {"flowchart_svg": dq.get("svg_diagram")}
        )
    votes["visual"] = {
        "approve": visual_ok,
        "notes": [] if visual_ok else ["Missing domain diagram or generic pedagogy flowchart."],
    }

    # Assessment Editor
    practice = adaptation.get("practice") or adaptation.get("short_answer") or adaptation.get("self_test")
    assess_ok = bool(practice) or "practice" in roles or adaptation_id in {"parent", "teacher"}
    votes["assessment"] = {
        "approve": assess_ok,
        "notes": [] if assess_ok else ["No practice/assessment pathway."],
    }

    # Language Editor — big idea not meta
    big = str(adaptation.get("big_idea") or "")
    lang_ok = bool(big) and "worth mastering" not in big.lower() and not has_teacher_objective_leak(big)
    if adaptation_id in {"vocabulary", "worksheet"}:
        lang_ok = True
    votes["language"] = {
        "approve": lang_ok,
        "notes": [] if lang_ok else ["Opening lacks natural teachable claim."],
    }

    # Publisher Editor — length / structure
    pub_ok = len(_sections(adaptation)) >= 4 or adaptation_id in {"vocabulary", "worksheet"}
    votes["publisher"] = {
        "approve": pub_ok,
        "notes": [] if pub_ok else ["Too thin for publisher-grade lesson."],
    }

    # Parent / Teacher editors
    if adaptation_id == "parent":
        parent_ok = "home" in blob.lower() or "child" in blob.lower() or "family" in blob.lower()
        votes["parent"] = {
            "approve": parent_ok,
            "notes": [] if parent_ok else ["Parent edition lacks home coaching voice."],
        }
    else:
        votes["parent"] = {"approve": True, "notes": ["N/A"]}

    if adaptation_id == "teacher":
        teacher_ok = "teacher" in blob.lower() or "differentiat" in blob.lower() or "misconception" in blob.lower()
        votes["teacher"] = {
            "approve": teacher_ok,
            "notes": [] if teacher_ok else ["Teacher edition lacks guidance substance."],
        }
    else:
        votes["teacher"] = {"approve": True, "notes": ["N/A"]}

    rejects = [name for name, vote in votes.items() if not vote.get("approve")]
    return {
        "adaptation_id": adaptation_id,
        "votes": votes,
        "approved": not rejects,
        "rejected_by": rejects,
        "notes": [n for v in votes.values() for n in (v.get("notes") or [])],
    }


def review_package_editorial(
    adaptations: Mapping[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    board = board or {}
    by_id: dict[str, Any] = {}
    rejects: list[str] = []
    for key, value in adaptations.items():
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key in {"vocabulary", "worksheet"}:
            # Specialist pages: lighter editorial pass
            report = review_adaptation_editorial(value, adaptation_id=key, board=board)
        else:
            report = review_adaptation_editorial(value, adaptation_id=key, board=board)
        by_id[key] = report
        if not report.get("approved"):
            rejects.append(key)

    return {
        "schema": "alora.publisher_editorial_board.v1",
        "approved": not rejects,
        "rejected_adaptations": rejects,
        "by_adaptation": by_id,
        "editors": list(EDITORS),
        "publication_ready": not rejects,
        "reject_rendering": bool(rejects),
    }
