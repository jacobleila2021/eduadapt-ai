"""Engine contribution — learner-visible value only; else Integration Failure."""

from __future__ import annotations

from typing import Any, Mapping

from uevb.constants import ENGINE_VISIBLE_TARGETS, TRACKED_ENGINES


def _blob(adaptations: Mapping[str, Any], board: Mapping[str, Any] | None = None) -> str:
    parts: list[str] = []
    board = board or {}
    parts.append(str(board))
    for key, value in adaptations.items():
        if key.startswith("_") or not isinstance(value, dict):
            continue
        parts.append(key)
        parts.append(str(value.get("big_idea") or ""))
        parts.append(str(value.get("lce") or ""))
        parts.append(str(value.get("diagram_package") or ""))
        for sec in value.get("sections") or []:
            if isinstance(sec, dict):
                parts.append(str(sec.get("title") or ""))
                parts.append(str(sec.get("body") or ""))
        if value.get("flowchart_svg") or value.get("svg_diagram"):
            parts.append("svg diagram flowchart")
        if value.get("word_wall"):
            parts.append("vocabulary word_wall")
    return " ".join(parts).lower()


def _subject_family(subject: str) -> str:
    s = (subject or "").lower()
    if s in {"mathematics", "maths", "math"}:
        return "MIP"
    if s in {"physics"}:
        return "PIP"
    if s in {"chemistry"}:
        return "CIP"
    if s in {"biology", "science"}:
        return "BIP"
    if s in {"english"}:
        return "ELIP"
    if s in {"history", "geography", "civics", "social"}:
        return "SSIP"
    if s in {"computer_science", "cs", "ict"}:
        return "CSIP"
    if s in {"economics", "business", "business_studies", "commerce"}:
        return "CEIP"
    if s in {"world_languages", "french", "spanish", "hindi"}:
        return "WLIP"
    return ""


def measure_engine_contributions(
    adaptations: Mapping[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
    subject: str = "",
    package_meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Report visible educational contribution per tracked engine."""
    board = board or adaptations.get("_intelligence_board") or {}
    meta = package_meta or {}
    blob = _blob(adaptations, board)
    family = _subject_family(subject or str(board.get("subject") or ""))

    rows: dict[str, Any] = {}
    failures: list[str] = []

    for engine in TRACKED_ENGINES:
        targets = ENGINE_VISIBLE_TARGETS.get(engine, ())
        hits = [t for t in targets if t.lower() in blob]
        # Subject packs only required for matching family
        if engine in {"MIP", "PIP", "CIP", "BIP", "ELIP", "SSIP", "CSIP", "CEIP", "WLIP"}:
            if family and engine != family:
                rows[engine] = {
                    "status": "not_applicable",
                    "visible": False,
                    "hits": [],
                    "note": f"Not required for subject family {family or 'general'}.",
                }
                continue
        # Pipeline engines expected when markers present in package
        if engine == "PQLE" and (meta.get("pqle") or any(
            isinstance(v, dict) and (v.get("lce") or {}).get("pqle") for v in adaptations.values()
        )):
            hits = list(hits) or ["pqle"]
        if engine == "PMES" and (
            meta.get("pmes")
            or adaptations.get("_pmes")
            or any(isinstance(v, dict) and (v.get("lce") or {}).get("pmes") for v in adaptations.values())
        ):
            hits = list(hits) or ["pmes"]
        if engine == "LCE" and any(
            isinstance(v, dict) and (v.get("sections") or v.get("word_wall")) for v in adaptations.values()
        ):
            hits = list(hits) or ["sections"]
        if engine in {"KIE", "ULI", "UCF"} and board.get("verified_claims"):
            hits = list(hits) or ["verified_claims"]
        if engine == "UVIE" and any(
            isinstance(v, dict)
            and str(v.get("flowchart_svg") or v.get("svg_diagram") or "").startswith("<svg")
            for v in adaptations.values()
        ):
            hits = list(hits) or ["svg"]
        if engine == "CMIF" and board.get("misconceptions"):
            hits = list(hits) or ["misconception"]
        if engine == "SIF" and (board.get("assessment_objectives") or board.get("misconceptions")):
            hits = list(hits) or ["subject"]
        if engine == "CEF" and (board.get("teaching_sequence") or board.get("concept_hierarchy")):
            hits = list(hits) or ["teaching_sequence"]

        visible = bool(hits)
        status = "contributing" if visible else "integration_failure"
        if not visible:
            failures.append(engine)
        rows[engine] = {
            "status": status,
            "visible": visible,
            "hits": hits[:6],
            "note": (
                "Learner-visible contribution detected."
                if visible
                else "Integration Failure — no learner-visible improvement detected."
            ),
        }

    return {
        "schema": "alora.uevb.engine_contribution.v1",
        "engines": rows,
        "integration_failures": failures,
        "ok": len(failures) == 0,
        "subject_family": family or "general",
    }
