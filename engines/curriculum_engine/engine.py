"""Curriculum Intelligence Engine — VLIE-compatible facade.

Wraps existing knowledge.service retrieval and enriches with CIE ontology.
Does not generate lessons. Does not alter STEM facts.
"""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class CurriculumEngine(BaseEngine):
    """
    Academic intelligence layer (CIE).

    Still engine_id=\"curriculum\" for VLIE backward compatibility.
    """

    engine_id = "curriculum"
    version = "2.0.0"
    layer = "knowledge"
    priority = 10

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from knowledge.service import prepare_knowledge_for_lesson
            from engines.curriculum_intelligence_engine.intelligence import (
                analyze_lesson_context,
            )

            lesson = context.get("lesson_text") or ""
            topic = context.get("topic") or ""
            resolution = context.get("curriculum_resolution") or {}
            profile = context.get("universal_profile") or {}
            grade = context.get("grade") or (
                profile.get("age_estimate") or {}
            ).get("band") or "unknown"
            board = (
                resolution.get("curriculum")
                if resolution.get("status") in {"recognized", "user_declared"}
                else "unknown"
            )
            subject = context.get("subject") or "unknown"

            ctx = {
                "topic": topic,
                "grade_level": grade,
            }
            if resolution.get("status") in {"recognized", "user_declared"}:
                knowledge = prepare_knowledge_for_lesson(lesson, ctx)
            else:
                knowledge = {
                    "pilot_id": None,
                    "board": None,
                    "grade": None,
                    "subject": None,
                    "book_title": None,
                    "rag_hits": [],
                    "official_mcqs": [],
                    "exam_bundle": {},
                    "citations": [],
                    "scope_matched": False,
                    "external_enrichment": {
                        "status": "no_hits",
                        "required": False,
                        "citation_notice": "No curriculum references available.",
                    },
                }

            cie = analyze_lesson_context(
                lesson_text=lesson,
                topic=topic,
                board=board,
                grade=str(grade),
                subject=subject,
                mastered=context.get("mastered_concepts") or [],
                reindex=bool(context.get("cie_reindex", False)),
            )

            # Prefer UCF projection when universal_curriculum already ran
            ucf_payload = ((context.get("engine_outputs") or {}).get("universal_curriculum") or {}).get("payload") or {}
            ucf_cie = (ucf_payload.get("adapters") or {}).get("cie") or ucf_payload.get("cie_projection") or {}
            if ucf_cie.get("concepts"):
                cie = {**cie, "ucf_concepts": ucf_cie.get("concepts"), "ucf_package_id": ucf_payload.get("package_id"), "consumes_ucf": True}

            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=True,
                payload={
                    "board": knowledge.get("board") or board,
                    "grade": knowledge.get("grade") or grade,
                    "subject": knowledge.get("subject") or subject,
                    "pilot_id": knowledge.get("pilot_id"),
                    "knowledge": knowledge,
                    "curriculum_intelligence": cie,
                    "concepts": ucf_cie.get("concepts") or cie.get("matched_concepts") or [],
                    "ucf": {"package_id": ucf_payload.get("package_id"), "consumes_ucf": bool(ucf_cie)},
                    "curriculum_agnostic": True,
                    "curriculum_resolution": resolution
                    or {
                        "status": "unknown",
                        "curriculum": None,
                        "confidence": 0.0,
                    },
                    "supported_boards_ready": [
                        c["name"] for c in cie.get("supported_curricula") or []
                    ],
                    "cie_version": self.version,
                },
                deterministic=False,
                warnings=[],
            )
        except Exception:  # noqa: BLE001
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=False,
                errors=["Optional curriculum resolution is unavailable."],
                warnings=["Source-grounded generation may continue."],
            )

    def health_check(self) -> EngineHealth:
        try:
            from engines.curriculum_intelligence_engine.intelligence import get_runtime

            rt = get_runtime()
            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=(
                    "curriculum_optional=true; "
                    f"concepts={len(rt['graph'].concepts)}; "
                    f"outcomes={len(rt['graph'].outcomes)}"
                ),
                dependencies={
                    "knowledge": True,
                    "cie_ontology": len(rt["graph"].concepts) > 0,
                },
            )
        except Exception:
            return EngineHealth(
                ok=False,
                engine_id=self.engine_id,
                detail="Curriculum enrichment health check is unavailable.",
            )
