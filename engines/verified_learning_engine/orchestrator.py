"""VLIE Orchestrator — lesson package pipeline + Learning Session Orchestrator (LSO)."""

from __future__ import annotations

from typing import Any, Callable

from engines.base import EngineResultBundle
from engines.verified_learning_engine.audit_logger import AuditLogger
from engines.verified_learning_engine.configuration import LSOConfig, get_lso_config
from engines.verified_learning_engine.decision_engine import DecisionEngine
from engines.verified_learning_engine.dependency_manager import DependencyManager
from engines.verified_learning_engine.engine_registry import get_registry
from engines.verified_learning_engine.event_bus import EventBus, get_event_bus
from engines.verified_learning_engine.execution_context import ExecutionContext
from engines.verified_learning_engine.health_monitor import HealthMonitor
from engines.verified_learning_engine.integration_registry import IntegrationRegistry
from engines.verified_learning_engine.intervention_manager import InterventionManager
from engines.verified_learning_engine.notification_manager import NotificationManager
from engines.verified_learning_engine.package_builder import PackageBuilder
from engines.verified_learning_engine.policy_engine import PolicyEngine
from engines.verified_learning_engine.recommendation_manager import RecommendationManager
from engines.verified_learning_engine.result_merger import ResultMerger
from engines.verified_learning_engine.retry_manager import RetryManager
from engines.verified_learning_engine.scheduler import OrchestrationScheduler
from engines.verified_learning_engine.session_manager import SessionManager
from engines.verified_learning_engine.session_memory import SessionMemory
from engines.verified_learning_engine.telemetry import TelemetryCollector
from engines.verified_learning_engine.validator import VLIEValidator
from engines.verified_learning_engine.workflow import WORKFLOW_STAGES, stage_description
from engines.verified_learning_engine.workflow_manager import WorkflowManager


