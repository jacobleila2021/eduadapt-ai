"""Validation helpers for subject packs — ULIQE remains certifier."""

from __future__ import annotations

from typing import Any, Mapping

from engines.subject_intelligence_core.shared_models import FindingSeed


def finding_seed(
    rule_id: str,
    severity: str,
    message: str,
    *,
    category: str = "pedagogy",
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return FindingSeed(
        rule_id=rule_id,
        severity=severity,
        message=message,
        category=category,
        evidence=dict(evidence or {}),
    ).to_dict()


def validate_metadata_shape(payload: Mapping[str, Any], required_keys: tuple[str, ...]) -> dict[str, Any]:
    missing = [k for k in required_keys if k not in payload]
    return {"ok": not missing, "missing": missing}


def validate_misconception_rows(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    required = ("misconception_id", "label", "correction_strategy", "provenance")
    bad: list[str] = []
    for i, row in enumerate(rows):
        for key in required:
            if key not in row:
                bad.append(f"row[{i}].{key}")
    return {"ok": not bad, "errors": bad}


def validate_diagram_rows(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    required = ("visual_type", "label", "provenance")
    bad: list[str] = []
    for i, row in enumerate(rows):
        for key in required:
            if key not in row:
                bad.append(f"row[{i}].{key}")
    return {"ok": not bad, "errors": bad}


def validate_accessibility_rows(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    required = ("recommendation", "detail", "owner")
    bad: list[str] = []
    for i, row in enumerate(rows):
        for key in required:
            if key not in row:
                bad.append(f"row[{i}].{key}")
    return {"ok": not bad, "errors": bad}


def validate_competency_graph(graph: Mapping[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    ok = isinstance(nodes, list) and isinstance(edges, list)
    return {"ok": ok, "node_count": len(nodes or []), "edge_count": len(edges or [])}


def map_seed_severity_to_uliqe_cap(severity: str) -> str:
    """CIP/PIP/BIP/MIP additive seeds never escalate ULIQE beyond WARNING."""
    raw = (severity or "info").lower()
    if raw in {"error", "critical"}:
        return "warning"
    if raw in {"info", "warning"}:
        return raw
    return "info"
