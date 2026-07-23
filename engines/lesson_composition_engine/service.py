"""Public API facade for the Lesson Composition Engine (LCE)."""

from __future__ import annotations

from typing import Any

from engines.lesson_composition_engine.composer import (
    attach_lce_to_adaptations,
    build_blueprint,
    compose_lesson_package,
    lce_prompt_block_from_meta,
)
from engines.lesson_composition_engine.contracts import (
    build_narrative_contract,
    composition_prompt_block,
)
from engines.lesson_composition_engine.quality_gate import evaluate_composition, gate_for_rendering
from engines.lesson_composition_engine.schemas import LCE_SCHEMA_VERSION, PRODUCTION_THRESHOLD
from engines.lesson_composition_engine.vocabulary import (
    compose_vocabulary_card,
    compose_vocabulary_page,
    upgrade_vocabulary_dict,
    vocabulary_card_html,
)

LESSON_COMPOSITION_ENGINE_SMOKE_OK = True
LCE_SMOKE_OK = LESSON_COMPOSITION_ENGINE_SMOKE_OK


def api_compose_lesson(context: dict[str, Any]) -> dict[str, Any]:
    # Prefer ULI/SIF/UVIE dict path used by generation pipeline
    if context.get("uli") is not None or context.get("sif") is not None:
        package = compose_lesson_package(
            context.get("uli"),
            sif=context.get("sif") or {},
            uvie=context.get("uvie") or {},
            topic_hint=str(context.get("topic_hint") or context.get("topic") or ""),
        )
        return {"ok": bool(package.get("ok")), "package": package}
    package = compose_lesson_package(
        lesson_text=str(context.get("lesson_text") or ""),
        universal_profile=context.get("universal_profile"),
        meta=context.get("meta") or context.get("_meta"),
        context=context.get("lesson_context") or context.get("context"),
        existing_vocabulary=context.get("vocabulary"),
        existing_standard=context.get("standard"),
        version_ids=context.get("version_ids"),
        allow_mermaid=bool(context.get("allow_mermaid")),
    )
    if hasattr(package, "to_dict"):
        return {"ok": True, "package": package.to_dict()}
    return {"ok": True, "package": package}


def api_build_blueprint(context: dict[str, Any]) -> dict[str, Any]:
    bp = build_blueprint(
        lesson_text=str(context.get("lesson_text") or ""),
        universal_profile=context.get("universal_profile"),
        meta=context.get("meta") or context.get("_meta"),
        context=context.get("lesson_context") or context.get("context"),
    )
    return {"ok": True, "blueprint": bp.to_dict(), "prompt_block": composition_prompt_block(bp.to_dict())}


def api_compose_vocabulary(terms: list[Any], *, topic: str = "", context: dict[str, Any] | None = None) -> dict[str, Any]:
    page = compose_vocabulary_page(terms, topic=topic, context=context)
    return {"ok": True, "vocabulary": page}


def api_evaluate_quality(lesson: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    report = evaluate_composition(lesson, **kwargs)
    return {"ok": True, **gate_for_rendering(report)}


def api_attach_to_adaptations(adaptations: dict[str, Any], *, lesson_text: str = "", reject_on_fail: bool = True) -> dict[str, Any]:
    return attach_lce_to_adaptations(
        adaptations, lesson_text=lesson_text, reject_on_fail=reject_on_fail
    )


def api_narrative_contract(subject: str = "general", version_id: str = "standard") -> dict[str, Any]:
    return {
        "ok": True,
        "contract": build_narrative_contract(subject=subject, version_id=version_id),
        "schema_version": LCE_SCHEMA_VERSION,
        "threshold": PRODUCTION_THRESHOLD,
    }


def pack_health() -> dict[str, Any]:
    from engines.lesson_composition_engine.engine import LessonCompositionEngine

    h = LessonCompositionEngine().health_check()
    return {
        "ok": h.ok,
        "engine_id": h.engine_id,
        "version": h.version,
        "detail": h.detail,
        "smoke": LESSON_COMPOSITION_ENGINE_SMOKE_OK,
    }


__all__ = [
    "LESSON_COMPOSITION_ENGINE_SMOKE_OK",
    "LCE_SMOKE_OK",
    "api_compose_lesson",
    "api_build_blueprint",
    "api_compose_vocabulary",
    "api_evaluate_quality",
    "api_attach_to_adaptations",
    "api_narrative_contract",
    "pack_health",
    "compose_lesson_package",
    "attach_lce_to_adaptations",
    "build_blueprint",
    "lce_prompt_block_from_meta",
    "compose_vocabulary_card",
    "compose_vocabulary_page",
    "upgrade_vocabulary_dict",
    "vocabulary_card_html",
    "evaluate_composition",
    "gate_for_rendering",
]
