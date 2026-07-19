"""Scientific Accuracy Engine — facade over Subject Tool Router / lesson STEM pipeline."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class ScientificAccuracyEngine(BaseEngine):
    engine_id = "scientific_accuracy"
    version = "1.0.0"
    layer = "computation"
    priority = 20

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.lesson_pipeline import process_lesson_stem
            from engines.visualization.priority import has_deterministic_visuals

            lesson = context.get("lesson_text") or ""
            topic = context.get("topic") or ""
            # Prefer topic from curriculum engine output if present
            curr = (context.get("engine_outputs") or {}).get("curriculum") or {}
            if isinstance(curr, dict):
                topic = topic or (curr.get("payload") or {}).get("knowledge", {}).get("book_title") or topic

            stem = process_lesson_stem(lesson, topic=str(topic or ""))
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=bool(stem.get("qa", {}).get("passed", True)),
                payload={
                    "stem": stem,
                    "artifacts": stem.get("artifacts") or [],
                    "preferred_visuals": stem.get("preferred_visuals") or [],
                    "biology_figures": stem.get("biology_figures") or [],
                    "prompt_block": stem.get("prompt_block") or "",
                    "has_deterministic_visuals": has_deterministic_visuals(
                        stem.get("preferred_visuals") or []
                    ),
                },
                assets=[
                    p
                    for v in (stem.get("preferred_visuals") or [])
                    for p in (v.get("asset_paths") or [])
                ],
                errors=[stem.get("qa", {}).get("blocked_reason")] if stem.get("qa", {}).get("publish_blocked") else [],
                deterministic=True,
            )
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)], deterministic=True)

    def health_check(self) -> EngineHealth:
        deps = {}
        for name, mod in (
            ("sympy", "sympy"),
            ("numpy", "numpy"),
            ("matplotlib", "matplotlib"),
        ):
            try:
                __import__(mod)
                deps[name] = True
            except ImportError:
                deps[name] = False
        return EngineHealth(
            ok=all(deps.values()),
            engine_id=self.engine_id,
            version=self.version,
            dependencies=deps,
            detail="Wraps engines.router + lesson_pipeline",
        )
