"""
Milestone 2.2 — Semantic enrichment collectors.

Attaches verified outputs from existing engines/extractors onto ULI.
Never invents educational content. Never calls LLMs.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from engines.content_classifier import classify_source_blocks
from engines.lesson_pipeline import engine_result_to_dict, process_lesson_stem


def _parse_declared_meta(text: str, user_metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    """Reuse header patterns already used across Alora (subject/grade declarations)."""
    meta = dict(user_metadata or {})
    sample = (text or "")[:800]
    subject = meta.get("subject")
    if not subject:
        m = re.search(r"\bsubject\s*:\s*([^\n|]+)", sample, re.I)
        if m:
            subject = m.group(1).strip()
    grade = meta.get("grade") or meta.get("grade_level")
    if not grade:
        m = re.search(r"\b(?:grade|class|year)\s*[: ]\s*(\d{1,2})\b", sample, re.I)
        if m:
            grade = m.group(1)
    board = meta.get("board")
    programme = meta.get("programme") or meta.get("program")
    return {
        "subject": subject,
        "grade": str(grade) if grade else None,
        "board": board,
        "programme": programme,
    }


def _stem_claims_as_dicts(stem: Mapping[str, Any], lesson_text: str = "") -> list[dict[str, Any]]:
    """
    Normalize STEM claims for ULI.

    ``process_lesson_stem`` returns ``claims_found`` as a *count* (int). The
    authoritative claim list is recovered via ``extract_stem_claims`` (same
    helper the pipeline uses) or from an explicit list in stem_metadata.
    """
    raw = stem.get("claims_found")
    if isinstance(raw, list):
        source = raw
    elif isinstance(stem.get("stem_claims"), list):
        source = list(stem["stem_claims"])
    else:
        source = []
        if lesson_text.strip():
            try:
                from engines.claim_extractor import extract_stem_claims

                source = list(extract_stem_claims(lesson_text))
            except Exception:  # noqa: BLE001
                source = []
    rows: list[dict[str, Any]] = []
    for claim in source:
        if isinstance(claim, Mapping):
            rows.append(dict(claim))
        else:
            rows.append(
                {
                    "kind": getattr(claim, "kind", ""),
                    "raw": getattr(claim, "raw", ""),
                    "line_no": getattr(claim, "line_no", None),
                    "extra": getattr(claim, "extra", {}) or {},
                }
            )
    return rows


def _formula_inventory(claims: list[dict[str, Any]], artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for claim in claims:
        kind = str(claim.get("kind") or "")
        if kind in {
            "math_equation",
            "chemistry_equation",
            "plot_expression",
            "force_problem",
            "geometry",
            "molecule",
            "circuit",
            "statistics",
            "physics_diagram",
            "chart",
        }:
            inventory.append(
                {
                    "kind": kind,
                    "expression": claim.get("raw"),
                    "line_no": claim.get("line_no"),
                    "provenance": "claim_extractor",
                }
            )
    for art in artifacts:
        if not isinstance(art, Mapping):
            continue
        exact = art.get("exact")
        if exact is not None:
            inventory.append(
                {
                    "kind": str(art.get("task_kind") or art.get("engine_id") or "artifact"),
                    "expression": exact,
                    "latex": art.get("latex"),
                    "engine_id": art.get("engine_id"),
                    "ok": art.get("ok"),
                    "provenance": "lesson_pipeline",
                }
            )
    return inventory


def _cie_payload(lesson_text: str, topic: str, declared: dict[str, Any]) -> dict[str, Any]:
    try:
        from engines.curriculum_intelligence_engine.intelligence import analyze_lesson_context

        return analyze_lesson_context(
            lesson_text=lesson_text,
            topic=topic,
            board=declared.get("board"),
            grade=declared.get("grade"),
            subject=declared.get("subject"),
        )
    except Exception as exc:  # noqa: BLE001 — enrichment must never fail ULI build
        return {
            "ok": False,
            "error": str(exc),
            "matched_concepts": [],
            "scope_matched": False,
        }


def _ame_misconceptions(lesson_text: str, concept_ids: list[str] | None) -> list[dict[str, Any]]:
    try:
        from engines.assessment_mastery_engine.misconceptions import detect_from_text

        hits = detect_from_text(lesson_text, concept_ids=concept_ids or None)
        out = []
        for hit in hits:
            if hasattr(hit, "to_dict"):
                out.append(hit.to_dict())
            elif isinstance(hit, Mapping):
                out.append(dict(hit))
            else:
                out.append(
                    {
                        "misconception_id": getattr(hit, "misconception_id", ""),
                        "confidence": getattr(hit, "confidence", None),
                        "patterns": getattr(hit, "matched_patterns", None),
                    }
                )
        return out
    except Exception:  # noqa: BLE001
        return []


def _aie_readability(lesson_text: str) -> dict[str, Any]:
    try:
        from engines.accessibility_intelligence_engine.readability import readability_report

        return readability_report(lesson_text)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def _duration_minutes(lesson_text: str) -> float | None:
    try:
        from engines.learning_experience_platform.progress import estimate_reading_minutes

        return float(estimate_reading_minutes(lesson_text))
    except Exception:  # noqa: BLE001
        return None


def collect_semantic_enrichment(
    source_envelope: Mapping[str, Any],
    universal_profile: Mapping[str, Any],
    *,
    stem_metadata: Mapping[str, Any] | None = None,
    classifications: list[Any] | None = None,
    run_stem: bool = True,
    run_cie: bool = True,
    run_ame: bool = True,
    run_aie: bool = True,
) -> dict[str, Any]:
    """
    Build a verified enrichment payload from existing pipelines.

    Returns a plain dict suitable for freezing on the ULI facade.
    """
    envelope = dict(source_envelope)
    profile = dict(universal_profile)
    text = str(envelope.get("text") or "")
    topic = str(profile.get("topic") or "")
    declared = _parse_declared_meta(text, envelope.get("user_metadata") if isinstance(envelope.get("user_metadata"), dict) else {})

    # Classifications
    class_rows: list[Any]
    if classifications is not None:
        class_rows = list(classifications)
    else:
        try:
            class_rows = classify_source_blocks(envelope)
        except Exception:  # noqa: BLE001
            class_rows = []

    # STEM pipeline (Computation Layer) — reuse lesson_pipeline only
    if stem_metadata is not None:
        stem = dict(stem_metadata)
    elif run_stem and text.strip():
        try:
            stem = process_lesson_stem(text, topic=topic)
        except Exception as exc:  # noqa: BLE001
            stem = {
                "claims_found": [],
                "artifacts": [],
                "routing_warnings": [
                    {
                        "stage": "uli_enrichment",
                        "code": "stem_pipeline_unavailable",
                        "message": str(exc),
                    }
                ],
                "preferred_visuals": [],
            }
    else:
        stem = {
            "claims_found": [],
            "artifacts": [],
            "routing_warnings": [],
            "preferred_visuals": [],
        }

    # Normalize artifacts to plain dicts
    artifacts: list[dict[str, Any]] = []
    for art in stem.get("artifacts") or []:
        if hasattr(art, "engine_id") and not isinstance(art, Mapping):
            try:
                artifacts.append(engine_result_to_dict(art))
            except Exception:  # noqa: BLE001
                continue
        elif isinstance(art, Mapping):
            artifacts.append(dict(art))

    claims_count = stem.get("claims_found") if isinstance(stem.get("claims_found"), int) else None
    claim_dicts = _stem_claims_as_dicts(stem, text)
    stem = {
        **stem,
        "claims_found": claim_dicts,
        "claims_found_count": claims_count if claims_count is not None else len(claim_dicts),
        "artifacts": artifacts,
        "preferred_visuals": list(stem.get("preferred_visuals") or []),
        "routing_warnings": list(stem.get("routing_warnings") or []),
        "biology_figures": list(stem.get("biology_figures") or []),
    }

    cie = _cie_payload(text, topic, declared) if run_cie else {}
    matched = list(cie.get("matched_concepts") or cie.get("concepts") or [])
    concept_ids = [
        str(c.get("concept_id") or c.get("id") or "")
        for c in matched
        if isinstance(c, Mapping)
    ]
    concept_ids = [c for c in concept_ids if c]

    ame_hits = _ame_misconceptions(text, concept_ids) if run_ame else []
    aie = _aie_readability(text) if run_aie else {}
    duration = _duration_minutes(text)

    claims = list(stem.get("claims_found") or [])
    formula_inv = _formula_inventory(claims, artifacts)

    # Diagram inventory from preferred visuals + profile opportunities + tables
    diagrams: list[dict[str, Any]] = []
    for vis in stem.get("preferred_visuals") or []:
        if isinstance(vis, Mapping):
            diagrams.append(
                {
                    "diagram_type": vis.get("kind") or vis.get("type") or "verified_visual",
                    "title": vis.get("title") or vis.get("label"),
                    "caption": vis.get("caption"),
                    "alt_text": vis.get("alt_text") or vis.get("accessibility_description"),
                    "source": vis.get("source") or vis.get("engine_id") or "visualization_priority",
                    "asset_path": vis.get("path") or vis.get("asset_path"),
                    "labels": vis.get("labels") or [],
                    "interactive_support": bool(vis.get("interactive")),
                    "provenance": "visualization_priority",
                }
            )
    for opp in profile.get("visual_opportunities") or []:
        if isinstance(opp, Mapping):
            diagrams.append(
                {
                    "diagram_type": "visual_opportunity",
                    "title": None,
                    "caption": opp.get("opportunity"),
                    "alt_text": None,
                    "source": "universal_profile",
                    "source_refs": opp.get("source_refs") or [],
                    "labels": [],
                    "interactive_support": False,
                    "provenance": "profile_visual_opportunity",
                }
            )

    # LXP / voice / analytics anchors from claim ledger (identifiers only)
    ledger = [c for c in (profile.get("claim_ledger") or []) if isinstance(c, Mapping)]
    section_anchors = [
        {
            "anchor_id": str(c.get("claim_id")),
            "block_ids": list(c.get("source_block_ids") or []),
            "text_preview": str(c.get("text") or "")[:160],
        }
        for c in ledger[:200]
    ]
    narration_segments = [
        {
            "segment_id": str(c.get("claim_id")),
            "text": str(c.get("text") or ""),
            "timing_ms": None,
            "block_ids": list(c.get("source_block_ids") or []),
        }
        for c in ledger[:200]
    ]

    gloss = list(profile.get("vocabulary") or [])
    glossary = [
        {
            "term": row.get("term"),
            "definition": None,
            "source_refs": row.get("source_refs") or [],
            "provenance": "profile_vocabulary",
        }
        for row in gloss
        if isinstance(row, Mapping)
    ]

    return {
        "schema_version": "3.2.0-semantic",
        "declared": declared,
        "classifications": class_rows,
        "stem": stem,
        "formula_inventory": formula_inv,
        "cie": cie,
        "ame_misconceptions": ame_hits,
        "aie_readability": aie,
        "estimated_duration_minutes": duration,
        "diagrams": diagrams,
        "glossary": glossary,
        "section_anchors": section_anchors,
        "narration_segments": narration_segments,
        "enrichment_sources": {
            "content_classifier": bool(class_rows),
            "lesson_pipeline": bool(stem.get("claims_found") or stem.get("artifacts")),
            "cie": bool(cie) and cie.get("ok") is not False,
            "ame": bool(ame_hits),
            "aie_readability": bool(aie) and "error" not in aie,
            "lxp_duration": duration is not None,
        },
    }
