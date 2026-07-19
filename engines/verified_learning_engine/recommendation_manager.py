"""Next-best-action recommendations — priority, confidence, evidence, engine."""

from __future__ import annotations

from typing import Any
import uuid


class RecommendationManager:
    ACTIONS = (
        "continue_lesson",
        "review_prerequisite",
        "start_revision",
        "practice_questions",
        "watch_animation",
        "use_ai_tutor",
        "ask_teacher",
        "repeat_assessment",
        "advance_next_lesson",
    )

    def build(
        self,
        *,
        decisions: list[dict[str, Any]],
        engine_outputs: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        engine_outputs = engine_outputs or {}
        recs: list[dict[str, Any]] = []

        def add(action: str, reason: str, engine: str, evidence: list, priority: int, confidence: float) -> None:
            recs.append(
                {
                    "recommendation_id": f"rec_{uuid.uuid4().hex[:8]}",
                    "action": action,
                    "priority": priority,
                    "confidence": confidence,
                    "supporting_evidence": evidence,
                    "responsible_engine": engine,
                    "reason": reason,
                }
            )

        for d in decisions:
            dt = d.get("decision_type")
            if dt == "remediation":
                add("start_revision", d.get("reason") or "", "adaptive_learning", d.get("evidence") or [], 10, float(d.get("confidence") or 0.8))
                add("use_ai_tutor", "Guided remediation with ATIE", "ai_tutor", d.get("evidence") or [], 15, 0.8)
            elif dt == "tutor_mode":
                add("use_ai_tutor", d.get("reason") or "", "ai_tutor", d.get("evidence") or [], 12, float(d.get("confidence") or 0.8))
            elif dt == "misconception_intervention":
                add("practice_questions", "Targeted practice after misconception", "assessment", d.get("evidence") or [], 14, 0.82)
            elif dt == "enrichment":
                add("advance_next_lesson", d.get("reason") or "", "adaptive_learning", d.get("evidence") or [], 30, 0.8)
            elif dt == "engagement":
                add("continue_lesson", "Re-engage with short chunk", "gamification", d.get("evidence") or [], 20, 0.7)

        # Pull ALE next activity if present
        ale = (engine_outputs.get("adaptive_learning") or {})
        payload = ale.get("payload") if isinstance(ale, dict) else {}
        next_act = (payload or {}).get("next_activity") if isinstance(payload, dict) else None
        if next_act:
            add(
                "continue_lesson",
                f"ALE next: {next_act.get('concept_id') or next_act.get('activity_type')}",
                "adaptive_learning",
                [{"next_activity": next_act}],
                18,
                0.85,
            )

        if not recs:
            add("continue_lesson", "Default progression", "vlie", [], 50, 0.6)

        recs.sort(key=lambda r: r["priority"])
        return recs
