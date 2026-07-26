"""Mathematics misconception library — pattern detection only; no invented curriculum."""

from __future__ import annotations

from typing import Any

# Curated pedagogical bank (not board-specific). Patterns match learner/source text.
MATH_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "math.frac_larger_denominator",
        "label": "Larger denominator means larger fraction",
        "domain": "arithmetic",
        "patterns": [
            r"bigger denominator.*bigger",
            r"1/8\s*(is\s*)?(greater|bigger|>)\s*1/4",
            r"larger bottom.*larger fraction",
        ],
        "correction": "Compare fractions with common denominators or number-line placement; more parts can mean smaller pieces.",
        "related_concepts": ["fractions", "comparison"],
    },
    {
        "misconception_id": "math.negative_smaller_absolute",
        "label": "Negative numbers with larger absolute value are greater",
        "domain": "number_systems",
        "patterns": [
            r"-5\s*(is\s*)?(greater|bigger|>)\s*-2",
            r"negatives.*bigger absolute.*greater",
        ],
        "correction": "On the number line, numbers farther left are smaller; −5 < −2.",
        "related_concepts": ["integers", "number_line"],
    },
    {
        "misconception_id": "math.place_value_digit",
        "label": "Place value treated as digit value only",
        "domain": "arithmetic",
        "patterns": [
            r"tens?\s*=\s*ones?",
            r"ignore place value",
            r"3 in 30\s*is\s*just\s*3",
        ],
        "correction": "Emphasize place-value charts: digit × place (tens, hundreds).",
        "related_concepts": ["place_value"],
    },
    {
        "misconception_id": "math.algebra_sign_distribution",
        "label": "Sign errors when distributing negatives",
        "domain": "algebra",
        "patterns": [
            r"-\s*\(\s*x\s*\+\s*y\s*\)\s*=\s*-x\s*\+\s*y",
            r"forget to change both signs",
            r"distribute only first term",
        ],
        "correction": "Distribute the negative to every term: −(x + y) = −x − y.",
        "related_concepts": ["distributive_property", "signed_numbers"],
    },
    {
        "misconception_id": "math.equation_balance_oneside",
        "label": "Operations applied to one side only",
        "domain": "algebra",
        "patterns": [
            r"only (add|subtract|multiply|divide).*(one|left|right) side",
            r"move term without inverse",
        ],
        "correction": "Whatever is done to one side must be done to the other to keep equality.",
        "related_concepts": ["equations", "balance"],
    },
    {
        "misconception_id": "math.order_operations",
        "label": "Left-to-right ignoring order of operations",
        "domain": "arithmetic",
        "patterns": [
            r"bodmas.*ignore",
            r"pemdas.*left to right only",
            r"2\s*\+\s*3\s*\*\s*4\s*=\s*20",
        ],
        "correction": "Apply brackets/exponents, then ×÷, then +− (BODMAS/PEMDAS).",
        "related_concepts": ["order_of_operations"],
    },
    {
        "misconception_id": "math.ratio_vs_fraction",
        "label": "Ratio conflated with fraction part-whole",
        "domain": "arithmetic",
        "patterns": [
            r"ratio\s*is\s*(the\s*)?same\s*as\s*fraction",
            r"3:2\s*=\s*3/5\s*always",
        ],
        "correction": "Ratios compare parts; fractions often mean part-of-whole — clarify the whole.",
        "related_concepts": ["ratio", "proportion", "fractions"],
    },
    {
        "misconception_id": "math.area_vs_perimeter",
        "label": "Area and perimeter swapped",
        "domain": "geometry",
        "patterns": [
            r"area\s*=\s*add\s*sides",
            r"perimeter\s*=\s*length\s*\*\s*width",
            r"confus(e|ion).*area.*perimeter",
        ],
        "correction": "Perimeter = boundary length; area = region covered (square units).",
        "related_concepts": ["area", "perimeter"],
    },
    {
        "misconception_id": "math.function_vertical",
        "label": "Function as calculation only; ignores input–output rule",
        "domain": "algebra",
        "patterns": [
            r"function\s*is\s*just\s*a\s*formula",
            r"any\s*graph\s*is\s*a\s*function",
            r"vertical line.*still function",
        ],
        "correction": "A function assigns each valid input exactly one output (vertical-line test).",
        "related_concepts": ["functions", "graphs"],
    },
)


def detect_math_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

    return detect_from_catalogue(
        MATH_MISCONCEPTIONS,
        text,
        provenance="mathematics_intelligence.misconceptions",
        limit=limit,
    )
