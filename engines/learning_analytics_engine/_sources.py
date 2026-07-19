"""Shared helpers — extract engine payloads without mutating them."""

from __future__ import annotations

from typing import Any


def engine_payload(outputs: dict[str, Any], engine_id: str) -> dict[str, Any]:
    block = (outputs or {}).get(engine_id) or {}
    if isinstance(block, dict):
        return block.get("payload") or {}
    return {}


def lesson_report(text: str) -> dict[str, Any]:
    """Wrap existing analytics_engine — never reimplement."""
    try:
        from analytics_engine import build_analytics_report

        return build_analytics_report(text or "")
    except Exception as exc:  # noqa: BLE001
        return {"complexity_score": 0, "reading_level": "N/A", "objective_count": 0, "error": str(exc)}


def collect_sources(context: dict[str, Any]) -> dict[str, Any]:
    outputs = context.get("engine_outputs") or {}
    return {
        "lesson": lesson_report(context.get("lesson_text") or ""),
        "kie": engine_payload(outputs, "knowledge_ingestion"),
        "cie": engine_payload(outputs, "curriculum").get("curriculum_intelligence")
        or engine_payload(outputs, "curriculum"),
        "ame": engine_payload(outputs, "assessment"),
        "aie": engine_payload(outputs, "accessibility"),
        "ale": engine_payload(outputs, "adaptive_learning"),
        "tutor": engine_payload(outputs, "ai_tutor"),
        "gamification": engine_payload(outputs, "gamification"),
        "context": {
            "learner_id": context.get("learner_id") or context.get("student_id") or "anonymous",
            "topic": context.get("topic") or "",
            "grade": context.get("grade") or "",
            "lesson_reader": context.get("lesson_reader") or {},
        },
    }
