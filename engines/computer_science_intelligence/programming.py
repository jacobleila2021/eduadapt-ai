"""Programming intelligence metadata — never invents assessment answers."""

from __future__ import annotations

from typing import Any

from engines.computer_science_intelligence._focus import build_focus_metadata

PROGRAMMING_FOCI: tuple[dict[str, str], ...] = (
    {"id": "variables", "label": "Variables"},
    {"id": "data_types", "label": "Data types"},
    {"id": "operators", "label": "Operators"},
    {"id": "loops", "label": "Loops"},
    {"id": "functions", "label": "Functions"},
    {"id": "recursion", "label": "Recursion"},
    {"id": "classes", "label": "Classes"},
    {"id": "objects", "label": "Objects"},
    {"id": "exception_handling", "label": "Exception handling"},
    {"id": "modular_programming", "label": "Modular programming"},
    {"id": "testing", "label": "Testing"},
    {"id": "debugging", "label": "Debugging"},
)


def programming_metadata(
    text: str,
    domains: list[dict[str, Any]],
    *,
    exam_mode: bool = False,
) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=PROGRAMMING_FOCI,
        text=text,
        domains=domains,
        domain_keys={"programming"},
        provenance="computer_science_intelligence.programming",
        default_count=8,
        extra={
            "scaffolds": [
                "trace_table",
                "pseudocode_first",
                "incremental_testing",
                "rubber_duck_debug",
            ],
            "reveals_assessment_answers": False,
            "exam_mode": exam_mode,
            "interactive_code_viewer": True,
        },
    )
