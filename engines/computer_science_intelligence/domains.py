"""Computer science domain detection — CT / programming / systems / AI family."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "computational_thinking": (
        "computational thinking",
        "decomposition",
        "pattern recognition",
        "abstraction",
        "algorithm design",
        "logical reasoning",
        "problem solving",
        "computational model",
    ),
    "programming": (
        "programming",
        "coding",
        "variable",
        "data type",
        "operator",
        "loop",
        "function",
        "recursion",
        "class",
        "object",
        "exception",
        "debugging",
        "pseudocode",
        "python",
        "java",
        "javascript",
    ),
    "algorithms": (
        "algorithm",
        "sorting",
        "searching",
        "complexity",
        "big o",
        "time complexity",
        "space complexity",
    ),
    "data_structures": (
        "data structure",
        "array",
        "linked list",
        "tree",
        "graph",
        "queue",
        "stack",
        "hash",
        "hashing",
    ),
    "databases": (
        "database",
        "sql",
        "relational",
        "er model",
        "normalisation",
        "normalization",
        "transaction",
        "query",
        "schema",
    ),
    "networking": (
        "network",
        "networking",
        "protocol",
        "tcp",
        "ip",
        "dns",
        "routing",
        "osi",
        "internet",
        "packet",
    ),
    "operating_systems": (
        "operating system",
        "process",
        "thread",
        "memory management",
        "file system",
        "scheduler",
        "kernel",
    ),
    "cybersecurity": (
        "cybersecurity",
        "security",
        "encryption",
        "authentication",
        "firewall",
        "secure coding",
        "cyber hygiene",
        "digital citizenship",
        "phishing",
    ),
    "web_development": (
        "web development",
        "html",
        "css",
        "http",
        "frontend",
        "backend",
        "api",
        "rest",
    ),
    "artificial_intelligence": (
        "artificial intelligence",
        "ai concept",
        "neural network",
        "ethical ai",
        "responsible ai",
        "prompt engineering",
        "data bias",
    ),
    "machine_learning": (
        "machine learning",
        "supervised",
        "unsupervised",
        "training data",
        "model",
        "feature",
        "overfitting",
    ),
    "robotics": (
        "robotics",
        "robot",
        "sensor",
        "actuator",
        "control system",
    ),
    "cloud_computing": (
        "cloud computing",
        "cloud",
        "saas",
        "iaas",
        "paas",
        "virtualisation",
        "virtualization",
        "container",
    ),
    "digital_literacy": (
        "digital literacy",
        "digital skills",
        "online safety",
        "media literacy",
        "information literacy",
    ),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("computational_thinking", "programming"),
    ("programming", "algorithms"),
    ("programming", "data_structures"),
    ("data_structures", "algorithms"),
    ("algorithms", "databases"),
    ("networking", "cybersecurity"),
    ("programming", "web_development"),
    ("databases", "web_development"),
    ("artificial_intelligence", "machine_learning"),
    ("computational_thinking", "artificial_intelligence"),
    ("programming", "operating_systems"),
    ("networking", "cloud_computing"),
    ("digital_literacy", "cybersecurity"),
    ("programming", "robotics"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="computer_science_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="computer_science_domain",
        provenance="computer_science_intelligence",
    )
