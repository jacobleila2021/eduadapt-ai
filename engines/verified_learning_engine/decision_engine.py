"""Central orchestration decisions — VLIE decides; engines supply expertise."""

from __future__ import annotations

from typing import Any
import uuid

from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DecisionEngine:
    """
    Runtime decision rules. Does not reimplement AME/ALE/AIE/ATIE logic —
    reads their payloads and emits orchestration directives.
    """

    def decide(self, engine_outputs: dict[str, Any], *, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        context = context or {}
        decisions: list[dict[str, Any]] = []

        def payload(eid: str) -> dict[str, Any]:
            block = engine_outputs.get(eid) or {}
            if isinstance(block, dict):
                return block.get("payload") or block
            return {}

        ame = payload("assessment")
        aie = payload("accessibility")
        ale = payload("adaptive_learning")
        atie = payload("ai_tutor")
        laie = payload("learning_analytics")

        mastery = ale.get("learner_model") or ame.get("mastery") or {}
        at_risk = mastery.get("concepts_at_risk") or []
        if isinstance(at_risk, list) and at_risk and isinstance(at_risk[0], dict):
            at_risk = [x.get("concept_id") for x in at_risk]
        conf = float(
            (ale.get("confidence") or {}).get("confidence")
            if isinstance(ale.get("confidence"), dict)
            else (mastery.get("confidence") or (ame.get("exam_readiness") or {}).get("confidence_level") or 0.5)
        )
        preds = ale.get("predictions") or laie.get("predictions") or {}
        misc = ame.get("misconceptions") or ale.get("misconceptions") or []

        # If mastery < threshold → ALE remediation
        if at_risk or float(preds.get("risk_of_failure") or 0) >= 0.55:
            decisions.append(
                self._row(
                    "remediation",
                    "ALE recommends remediation pathway",
                    responsible_engine="adaptive_learning",
                    evidence=[{"at_risk": at_risk, "risk": preds.get("risk_of_failure")}],
                    confidence=0.85,
                    action={"workflow_hint": "exam_revision", "call": "adaptive_learning"},
                )
            )

        # Confidence drop → ATIE guided discovery
        if conf < 0.45:
            decisions.append(
                self._row(
                    "tutor_mode",
                    "ATIE switches toward guided discovery / scaffolding",
                    responsible_engine="ai_tutor",
                    evidence=[{"confidence": conf}],
                    confidence=0.8,
                    action={"tutor_mode": "guided_discovery", "require_socratic": conf < 0.35},
                )
            )

        # Repeated help / misconceptions → AIE alt presentation + AME intervention
        if len(misc) >= 1:
            decisions.append(
                self._row(
                    "misconception_intervention",
                    "AME supplies targeted intervention; AIE may adjust presentation",
                    responsible_engine="assessment",
                    evidence=[{"misconceptions": misc[:3]}],
                    confidence=0.82,
                    action={"call": ["assessment", "accessibility"], "intervention": True},
                )
            )

        profiles = (aie.get("learner_profile") or {}).get("active_profiles") or aie.get("profiles_generated") or []
        help_count = int(context.get("help_requests") or 0)
        if help_count >= 3 or (profiles and conf < 0.5):
            decisions.append(
                self._row(
                    "presentation_adjust",
                    "AIE recommends alternative presentation (facts locked)",
                    responsible_engine="accessibility",
                    evidence=[{"help_requests": help_count, "profiles": profiles}],
                    confidence=0.78,
                    action={"call": "accessibility", "presentation_only": True},
                )
            )

        # Mastery achieved → enrichment
        mastered = mastery.get("concepts_mastered") or []
        if mastered and not at_risk and conf >= 0.75:
            decisions.append(
                self._row(
                    "enrichment",
                    "ALE unlocks enrichment",
                    responsible_engine="adaptive_learning",
                    evidence=[{"mastered": mastered[:5], "confidence": conf}],
                    confidence=0.8,
                    action={"call": "adaptive_learning", "pathway_type": "enrichment"},
                )
            )

        # Engagement fall → gamification notify
        eng_risk = float(preds.get("risk_of_disengagement") or preds.get("engagement_decline_risk") or 0)
        if eng_risk >= 0.55:
            decisions.append(
                self._row(
                    "engagement",
                    "Notify Gamification module for intrinsic motivation hooks",
                    responsible_engine="gamification",
                    evidence=[{"engagement_risk": eng_risk}],
                    confidence=0.7,
                    action={"call": "gamification"},
                )
            )

        if not decisions:
            decisions.append(
                self._row(
                    "continue",
                    "Continue current workflow — no critical triggers",
                    responsible_engine="vlie",
                    evidence=[],
                    confidence=0.6,
                    action={"continue": True},
                )
            )
        return decisions

    def _row(
        self,
        decision_type: str,
        reason: str,
        *,
        responsible_engine: str,
        evidence: list[dict[str, Any]],
        confidence: float,
        action: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "decision_id": f"dec_{uuid.uuid4().hex[:8]}",
            "decision_type": decision_type,
            "reason": reason,
            "responsible_engine": responsible_engine,
            "evidence": evidence,
            "confidence": confidence,
            "action": action,
            "ts": _now(),
            "explainable": True,
            "teacher_override_allowed": True,
        }
