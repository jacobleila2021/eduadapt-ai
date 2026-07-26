"""Adapters — convert SIF analysis into consumer-friendly DTOs (ATIE/LXP/AME hints)."""

from __future__ import annotations

from typing import Any, Mapping


def to_atie_hints(sif_payload: Mapping[str, Any]) -> dict[str, Any]:
    analysis = sif_payload.get("analysis") or {}
    return {
        "subject_key": sif_payload.get("subject_key"),
        "tutor_guidance": list(analysis.get("tutor_guidance") or []),
        "misconception_anchors": list(analysis.get("misconceptions") or []),
        "placeholder": bool(sif_payload.get("placeholder", True)),
    }


def to_lxp_hints(sif_payload: Mapping[str, Any]) -> dict[str, Any]:
    analysis = sif_payload.get("analysis") or {}
    return {
        "subject_key": sif_payload.get("subject_key"),
        "lxp_hints": list(analysis.get("lxp_hints") or []),
        "interactions": list(analysis.get("interactions") or []),
        "visuals": list(analysis.get("visuals") or []),
        "placeholder": bool(sif_payload.get("placeholder", True)),
    }


def to_ame_hints(sif_payload: Mapping[str, Any]) -> dict[str, Any]:
    analysis = sif_payload.get("analysis") or {}
    return {
        "subject_key": sif_payload.get("subject_key"),
        "assessment_hints": list(analysis.get("assessment_hints") or []),
        "revision_summary": dict(analysis.get("revision_summary") or {}),
        "placeholder": bool(sif_payload.get("placeholder", True)),
    }


def to_aie_hints(sif_payload: Mapping[str, Any]) -> dict[str, Any]:
    analysis = sif_payload.get("analysis") or {}
    return {
        "subject_key": sif_payload.get("subject_key"),
        "accessibility_guidance": list(analysis.get("accessibility_guidance") or []),
        "placeholder": bool(sif_payload.get("placeholder", True)),
    }
