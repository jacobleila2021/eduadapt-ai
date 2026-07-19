"""Repeatable, network-free production benchmark for Alora core paths."""

from __future__ import annotations

import json
import time
import tracemalloc


def _timed(name, fn):
    started = time.perf_counter()
    value = fn()
    return {
        "name": name,
        "seconds": round(time.perf_counter() - started, 4),
        "result": value,
    }


def main() -> None:
    tracemalloc.start()

    def deterministic():
        from engines.router import route
        from engines.types import TaskKind, ToolTask

        tasks = [
            ToolTask(TaskKind.SOLVE_MATH, {"expression": "2*x + 3 = 11"}),
            ToolTask(
                TaskKind.CALCULATE_FORCE,
                {"problem": "Force 100 N, area 0.5 m^2, calculate pressure P=F/A"},
            ),
            ToolTask(TaskKind.BALANCE_EQUATION, {"equation": "H2 + O2 -> H2O"}),
        ]
        results = [route(task) for task in tasks]
        return {"passed": sum(bool(result.ok) for result in results), "total": len(results)}

    def out_of_scope():
        from knowledge.service import prepare_knowledge_for_lesson

        result = prepare_knowledge_for_lesson(
            "Grade Level: 8 | Subject: English\nThe narrator reflects on pressure.",
            {"topic": "Narrative voice", "grade_level": "8"},
        )
        return {
            "scope_matched": result.get("scope_matched"),
            "hits": len(result.get("rag_hits") or []),
        }

    def index_health():
        from knowledge.service import ensure_knowledge_index

        return ensure_knowledge_index()

    results = [
        _timed("deterministic_stem_three_tasks", deterministic),
        _timed("out_of_scope_retrieval", out_of_scope),
        _timed("knowledge_index_health", index_health),
        _timed("knowledge_index_health_warm", index_health),
    ]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    report = {
        "schema": "alora-production-benchmark/1.0",
        "network_calls": 0,
        "results": results,
        "memory": {
            "current_mib": round(current / 1024 / 1024, 2),
            "peak_mib": round(peak / 1024 / 1024, 2),
        },
    }
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
