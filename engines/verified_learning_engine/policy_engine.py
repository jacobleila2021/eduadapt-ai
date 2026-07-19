"""Central policy engine — orchestration guardrails."""

from __future__ import annotations

from typing import Any

DEFAULT_POLICIES = {
    "no_ai_explanation_before_curriculum_retrieval": True,
    "never_generate_official_answers": True,
    "always_validate_stem_via_deterministic_engines": True,
    "teacher_override_always_available": True,
    "accessibility_overrides_presentation_only": True,
    "engines_must_not_call_each_other": True,
    "retrieve_before_tutor_generate": True,
    "insights_must_not_mutate_content": True,
}


class PolicyEngine:
    def __init__(self, overrides: dict[str, Any] | None = None) -> None:
        self.policies = {**DEFAULT_POLICIES, **(overrides or {})}

    def get(self, key: str, default: Any = None) -> Any:
        return self.policies.get(key, default)

    def assert_allowed(self, action: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        if action == "generate_official_answer" and self.policies.get("never_generate_official_answers"):
            return {"allowed": False, "reason": "Policy: never generate official answers"}
        if action == "tutor_without_retrieval" and self.policies.get("retrieve_before_tutor_generate"):
            if not context.get("grounding_ok"):
                return {"allowed": False, "reason": "Policy: retrieve before tutor generate"}
        if action == "mutate_curriculum" and self.policies.get("accessibility_overrides_presentation_only"):
            return {"allowed": False, "reason": "Accessibility may only change presentation"}
        return {"allowed": True, "reason": "ok"}

    def export(self) -> dict[str, Any]:
        return dict(self.policies)