class VerifiedLearningOrchestrator:
    """
    Verified Learning Intelligence Engine (VLIE) — Alora OS orchestration layer.

    1) Lesson package pipeline (backward compatible): Curriculum → STEM → …
    2) Learning Session Orchestrator (LSO): event-driven session lifecycle,
       workflow, decisions, interventions, recommendations — without duplicating
       domain engine business logic.
    """

    def __init__(self, on_progress: Callable[[str, float], None] | None = None):
        self.on_progress = on_progress
        self.registry = get_registry()
        self.audit = AuditLogger()
        self.merger = ResultMerger()
        self.packages = PackageBuilder()
        self.validator = VLIEValidator()
        # LSO components
        self.config: LSOConfig = get_lso_config()
        self.bus: EventBus = get_event_bus()
        self.sessions = SessionManager()
        self.memory = SessionMemory(self.sessions)
        self.decisions = DecisionEngine()
        self.interventions = InterventionManager()
        self.recommendations = RecommendationManager()
        self.scheduler = OrchestrationScheduler()
        self.dependencies = DependencyManager(self.registry)
        self.policies = PolicyEngine()
        self.telemetry = TelemetryCollector()
        self.retry = RetryManager(**self.config.retry)
        self.health = HealthMonitor(self.registry)
        self.notifications = NotificationManager()
        self.integrations = IntegrationRegistry(self.registry)
        self._seed_future_engines()

    def _seed_future_engines(self) -> None:
        for eid, name, caps in (
            ("multi_curriculum", "Multi-Curriculum Expansion", ["curriculum_pack"]),
            ("enterprise_services", "Enterprise Services", ["sso", "tenant"]),
        ):
            if not any(e.get("engine_id") == eid and e.get("planned") for e in self.integrations.list_all()):
                self.integrations.register_future_engine(
                    eid,
                    name=name,
                    depends_on=["adaptive_learning"],
                    capabilities=caps,
                    api_endpoints=[f"/api/vlie/{eid}"],
                )
        self.integrations.register_capability(
            "voice_multimodal",
            capabilities=["speech", "tts", "stt", "read_along", "pronunciation", "interactive_stem"],
            api_endpoints=["/api/vlie/voice_multimodal"],
            health="ok",
        )
        self.integrations.register_capability(
            "learning_companion",
            capabilities=["companion", "motivation", "encouragement", "celebration", "executive_function"],
            api_endpoints=["/api/vlie/learning_companion"],
            health="ok",
        )
        self.integrations.register_capability(
            "learning_motivation",
            capabilities=["xp", "achievements", "quests", "skill_tree", "certificates", "streaks"],
            api_endpoints=["/api/vlie/learning_motivation"],
            health="ok",
        )
        self.integrations.register_capability(
            "universal_curriculum",
            capabilities=["ucf_schema", "board_importers", "competency_graph", "curriculum_search"],
            api_endpoints=["/api/vlie/universal_curriculum"],
            health="ok",
        )
        self.integrations.register_capability(
            "curriculum_expansion",
            capabilities=[
                "multi_board_import",
                "ucf_mapping",
                "versioning",
                "equivalency",
                "curriculum_registry",
                "validation",
            ],
            api_endpoints=["/api/vlie/curriculum_expansion"],
            health="ok",
        )
        self.integrations.register_capability(
            "curriculum_migration",
            capabilities=[
                "production_ingest",
                "mandatory_pipeline",
                "checksum_security",
                "immutable_publish",
                "batch_jobs",
                "cmif_dashboard",
            ],
            api_endpoints=["/api/vlie/curriculum_migration"],
            health="ok",
        )
        self.integrations.register_capability(
            "learning_experience",
            capabilities=["reader", "notes", "highlights", "bookmarks", "offline", "ai_explain", "read_along"],
            api_endpoints=["/api/vlie/learning_experience"],
            health="ok",
        )

    def _emit(self, msg: str, frac: float) -> None:
        if self.on_progress:
            self.on_progress(msg, frac)

    # ── Legacy lesson package pipeline (unchanged contract) ───────────────

    def run_engines(self, ctx: ExecutionContext) -> dict[str, EngineResultBundle]:
        """Execute registered engines in priority order (pre-generation enrichment)."""
        outputs: dict[str, EngineResultBundle] = {}
        engines = self.registry.execution_order(only_enabled=True)
        pre = [e for e in engines if e.engine_id != "multi_agent"]
        n = max(len(pre), 1)
        for i, engine in enumerate(pre):
            self._emit(f"VLIE · {engine.engine_id}: {stage_description(engine.engine_id)}", 0.05 + 0.25 * (i / n))
            self.audit.log("engine_start", engine_id=engine.engine_id)
            self.telemetry.start_timer(f"engine:{engine.engine_id}")
            context = ctx.to_dict()
            context["engine_outputs"] = {
                eid: {"ok": r.ok, "payload": r.payload, "errors": r.errors} for eid, r in outputs.items()
            }
            try:
                result = engine.process(context)
                result = engine.validate(context, result)
                result = engine.enrich(context, result)
            except Exception as exc:  # noqa: BLE001
                result = EngineResultBundle(engine_id=engine.engine_id, ok=False, errors=[str(exc)])
                self.health.record_failure(engine.engine_id)
            self.telemetry.stop_timer(f"engine:{engine.engine_id}")
            outputs[engine.engine_id] = result
            ctx.engine_outputs[engine.engine_id] = engine.export(result)
            self.audit.log(
                "engine_done",
                engine_id=engine.engine_id,
                ok=result.ok,
                errors=result.errors,
            )
        return outputs

    def process_lesson(
        self,
        lesson_text: str,
        *,
        override_api_key: str = "",
        feature_flags: dict[str, bool] | None = None,
        generate_adaptations: bool = True,
        source_envelope: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run the source-bound v3 lesson pipeline with optional enrichment."""
        import hashlib

        from engines.content_classifier import classify_source_blocks
        from engines.knowledge_ingestion_engine.universal_ingest import (
            ingest_source_bytes,
        )
        from engines.universal_lesson.profile import (
            build_universal_lesson_profile,
        )
        from engines.verified_learning_engine.result_envelope import (
            failed,
            partial,
            success,
        )

        if not source_envelope:
            source_envelope = ingest_source_bytes(
                "lesson.txt", (lesson_text or "").encode("utf-8")
            ).to_dict()
        lesson_text = str(source_envelope.get("text") or lesson_text or "")
        ctx = ExecutionContext.from_lesson(
            lesson_text,
            api_key=override_api_key,
            feature_flags=feature_flags or {},
        )
        ctx.source_envelope = source_envelope
        ctx.source_id = str(source_envelope.get("source_id") or "")
        self.audit.log("vlie_start", run_id=ctx.run_id)

        adaptations: dict[str, Any] | None = None
        outputs: dict[str, EngineResultBundle] = {}
        stage_results: list[dict[str, Any]] = []

        def stage(
            name: str,
            status: str,
            *,
            engine: str = "vlie",
            message: str = "",
            warnings: list[dict[str, Any]] | None = None,
            fallback_used: str = "none",
        ) -> None:
            digest = hashlib.sha256(
                f"{ctx.source_id}:{name}:{lesson_text[:1000]}".encode("utf-8")
            ).hexdigest()
            ctx.stage_input_hashes[name] = digest
            row = {
                "stage": name,
                "engine": engine,
                "status": status,
                "message": message,
                "warnings": warnings or [],
                "fallback_used": fallback_used,
                "run_id": ctx.run_id,
                "source_id": ctx.source_id,
                "input_hash": digest,
            }
            ctx.stage_status[name] = row
            ctx.audit_trail.append(row)
            stage_results.append(row)
            self.audit.log("stage_status", **row)

        if source_envelope.get("status") not in {"readable", "partial"} or not lesson_text.strip():
            issue = (source_envelope.get("errors") or [{}])[0]
            result = failed(
                "source_ingestion",
                "knowledge_ingestion",
                str(
                    issue.get("safe_message")
                    or issue.get("reason")
                    or "No readable educational content was found."
                ),
                code=str(issue.get("code") or "source_ingestion.unreadable"),
                retryable=bool(issue.get("retryable")),
                recovery=str(
                    issue.get("recovery")
                    or "Upload a readable educational source."
                ),
                fallback_used=str(issue.get("fallback_used") or "none"),
                audit_reference=ctx.run_id,
            )
            stage("source_ingestion", "failed", message=result.message)
            return {
                "run_id": ctx.run_id,
                "source_id": ctx.source_id,
                "adaptations": None,
                "package": None,
                "validation": {"ok": False, "errors": [result.message]},
                "pipeline_result": result.to_dict(),
                "stages": stage_results,
                "audit": self.audit.export(),
                "registry": self.registry.list_engines(),
            }

        stage(
            "source_ingestion",
            "partial" if source_envelope.get("warnings") else "success",
            engine="knowledge_ingestion",
            message="Readable source content extracted.",
            warnings=source_envelope.get("warnings") or [],
            fallback_used=(
                "local_ocr" if source_envelope.get("ocr_used") else "native_extraction"
            ),
        )
        ctx.classifications = classify_source_blocks(source_envelope)
        stage(
            "content_classification",
            "success",
            engine="content_classifier",
            message=f"Classified {len(ctx.classifications)} source blocks.",
        )
        profile = build_universal_lesson_profile(source_envelope).to_dict()
        ctx.universal_profile = profile
        ctx.curriculum_resolution = profile.get("curriculum_resolution") or {}
        ctx.topic = str(profile.get("topic") or "")
        ctx.board = str(ctx.curriculum_resolution.get("curriculum") or "unknown")
        ctx.meta.update(
            {
                "source_profile": profile,
                "curriculum_resolution": ctx.curriculum_resolution,
                "grounding_mode": "uploaded_source",
            }
        )
        stage(
            "universal_profile",
            "success",
            engine="universal_curriculum",
            message=(
                f"Source profile created; curriculum status is "
                f"{ctx.curriculum_resolution.get('status', 'unknown')}."
            ),
        )

        if generate_adaptations:
            post_generation_ids = {"learning_experience", "quality_assurance"}
            for engine in self.registry.execution_order(only_enabled=True):
                if engine.engine_id in post_generation_ids or engine.engine_id == "multi_agent":
                    continue
                self._emit(
                    f"VLIE · {engine.engine_id}: {stage_description(engine.engine_id)}",
                    0.05,
                )
                context = ctx.to_dict()
                context["engine_outputs"] = {
                    eid: {"ok": r.ok, "payload": r.payload, "errors": r.errors}
                    for eid, r in outputs.items()
                }
                try:
                    result = engine.process(context)
                    result = engine.validate(context, result)
                    result = engine.enrich(context, result)
                except Exception:
                    result = EngineResultBundle(
                        engine_id=engine.engine_id,
                        ok=False,
                        errors=["This optional planning stage could not complete."],
                    )
                outputs[engine.engine_id] = result
                ctx.engine_outputs[engine.engine_id] = engine.export(result)
                stage(
                    f"engine_{engine.engine_id}",
                    "success" if result.ok else "partial",
                    engine=engine.engine_id,
                    message=(
                        f"{engine.engine_id} completed."
                        if result.ok
                        else f"{engine.engine_id} used a scoped fallback."
                    ),
                    fallback_used="engine_plan_omitted" if not result.ok else "none",
                )

            self._emit("VLIE · Multi-Agent teaching generation…", 0.30)
            self.audit.log("teaching_start")
            from agents.orchestration import AloraOrchestrator

            teaching = AloraOrchestrator(on_progress=self.on_progress)
            try:
                adaptations = teaching.run_lesson_pipeline(
                    lesson_text,
                    override_api_key=override_api_key,
                    source_envelope=source_envelope,
                    universal_profile=profile,
                    grounding_mode="uploaded_source",
                )
            except Exception:
                result = failed(
                    "adaptation_generation",
                    "multi_agent",
                    "Required lesson adaptations could not be generated after retries.",
                    retryable=True,
                    recovery="Retry generation or verify the AI service configuration.",
                    fallback_used="bounded_retries_exhausted",
                    audit_reference=ctx.run_id,
                )
                stage(
                    "adaptation_generation",
                    "failed",
                    engine="multi_agent",
                    message=result.message,
                    fallback_used=result.fallback_used,
                )
                return {
                    "run_id": ctx.run_id,
                    "source_id": ctx.source_id,
                    "adaptations": None,
                    "package": None,
                    "validation": {"ok": False, "errors": [result.message]},
                    "pipeline_result": result.to_dict(),
                    "stages": stage_results,
                    "audit": self.audit.export(),
                    "registry": self.registry.list_engines(),
                }
            meta = adaptations.setdefault("_meta", {})
            meta["vlie_run_id"] = ctx.run_id
            meta["schema_version"] = "3.0.0"
            meta["source_envelope"] = source_envelope
            meta["universal_profile"] = profile
            meta["curriculum_resolution"] = ctx.curriculum_resolution
            meta["grounding_mode"] = "uploaded_source"
            meta["stage_status"] = ctx.stage_status
            meta["vlie_engine_outputs"] = {
                eid: {"ok": r.ok, "summary_keys": list((r.payload or {}).keys())[:12]}
                for eid, r in outputs.items()
            }
            stage(
                "adaptation_generation",
                "success",
                engine="multi_agent",
                message="Nine source-grounded adaptations generated.",
            )
            outputs["scientific_accuracy"] = EngineResultBundle(
                engine_id="scientific_accuracy",
                ok=bool((meta.get("stem_qa") or {}).get("passed", True)),
                payload={
                    "artifacts": meta.get("engine_artifacts") or [],
                    "preferred_visuals": meta.get("preferred_visuals") or [],
                    "biology_figures": meta.get("biology_figures") or [],
                    "stem": {
                        "artifacts": meta.get("engine_artifacts") or [],
                        "preferred_visuals": meta.get("preferred_visuals") or [],
                        "qa": meta.get("stem_qa") or {},
                    },
                },
                deterministic=True,
            )
            outputs["curriculum"] = EngineResultBundle(
                engine_id="curriculum",
                ok=True,
                payload={"knowledge": meta.get("knowledge") or {}},
            )
            outputs["quality_assurance"] = EngineResultBundle(
                engine_id="quality_assurance",
                ok=not bool((meta.get("publish_qa") or {}).get("publish_blocked")),
                payload=meta.get("publish_qa") or {},
                deterministic=True,
            )
            for engine in self.registry.execution_order(only_enabled=True):
                if engine.engine_id not in post_generation_ids:
                    continue
                context = ctx.to_dict()
                context["adaptations"] = adaptations
                context["engine_outputs"] = {
                    eid: {"ok": row.ok, "payload": row.payload}
                    for eid, row in outputs.items()
                }
                try:
                    post_result = engine.process(context)
                except Exception:
                    post_result = EngineResultBundle(
                        engine_id=engine.engine_id,
                        ok=False,
                        errors=["This post-generation stage could not complete."],
                    )
                if engine.engine_id != "quality_assurance":
                    outputs[engine.engine_id] = post_result
                stage(
                    f"engine_{engine.engine_id}",
                    "success" if post_result.ok else "partial",
                    engine=engine.engine_id,
                    message=f"{engine.engine_id} consumed completed adaptations.",
                    fallback_used="post_stage_omitted" if not post_result.ok else "none",
                )
            self.audit.log("teaching_done")
        else:
            outputs = self.run_engines(ctx)

        merged = self.merger.merge(outputs)
        package = self.packages.build(
            run_id=ctx.run_id,
            lesson_text=lesson_text,
            adaptations=adaptations,
            merged=merged,
            qa_report=(outputs.get("quality_assurance").payload if outputs.get("quality_assurance") else {}),
            audit=self.audit.export(),
        )
        validation = self.validator.validate_package(package)
        package["vlie_validation"] = validation
        package["schema_version"] = "3.0.0"
        package["source"] = source_envelope
        package["universal_profile"] = profile
        package["curriculum_resolution"] = ctx.curriculum_resolution
        package["stage_status"] = ctx.stage_status
        package["grounding_mode"] = "uploaded_source"
        package["lifecycle_state"] = (
            "validated" if validation.get("ok") else "review_required"
        )
        path = self.packages.persist(package)
        package["persisted_path"] = str(path)
        self.audit.log("vlie_complete", path=str(path), ok=validation.get("ok"))

        final_result = (
            success(
                "package",
                "vlie",
                payload={"package_id": package.get("package_id")},
                audit_reference=ctx.run_id,
            )
            if validation.get("ok")
            else partial(
                "package",
                "vlie",
                "The lesson is available for review with quality warnings.",
                payload={"package_id": package.get("package_id")},
                recovery="Review the listed quality warnings before official publication.",
                fallback_used="review_draft",
                audit_reference=ctx.run_id,
            )
        )
        stage(
            "package",
            "success" if validation.get("ok") else "partial",
            message=final_result.message,
            fallback_used=final_result.fallback_used,
        )
        return {
            "run_id": ctx.run_id,
            "source_id": ctx.source_id,
            "adaptations": adaptations,
            "package": package,
            "merged": merged,
            "validation": validation,
            "audit": self.audit.export(),
            "registry": self.registry.list_engines(),
            "pipeline_result": final_result.to_dict(),
            "stages": stage_results,
        }

    # ── Learning Session Orchestrator (LSO) ───────────────────────────────

    def create_session(
        self,
        *,
        learner_id: str = "anonymous",
        lesson_id: str = "",
        topic: str = "",
        workflow_id: str = "lesson_learning",
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        doc = self.sessions.create(
            learner_id=learner_id,
            lesson_id=lesson_id,
            topic=topic,
            workflow_id=workflow_id or self.config.workflow_default,
            meta=meta,
        )
        ev = self.bus.emit(
            "SessionCreated",
            session_id=doc["session_id"],
            learner_id=learner_id,
            lesson_id=doc.get("lesson_id") or "",
            payload={"workflow_id": doc.get("workflow_id")},
        )
        self.telemetry.record_event(ev.event_type)
        self.audit.log("session_created", session_id=doc["session_id"], learner=learner_id)
        return doc

    def resume_session(self, session_id: str) -> dict[str, Any]:
        doc = self.sessions.resume(session_id)
        self.bus.emit(
            "SessionResumed",
            session_id=session_id,
            learner_id=doc.get("learner_id") or "",
            lesson_id=doc.get("lesson_id") or "",
        )
        self.telemetry.record_event("SessionResumed")
        return doc

    def pause_session(self, session_id: str) -> dict[str, Any]:
        doc = self.sessions.pause(session_id)
        self.bus.emit(
            "SessionPaused",
            session_id=session_id,
            learner_id=doc.get("learner_id") or "",
            lesson_id=doc.get("lesson_id") or "",
        )
        self.telemetry.record_event("SessionPaused")
        return doc

    def close_session(self, session_id: str) -> dict[str, Any]:
        doc = self.sessions.close(session_id)
        self.bus.emit(
            "SessionClosed",
            session_id=session_id,
            learner_id=doc.get("learner_id") or "",
            lesson_id=doc.get("lesson_id") or "",
        )
        self.telemetry.record_event("SessionClosed")
        return doc

    def publish_event(
        self,
        event_type: str,
        *,
        session_id: str,
        payload: dict[str, Any] | None = None,
        learner_id: str = "",
        lesson_id: str = "",
    ) -> dict[str, Any]:
        doc = self.sessions.load(session_id) or {}
        learner_id = learner_id or doc.get("learner_id") or ""
        lesson_id = lesson_id or doc.get("lesson_id") or ""
        ev = self.bus.emit(
            event_type,
            session_id=session_id,
            learner_id=learner_id,
            lesson_id=lesson_id,
            payload=payload,
        )
        self.telemetry.record_event(event_type)
        orchestration_errors: list[dict[str, str]] = []
        if doc:
            try:
                self.sessions.apply_state_event(session_id, event_type)
            except Exception as exc:  # noqa: BLE001
                error = {
                    "operation": "apply_state_event",
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:500],
                }
                orchestration_errors.append(error)
                self.audit.log(
                    "event_state_update_failed",
                    session_id=session_id,
                    event_type=event_type,
                    **error,
                )
            stage_map = {
                "LessonLoaded": "lesson_loaded",
                "LessonOpened": "lesson_started",
                "LessonCompleted": "lesson_completed",
                "ReflectionCompleted": "reflection_completed",
                "AssessmentStarted": "assessment_started",
                "AssessmentCompleted": "assessment_submitted",
                "MasteryUpdated": "mastery_updated",
                "RecommendationGenerated": "recommendation_generated",
            }
            if event_type in stage_map:
                try:
                    self.sessions.set_stage(session_id, stage_map[event_type])
                except Exception as exc:  # noqa: BLE001
                    error = {
                        "operation": "set_stage",
                        "error_type": type(exc).__name__,
                        "error": str(exc)[:500],
                    }
                    orchestration_errors.append(error)
                    self.audit.log(
                        "event_stage_update_failed",
                        session_id=session_id,
                        event_type=event_type,
                        **error,
                    )
        result = ev.to_dict()
        if orchestration_errors:
            result["orchestration_errors"] = orchestration_errors
        return result

    def orchestrate_from_engines(
        self,
        session_id: str,
        engine_outputs: dict[str, Any],
        *,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Central LSO step: decisions → interventions → recommendations →
        schedule/notify/audit. Does not re-run domain engines.
        """
        # Guardrail: VLIE never invents official answers (policy check for audit)
        blocked = self.policies.assert_allowed("generate_official_answer")
        if blocked.get("allowed"):
            self.audit.log("policy_violation", reason="official_answers_must_be_blocked")

        decisions = self.decisions.decide(engine_outputs, context=context)
        interventions = self.interventions.from_decisions(decisions)
        for iv in interventions:
            self.telemetry.record_intervention(iv.get("kind") or "unknown")
            self.bus.emit(
                "InterventionTriggered",
                session_id=session_id,
                payload=iv,
            )
            self.memory.queue_intervention(session_id, iv)

        recs = self.recommendations.build(decisions=decisions, engine_outputs=engine_outputs)
        self.bus.emit(
            "RecommendationGenerated",
            session_id=session_id,
            payload={"recommendations": recs},
        )

        for d in decisions:
            self.audit.log_decision(
                session_id=session_id,
                learner=(self.sessions.load(session_id) or {}).get("learner_id") or "",
                lesson=(self.sessions.load(session_id) or {}).get("lesson_id") or "",
                event="OrchestrationDecision",
                engine=d.get("responsible_engine") or "vlie",
                decision=d.get("decision_type") or "",
                reason=d.get("reason") or "",
                confidence=d.get("confidence"),
                evidence=d.get("evidence") or [],
            )
            self.bus.emit("OrchestrationDecision", session_id=session_id, payload=d)

        doc = self.sessions.load(session_id)
        if doc:
            doc["decisions"] = (doc.get("decisions") or []) + decisions
            doc["recommendations"] = recs
            doc["engine_outputs_summary"] = {
                eid: list((block.get("payload") or block or {}).keys())[:8]
                if isinstance(block, dict)
                else []
                for eid, block in engine_outputs.items()
            }
            self.sessions._save(doc)
            try:
                self.sessions.set_stage(session_id, "recommendation_generated")
            except Exception:  # noqa: BLE001
                pass

            ale = engine_outputs.get("adaptive_learning") or {}
            payload = ale.get("payload") if isinstance(ale, dict) else {}
            spaced = (payload or {}).get("spaced_repetition") or []
            if spaced and self.config.flag("scheduler"):
                self.scheduler.from_ale_spaced_repetition(
                    spaced if isinstance(spaced, list) else [spaced],
                    learner_id=doc.get("learner_id") or "",
                    session_id=session_id,
                )

            if self.config.flag("notifications"):
                self.notifications.from_decisions(
                    decisions,
                    learner_id=doc.get("learner_id") or "",
                    teacher_id=(doc.get("meta") or {}).get("teacher_id") or "",
                    parent_id=(doc.get("meta") or {}).get("parent_id") or "",
                )

        return {
            "session_id": session_id,
            "decisions": decisions,
            "interventions": interventions,
            "recommendations": recs,
            "scheduled": self.scheduler.export()[-10:],
            "notifications": self.notifications.export()[-10:],
            "policies": self.policies.export(),
        }

    def advance_workflow(self, session_id: str) -> dict[str, Any]:
        doc = self.sessions.load(session_id)
        if not doc:
            raise FileNotFoundError(session_id)
        wf_data = doc.get("workflow") or {}
        wf = WorkflowManager(doc.get("workflow_id") or "lesson_learning")
        wf.index = int(wf_data.get("index") or 0)
        wf.completed = list(wf_data.get("completed") or [])
        result = wf.advance()
        engines = self.dependencies.plan_for_workflow_step(result.get("engines_next") or [])
        doc["workflow"] = wf.to_dict()
        self.sessions._save(doc)
        self.bus.emit(
            "WorkflowAdvanced",
            session_id=session_id,
            payload={**result, "engines_ordered": engines},
        )
        return {"session_id": session_id, **result, "engines_ordered": engines, "workflow": wf.to_dict()}

    def health_report(self) -> dict[str, Any]:
        return self.health.report(telemetry=self.telemetry.snapshot())

    def event_history(self, session_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        return self.bus.history(session_id=session_id, limit=limit)

    def session_timeline(self, session_id: str) -> dict[str, Any]:
        return self.sessions.timeline(session_id)


# Back-compat alias
VLIE = VerifiedLearningOrchestrator
