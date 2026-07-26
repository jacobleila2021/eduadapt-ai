"""Computer science misconceptions — SICS catalogue detection."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

COMPUTER_SCIENCE_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "cs.equals_assigns",
        "label": "Equals means mathematical equality in code",
        "domain": "programming",
        "patterns": [
            r"=\s*(means|is)\s*(math(ematical)?\s*)?equal",
            r"equals?\s*means\s*(math(ematical)?\s*)?equal",
            r"assignment\s*(is\s*)?(the\s*)?same\s*as\s*equality",
            r"equals?\s*sign\s*(always\s*)?compares",
        ],
        "correction": "In most languages `=` assigns; comparison uses `==` / `===` / `equals`. Separate state change from testing equality.",
        "related_concepts": ["variables", "operators", "boolean"],
    },
    {
        "misconception_id": "cs.loop_runs_once",
        "label": "A loop body runs only once",
        "domain": "programming",
        "patterns": [
            r"loops?\s*(only\s*)?run\s*once",
            r"for\s*loop\s*(executes|runs)\s*(just\s*)?one\s*time",
        ],
        "correction": "Loop bodies repeat while the condition holds; use a trace table to see each iteration.",
        "related_concepts": ["loops", "trace_tables", "control_flow"],
    },
    {
        "misconception_id": "cs.o_n_always_slow",
        "label": "Big-O O(n) always means slow",
        "domain": "algorithms",
        "patterns": [
            r"o\s*\(\s*n\s*\)\s*(is\s*)?(always\s*)?slow",
            r"linear\s*(is\s*)?(always\s*)?bad",
            r"big\s*o\s*(means\s*)?runtime\s*on\s*(my|this)\s*machine",
        ],
        "correction": "Big-O describes growth rate as input size grows, not wall-clock time on one machine; compare asymptotics and constants carefully.",
        "related_concepts": ["complexity", "big_o", "scalability"],
    },
    {
        "misconception_id": "cs.array_equals_list",
        "label": "Array and linked list are the same",
        "domain": "data_structures",
        "patterns": [
            r"arrays?\s*(and|&)\s*linked\s*lists?\s*(are\s*)?(the\s*)?same",
            r"list\s*(is\s*)?(always\s*)?(an\s*)?array",
        ],
        "correction": "Arrays give indexed access; linked lists favour insert/delete at known nodes—trade-offs differ.",
        "related_concepts": ["arrays", "linked_lists", "tradeoffs"],
    },
    {
        "misconception_id": "cs.sql_select_star_fine",
        "label": "SELECT * is always fine",
        "domain": "databases",
        "patterns": [
            r"select\s*\*\s*(is\s*)?(always\s*)?(fine|ok|best)",
            r"never\s*need\s*to\s*name\s*columns",
        ],
        "correction": "Prefer explicit columns for clarity, performance, and schema change safety; * is a teaching shortcut, not a default.",
        "related_concepts": ["sql", "queries", "schema"],
    },
    {
        "misconception_id": "cs.internet_is_cloud",
        "label": "The Internet and the cloud are the same thing",
        "domain": "networking",
        "patterns": [
            r"internet\s*(is\s*)?(the\s*)?same\s*as\s*(the\s*)?cloud",
            r"cloud\s*=\s*internet",
        ],
        "correction": "The Internet is a global network; cloud services are remote compute/storage products delivered over networks.",
        "related_concepts": ["networking", "cloud_computing"],
    },
    {
        "misconception_id": "cs.https_means_safe_site",
        "label": "HTTPS means a website is trustworthy",
        "domain": "cybersecurity",
        "patterns": [
            r"https\s*(means|proves)\s*(the\s*)?(site|website)\s*(is\s*)?(safe|trusted|trustworthy)",
            r"padlock\s*(means\s*)?(safe|legit)",
        ],
        "correction": "HTTPS encrypts transit; it does not prove honesty. Still verify identity, permissions, and phishing cues.",
        "related_concepts": ["encryption", "authentication", "cyber_hygiene"],
    },
    {
        "misconception_id": "cs.ai_thinks_like_humans",
        "label": "AI systems think and understand like humans",
        "domain": "artificial_intelligence",
        "patterns": [
            r"ai\s*(thinks|understands)\s*(like\s*)?(a\s*)?human",
            r"neural\s*networks?\s*(have\s*)?(real\s*)?consciousness",
            r"models?\s*(truly\s*)?know\s*what\s*they\s*(say|mean)",
        ],
        "correction": "School AI topics treat systems as statistical / rule-based tools with limits, bias, and no human understanding—stress responsible use.",
        "related_concepts": ["ethical_ai", "machine_learning", "data_bias"],
    },
    {
        "misconception_id": "cs.ml_more_data_always",
        "label": "More training data always improves ML models",
        "domain": "machine_learning",
        "patterns": [
            r"more\s*data\s*(always|guarantees)\s*(better|improves)",
            r"just\s*add\s*more\s*(training\s*)?data",
        ],
        "correction": "Quality, representativeness, and leakage matter; noisy or biased data can hurt performance and fairness.",
        "related_concepts": ["training_data", "bias", "overfitting"],
    },
)


def detect_computer_science_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    return detect_from_catalogue(
        COMPUTER_SCIENCE_MISCONCEPTIONS,
        text,
        provenance="computer_science_intelligence.misconceptions",
        limit=limit,
    )
